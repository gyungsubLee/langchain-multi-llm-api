# LangChain Multi-LLM FastAPI

FastAPI와 LangChain을 사용하여 여러 LLM 모델을 제공하는 API 서버입니다.

## 제공 엔드포인트

- `POST /gpt` — OpenAI GPT 모델 (`langchain-openai` 사용, `OPENAI_MODEL`로 설정 가능)
- `POST /gemini` — Google Gemini 모델 (`langchain-google-genai` 사용)
- `POST /claude` — Anthropic Claude 모델 (`langchain-anthropic` 사용)

기본적으로 서버는 `MOCK=true` 모드로 실행되어 API 키 없이도 테스트할 수 있습니다. 실제 모델을 호출하려면 `MOCK=false`로 설정하고 적절한 API 키를 환경 변수에 제공해야 합니다 (`.env.example` 참조).

---

## 빠른 시작 (macOS / Linux)

### 1. 가상환경 생성 및 활성화

```bash
cd /Users/igyeongseob/Develop/ai/bootcamp_ai/09-API

# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# Windows의 경우
# venv\Scripts\activate
```

활성화되면 터미널 프롬프트 앞에 `(venv)`가 표시됩니다.

### 2. 패키지 설치

```bash
# pip 업그레이드
pip install --upgrade pip

# 필요한 패키지 설치
pip install -r requirements.txt
```

### 3. 환경 변수 설정 (선택)

실제 API를 사용하려면:

```bash
# .env.example을 .env로 복사
cp .env.example .env

# .env 파일 편집하여 API 키 설정
# MOCK=false로 설정하고 API 키 입력
```

Mock 모드로 테스트하려면 이 단계를 건너뛰어도 됩니다.

### 4. 테스트 실행

```bash
# 자동으로 서버 시작/테스트/종료
python run_tests.py
```

---

## 상세 실행 방법

### 방법 1: 자동 테스트 (권장)

테스트 스크립트가 서버 시작/종료를 자동으로 처리합니다:

```bash
python run_tests.py
```

**동작 과정:**
- uvicorn 서버 자동 시작 (포트 8000)
- 서버 준비 대기
- GPT/Gemini/Claude 엔드포인트 테스트
- 서버 자동 종료

---

### 방법 2: 수동 서버 실행

#### 서버 실행

```bash
# Mock 모드로 실행 (API 키 불필요)
MOCK=true uvicorn app.main:app --reload

# 실제 API 사용 (API 키 필요)
uvicorn app.main:app --reload
```

#### API 테스트

**curl로 테스트:**

```bash
# GPT 엔드포인트
curl -X POST http://127.0.0.1:8000/gpt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "안녕하세요"}'

# Gemini 엔드포인트
curl -X POST http://127.0.0.1:8000/gemini \
  -H "Content-Type: application/json" \
  -d '{"prompt": "테스트"}'

# Claude 엔드포인트
curl -X POST http://127.0.0.1:8000/claude \
  -H "Content-Type: application/json" \
  -d '{"prompt": "반가워요"}'
```

**Python으로 테스트:**

```python
import httpx

client = httpx.Client()
response = client.post(
    "http://127.0.0.1:8000/gpt",
    json={"prompt": "안녕하세요"}
)
print(response.json())
```

---

### 브라우저에서 API 문서 확인

서버 실행 후 브라우저에서 접속:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

Swagger UI에서 각 엔드포인트를 직접 테스트할 수 있습니다.

---

## 환경 변수 설정

### Mock 모드 (기본값)

```bash
# .env 파일
MOCK=true
```

또는 환경변수로 직접 설정:

```bash
export MOCK=true
uvicorn app.main:app --reload
```

### 실제 API 사용

`.env` 파일에 API 키 설정:

```bash
MOCK=false
OPENAI_API_KEY=sk-your-openai-key
GOOGLE_API_KEY=your-google-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
OPENAI_MODEL=gpt-4  # 선택사항, 기본값: gpt-3.5-turbo
```

---

## VSCode에서 가상환경 사용

1. VSCode에서 `Cmd+Shift+P` (Windows: `Ctrl+Shift+P`)
2. "Python: Select Interpreter" 선택
3. `./venv/bin/python` 선택
4. 터미널 재시작하면 자동으로 가상환경 활성화

---

## 가상환경 종료

작업 완료 후:

```bash
deactivate
```

---

## 프로젝트 구조

```
09-API/
├── app/
│   ├── __init__.py
│   └── main.py          # FastAPI 서버 및 엔드포인트
├── .env.example         # 환경 변수 템플릿
├── requirements.txt     # Python 패키지 목록
├── run_tests.py         # 자동 테스트 스크립트
└── README.md
```

---

## 문제 해결

### 포트 8000이 이미 사용 중인 경우

다른 포트로 서버 실행:

```bash
uvicorn app.main:app --reload --port 8001
```

### API 키 오류

- `.env` 파일이 올바른 위치에 있는지 확인
- API 키가 정확한지 확인
- `MOCK=true`로 설정하여 API 키 없이 테스트

### 패키지 설치 오류

가상환경이 활성화되어 있는지 확인:

```bash
which python
# 출력: /Users/igyeongseob/Develop/ai/bootcamp_ai/09-API/venv/bin/python
```
