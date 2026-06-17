import os
import sys
from http.server import SimpleHTTPRequestHandler, HTTPServer
from infrastructure.outlook_mail import OutlookMailService
from infrastructure.local_storage import LocalFileStorage
from presentation.router import Router
from presentation.web_handlers import WebController

# 1. 의존성 주입 대상 객체 및 설정 구성
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_attachments')
mail_service = OutlookMailService()
file_storage = LocalFileStorage(UPLOAD_DIR)

# 2. HTTP 라우터 초기화 및 웹 컨트롤러 인스턴스화
router = Router()
controller = WebController(mail_service, file_storage, router)

# API 엔드포인트 라우팅 매핑
@router.post('/api/upload')
def upload_api(request_handler, body_bytes):
    controller.handle_upload(request_handler, body_bytes)

@router.post('/api/send')
def send_api(request_handler, body_bytes):
    controller.handle_send(request_handler, body_bytes)

# 3. HTTP 서버 요청 핸들러
class OutlookServerHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b""
        router.handle(self, self.path, 'POST', body)

    def do_OPTIONS(self):
        router.handle(self, self.path, 'OPTIONS')


def run(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, OutlookServerHandler)
    print(f"Starting server on http://localhost:{port} ...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()


if __name__ == '__main__':
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run(port)
