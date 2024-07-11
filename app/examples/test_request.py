from dotenv import load_dotenv
import os
import requests

load_dotenv()

SERVER_PORT = os.getenv("SERVER_PORT", 5000)
MODELS = os.getenv("OLLAMA_API_URL", "tiny,small").split(",")

url = f"http://localhost:{SERVER_PORT}/v1/audio/transcriptions"  # Replace with your actual endpoint URL
file_path = "speech.mp3"
model = MODELS[0]
language = "en"

# Open the audio file as binary
files = {"file": open(file_path, "rb")}

# Define the payload (form data)
data = {"model": model, "language": language}

try:
    # Send POST request to the endpoint
    response = requests.post(url, files=files, data=data)

    # Check if request was successful (HTTP status code 200)
    if response.status_code == 200:
        transcription = response.json()
        print(f"Result: {transcription['text']}")  # Print response JSON data
    else:
        print(f"Request failed with status code {response.status_code}:")
        print(response.text)  # Print error message if any
except requests.exceptions.RequestException as e:
    print("Request failed:", e)
