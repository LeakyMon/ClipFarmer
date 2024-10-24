import requests
import json
import os

def narrate_story_elevenlabs(text):
    print("IN NARRATE ELEMENTS")

    narration_filepath = 'story_narration.mp3'

    # Check if narration file already exists
    if os.path.exists(narration_filepath):
        print(f"'{narration_filepath}' already exists, skipping Eleven Labs request.")
        return narration_filepath

    # ElevenLabs API credentials
    API_KEY = 'sk_160b55a580791235d3933fa66d354db0eefea6bddc1d55f3'
    url = 'https://api.elevenlabs.io/v1/text-to-speech/e5WNhrdI30aXpS2RSGm1'  # Use Adam (legacy) Voice ID here

    headers = {
        'xi-api-key': API_KEY,
        'Content-Type': 'application/json',
    }

    data = {
        'text': text,  # Send the full text without limiting words
        'voice_settings': {
            'stability': 0.75,
            'similarity_boost': 0.85
        }
    }

    # Send request to ElevenLabs API
    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        with open(narration_filepath, 'wb') as f:
            f.write(response.content)
        print(f"Narration saved to '{narration_filepath}'")
        return narration_filepath
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None
