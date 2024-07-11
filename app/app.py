from flask import Flask, request, jsonify, redirect
from faster_whisper import WhisperModel
from flask_cors import CORS
from dotenv import load_dotenv
import os, traceback, random, string, logging, colorlog
from models.Response import Response as ApiResponse
from time import time

load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
SERVER_ADDRESS = os.getenv("SERVER_ADDRESS", "0.0.0.0")
SERVER_PORT = os.getenv("SERVER_PORT", 5000)
DEVICE = os.getenv("DEVICE", "cpu")
MODELS = os.getenv("OLLAMA_API_URL", "tiny,small").split(",")
AUDIO_FILES_FOLDER = os.getenv("AUDIO_FILES_FOLDER", "/tmp")

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "/tmp"
CORS(app)

# Configure colored logging
handler = colorlog.StreamHandler()
formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    log_colors={
        "DEBUG": "white",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    },
)
handler.setFormatter(formatter)
logger = colorlog.getLogger()
logger.addHandler(handler)
logger.setLevel(LOG_LEVEL)

ApiResponse.set_logger(logger)

# Initialize WhisperModel with each model size
whisper_models = {}
for model in MODELS:
    logger.debug(f">>> Loading Whisper model {model}")
    whisper_models[model] = WhisperModel(model.strip(), device=DEVICE)

# Directory to save uploaded files
UPLOAD_FOLDER = AUDIO_FILES_FOLDER  # Save files in /tmp directory
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Supported file extensions for transcription
SUPPORTED_EXTENSIONS = ["mp3", "wav", "ogg", "webm"]


def allowed_file(filename):
    return (
        "." in filename and filename.rsplit(".", 1)[1].lower() in SUPPORTED_EXTENSIONS
    )


@app.before_request
def log_request_info():
    logger.debug(
        f"Started processing {request.method} request from {request.remote_addr} => {request.url}"
    )
    if request.path.endswith("/") and request.path != "/":
        return redirect(request.path[:-1], code=308)
    request.start_time = time()


@app.after_request
def add_header(response):
    if hasattr(request, "start_time"):
        elapsed_time = time() - request.start_time
        response.headers["X-Elapsed-Time"] = str(elapsed_time)
        response.headers["Access-Control-Expose-Headers"] = "X-Elapsed-Time"
    return response


@app.teardown_request
def log_teardown(exception=None):
    if exception:
        logger.error(f"Exception occurred: {exception}")
    logger.debug(
        f"Finished processing {request.method} request from {request.remote_addr} => {request.url}"
    )


@app.route("/")
def home():
    payload_response = ApiResponse.payload(
        True, 200, "Fast Whisper API", {"models": MODELS, "device": DEVICE}
    )
    return ApiResponse.output(payload_response, 200)


@app.route("/v1/audio/transcriptions", methods=["POST"])
def transcribe_audio():

    if "file" not in request.files:
        payload_response = ApiResponse.payload(
            False, 400, "File parameter is required."
        )
        return ApiResponse.output(payload_response, 400)

    VALID_PARAMS = ["model", "language"]
    invalid_params = [
        param for param in request.form.keys() if param not in VALID_PARAMS
    ]

    if invalid_params:
        payload_response = ApiResponse.payload(
            False,
            400,
            f"Invalid parameters: {', '.join(invalid_params)} ,supported params are {','.join(VALID_PARAMS)}",
        )
        return ApiResponse.output(payload_response, 400)

    file = request.files["file"]
    model = request.form.get("model", MODELS[0])
    language = request.form.get("language", "en")
    # response_format = request.form.get("response_format", "json")

    if model not in MODELS:
        payload_response = ApiResponse.payload(
            False,
            400,
            f"Invalid model parameter {model} , supported models are {','.join(MODELS)}",
        )
        return ApiResponse.output(payload_response, 400)

    file_extension = (
        file.filename.rsplit(".", 1)[1].lower() if "." in file.filename else ""
    )

    if file_extension not in SUPPORTED_EXTENSIONS:
        payload_response = ApiResponse.payload(
            False,
            400,
            f"Unsupported file format {file_extension} , suppported extensions are {','.join(SUPPORTED_EXTENSIONS)}",
        )
        return ApiResponse.output(payload_response, 400)

    random_name = "".join(random.choices(string.ascii_letters + string.digits, k=16))
    filename = f"{random_name}.{file_extension}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)
    try:
        segments, info = whisper_models[model].transcribe(file_path, language=language)
        if segments:
            segments_list = list(segments)
            if segments_list:
                print(segments_list)
                transcription = segments_list[0].text.strip()

        payload_response = ApiResponse.transcription(
            True, 200, "Successfully converted text to speech", transcription
        )
        return ApiResponse.output(payload_response, 200)

    except Exception as e:

        app.logger.error(f" > Error: {str(e)}")

        if LOG_LEVEL == "DEBUG":
            app.logger.error(traceback.format_exc())

        payload_response = ApiResponse.payload(False, 500, "Internal Server Error")
        return ApiResponse.output(payload_response, 500)


# Handle 404 errors
@app.errorhandler(404)
def page_not_found(error):

    msg = f" > No service is associated with the url => {request.method}:{request.url}"
    app.logger.error(msg)
    payload_response = ApiResponse.not_found(msg, {})
    return ApiResponse.output(payload_response, 404)


if __name__ == "__main__":
    app.run(debug=True, host=SERVER_ADDRESS, port=SERVER_PORT)
