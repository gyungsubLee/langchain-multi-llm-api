from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="LangChain Multi-LLM API")


class PromptRequest(BaseModel):
    prompt: str


MOCK = os.getenv("MOCK", "true").lower() == "true"


def _safe_invoke(model_obj, prompt: str):
    try:
        resp = model_obj.invoke(prompt)
        # many LangChain model wrappers expose `.content`
        content = getattr(resp, "content", None)
        if content is None:
            # maybe string
            return str(resp)
        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model invocation error: {e}")


@app.get("/")
def root():
    return {"status": "ok", "mock": MOCK}


@app.post("/gpt")
def gpt_endpoint(req: PromptRequest):
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


@app.post("/gemini")
def gemini_endpoint(req: PromptRequest):
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


@app.post("/claude")
def claude_endpoint(req: PromptRequest):
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
