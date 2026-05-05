import whisper
import yt_dlp
import tempfile
from google import genai
import os
from dotenv import load_dotenv

def get_transcript(url):
    tmp_filename = tempfile.NamedTemporaryFile(delete=False).name
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": tmp_filename,
        "quiet": True,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    return tmp_filename

def transcribe_audio(file_path):
    model = whisper.load_model("turbo")
    result = model.transcribe(file_path)
    return result["text"]

def generate_questions(transcript):
    client = genai.Client(api_key='GEMINI_API_KEY')
    export GEMINI_API_KEY='your-api-key'
    
