"""
API v1 - Basic LLM Endpoints
기본 GPT/Gemini/Claude 호출 기능
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os

router = APIRouter(prefix="/v1", tags=["v1-basic-llm"])


class PromptRequest(BaseModel):
    prompt: str


MOCK = os.getenv("MOCK", "true").lower() == "true"


def _safe_invoke(model_obj, prompt: str):
    """모델 호출 헬퍼 함수"""
    try:
        resp = model_obj.invoke(prompt)
        content = getattr(resp, "content", None)
        if content is None:
            return str(resp)
        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model invocation error: {e}")


@router.post("/gpt")
def gpt_endpoint(req: PromptRequest):
    """GPT 기본 호출"""
    prompt = req.prompt
    if MOCK:
        return {"model": "gpt-mock", "content": f"[MOCK GPT] {prompt}"}

    try:
        from langchain_openai import ChatOpenAI
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Missing OpenAI LangChain package: {e}")

    model_name = os.getenv("OPENAI_MODEL", "gpt-4o")
    model = ChatOpenAI(model=model_name)
    content = _safe_invoke(model, prompt)
    return {"model": model_name, "content": content}


@router.post("/gemini")
def gemini_endpoint(req: PromptRequest):
    """Gemini 기본 호출"""
    prompt = req.prompt
    if MOCK:
        return {"model": "gemini-mock", "content": f"[MOCK Gemini] {prompt}"}

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Missing Google GenAI LangChain package: {e}")

    model_name = os.getenv("GOOGLE_MODEL", "gemini-1.5-pro")
    model = ChatGoogleGenerativeAI(model=model_name)
    content = _safe_invoke(model, prompt)
    return {"model": model_name, "content": content}


@router.post("/claude")
def claude_endpoint(req: PromptRequest):
    """Claude 기본 호출"""
    prompt = req.prompt
    if MOCK:
        return {"model": "claude-mock", "content": f"[MOCK Claude] {prompt}"}

    try:
        from langchain_anthropic import ChatAnthropic
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Missing Anthropic LangChain package: {e}")

    model_name = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
    model = ChatAnthropic(model=model_name)
    content = _safe_invoke(model, prompt)
    return {"model": model_name, "content": content}
