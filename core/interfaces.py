from abc import ABC, abstractmethod
from typing import List, Optional

class MailService(ABC):
    @abstractmethod
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
        """이메일을 발송하거나 초안 창을 엽니다.
        
        Args:
            to: 수신자 주소
            subject: 메일 제목
            body: 메일 본문 (HTML 여부는 서비스 내부에서 판별)
            cc: 참조 주소
            bcc: 숨은 참조 주소
            attachments: 첨부파일의 로컬 경로 목록
            sender: 발신자 지정 메일 주소
            draft: True일 경우 메일을 즉시 전송하지 않고 아웃룩 편집(초안) 창을 표시
            force_sender: 발신자 불일치 경고를 우회할 것인지 여부 (자동화 스크립트용)
            is_interactive: 대화형 CLI 모드 여부 (발신 계정 경고 시 사용자 입력을 받기 위해 사용)
            
        Returns:
            성공적으로 수행되었을 경우 True, 실패 시 예외를 발생시키거나 False 반환
        """
        pass

class FileStorage(ABC):
    @abstractmethod
    def save_file(self, filename: str, content: bytes) -> str:
        """업로드된 파일 콘텐츠를 특정 영속 경로에 저장합니다.
        
        Args:
            filename: 원본 파일 이름
            content: 파일 바이너리 내용
            
        Returns:
            저장된 파일의 절대 경로 문자열
        """
        pass
