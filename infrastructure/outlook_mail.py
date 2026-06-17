import os
import win32com.client
import pythoncom
from typing import List, Optional
from core.interfaces import MailService

class OutlookMailService(MailService):
    def send_mail(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        sender: Optional[str] = None,
        draft: bool = False,
        force_sender: bool = False,
        is_interactive: bool = False
    ) -> bool:
        """아웃룩 COM 인터페이스를 이용해 메일을 전송하거나 초안 창을 띄웁니다."""
        if attachments is None:
            attachments = []

        # COM 라이브러리 초기화
        pythoncom.CoInitialize()
        try:
            outlook = win32com.client.Dispatch("Outlook.Application")
            namespace = outlook.GetNamespace("MAPI")
            
            # [안전장치 1] 오프라인 작업 상태 체크 및 경고
            if namespace.Offline:
                print("\n[!] 경고: 현재 아웃룩이 오프라인 또는 연결이 끊긴 상태입니다.")
                print("    메일이 발송되지 않고 아웃룩 [보낼 편지함(Outbox)]에 대기하게 됩니다.\n")

            matched_account = None
            primary_email = ""
            accounts = outlook.Session.Accounts
            
            if accounts.Count > 0:
                primary_email = accounts.Item(1).SmtpAddress

            # [안전장치 2] 발신자 주소 엄격 유효성 검사
            if sender:
                sender_strip = sender.strip()
                for i in range(1, accounts.Count + 1):
                    act = accounts.Item(i)
                    if act.SmtpAddress.lower() == sender_strip.lower():
                        matched_account = act
                        break

                if not matched_account:
                    raise ValueError(
                        f"지정한 발신자 이메일('{sender}')은 아웃룩 프로필에 등록된 계정이 아닙니다.\n"
                        "아웃룩 계정 설정을 확인하시거나 올바른 이메일 주소를 입력해 주세요."
                    )

                # [안전장치 3] 기본 송신 계정(Primary)과 불일치할 때 경고 처리
                if primary_email and sender_strip.lower() != primary_email.lower():
                    if is_interactive:
                        confirm = input(
                            f"\n[경고] 기본 계정('{primary_email}')이 아닌 '{sender}' 계정으로 메일을 전송합니다.\n"
                            "계속 진행하시겠습니까? (y/N): "
                        ).strip().lower()
                        if confirm not in ["y", "yes"]:
                            print("사용자 요청으로 메일 발송이 취소되었습니다.")
                            return False
                    else:
                        if not force_sender:
                            raise PermissionError(
                                f"기본 송신 계정('{primary_email}')이 아닌 '{sender}' 계정으로 메일 발송이 시도되었습니다.\n"
                                "오발송 방지를 위해 자동화 모드에서는 발송이 차단됩니다.\n"
                                "이 계정으로의 발송을 원하신다면 명령줄에 '--force-sender' 플래그를 추가해 주십시오."
                            )

            # 4. 메일 생성 및 속성 주입
            # 0 = olMailItem
            mail = outlook.CreateItem(0)
            mail.To = to
            if cc:
                mail.CC = cc
            if bcc:
                mail.BCC = bcc
            mail.Subject = subject

            # 본문 형식 (HTML 여부 판별)
            body_lower = body.lower()
            if any(tag in body_lower for tag in ["<html>", "<body>", "<div", "<p>", "<br"]):
                mail.HTMLBody = body
            else:
                mail.Body = body

            # 발신자 계정 바인딩
            if matched_account:
                mail.SendUsingAccount = matched_account

            # 첨부파일 연동
            for path in attachments:
                if not path.strip():
                    continue
                clean_path = path.strip().strip('"').strip("'")
                abs_path = os.path.abspath(clean_path)
                if os.path.exists(abs_path):
                    mail.Attachments.Add(abs_path)
                else:
                    raise FileNotFoundError(f"첨부할 파일을 찾을 수 없습니다: {abs_path}")

            # 5. 발송 실행
            if draft:
                mail.Display()
            else:
                mail.Send()
            return True

        finally:
            # COM 라이브러리 역초기화
            pythoncom.CoUninitialize()
