from fastapi import FastAPI, Form
import requests

app = FastAPI()

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:1b"


def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50):
    words = text.split()
    chunks = []

    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap

    return chunks


def call_ollama(prompt: str):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        },
        timeout=500
    )

    if response.status_code != 200:
        raise Exception(f"Ollama request failed with status {response.status_code}")

    result = response.json()
    return result.get("response", "").strip()


@app.post("/summarize/")
def summarize(text: str = Form(...)):
    try:
        text = text.strip()

        if not text:
            return {"error": "Empty input text"}

        chunks = chunk_text(text, chunk_size=300, overlap=50)

        # If text is short, skip multi-step summarization
        if len(chunks) == 1:
            prompt = f"""
Summarize the following text clearly and concisely in bullet points.
Focus only on the main ideas.
Keep the summary under 150 words.

Text:
{text}
"""
            summary = call_ollama(prompt)
            return {"summary": summary}

        # Step 1: summarize each chunk
        chunk_summaries = []
        for i, chunk in enumerate(chunks, start=1):
            prompt = f"""
You are summarizing one part of a larger document.

Summarize the following chunk clearly in bullet points.
Keep only the important ideas.
Do not repeat unnecessary details.

Chunk {i}:
{chunk}
"""
            chunk_summary = call_ollama(prompt)
            chunk_summaries.append(chunk_summary)

        # Step 2: combine chunk summaries
        combined_summary_text = "\n\n".join(chunk_summaries)

        final_prompt = f"""
The following are summaries of parts of a larger document.

Combine them into one clear final summary in bullet points.
Remove repetition.
Keep only the most important overall ideas.
Keep the final answer under 150 words.

Partial summaries:
{combined_summary_text}
"""
        final_summary = call_ollama(final_prompt)

        return {
            "summary": final_summary,
            "chunks_used": len(chunks)
        }

    except Exception as e:
        return {"error": str(e)}