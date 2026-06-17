"""
CLI(outlook_cli.py) 기능을 종합적으로 검증하는 스크립트입니다.
subprocess를 사용하여 다양한 시나리오를 실행하고 exit code 및 출력을 검증합니다.

환경변수 OUTLOOK_TEST_ENABLED=true 설정 시 아웃룩 COM 연동 테스트가 추가로 실행됩니다.
"""
import os
import sys
import json
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI_SCRIPT = os.path.join(PROJECT_ROOT, "outlook_cli.py")
CONFIG_PATH = os.path.join(PROJECT_ROOT, "outlook_config.json")
OUTLOOK_ENABLED = os.environ.get("OUTLOOK_TEST_ENABLED", "").lower() == "true"

def load_test_email():
    """outlook_config.json에서 테스트용 이메일 주소를 로드합니다."""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
            return config.get("default_from", "").strip()
    except Exception:
        return ""

def run_cli(*args, timeout=30):
    """CLI 스크립트를 실행하고 결과를 반환합니다."""
    cmd = [sys.executable, CLI_SCRIPT] + list(args)
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            cwd=PROJECT_ROOT,
            env=env
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.details = []
    
    def record(self, name, success, message="", skipped=False):
        if skipped:
            self.skipped += 1
            status = "⏭️ SKIP"
        elif success:
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

def main():
    test_email = load_test_email()
    results = TestResult()
    
    print(f"[cli-tester] CLI 기능 종합 검증 시작...")
    print(f"  아웃룩 연동 테스트: {'활성화' if OUTLOOK_ENABLED else '비활성화 (OUTLOOK_TEST_ENABLED=true 로 활성화)'}")
    if test_email:
        print(f"  테스트 이메일: {test_email}")
    print()
    
    # ──────────────────────────────────────
    # 테스트 1: --help 정상 실행
    # ──────────────────────────────────────
    code, stdout, stderr = run_cli("--help")
    results.record(
        "--help 정상 실행 (exit code 0)",
        code == 0,
        f"exit code={code}" if code != 0 else ""
    )
    
    # ──────────────────────────────────────
    # 테스트 2: 미등록 발신자 차단
    # (아웃룩이 필요한 테스트)
    # ──────────────────────────────────────
    if OUTLOOK_ENABLED:
        code, stdout, stderr = run_cli(
            "--to", "test@example.com",
            "--from", "wrong@example.com",
            "--subject", "Test",
            "--body", "Test",
            "--draft"
        )
        has_error_msg = "등록된 계정이 아닙니다" in stdout or "등록된 계정이 아닙니다" in stderr
        results.record(
            "--from wrong@example.com 미등록 계정 차단 (exit code 1)",
            code == 1 and has_error_msg,
            f"exit code={code}, 에러 메시지 포함={'예' if has_error_msg else '아니오'}"
        )
    else:
        results.record(
            "--from wrong@example.com 미등록 계정 차단",
            False,
            "OUTLOOK_TEST_ENABLED 미설정으로 스킵",
            skipped=True
        )

    # ──────────────────────────────────────
    # 테스트 3: 초안 생성 (--draft)
    # ──────────────────────────────────────
    if OUTLOOK_ENABLED and test_email:
        code, stdout, stderr = run_cli(
            "--to", test_email,
            "--subject", "[CLI-TESTER] 초안 테스트",
            "--body", "이것은 cli-tester 서브에이전트의 자동 검증 초안입니다.",
            "--draft"
        )
        has_success = "성공" in stdout
        results.record(
            f"--to {test_email} --draft 초안 생성",
            code == 0 and has_success,
            f"exit code={code}, '성공' 출력={'예' if has_success else '아니오'}"
        )
    else:
        results.record(
            "--draft 초안 생성",
            False,
            "OUTLOOK_TEST_ENABLED 미설정 또는 test_email 없음으로 스킵",
            skipped=True
        )
    
    # ──────────────────────────────────────
    # 테스트 4: 첨부 파일 포함 실제 발송
    # ──────────────────────────────────────
    if OUTLOOK_ENABLED and test_email:
        # 테스트용 첨부 파일 생성
        test_attach_path = os.path.join(PROJECT_ROOT, "tests", "_test_attachment.txt")
        with open(test_attach_path, "w", encoding="utf-8") as f:
            f.write("cli-tester 자동 검증용 테스트 첨부 파일입니다.\n")
        
        code, stdout, stderr = run_cli(
            "--to", test_email,
            "--subject", "[CLI-TESTER] 첨부 포함 발송 테스트",
            "--body", "이것은 cli-tester 서브에이전트의 첨부 파일 포함 자동 검증 메일입니다.",
            "--attach", test_attach_path
        )
        has_success = "성공" in stdout
        results.record(
            f"--to {test_email} --attach 첨부 포함 실제 발송",
            code == 0 and has_success,
            f"exit code={code}, '성공' 출력={'예' if has_success else '아니오'}"
        )
        
        # 테스트 첨부 파일 정리
        if os.path.exists(test_attach_path):
            os.remove(test_attach_path)
    else:
        results.record(
            "첨부 포함 실제 발송",
            False,
            "OUTLOOK_TEST_ENABLED 미설정 또는 test_email 없음으로 스킵",
            skipped=True
        )
    
    # ──────────────────────────────────────
    # 결과 요약
    # ──────────────────────────────────────
    total = results.passed + results.failed + results.skipped
    print(f"\n{'='*50}")
    print(f"[결과] 총 {total}개 테스트 | ✅ {results.passed} 통과 | ❌ {results.failed} 실패 | ⏭️ {results.skipped} 스킵")
    print(f"{'='*50}")
    
    if results.failed > 0:
        print("\n[경고] 일부 CLI 테스트가 실패했습니다.")
        sys.exit(1)
    else:
        print("\n[성공] 모든 CLI 테스트를 통과했습니다.")
        sys.exit(0)

if __name__ == "__main__":
    main()
