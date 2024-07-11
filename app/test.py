import os
from faster_whisper import WhisperModel

# Define the file path and model size
file_path = "speech.mp3"  # Update with your actual file path
model_size = "tiny"  # Choose from 'tiny', 'base', 'small', 'medium', 'large'

# Check if file exists
if not os.path.exists(file_path):
    raise FileNotFoundError(f"The file {file_path} does not exist.")

# Initialize the Whisper model
model = WhisperModel(model_size)

# Load and transcribe the audio file
segments, info = model.transcribe(file_path, language="en")

# Print the transcribed text
print("Transcription:")
for segment in segments:
    print(segment.text)
