import logging
import os
from typing import Literal

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from backend.agents.supervisor import create_supervisor

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("tkd_intelligence")

app = FastAPI(
    title="TKD Intelligence API",
    description="Free AI-powered Taekwondo assistant for athletes, coaches, and referees.",
    version="1.2.0",
)

# Keep the existing four-agent LangGraph supervisor.
supervisor = create_supervisor()


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=10000)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=5000)
    user_level: str = Field(default="Beginner", max_length=50)
    chat_history: list[ChatMessage] = Field(default_factory=list, max_length=20)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    logger.info("Request validation failed on %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": "Please check your question and try again.",
        },
    )


@app.exception_handler(Exception)
async def unexpected_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled API error on %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Something went wrong while processing your request. Please try again shortly.",
        },
    )


@app.get("/")
def home():
    return {
        "status": "success",
        "message": "TKD Intelligence API is running.",
        "access": "free",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "access": "free",
        "agents": ["rules", "training", "fitness", "competition"],
        "conversation_memory": "session-based",
    }


@app.post("/chat")
def chat(request: ChatRequest):
    question = request.question.strip()
    if not question:
        return JSONResponse(
            status_code=422,
            content={"status": "error", "message": "Please enter a question."},
        )

    try:
        history = [
            {"role": msg.role, "content": msg.content.strip()[:1000]}
            for msg in request.chat_history[-6:]
            if msg.content.strip()
        ]

        result = supervisor.invoke(
            {
                "question": question,
                "category": "",
                "response": "",
                "sources": [],
                "chat_history": history,
                "user_level": request.user_level,
            }
        )

        answer = result.get("response") or (
            "I couldn't generate a response just now. Please try asking again."
        )

        return {
            "status": "success",
            "category": result.get("category", "training"),
            "answer": answer,
            "sources": result.get("sources", []),
        }

    except Exception:
        logger.exception("Multi-agent chat processing failed")
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "message": "The Taekwondo AI assistant is temporarily unavailable. Please try again in a moment.",
            },
        )
