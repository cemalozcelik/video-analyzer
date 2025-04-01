from openai import OpenAI
from utils.logger import log_info, log_error
from dotenv import load_dotenv
import os
import anthropic

load_dotenv()

def get_openai_client():
    return OpenAI()

def analyze_transcript(transcript: str, engine: str = "OpenAI GPT", target_language: str = "English") -> dict:
    try:
        log_info(f"🧠 Starting AI analysis with {engine}...")

        prompt = f"""
You are an expert AI educational assistant. Given the following transcript of a video, your task is to analyze and summarize the content clearly in a well-structured **Markdown format**.

🎯 Your goals:
- Identify the topic and give the video a clear title
- Write a brief, insightful description (3–5 sentences)
- List key concepts or terms
- Extract key takeaways or highlights
- If code is discussed, include code blocks
- Generate a few insightful practice questions

Format your response using proper Markdown with headers, lists, and code blocks where appropriate.
Output the entire response in **{target_language}**.

---

Transcript:
\"\"\"
{transcript}
\"\"\"
"""

        if engine == "Claude (Anthropic)":
            client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            message = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1000,
                temperature=0.6,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            result = message.content[0].text
        else:
            client = get_openai_client()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert AI video assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=800
            )
            result = response.choices[0].message.content

        log_info("✅ AI analysis complete")
        return {"result": result}

    except Exception as e:
        log_error(f"❌ AI analysis failed: {e}")
        return {"error": str(e)}
