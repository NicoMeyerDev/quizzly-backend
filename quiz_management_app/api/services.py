import glob
import os
import tempfile
import json
import re


import whisper
import yt_dlp
from dotenv import load_dotenv
from google import genai



load_dotenv()

    
def download_audio(url: str) -> str:
    """
    Downloads the audio track of a YouTube video and saves it temporarily.

    :param url: URL of the YouTube video
    :return: Path to the downloaded audio file
    """
    tmp_dir = tempfile.mkdtemp()
    tmp_filename = os.path.join(tmp_dir, "audio")

    ydl_opts = {
        "format": "bestaudio",
        "outtmpl": tmp_filename,
        "quiet": True,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        ext = info.get("ext", "webm")

    

    files = glob.glob(tmp_filename + "*")
    if not files:
        raise ValueError("Audio download fehlgeschlagen")
    
    return files[0]

def transcribe_audio(file_path: str) -> str:
    """
    Transcribes an audio file into text using Whisper.

    :param file_path: Path to the audio file
    :return: Transcribed text content
    """
    model = whisper.load_model("turbo")
    result = model.transcribe(file_path)
    return result["text"]


def clean_output(text: str) -> str:
    """
    Removes Markdown code blocks from the AI output to extract valid JSON.

    :param text: aw text from the AI response
    :return: Cleaned text without Markdown syntax
    """
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def generate_quiz(transcript: str) -> dict:
    """
    Creates a quiz in JSON format based on a transcript using the Gemini API.

    :param transcript: Transcribed text of the video
    :return: Quiz data as a Python dictionary
    :raises ValueError: If no API key is available or invalid JSON is returned
    """
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY fehlt. Prüfe die .env Datei.")

    client = genai.Client(api_key=api_key)

    prompt = f"""
Based on the following transcript, generate a quiz in valid JSON format.

The quiz must follow this exact structure:

{{
  "title": "Quiz title",
  "description": "Max 150 characters summary",
  "questions": [
    {{
      "question_title": "Question",
      "answers": [
        {{"answer_text": "Option A", "is_correct": true}},
        {{"answer_text": "Option B", "is_correct": false}},
        {{"answer_text": "Option C", "is_correct": false}},
        {{"answer_text": "Option D", "is_correct": false}}
      ]
    }}
  ]
}}

Requirements:
- Exactly 10 questions
- Exactly 4 options per question
- Only one correct answer
- Output must be valid JSON
- No markdown, no extra text

Transcript:
{transcript}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    cleaned = clean_output(response.text)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Ungültiges JSON von der KI erhalten: {e}")