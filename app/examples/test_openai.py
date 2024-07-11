from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

SERVER_PORT = os.getenv("SERVER_PORT", 5000)
MODELS = os.getenv("OLLAMA_API_URL", "tiny,small").split(",")

url = f"http://localhost:{SERVER_PORT}/v1"
file_path = "speech.mp3"
model = MODELS[0]
language = "en"

client = OpenAI(
    api_key="not-used",
    base_url=url,
)

extra_body = {"language": language}
audio_file = open(file_path, "rb")
transcription = client.audio.transcriptions.create(
    model=model, file=audio_file, extra_body=extra_body
)
print(transcription.text)
