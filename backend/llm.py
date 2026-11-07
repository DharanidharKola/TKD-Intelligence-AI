import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")

def get_llm():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY is missing from .env")

    return ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0.3,
        max_tokens=3072,
        api_key=api_key
    )