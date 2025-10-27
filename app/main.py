from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from app.core.database import init_db
from app.core.logging_config import setup_logging
from app.routers.drive import router as drive_router
from app.routers.rag import router as rag_router
from app.routers.user import router as user_router
from app.routers.chat import router as chat_router
from app.routers.message import router as message_router
from app.routers.document import router as document_router

setup_logging()
logger = logging.getLogger("app")

app = FastAPI(title="Chatbot RAG Backend")

app.include_router(drive_router)
app.include_router(rag_router)
app.include_router(user_router)
app.include_router(chat_router)
app.include_router(message_router)
app.include_router(document_router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Init Crecenia Chatbot...")
    init_db()
    yield
    logger.info("Closing Crecenia Chatbot...")


@app.get("/")
def root():
    return {"message": "Chatbot RAG Backend running"}
