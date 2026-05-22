import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from routes import ask, questions, summary, upload

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

app = FastAPI(title="DeepDocAI", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, tags=["Upload"])
app.include_router(ask.router, tags=["Agent Q&A"])
app.include_router(summary.router, tags=["Summary"])
app.include_router(questions.router, tags=["Questions"])


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "version": "2.0.0"}

