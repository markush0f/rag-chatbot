from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.core.database import get_session
from app.domain.chat.service import ChatService
from app.domain.chat.schemas import ChatCreate, ChatRead, ChatPage
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["chat"])


def get_service(session: Session = Depends(get_session)) -> ChatService:
    """Inject ChatService with an active database session."""
    return ChatService(session)


@router.get("", response_model=ChatPage)
def list_chat(
    offset: int = 0,
    limit: int = 50,
    svc: ChatService = Depends(get_service),
):
    """List chats with pagination."""
    items, total = svc.list_with_total(offset=offset, limit=limit)
    return ChatPage(total=total, items=items)


@router.post("", response_model=ChatRead)
def create_chat(
    payload: ChatCreate,
    svc: ChatService = Depends(get_service),
):
    """Create a new chat instance."""
    return svc.create(payload)


@router.get("/user/{user_id}", response_model=List[ChatRead])
def list_user_chats(
    user_id: int,
    svc: ChatService = Depends(get_service),
):
    """List all chats belonging to a specific user."""
    return svc.list_by_user(user_id)


class ChatAsk(BaseModel):
    question: str


@router.post("/{chat_id}/ask")
def ask_question(
    chat_id: int,
    payload: ChatAsk,
    svc: ChatService = Depends(get_service),
):
    """Ask a question within a chat (restricted to selected documents)."""
    try:
        answer = svc.ask(chat_id, payload.question)
        return {"answer": answer.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
