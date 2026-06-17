import os
from core.interfaces import FileStorage

class LocalFileStorage(FileStorage):
    def __init__(self, upload_dir: str):
        """로컬 파일 저장소를 초기화하고 저장 폴더를 준비합니다."""
        self.upload_dir = os.path.abspath(upload_dir)
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)

    def save_file(self, filename: str, content: bytes) -> str:
        """업로드된 파일을 디렉토리에 바이너리로 저장하고 절대 경로를 반환합니다."""
        filepath = os.path.join(self.upload_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(content)
        return os.path.abspath(filepath)
