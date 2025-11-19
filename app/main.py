"""
LangChain Multi-LLM FastAPI Server
버전별 API 엔드포인트 제공
"""
from fastapi import FastAPI
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="LangChain Multi-LLM API",
    description="GPT/Gemini/Claude with version management + RAG",
    version="4.0.0"
)

MOCK = os.getenv("MOCK", "true").lower() == "true"


@app.get("/")
def root():
    """서버 상태 확인"""
    return {
        "status": "ok",
        "mock": MOCK,
        "versions": ["v1", "v2", "v4"],
        "endpoints": {
            "v1": ["/v1/gpt", "/v1/gemini", "/v1/claude"],
            "v2": ["/v2/prompt-template", "/v2/chat-prompt-template", "/v2/translate"],
            "v4": ["/v4/search", "/v4/rag", "/v4/upload-pdf"]
        }
    }


# API v1 라우터 등록 (기본 LLM 호출)
from app.api.v1.llm import router as v1_router
app.include_router(v1_router)

# API v2 라우터 등록 (Prompt Template)
from app.api.v2.prompt import router as v2_router
app.include_router(v2_router)

# API v4 라우터 등록 (Retrieval & RAG)
from app.api.v4.retrieval import router as v4_router
app.include_router(v4_router)
