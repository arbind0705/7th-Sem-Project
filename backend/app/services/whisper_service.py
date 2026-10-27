import os
import httpx

# ponytail: hosted Groq Whisper API, not local openai-whisper — no ffmpeg/torch
# install needed. Swap to a local model in transcribe() if offline transcription
# or data-residency becomes a requirement.
GROQ_TRANSCRIBE_URL = "https://api.groq.com/openai/v1/audio/transcriptions"


def transcribe(filename: str, content: bytes) -> str:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set")

    response = httpx.post(
        GROQ_TRANSCRIBE_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        files={"file": (filename, content)},
        data={"model": "whisper-large-v3"},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["text"]
