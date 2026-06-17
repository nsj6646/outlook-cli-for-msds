"""
웹 서버(app.py)의 기동 및 API 엔드포인트를 검증하는 스크립트입니다.
서버를 백그라운드 프로세스로 띄운 후 urllib로 HTTP 요청을 보내 응답을 확인합니다.
"""
import os
import sys
import json
import time
import signal
import subprocess
import urllib.request
import urllib.error

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_SCRIPT = os.path.join(PROJECT_ROOT, "app.py")
TEST_PORT = 18923  # 일반 사용 포트와 충돌 방지를 위해 비표준 포트 사용

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.details = []
    
    def record(self, name, success, message=""):
        if success:
            self.passed += 1
            status = "✅ PASS"
        else:
            self.failed += 1
            status = "❌ FAIL"
        
        line = f"  {status}: {name}"
        if message:
            line += f"\n         {message}"
        self.details.append(line)
        print(line)

def start_server():
    """app.py를 백그라운드 프로세스로 기동합니다."""
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.Popen(
        [sys.executable, APP_SCRIPT, str(TEST_PORT)],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
    )
    return proc

def wait_for_server(port, timeout=10):
    """서버가 응답할 때까지 대기합니다."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            urllib.request.urlopen(f"http://localhost:{port}/", timeout=2)
            return True
        except Exception:
            time.sleep(0.5)
    return False

def stop_server(proc):
    """서버 프로세스를 종료합니다."""
    try:
        proc.terminate()
        proc.wait(timeout=5)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass

def http_post(port, path, data=None, content_type="application/json"):
    """HTTP POST 요청을 보내고 (status_code, response_body) 튜플을 반환합니다."""
    url = f"http://localhost:{port}{path}"
    if data is not None:
        if isinstance(data, dict):
            body = json.dumps(data).encode("utf-8")
        else:
            body = data
    else:
        body = b""
    
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": content_type},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            resp_body = json.loads(e.read().decode("utf-8"))
        except Exception:
            resp_body = {}
        return e.code, resp_body
    except Exception as e:
        return -1, {"error": str(e)}

def main():
    results = TestResult()
    
    print(f"[web-tester] 웹 서버 및 API 엔드포인트 검증 시작...")
    print(f"  테스트 포트: {TEST_PORT}\n")
    
    # 서버 기동
    print("  서버 기동 중...")
    server_proc = start_server()
    
    try:
        server_ready = wait_for_server(TEST_PORT)
        if not server_ready:
            print("  ❌ 서버가 시간 내에 응답하지 않습니다. 테스트를 중단합니다.")
            stop_server(server_proc)
            sys.exit(1)
        
        print(f"  서버 기동 완료 (http://localhost:{TEST_PORT})\n")
        
        # ──────────────────────────────────────
        # 테스트 1: 메인 페이지 접속 확인 (GET /)
        # ──────────────────────────────────────
        try:
            with urllib.request.urlopen(f"http://localhost:{TEST_PORT}/", timeout=5) as resp:
                results.record(
                    "GET / 메인 페이지 (HTTP 200)",
                    resp.status == 200,
                    f"HTTP {resp.status}"
                )
        except Exception as e:
            results.record("GET / 메인 페이지 (HTTP 200)", False, str(e))
        
        # ──────────────────────────────────────
        # 테스트 2: POST /api/send 필수 필드 누락 (To 없음)
        # ──────────────────────────────────────
        status, body = http_post(TEST_PORT, "/api/send", {"subject": "test", "body": "test"})
        results.record(
            "POST /api/send 필수 필드 누락 (HTTP 400)",
            status == 400 and body.get("status") == "error",
            f"HTTP {status}, status={body.get('status', 'N/A')}"
        )
        
        # ──────────────────────────────────────
        # 테스트 3: POST /api/upload boundary 누락
        # ──────────────────────────────────────
        status, body = http_post(
            TEST_PORT, "/api/upload",
            b"dummy data",
            content_type="multipart/form-data"  # boundary 없음
        )
        results.record(
            "POST /api/upload boundary 누락 (HTTP 400)",
            status == 400 and body.get("status") == "error",
            f"HTTP {status}, status={body.get('status', 'N/A')}"
        )
        
        # ──────────────────────────────────────
        # 테스트 4: 존재하지 않는 경로 (404)
        # ──────────────────────────────────────
        status, body = http_post(TEST_PORT, "/api/nonexistent", {})
        results.record(
            "POST /api/nonexistent (HTTP 404)",
            status == 404 and body.get("status") == "error",
            f"HTTP {status}, status={body.get('status', 'N/A')}"
        )
        
    finally:
        # 서버 종료
        print("\n  서버 종료 중...")
        stop_server(server_proc)
        print("  서버 종료 완료.")
    
    # ──────────────────────────────────────
    # 결과 요약
    # ──────────────────────────────────────
    total = results.passed + results.failed
    print(f"\n{'='*50}")
    print(f"[결과] 총 {total}개 테스트 | ✅ {results.passed} 통과 | ❌ {results.failed} 실패")
    print(f"{'='*50}")
    
    if results.failed > 0:
        print("\n[경고] 일부 웹 API 테스트가 실패했습니다.")
        sys.exit(1)
    else:
        print("\n[성공] 모든 웹 API 테스트를 통과했습니다.")
        sys.exit(0)

if __name__ == "__main__":
    main()
