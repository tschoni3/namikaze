import os
from dotenv import load_dotenv
import base64
import openai
from flask import Flask, request, jsonify
from flask_cors import CORS
from pydub import AudioSegment
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
CORS(app)

# Set the OpenAI API key
openai.api_key = os.environ.get('OPENAI_API_KEY')

messages = [{"role": "system", "content": 'You are an AI-powered summarization assistant. Help users by summarizing and organizing their thoughts. Give motivation and inspiration to user.'}]

@app.route('/')
def index():
    return "Welcome to the Flask server!"


@app.route('/transcribe', methods=['POST'])
def transcribe():
    global messages

    if 'audio' in request.files:
        audio = request.files['audio']
        filename = secure_filename(audio.filename)
        audio.save(filename)

        try:
            sound = AudioSegment.from_file(filename)
        except Exception as e:
            return jsonify({"error": f"Error reading the audio file: {e}"})

        converted_audio = "converted_audio.wav"
        sound.export(converted_audio, format="wav")
        audio_file = open(converted_audio, "rb")

        transcript = openai.Audio.transcribe("whisper-1", audio_file, extension="wav")
        print(transcript)

        messages.append({"role": "user", "content": transcript["text"]})
    else:
        return jsonify({"error": "Please provide an audio file."})

    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)

    system_message = response["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": system_message})

    chat_transcript = ""
    # Get only the last two messages (the latest user's request and the assistant's response)
    latest_messages = messages[-2:]
    for message in latest_messages:
        if message['role'] != 'system':
            chat_transcript += message['role'] + ": " + message['content'] + "\n\n"

    return jsonify(chat_transcript)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)