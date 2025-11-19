#!/usr/bin/env python3
"""
LangChain Multi-LLM API 테스트 스크립트
v1, v2 엔드포인트 자동 테스트
"""
import httpx
import subprocess
import time
import sys
import os
import signal

BASE_URL = "http://127.0.0.1:8000"
UVICORN_CMD = ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--log-level", "info"]


def wait_for_server(max_attempts=30):
    """서버가 준비될 때까지 대기"""
    client = httpx.Client()
    for _ in range(max_attempts):
        try:
            resp = client.get(BASE_URL)
            if resp.status_code == 200:
                return True
        except httpx.ConnectError:
            time.sleep(0.5)
    return False


def test_v1_endpoints():
    """v1 엔드포인트 테스트 (기본 LLM 호출)"""
    print("\n" + "=" * 60)
    print("V1 엔드포인트 테스트 (기본 LLM)")
    print("=" * 60)

    client = httpx.Client(timeout=20.0)

    v1_tests = [
        ("/v1/gpt", {"prompt": "안녕, gpt 테스트해줘"}),
        ("/v1/gemini", {"prompt": "안녕, gemini 테스트해줘"}),
        ("/v1/claude", {"prompt": "안녕, claude 테스트해줘"}),
    ]

    for endpoint, payload in v1_tests:
        url = f"{BASE_URL}{endpoint}"
        print(f"\n-> POST {url}")
        print(f"   payload={payload}")

        try:
            resp = client.post(url, json=payload)
            print(f"   Response ({resp.status_code}): {resp.json()}\n")
        except Exception as e:
            print(f"   Error: {e}\n")


def test_v2_endpoints():
    """v2 엔드포인트 테스트 (Prompt Template)"""
    print("\n" + "=" * 60)
    print("V2 엔드포인트 테스트 (Prompt Template)")
    print("=" * 60)

    client = httpx.Client(timeout=20.0)

    v2_tests = [
        ("/v2/prompt-template", {"text": "안녕", "target_lang": "영어"}),
        ("/v2/chat-prompt-template", {"text": "좋은 아침", "system_message": "사용자의 질의를 일본어로 번역해라."}),
        ("/v2/translate", {"text": "고마워", "target_lang": "중국어"}),
    ]

    for endpoint, payload in v2_tests:
        url = f"{BASE_URL}{endpoint}"
        print(f"\n-> POST {url}")
        print(f"   payload={payload}")

        try:
            resp = client.post(url, json=payload)
            print(f"   Response ({resp.status_code}):")
            response_data = resp.json()
            for key, value in response_data.items():
                print(f"     {key}: {value}")
            print()
        except Exception as e:
            print(f"   Error: {e}\n")


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("LangChain Multi-LLM API 테스트 시작")
    print("=" * 60)

    # 환경변수 설정
    env = os.environ.copy()
    env.setdefault("MOCK", "true")
    mock_mode = env.get("MOCK", "true").lower() == "true"
    print(f"🔧 MOCK Mode: {mock_mode}\n")

    # uvicorn 서버 시작
    print("Starting uvicorn server...")
    server_process = subprocess.Popen(UVICORN_CMD, env=env)

    # 서버 준비 대기
    if not wait_for_server():
        print("❌ Server failed to start")
        server_process.terminate()
        sys.exit(1)

    print("✅ Server ready — running endpoint tests\n")

    try:
        # v1 엔드포인트 테스트
        test_v1_endpoints()

        # v2 엔드포인트 테스트
        test_v2_endpoints()

        print("\n" + "=" * 60)
        print("✅ 모든 테스트 완료!")
        print("=" * 60)

    finally:
        # 서버 종료
        print("\nStopping server...")
        try:
            server_process.send_signal(signal.SIGINT)
            server_process.wait(timeout=5)
        except Exception:
            server_process.kill()


if __name__ == "__main__":
    main()
