import os
import logging
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from tqdm import tqdm
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

FILEPATH = f"write file name with path"  # 업로드할 로컬 파일 경로
UPLOAD_TITLE = "write file name"  # 드라이브에 올라갈 이름
PARENT_FOLDER_ID = "1gatOaj0spPS9z-XG83xEP7g00xery4ZR"  # 특정 폴더에 올릴 경우 폴더 ID 넣기 (예: "1AbC..."), 아니면 None

class TqdmFile:
    """Wrap file object to track reading progress with tqdm."""
    def __init__(self, file, total_size):
        self.file = file
        self.total_size = total_size
        self.tqdm = tqdm(total=total_size, unit="B", unit_scale=True, desc="Uploading")

    def read(self, size=-1):
        data = self.file.read(size)
        self.tqdm.update(len(data) if data else 0)
        return data

    def __getattr__(self, attr):
        return getattr(self.file, attr)

    def close(self):
        self.tqdm.close()
        self.file.close()

def ensure_file(path: str):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("hello drive")
        logging.info(f"테스트 파일 생성: {path}")

def auth_login(headless: bool = False):
    gauth = GoogleAuth()
    if headless:
        logging.info("브라우저 없는 환경: CommandLineAuth() 사용")
        gauth.CommandLineAuth()
    else:
        logging.info("로컬환경: LocalWebserverAuth() 사용(브라우저 팝업)")
        gauth.LocalWebserverAuth()
    return gauth

def upload_file(filepath: str, title: str, parent_id: str | None):
    gauth = auth_login(headless=False)  # GUI 없는 서버면 True
    drive = GoogleDrive(gauth)

    metadata = {"title": title}
    if parent_id:
        metadata["parents"] = [{"id": parent_id}]

    # Get file size for progress bar
    file_size = os.path.getsize(filepath)
    
    # Wrap file with TqdmFile for progress tracking
    with open(filepath, "rb") as f:
        tqdm_file = TqdmFile(f, file_size)
        f = drive.CreateFile(metadata)
        f.content = tqdm_file  # Set the wrapped file object
        f.Upload()  # Perform upload
        f.FetchMetadata(fields="id, title, alternateLink, webViewLink, webContentLink")
    
    logging.info("업로드 완료!")
    logging.info(f"ID: {f['id']}")
    logging.info(f"제목: {f['title']}")
    logging.info(f"보기 링크(webViewLink): {f.get('webViewLink')}")
    logging.info(f"다운로드 링크(webContentLink): {f.get('webContentLink')}")

if __name__ == "__main__":
    ensure_file(FILEPATH)
    upload_file(FILEPATH, UPLOAD_TITLE, PARENT_FOLDER_ID)