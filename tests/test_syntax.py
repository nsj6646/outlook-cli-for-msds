"""
프로젝트 내 모든 .py 파일의 Python 문법을 검사하는 스크립트입니다.
py_compile을 사용하여 각 파일의 컴파일 가능 여부를 확인합니다.
"""
import os
import sys
import py_compile

EXCLUDED_DIRS = {'.git', '__pycache__', 'temp_attachments', '.agents'}

def find_python_files(root_dir):
    """프로젝트 루트에서 .py 파일을 재귀적으로 탐색합니다."""
    py_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # 제외할 디렉토리를 건너뜁니다
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        for filename in filenames:
            if filename.endswith('.py'):
                py_files.append(os.path.join(dirpath, filename))
    return py_files

def check_syntax(filepath):
    """단일 파일의 Python 문법을 검사합니다."""
    try:
        py_compile.compile(filepath, doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, str(e)

def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    py_files = find_python_files(project_root)
    
    if not py_files:
        print("[경고] 검사할 .py 파일을 찾지 못했습니다.")
        sys.exit(0)
    
    print(f"[syntax-checker] {len(py_files)}개의 Python 파일 문법 검사 시작...\n")
    
    passed = 0
    failed = 0
    errors = []
    
    for filepath in sorted(py_files):
        rel_path = os.path.relpath(filepath, project_root)
        ok, error_msg = check_syntax(filepath)
        if ok:
            print(f"  ✅ PASS: {rel_path}")
            passed += 1
        else:
            print(f"  ❌ FAIL: {rel_path}")
            print(f"         {error_msg}")
            failed += 1
            errors.append((rel_path, error_msg))
    
    print(f"\n{'='*50}")
    print(f"[결과] 총 {len(py_files)}개 파일 | ✅ {passed} 통과 | ❌ {failed} 실패")
    print(f"{'='*50}")
    
    if failed > 0:
        print("\n[오류] 문법 오류가 발견된 파일:")
        for rel_path, error_msg in errors:
            print(f"  - {rel_path}: {error_msg}")
        sys.exit(1)
    else:
        print("\n[성공] 모든 Python 파일의 문법이 정상입니다.")
        sys.exit(0)

if __name__ == "__main__":
    main()
