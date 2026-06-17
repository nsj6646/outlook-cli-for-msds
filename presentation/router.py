import json

class Router:
    def __init__(self):
        # (HTTP_METHOD, PATH) -> handler_function
        self.routes = {}

    def add_route(self, method: str, path: str, handler):
        self.routes[(method.upper(), path)] = handler

    def get(self, path: str):
        def decorator(handler):
            self.add_route('GET', path, handler)
            return handler
        return decorator

    def post(self, path: str):
        def decorator(handler):
            self.add_route('POST', path, handler)
            return handler
        return decorator

    def handle(self, request_handler, path: str, method: str, body: bytes = b""):
        """HTTP 요청을 적절한 라우트로 디스패치하고 응답을 보냅니다."""
        # CORS OPTIONS 사전 요청 처리
        if method.upper() == 'OPTIONS':
            request_handler.send_response(200)
            self.send_cors_headers(request_handler)
            request_handler.end_headers()
            return

        route_key = (method.upper(), path)
        if route_key in self.routes:
            handler = self.routes[route_key]
            try:
                handler(request_handler, body)
            except Exception as e:
                self.send_json_response(request_handler, 500, {
                    "status": "error",
                    "message": f"서버 내부 오류가 발생했습니다: {str(e)}"
                })
        else:
            self.send_json_response(request_handler, 404, {
                "status": "error",
                "message": "엔드포인트를 찾을 수 없습니다."
            })

    def send_cors_headers(self, request_handler):
        """CORS 접근을 허용하기 위한 헤더를 보냅니다."""
        request_handler.send_header('Access-Control-Allow-Origin', '*')
        request_handler.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        request_handler.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def send_json_response(self, request_handler, status_code: int, data: dict):
        """JSON 형식으로 HTTP 응답을 전송합니다."""
        request_handler.send_response(status_code)
        request_handler.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_cors_headers(request_handler)
        request_handler.end_headers()
        request_handler.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
