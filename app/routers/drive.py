from fastapi import APIRouter
from app.domain.drive.service import DriveService

router = APIRouter(prefix="/drive", tags=["Drive"])


@router.get("/files")
def list_drive_files():
    """
    Lista todos los documentos del Drive.
    """
    drive = DriveService()
    docs = drive.list_files(
        mime_filters=[
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain",
        ]
    )
    return {"total": len(docs), "files": docs}
