from flask import Flask, request, jsonify, send_from_directory
import yt_dlp
import os
import requests

app = Flask(__name__, static_url_path='', static_folder='.')

# Whisper API endpoint and API key
WHISPER_API_URL = "https://api.openai.com/v1/audio/transcriptions"
WHISPER_API_KEY = " "  # Replace with your actual Whisper API key


@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/style.css')
def serve_css():
    return send_from_directory('.', 'style.css')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.get_json()
    video_url = data.get('videoUrl')
    
    try:
        # Download video
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'yt_audio.%(ext)s'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        
        # Convert video to audio (assuming the download was successful and created yt_audio.webm)
        audio_path = 'yt_audio.webm'
        
        # Call Whisper API to transcribe audio
        with open(audio_path, 'rb') as audio_file:
            headers = {
                'Authorization': f'Bearer {WHISPER_API_KEY}',
                'Content-Type': 'audio/webm'
            }
            response = requests.post(WHISPER_API_URL, headers=headers, files={'file': audio_file})

        if response.status_code == 200:
            transcribed_text = response.json().get('text', '')
        else:
            transcribed_text = "Failed to transcribe audio"

        # Clean up temporary files
        os.remove(audio_path)
        if os.path.exists("yt_audio.webm"):
            os.remove("yt_audio.webm")

        return jsonify({'text': transcribed_text})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
