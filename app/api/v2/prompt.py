"""
API v2 - Prompt Template Endpoints
LangChain Prompt Template 기능 (PromptTemplate, ChatPromptTemplate)
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os

router = APIRouter(prefix="/v2", tags=["v2-prompt-template"])


class TranslateRequest(BaseModel):
    text: str
    target_lang: str = "영어"


class ChatPromptRequest(BaseModel):
    text: str
    system_message: Optional[str] = "사용자의 질의를 영어로 번역해라."


MOCK = os.getenv("MOCK", "true").lower() == "true"


def _safe_invoke(model_obj, prompt_value):
    """모델 호출 헬퍼 함수"""
    try:
        resp = model_obj.invoke(prompt_value)
        content = getattr(resp, "content", None)
        if content is None:
            return str(resp)
        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model invocation error: {e}")


@router.post("/prompt-template")
def prompt_template_endpoint(req: TranslateRequest):
    """
    PromptTemplate 사용 예제
    '{text}' 이 문장을 {target_lang}로 번역해줘
    """
    if MOCK:
        formatted = f"'{req.text}' 이 문장을 {req.target_lang}로 번역해줘"
        return {
            "template": "'{text}' 이 문장을 {target_lang}로 번역해줘",
            "formatted_prompt": formatted,
            "content": f"[MOCK] {formatted}",
        }

    try:
        from langchain_core.prompts import PromptTemplate
        from langchain_openai import ChatOpenAI
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Missing packages: {e}")

    # PromptTemplate 생성
    prompt_template = PromptTemplate.from_template(
        "'{text}' 이 문장을 {target_lang}로 번역해줘"
    )

    # Prompt 포맷팅
    prompt_value = prompt_template.invoke({"text": req.text, "target_lang": req.target_lang})

    # LLM 호출
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o")
    model = ChatOpenAI(model=model_name)
    content = _safe_invoke(model, prompt_value)

    return {
        "template": prompt_template.template,
        "formatted_prompt": prompt_value.to_string(),
        "model": model_name,
        "content": content,
    }


@router.post("/chat-prompt-template")
def chat_prompt_template_endpoint(req: ChatPromptRequest):
    """
    ChatPromptTemplate 사용 예제
    System: {system_message}
    Human: {text}
    """
    if MOCK:
        return {
            "system_message": req.system_message,
            "user_message": req.text,
            "content": f"[MOCK] System: {req.system_message}\nHuman: {req.text}",
        }

    try:
        from langchain_core.prompts.chat import ChatPromptTemplate
        from langchain_openai import ChatOpenAI
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Missing packages: {e}")

    # ChatPromptTemplate 생성
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", req.system_message),
        ("user", "{text}")
    ])

    # Prompt 포맷팅
    chat_value = chat_prompt.invoke({"text": req.text})

    # LLM 호출
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o")
    model = ChatOpenAI(model=model_name)
    content = _safe_invoke(model, chat_value)

    return {
        "system_message": req.system_message,
        "user_message": req.text,
        "formatted_prompt": chat_value.to_string(),
        "model": model_name,
        "content": content,
    }


@router.post("/translate")
def translate_endpoint(req: TranslateRequest):
    """
    간단한 번역 엔드포인트 (ChatPromptTemplate 활용)
    """
    if MOCK:
        return {
            "original": req.text,
            "target_lang": req.target_lang,
            "translated": f"[MOCK] Translation of '{req.text}' to {req.target_lang}",
        }

    try:
        from langchain_core.prompts.chat import ChatPromptTemplate
        from langchain_openai import ChatOpenAI
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Missing packages: {e}")

    # 번역용 ChatPromptTemplate
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", f"사용자의 질의를 {req.target_lang}로 번역해라. 번역 결과만 출력하고 다른 설명은 하지 마라."),
        ("user", "{text}")
    ])

    # Prompt 포맷팅
    prompt_value = chat_prompt.invoke({"text": req.text})

    # LLM 호출
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o")
    model = ChatOpenAI(model=model_name)
    content = _safe_invoke(model, prompt_value)

    return {
        "original": req.text,
        "target_lang": req.target_lang,
        "translated": content,
        "model": model_name,
    }
