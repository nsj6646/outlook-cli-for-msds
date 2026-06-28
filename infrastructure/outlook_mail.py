import os
import win32com.client
import pythoncom
from typing import List, Optional

class OutlookMailService:
    def __init__(self, force_sender: bool = False, is_interactive: bool = False):
        self.force_sender = force_sender
        self.is_interactive = is_interactive

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
        deferred_time: Optional[str] = None
    ) -> bool:
        """아웃룩 COM 인터페이스를 이용해 메일을 전송하거나 초안 창을 띄웁니다."""
        if attachments is None:
            attachments = []

        # COM 라이브러리 초기화
        pythoncom.CoInitialize()
        try:
            outlook = win32com.client.Dispatch("Outlook.Application")
            namespace = outlook.GetNamespace("MAPI")
            
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

                # [안전장치 3] 기본 송신 계정(Primary)과 불일치할 때 처리
                if primary_email and sender_strip.lower() != primary_email.lower():
                    if not self.force_sender:
                        raise ValueError(
                            f"기본 송신 계정('{primary_email}')이 아닌 '{sender}' 계정으로 메일 발송이 시도되었습니다."
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
            if any(tag in body_lower for tag in ["<html>", "<body>", "<div", "<p>", "<br", "<table", "<tr", "<td"]):
                mail.HTMLBody = body
            else:
                mail.Body = body

            # 발신자 계정 바인딩
            if matched_account:
                mail.SendUsingAccount = matched_account

            # 예약 발송 설정 (Deferred Delivery)
            if deferred_time:
                if isinstance(deferred_time, str):
                    if deferred_time.strip():
                        mail.DeferredDeliveryTime = deferred_time.strip()
                else:
                    mail.DeferredDeliveryTime = deferred_time

            # 첨부파일 연동
            # ponytail: core/distribution.py에서 이미 절대경로 및 파일 존재 검증이 처리되어 넘겨지므로 이중 검증 생략
            for path in attachments:
                if path and path.strip():
                    mail.Attachments.Add(path.strip())

            # 5. 발송 실행
            if draft:
                if self.is_interactive:
                    mail.Display()
                else:
                    # 비대화형 모드(대량 발송 등)에서는 대화상자 포커스 에러 방지를 위해 초안 보관함(Drafts)에 저장만 수행
                    mail.Save()
            else:
                mail.Send()
            return True

        finally:
            # COM 라이브러리 역초기화
            pythoncom.CoUninitialize()
