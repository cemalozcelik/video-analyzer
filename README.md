# 🎥 AI-Powered Video Analyzer

> Turn any YouTube or local video into structured, intelligent learning material using Whisper, GPT, and Claude.

This project is a desktop application that allows you to import or download educational videos, automatically extract the audio, transcribe it with AI (Whisper or OpenAI), and generate insightful summaries and study guides using GPT or Claude.

---

## Features

- Download videos from YouTube or import local files
-  Audio extraction via `moviepy`
-  AI-powered transcription using:
  - Local Whisper
  - OpenAI Whisper API
-  Transcript summarization using:
  - OpenAI GPT-3.5
  - Claude (Anthropic)
-  Markdown-formatted AI analysis:
  - Title + description
  - Key concepts
  - Takeaways
  - Practice questions
  - Code blocks (if detected)
-  Download progress feedback
-  Engine selector for transcription and analysis
- Language selection for AI summaries (English & Turkish)
-  Save output summaries
---

## 🛠 Tech Stack

| Category           | Tools & Libraries                                |
|--------------------|--------------------------------------------------|
| Frontend (UI)      | PySide6 (Qt for Python)                          |
| Audio Processing   | pydub, moviepy                                   |
| Transcription      | whisper (local), OpenAI Whisper API              |
| AI Analysis        | OpenAI GPT-3.5, Anthropic Claude 2               |
| YouTube Downloads  | yt-dlp                                           |
| Logging            | Custom `logger.py`                               |
| Async + Threads    | QThread + Workers for background processing      |
| Environment Config | `python-dotenv` (.env support)                   |

---

## Getting Started
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

## Application Image
![AI-Powered Video Analyzer Screenshot](log/screenshot.png)
