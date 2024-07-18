from flask import Flask, request, jsonify
import os
import speech_recognition as sr
from pydub import AudioSegment
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

def convert_to_wav(audio_file_path, output_file_path):
    audio = AudioSegment.from_file(audio_file_path)
    audio.export(output_file_path, format='wav')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400

        audio_file = request.files['audio']
        audio_path = 'temp_audio'
        audio_wav_path = 'temp_audio/temp_audio.wav'

        # Create temp_audio directory if it doesn't exist
        if not os.path.exists(audio_path):
            os.makedirs(audio_path)

        audio_file.save(os.path.join(audio_path, 'temp_audio'))

        convert_to_wav(os.path.join(audio_path, 'temp_audio'), audio_wav_path)

        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_wav_path) as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)  # Using CMU Sphinx

        return jsonify({"transcription": text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Clean up: remove temporary files and directory
        if os.path.exists(os.path.join(audio_path, 'temp_audio')):
            os.remove(os.path.join(audio_path, 'temp_audio'))
        if os.path.exists(audio_wav_path):
            os.remove(audio_wav_path)
        if os.path.exists(audio_path):
            os.rmdir(audio_path)


@app.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "API is working"}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)
