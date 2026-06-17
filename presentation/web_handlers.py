import json
import re
from core.interfaces import FileStorage, MailService

def parse_multipart(body: bytes, boundary: str):
    """표준 라이브러리 파서가 없는 환경을 위해 바이너리 멀티파트 폼 데이터를 파싱합니다."""
    boundary_bytes = b'--' + boundary.encode('utf-8')
    parts = body.split(boundary_bytes)
    
    files = []
    for part in parts:
        if part.startswith(b'\r\n'):
            part = part[2:]
        if part.endswith(b'\r\n'):
            part = part[:-2]
        if part.endswith(b'--') or not part:
            continue
            
        if b'\r\n\r\n' in part:
            headers_part, content = part.split(b'\r\n\r\n', 1)
            headers_str = headers_part.decode('utf-8', errors='ignore')
            
            if 'filename="' in headers_str:
                filename_match = re.search(r'filename="([^"]+)"', headers_str)
                field_match = re.search(r'name="([^"]+)"', headers_str)
                
                if filename_match:
                    filename = filename_match.group(1)
                    fieldname = field_match.group(1) if field_match else "file"
                    files.append({
                        "fieldname": fieldname,
                        "filename": filename,
                        "content": content
                    })
    return files

class WebController:
    def __init__(self, mail_service: MailService, storage: FileStorage, router):
        """컨트롤러에 외부 의존성들을 주입받아 바인딩합니다 (의존성 주입)."""
        self.mail_service = mail_service
        self.storage = storage
        self.router = router

    def handle_upload(self, request_handler, body_bytes: bytes):
        """파일 업로드 요청을 처리하고 파일 저장소에 위임합니다."""
        content_type = request_handler.headers.get('Content-Type', '')
        if 'boundary=' not in content_type:
            self.router.send_json_response(request_handler, 400, {
                "status": "error",
                "message": "잘못된 Content-Type 헤더입니다. (boundary 누락)"
            })
            return
        boundary = content_type.split('boundary=')[1].strip()
        
        try:
            uploaded_files = parse_multipart(body_bytes, boundary)
            if not uploaded_files:
                self.router.send_json_response(request_handler, 400, {
                    "status": "error",
                    "message": "업로드된 파일이 없습니다."
                })
                return
                
            file_info = uploaded_files[0]
            filename = file_info['filename']
            content = file_info['content']
            
            # FileStorage 인터페이스를 통해 파일 저장 수행
            abs_path = self.storage.save_file(filename, content)
            
            self.router.send_json_response(request_handler, 200, {
                "status": "success",
                "message": "파일이 서버 임시 폴더에 업로드되었습니다.",
                "filepath": abs_path, 
                "filename": filename
            })
        except Exception as e:
            self.router.send_json_response(request_handler, 500, {
                "status": "error",
                "message": f"파일 업로드 중 오류가 발생했습니다: {str(e)}"
            })

    def handle_send(self, request_handler, body_bytes: bytes):
        """메일 발송 요청을 처리하고 메일 서비스에 위임합니다."""
        try:
            data = json.loads(body_bytes.decode('utf-8'))
            to_address = data.get('to', '')
            cc_address = data.get('cc', '')
            bcc_address = data.get('bcc', '')
            subject = data.get('subject', '')
            body = data.get('body', '')
            attachments = data.get('attachments', [])
            display = data.get('display', False)
            sender = data.get('sender', '')
            
            if not to_address:
                self.router.send_json_response(request_handler, 400, {
                    "status": "error",
                    "message": "수신자(To) 이메일 주소는 필수 항목입니다."
                })
                return

            # MailService 인터페이스를 사용하여 메일 발송 수행
            # 웹 서버 호출 시에는 대화형 입력이 차단되므로 force_sender=True, is_interactive=False로 지정
            self.mail_service.send_mail(
                to=to_address,
                subject=subject,
                body=body,
                cc=cc_address if cc_address else None,
                bcc=bcc_address if bcc_address else None,
                attachments=attachments,
                sender=sender if sender else None,
                draft=display,
                force_sender=True,
                is_interactive=False
            )
            
            msg = "Outlook 창에 이메일 초안이 열렸습니다." if display else "이메일이 성공적으로 전송되었습니다."
            self.router.send_json_response(request_handler, 200, {
                "status": "success",
                "message": msg
            })
        except json.JSONDecodeError:
            self.router.send_json_response(request_handler, 400, {
                "status": "error",
                "message": "잘못된 JSON 데이터 형식입니다."
            })
        except Exception as e:
            self.router.send_json_response(request_handler, 500, {
                "status": "error",
                "message": f"메일 전송 중 오류가 발생했습니다: {str(e)}"
            })
