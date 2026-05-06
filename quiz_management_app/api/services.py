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
    Lädt die Audiospur eines YouTube-Videos herunter und speichert sie temporär.

    :param url: URL des YouTube-Videos
    :return: Pfad zur heruntergeladenen Audiodatei
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

    return f"{tmp_filename}.{ext}"


def transcribe_audio(file_path: str) -> str:
    """
    Wandelt eine Audiodatei mittels Whisper in Text um.

    :param file_path: Pfad zur Audiodatei
    :return: Transkribierter Textinhalt
    """
    model = whisper.load_model("turbo")
    result = model.transcribe(file_path)
    return result["text"]


def clean_output(text: str) -> str:
    """
    Entfernt Markdown-Codeblöcke aus der KI-Ausgabe, um gültiges JSON zu extrahieren.

    :param text: Rohtext aus der KI-Antwort
    :return: Bereinigter Text ohne Markdown-Syntax
    """
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def generate_quiz(transcript: str) -> dict:
    """
    Erstellt basierend auf einem Transkript ein Quiz im JSON-Format über die Gemini API.

    :param transcript: Transkribierter Text des Videos
    :return: Quiz-Daten als Python-Dictionary
    :raises ValueError: Wenn kein API-Key vorhanden ist oder ungültiges JSON zurückgegeben wird
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