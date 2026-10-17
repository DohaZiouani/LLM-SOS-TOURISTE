"""
api.py — expose le RAG SOS Tourist en HTTP.

Lancer :  uvicorn api:app --host 0.0.0.0 --port 8001
Tester :  curl -X POST http://localhost:8001/chat -H "Content-Type: application/json" \
              -d '{"question":"un trek dans l'\''Atlas ?", "history":[]}'
"""
from typing import List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from orchestrateur import repondre

app = FastAPI(title="SOS Tourist — Service RAG (Yasmine)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    role: str
    content: str


class ChatIn(BaseModel):
    question: str
    history: Optional[List[Message]] = []


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(body: ChatIn):
    # Inject the last 4 turns as context if available
    context_prefix = ""
    if body.history:
        turns = body.history[-4:]
        context_prefix = "\n".join(
            f"{'Voyageur' if m.role == 'user' else 'Yasmine'}: {m.content}"
            for m in turns
        ) + "\n\n"

    full_question = context_prefix + body.question if context_prefix else body.question
    reply = repondre(full_question, verbose=False)
    return {"reply": reply}
