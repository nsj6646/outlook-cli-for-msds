import os
import sys
import json
import argparse
import re
from typing import Optional, List
from infrastructure.outlook_mail import OutlookMailService
from core.distribution import MailDistributionContext

CONFIG_FILENAME = "outlook_config.json"

def send_bulk_mails_from_excel(excel_path: str, sender_email: Optional[str], force_sender: bool, draft: bool, msds_dir: Optional[str] = None):
    """MailDistributionContext 모듈을 통해 조립된 jobs를 로드하여 아웃룩으로 순차 발송합니다."""
    try:
        dist_context = MailDistributionContext(excel_path, msds_dir, sender_email)
        jobs = dist_context.load_jobs()
    except Exception as e:
        raise ValueError(f"배포 대상 로딩에 실패했습니다: {str(e)}")

    mail_service = OutlookMailService(force_sender=force_sender, is_interactive=False)
    
    success_count = 0
    failure_count = 0
    
    print(f"\n[대량 메일 발송 시작] 총 {len(jobs)}건의 발송 대기열 처리를 시작합니다.")
    
    for idx, job in enumerate(jobs, 1):
        print(f"[{idx}/{len(jobs)}] '{job.to_addr}' 대상 메일 초안 작성 시도 중...")
        try:
            success = mail_service.send_mail(
                to=job.to_addr,
                subject=job.subject,
                body=job.body,
                cc=job.cc_addr,
                bcc=job.bcc_addr,
                attachments=job.attachments,
                sender=job.from_addr,
                draft=draft,
                deferred_time=job.deferred_time
            )
            if success:
                success_count += 1
                mode_str = "초안 보관함 저장" if draft else "즉시 발송"
                print(f"   -> [성공] {mode_str} 완료")
            else:
                failure_count += 1
                print("   -> [실패] 발송 작업이 중단되었습니다.")
        except Exception as ex:
            failure_count += 1
            print(f"   -> [에러] 발송 실패: {str(ex)}")
            
    print("\n==============================================")
    print("               대량 발송 결과 요약")
    print("==============================================")
    print(f"성공 건수: {success_count}건")
    print(f"실패 건수: {failure_count}건")
    print(f"총 처리 건수: {success_count + failure_count}건")
    print("==============================================")


def load_config():
    """outlook_config.json 파일에서 설정을 로드합니다."""
    config = {"default_from": ""}
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
    
    to_addr = ""
    while not to_addr:
        to_addr = input("1. 받는 사람 (To) [필수]: ").strip()
        if not to_addr:
            print("[오류] 받는 사람 이메일 주소는 필수 입력 사항입니다.")
            
    cc_addr = input("2. 참조 (CC) [선택, 없으면 Enter]: ").strip()
    bcc_addr = input("3. 숨은 참조 (BCC) [선택, 없으면 Enter]: ").strip()
    subject = input("4. 메일 제목 [선택, 없으면 Enter]: ").strip()
    
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
        nums = re.findall(r"\d+", attach_input)
        if nums and all(1 <= int(n) <= len(local_files) for n in nums):
            for n in nums:
                filepath = os.path.abspath(local_files[int(n) - 1])
                attachments.append(filepath)
                print(f"  -> 첨부 대기열 추가: {local_files[int(n) - 1]}")
        else:
            clean_path = attach_input.strip('"').strip("'")
            if os.path.exists(clean_path):
                attachments.append(os.path.abspath(clean_path))
                print(f"  -> 첨부 대기열 추가: {clean_path}")
            else:
                print(f"[오류] 파일 경로를 찾을 수 없어 스킵합니다: {clean_path}")
                
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
    parser.add_argument("-e", "--excel", help="엑셀 파일 경로 (.xlsx) 지정 시 대량 메일 발송 모드로 작동합니다.")
    parser.add_argument("--msds-dir", help="MSDS 파일들이 모여있는 폴더 경로 (지정하지 않으면 현재 폴더)")
    
    args = parser.parse_args()
    
    if args.excel:
        sender_email = args.sender or config.get("default_from", "").strip()
        try:
            send_bulk_mails_from_excel(
                excel_path=args.excel,
                sender_email=sender_email if sender_email else None,
                force_sender=args.force_sender,
                draft=args.draft,
                msds_dir=args.msds_dir
            )
        except Exception as ex:
            print(f"\n[오류] 엑셀 대량 발송 중 실패가 발생했습니다: {str(ex)}")
            sys.exit(1)
        sys.exit(0)
    
    is_interactive = (
        args.interactive or
        (len(sys.argv) == 1) or
        (not args.to)
    )
    
    mail_data = {}
    
    if is_interactive:
        mail_data = run_interactive_mode(local_files)
        sender_email = args.sender or config.get("default_from", "").strip()
        force_sender = False
    else:
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

    mail_service = OutlookMailService(force_sender=force_sender, is_interactive=is_interactive)
    try:
        success = mail_service.send_mail(
            to=mail_data["to"],
            subject=mail_data["subject"],
            body=mail_data["body"],
            cc=mail_data["cc"] if mail_data["cc"] else None,
            bcc=mail_data["bcc"] if mail_data["bcc"] else None,
            attachments=mail_data["attachments"],
            sender=sender_email if sender_email else None,
            draft=mail_data["draft"]
        )
        if success:
            msg = "아웃룩 이메일 편집창(초안)이 화면에 표시되었습니다." if mail_data["draft"] else "아웃룩에 메일 전송 요청을 전달했습니다."
            print(f"\n[성공] {msg}")
        else:
            print("\n[알림] 메일 발송 작업이 중단되었거나 취소되었습니다.")
            sys.exit(0)
    except ValueError as ex:
        err_msg = str(ex)
        if is_interactive and "기본 송신 계정" in err_msg and sender_email:
            ans = input(f"기본 계정이 아닌 {sender_email} 계정으로 메일을 전송합니다. 계속 진행하시겠습니까? (y/N): ").strip().lower()
            if ans in ["y", "yes"]:
                try:
                    retry_service = OutlookMailService(force_sender=True, is_interactive=is_interactive)
                    success = retry_service.send_mail(
                        to=mail_data["to"],
                        subject=mail_data["subject"],
                        body=mail_data["body"],
                        cc=mail_data["cc"] if mail_data["cc"] else None,
                        bcc=mail_data["bcc"] if mail_data["bcc"] else None,
                        attachments=mail_data["attachments"],
                        sender=sender_email if sender_email else None,
                        draft=mail_data["draft"]
                    )
                    if success:
                        msg = "아웃룩 이메일 편집창(초안)이 화면에 표시되었습니다." if mail_data["draft"] else "아웃룩에 메일 전송 요청을 전달했습니다."
                        print(f"\n[성공] {msg}")
                    else:
                        print("\n[알림] 메일 발송 작업이 중단되었거나 취소되었습니다.")
                except Exception as retry_ex:
                    print(f"\n[오류] 아웃룩 자동화 과정 중 문제가 발생했습니다: {str(retry_ex)}")
                    sys.exit(1)
            else:
                print("사용자 요청으로 메일 발송이 취소되었습니다.")
                sys.exit(0)
        else:
            print(f"\n[오류] 아웃룩 자동화 과정 중 문제가 발생했습니다: {err_msg}")
            sys.exit(1)
    except Exception as ex:
        print(f"\n[오류] 아웃룩 자동화 과정 중 문제가 발생했습니다: {str(ex)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
