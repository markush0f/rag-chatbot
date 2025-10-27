import os
import pickle
import webbrowser
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


class DriveService:
    def __init__(self):
        self.creds = None
        self.service = self._load_service()

    def _load_service(self):
        """
        Flujo OAuth automático para WSL o entornos sin GUI.
        Muestra la URL para autorizar y captura el token automáticamente.
        """
        creds_path = "credentials.json"
        token_path = "token.pickle"

        # Cargar token si ya existe
        if os.path.exists(token_path):
            with open(token_path, "rb") as token:
                self.creds = pickle.load(token)

        # Si no hay credenciales válidas → crear nuevas
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                print("🔄 Refrescando token de acceso a Google Drive...")
                self.creds.refresh(Request())
            else:
                print("🔐 Iniciando autenticación manual (sin navegador automático)...")
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)

                # Captura automática del token tras autorización
                self.creds = flow.run_local_server(port=8080, open_browser=False)

                print("✅ Autenticación completada correctamente y token guardado.")

            # Guardar token para próximos usos
            with open(token_path, "wb") as token:
                pickle.dump(self.creds, token)

        # Construir servicio Drive
        return build("drive", "v3", credentials=self.creds)

    def list_files(self, mime_filters: list[str] | None = None) -> list[dict]:
        """Lista archivos del Drive"""
        query = (
            " or ".join([f"mimeType='{m}'" for m in mime_filters])
            if mime_filters
            else None
        )
        results = (
            self.service.files()
            .list(q=query, fields="files(id, name, mimeType, modifiedTime, size)")
            .execute()
        )
        files = results.get("files", [])
        return [
            {
                "id": f["id"],
                "name": f["name"],
                "mimeType": f["mimeType"],
                "size": f.get("size", "—"),
                "modified": f.get("modifiedTime", ""),
            }
            for f in files
        ]
