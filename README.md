# LangChain Multi-LLM FastAPI

FastAPI와 LangChain을 사용하여 여러 LLM 모델을 제공하는 API 서버입니다.
**버전 관리**를 통해 기본 LLM 호출(v1)과 Prompt Template 기능(v2)을 제공합니다.

---

## 📑 목차

- [제공 API](#제공-api)
- [빠른 시작](#빠른-시작)
- [API 사용 예제](#api-사용-예제)
- [환경 변수 설정](#환경-변수-설정)
- [프로젝트 구조](#프로젝트-구조)
- [문제 해결](#문제-해결)

---

## 🚀 제공 API

### **V1 - 기본 LLM 호출**

간단한 프롬프트로 LLM을 직접 호출합니다.

- `POST /v1/gpt` — OpenAI GPT 모델
- `POST /v1/gemini` — Google Gemini 모델
- `POST /v1/claude` — Anthropic Claude 모델

**요청 예시:**
```json
{
  "prompt": "안녕하세요"
}
```

---

### **V2 - Prompt Template** (신규!)

LangChain의 PromptTemplate과 ChatPromptTemplate을 활용한 고급 기능입니다.

- `POST /v2/prompt-template` — PromptTemplate 사용 예제
- `POST /v2/chat-prompt-template` — ChatPromptTemplate 사용 예제
- `POST /v2/translate` — 번역 전용 엔드포인트

**요청 예시:**
```json
{
  "text": "안녕",
  "target_lang": "영어"
}
```

---

## 빠른 시작

### 1. 가상환경 생성 및 활성화

```bash
cd 09-API

# 가상환경 생성 (Python 3.12 권장)
python3.12 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# Windows의 경우
# venv\Scripts\activate
```

> **중요**: Python 3.13은 일부 패키지 호환성 문제가 있을 수 있습니다. Python 3.11 또는 3.12 사용을 권장합니다.

---

### 2. 패키지 설치

```bash
# pip 업그레이드
pip install --upgrade pip

# 필요한 패키지 설치
pip install -r requirements.txt
```

---

### 3. 환경 변수 설정 (선택)

Mock 모드로 테스트하려면 이 단계를 건너뛰어도 됩니다.

실제 API를 사용하려면:

```bash
# .env.example을 .env로 복사
cp .env.example .env

# .env 파일 편집하여 API 키 설정
# MOCK=false로 설정하고 API 키 입력
```

---

### 4. 테스트 실행

```bash
# 자동으로 서버 시작/v1 v2 테스트/종료
python run_tests.py
```

**테스트 결과:**
```
============================================================
V1 엔드포인트 테스트 (기본 LLM)
============================================================

-> POST http://127.0.0.1:8000/v1/gpt
   Response (200): {'model': 'gpt-mock', 'content': '[MOCK GPT] 안녕'}

============================================================
V2 엔드포인트 테스트 (Prompt Template)
============================================================

-> POST http://127.0.0.1:8000/v2/translate
   Response (200):
     original: 고마워
     target_lang: 중국어
     translated: [MOCK] Translation of '고마워' to 중국어
```

---

## 📖 API 사용 예제

### V1 - 기본 LLM 호출

**curl:**
```bash
curl -X POST http://127.0.0.1:8000/v1/gpt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "안녕하세요"}'
```

**Python:**
```python
import httpx

client = httpx.Client()
response = client.post(
    "http://127.0.0.1:8000/v1/gpt",
    json={"prompt": "안녕하세요"}
)
print(response.json())
# {'model': 'gpt-mock', 'content': '[MOCK GPT] 안녕하세요'}
```

---

### V2 - Prompt Template

#### 1️⃣ PromptTemplate 사용

```bash
curl -X POST http://127.0.0.1:8000/v2/prompt-template \
  -H "Content-Type: application/json" \
  -d '{"text": "안녕", "target_lang": "영어"}'
```

**응답:**
```json
{
  "template": "'{text}' 이 문장을 {target_lang}로 번역해줘",
  "formatted_prompt": "'안녕' 이 문장을 영어로 번역해줘",
  "content": "[MOCK] '안녕' 이 문장을 영어로 번역해줘"
}
```

---

#### 2️⃣ ChatPromptTemplate 사용

```bash
curl -X POST http://127.0.0.1:8000/v2/chat-prompt-template \
  -H "Content-Type: application/json" \
  -d '{
    "text": "좋은 아침",
    "system_message": "사용자의 질의를 일본어로 번역해라."
  }'
```

**응답:**
```json
{
  "system_message": "사용자의 질의를 일본어로 번역해라.",
  "user_message": "좋은 아침",
  "formatted_prompt": "System: 사용자의 질의를 일본어로 번역해라.\nHuman: 좋은 아침",
  "content": "[MOCK] System: 사용자의 질의를 일본어로 번역해라.\nHuman: 좋은 아침"
}
```

---

#### 3️⃣ 번역 엔드포인트

```bash
curl -X POST http://127.0.0.1:8000/v2/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "고마워", "target_lang": "중국어"}'
```

**응답:**
```json
{
  "original": "고마워",
  "target_lang": "중국어",
  "translated": "[MOCK] Translation of '고마워' to 중국어"
}
```

---

## 🌐 브라우저에서 API 문서 확인

서버 실행 후 브라우저에서 접속:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

Swagger UI에서 각 엔드포인트를 직접 테스트할 수 있습니다!

---

## ⚙️ 환경 변수 설정

### Mock 모드 (기본값)

API 키 없이 테스트 가능:

```bash
# .env 파일
MOCK=true
```

또는 환경변수로 직접 설정:

```bash
export MOCK=true
uvicorn app.main:app --reload
```

---

### 실제 API 사용

`.env` 파일에 API 키 설정:

```bash
MOCK=false
OPENAI_API_KEY=sk-your-openai-key
GOOGLE_API_KEY=your-google-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
OPENAI_MODEL=gpt-4o  # 선택사항, 기본값: gpt-4o
```

---

## 🗂️ 프로젝트 구조

```
09-API/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI 메인 서버 (라우터 등록)
│   └── api/
│       ├── v1/
│       │   ├── __init__.py
│       │   └── llm.py            # V1: 기본 GPT/Gemini/Claude
│       └── v2/
│           ├── __init__.py
│           └── prompt.py         # V2: Prompt Template 기능
├── Chapter 7. LangChain/          # LangChain 학습 노트북
├── .env.example                   # 환경 변수 템플릿
├── .gitignore                     # Git 제외 파일 설정
├── requirements.txt               # Python 패키지 목록
├── run_tests.py                   # 자동 테스트 스크립트 (v1 + v2)
└── README.md
```

---

## 🛠️ VSCode에서 가상환경 사용

1. VSCode에서 `Cmd+Shift+P` (Windows: `Ctrl+Shift+P`)
2. "Python: Select Interpreter" 선택
3. `./venv/bin/python` 선택
4. 터미널 재시작하면 자동으로 가상환경 활성화

---

## 🔧 수동 서버 실행

```bash
# Mock 모드로 실행 (API 키 불필요)
MOCK=true uvicorn app.main:app --reload

# 실제 API 사용 (API 키 필요)
uvicorn app.main:app --reload

# 다른 포트로 실행
uvicorn app.main:app --reload --port 8001
```

---

## ❓ 문제 해결

### Python 버전 문제

Python 3.13에서 `tiktoken` 빌드 오류가 발생할 수 있습니다.

**해결 방법**: Python 3.12 또는 3.11 사용

```bash
# 기존 가상환경 삭제
deactivate
rm -rf venv

# Python 3.12로 가상환경 재생성
python3.12 -m venv venv
source venv/bin/activate

# 패키지 재설치
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 포트 8000이 이미 사용 중인 경우

다른 포트로 서버 실행:

```bash
uvicorn app.main:app --reload --port 8001
```

---

### API 키 오류

- `.env` 파일이 올바른 위치에 있는지 확인
- API 키가 정확한지 확인
- `MOCK=true`로 설정하여 API 키 없이 테스트

---

### 패키지 설치 오류

가상환경이 활성화되어 있는지 확인:

```bash
which python
# 출력: /Users/.../09-API/venv/bin/python
```

---

## 🔗 관련 링크

- **GitHub 저장소**: https://github.com/gyungsubLee/langchain-multi-llm-api
- **LangChain 공식 문서**: https://python.langchain.com/
- **FastAPI 공식 문서**: https://fastapi.tiangolo.com/

---

## 📝 버전 관리

### v2.0.0 (현재)
- ✅ API 버전 관리 시스템 도입
- ✅ v1: 기본 LLM 호출 엔드포인트
- ✅ v2: Prompt Template 기능 추가
- ✅ 파일별 엔드포인트 분리 구조

### v1.0.0
- ✅ 기본 GPT/Gemini/Claude 엔드포인트
- ✅ Mock 모드 지원
- ✅ 자동 테스트 스크립트

---

## 🤝 Contributing

이슈나 개선 사항이 있으면 GitHub Issues에 등록해주세요!

---

## 📄 License

MIT License
