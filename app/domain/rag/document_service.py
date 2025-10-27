import io
import shutil
from pathlib import Path
from googleapiclient.http import MediaIoBaseDownload
from app.domain.drive.service import DriveService


class DocumentService:
    def __init__(self):
        self.drive = DriveService()
        self.docs_path = Path("data/docs")
        self.docs_path.mkdir(parents=True, exist_ok=True)

    def download_documents(self, file_ids: list[str]):
        for file_id in file_ids:
            try:
                file = (
                    self.drive.service.files()
                    .get(
                        fileId=file_id, fields="name, mimeType", supportsAllDrives=True
                    )
                    .execute()
                )

                name = file["name"]
                mime_type = file["mimeType"]

                if "." not in name:
                    if mime_type == "application/pdf":
                        name += ".pdf"
                    elif mime_type.startswith("text/"):
                        name += ".txt"
                    elif "wordprocessingml" in mime_type:
                        name += ".docx"

                local_path = self.docs_path / name
                request = self.drive.service.files().get_media(
                    fileId=file_id, supportsAllDrives=True
                )
                fh = io.FileIO(local_path, "wb")
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                print(f"📄 Downloaded: {name}")

            except Exception as e:
                print(f"⚠️ Error downloading {file_id}: {e}")

    def cleanup(self):
        shutil.rmtree(self.docs_path, ignore_errors=True)
        self.docs_path.mkdir(parents=True, exist_ok=True)
