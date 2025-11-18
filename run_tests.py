"""Start the FastAPI server locally and run a few test requests against endpoints.
This script runs the server as a subprocess, calls endpoints, prints responses, then stops the server.

Usage: python run_tests.py
"""
import subprocess
import time
import os
import signal
import httpx


UVICORN_CMD = ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--log-level", "info"]


def wait_for_server(timeout=10.0):
    client = httpx.Client()
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = client.get("http://127.0.0.1:8000/")
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def run_tests():
    env = os.environ.copy()
    # Ensure mock mode is on for CI-free tests unless user overrides
    env.setdefault("MOCK", "true")

    print("Starting uvicorn server...")
    proc = subprocess.Popen(UVICORN_CMD, env=env)

    try:
        ok = wait_for_server()
        if not ok:
            print("Server did not start in time")
            proc.terminate()
            return

        print("Server ready — running endpoint tests")
        client = httpx.Client(timeout=20.0)
        endpoints = ["gpt", "gemini", "claude"]
        for ep in endpoints:
            url = f"http://127.0.0.1:8000/{ep}"
            payload = {"prompt": f"안녕, {ep} 테스트해줘"}
            print(f"-> POST {url} payload={payload}")
            r = client.post(url, json=payload)
            print(f"Response ({r.status_code}): {r.text}\n")

    finally:
        print("Stopping server...")
        try:
            proc.send_signal(signal.SIGINT)
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


if __name__ == "__main__":
    run_tests()
