import os
import sys
import json
import argparse
import re
from infrastructure.outlook_mail import OutlookMailService

CONFIG_FILENAME = "outlook_config.json"

def load_config():
    """outlook_config.json 파일에서 설정을 로드합니다."""
    config = {"default_from": ""}
    # 스크립트가 있는 디렉토리 기준 경로 획득
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, CONFIG_FILENAME)
    
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, dict):
                    config.update(loaded)
        except Exception as e:
            print(f"[경고] 설정 파일을 읽는 중 오류가 발생했습니다: {str(e)}")
    return config

def get_local_files():
    """현재 작업 폴더의 파일 목록을 획득합니다."""
    try:
        return [f for f in os.listdir(".") if os.path.isfile(f)]
    except Exception:
        return []

def run_interactive_mode(local_files):
    """사용자와 인터랙티브하게 메일 정보를 묻고 수집합니다."""
    print("\n==============================================")
    print("      아웃룩 메일 발송 CLI 대화형 모드")
    print("==============================================")
    
    # 1. 수신자 (To) - 필수
    to_addr = ""
    while not to_addr:
        to_addr = input("1. 받는 사람 (To) [필수]: ").strip()
        if not to_addr:
            print("[오류] 받는 사람 이메일 주소는 필수 입력 사항입니다.")
            
    # 2. 참조 (CC), 숨은 참조 (BCC)
    cc_addr = input("2. 참조 (CC) [선택, 없으면 Enter]: ").strip()
    bcc_addr = input("3. 숨은 참조 (BCC) [선택, 없으면 Enter]: ").strip()
    
    # 3. 제목
    subject = input("4. 메일 제목 [선택, 없으면 Enter]: ").strip()
    
    # 4. 본문 내용 작성 방식 선택
    body_content = ""
    print("\n5. 본문 내용 입력 방식을 선택해 주세요:")
    print("  [1] 직접 텍스트 기입 (여러 줄 입력)")
    print("  [2] 외부 파일 로드 (.html 또는 .txt)")
    
    body_choice = ""
    while body_choice not in ["1", "2"]:
        body_choice = input("선택 (1 또는 2): ").strip()
        
    if body_choice == "1":
        print("본문을 입력하세요. 작성을 완료하려면 빈 줄(Enter)을 두 번 연속으로 입력하세요:")
        lines = []
        empty_count = 0
        while True:
            line = input()
            if not line:
                empty_count += 1
                if empty_count >= 2:
                    break
            else:
                empty_count = 0
                lines.append(line)
        body_content = "\n".join(lines)
    else:
        file_loaded = False
        while not file_loaded:
            file_path = input("본문 파일 경로를 입력하세요: ").strip().strip('"').strip("'")
            if not file_path:
                print("본문 없이 공백으로 진행합니다.")
                break
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        body_content = f.read()
                    file_loaded = True
                except Exception as e:
                    print(f"[오류] 파일을 읽을 수 없습니다: {str(e)}")
            else:
                print("[오류] 파일이 존재하지 않습니다. 다시 입력해 주세요.")
                
    # 5. 첨부 파일 수동 선택
    attachments = []
    print("\n6. 첨부 파일 추가 섹션")
    if local_files:
        print("--- 현재 작업 폴더 내 파일 리스트 ---")
        for idx, fname in enumerate(local_files, 1):
            print(f"  [{idx}] {fname}")
        print("-------------------------------------")
        print("  - 첨부할 파일 번호를 쉼표로 입력해 주세요 (예: 1, 3).")
    
    print("  - 직접 파일의 로컬 절대 경로를 입력해도 됩니다.")
    print("  - 첨부할 파일이 없다면 입력 없이 Enter를 누르세요.")
    
    attach_input = input("입력: ").strip()
    if attach_input:
        # 번호 선택 파싱 시도
        nums = re.findall(r"\d+", attach_input)
        if nums and all(1 <= int(n) <= len(local_files) for n in nums):
            for n in nums:
                filepath = os.path.abspath(local_files[int(n) - 1])
                attachments.append(filepath)
                print(f"  -> 첨부 대기열 추가: {local_files[int(n) - 1]}")
        else:
            # 절대 경로 직접 처리
            clean_path = attach_input.strip('"').strip("'")
            if os.path.exists(clean_path):
                attachments.append(os.path.abspath(clean_path))
                print(f"  -> 첨부 대기열 추가: {clean_path}")
            else:
                print(f"[경고] 파일 경로를 찾을 수 없어 스킵합니다: {clean_path}")
                
    # 6. 발송 모드 선택
    print("\n7. 발송 방식 선택:")
    print("  [1] 아웃룩을 통한 즉시 발송 (기본)")
    print("  [2] 아웃룩 초안 창 열기 (Display)")
    
    send_choice = input("선택 (1 또는 2): ").strip()
    is_draft = (send_choice == "2")
    
    return {
        "to": to_addr,
        "cc": cc_addr,
        "bcc": bcc_addr,
        "subject": subject,
        "body": body_content,
        "attachments": attachments,
        "draft": is_draft
    }

def main():
    config = load_config()
    local_files = get_local_files()
    
    parser = argparse.ArgumentParser(description="Outlook Mail Automator CLI Tool")
    parser.add_argument("-t", "--to", help="수신자 이메일 주소 (To)")
    parser.add_argument("-c", "--cc", help="참조 이메일 주소 (CC)")
    parser.add_argument("-b", "--bcc", help="숨은 참조 이메일 주소 (BCC)")
    parser.add_argument("-s", "--subject", help="메일 제목")
    parser.add_argument("--body", help="메일 본문 텍스트")
    parser.add_argument("-f", "--body-file", help="메일 본문으로 사용할 외부 템플릿 파일 경로 (.html 또는 .txt)")
    parser.add_argument("-a", "--attach", action="append", default=[], help="첨부파일 절대 경로 (여러 개 지정 시 반복 입력)")
    parser.add_argument("--from", dest="sender", help="발신자 이메일 주소 (미지정 시 설정 파일 또는 기본 계정 사용)")
    parser.add_argument("--force-sender", action="store_true", help="기본 발신 계정과 일치하지 않을 때의 자동화 경고 우회 플래그")
    parser.add_argument("--draft", action="store_true", help="즉시 발송하지 않고 아웃룩 초안 창을 띄우는 플래그")
    parser.add_argument("-i", "--interactive", action="store_true", help="명령줄 인자가 있더라도 강제로 대화형 모드 진입")
    
    args = parser.parse_args()
    
    # 1. 대화형 모드(Interactive Mode) 판별 조건
    is_interactive = (
        args.interactive or
        (len(sys.argv) == 1) or
        (not args.to)
    )
    
    mail_data = {}
    
    if is_interactive:
        mail_data = run_interactive_mode(local_files)
        sender_email = args.sender or config.get("default_from", "").strip()
        force_sender = False # 대화형 모드에서는 프롬프트로 확인받음
    else:
        # 명령줄 인수 기반 파싱
        body_content = ""
        if args.body_file:
            if os.path.exists(args.body_file):
                try:
                    with open(args.body_file, "r", encoding="utf-8") as f:
                        body_content = f.read()
                except Exception as e:
                    print(f"[오류] 본문 파일을 읽을 수 없습니다: {str(e)}")
                    sys.exit(1)
            else:
                print(f"[오류] 지정한 본문 파일을 찾을 수 없습니다: {args.body_file}")
                sys.exit(1)
        else:
            body_content = args.body or ""
            
        mail_data = {
            "to": args.to.strip(),
            "cc": (args.cc or "").strip(),
            "bcc": (args.bcc or "").strip(),
            "subject": (args.subject or "").strip(),
            "body": body_content,
            "attachments": [os.path.abspath(p.strip('"').strip("'")) for p in args.attach if p.strip()],
            "draft": args.draft
        }
        sender_email = args.sender or config.get("default_from", "").strip()
        force_sender = args.force_sender

    # 2. 아웃룩 공통 서비스 인스턴스화 및 실행
    mail_service = OutlookMailService()
    try:
        success = mail_service.send_mail(
            to=mail_data["to"],
            subject=mail_data["subject"],
            body=mail_data["body"],
            cc=mail_data["cc"] if mail_data["cc"] else None,
            bcc=mail_data["bcc"] if mail_data["bcc"] else None,
            attachments=mail_data["attachments"],
            sender=sender_email if sender_email else None,
            draft=mail_data["draft"],
            force_sender=force_sender,
            is_interactive=is_interactive
        )
        if success:
            msg = "아웃룩 이메일 편집창(초안)이 화면에 표시되었습니다." if mail_data["draft"] else "아웃룩에 메일 전송 요청을 전달했습니다."
            print(f"\n[성공] {msg}")
        else:
            print("\n[알림] 메일 발송 작업이 중단되었거나 취소되었습니다.")
            sys.exit(0)
    except Exception as ex:
        print(f"\n[오류] 아웃룩 자동화 과정 중 문제가 발생했습니다: {str(ex)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
