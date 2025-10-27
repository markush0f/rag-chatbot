from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from app.core.database import get_session
from app.domain.message.service import MessageService
from app.domain.message.schemas import MessageCreate, MessageRead, MessagePage

router = APIRouter(prefix="/message", tags=["message"])

def get_service(session: Session = Depends(get_session)) -> MessageService:
    return MessageService(session)

@router.get("", response_model=MessagePage)
def list_message(offset: int = 0, limit: int = 50, svc: MessageService = Depends(get_service)):
    items, total = svc.list_with_total(offset=offset, limit=limit)
    return MessagePage(total=total, items=items)

@router.post("", response_model=MessageRead)
def create_message(payload: MessageCreate, svc: MessageService = Depends(get_service)):
    return svc.create(payload)

@router.get("/{chat_id}/messages", response_model=MessagePage)
def list_chat_messages(
    chat_id: int,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    session: Session = Depends(get_session),
):
    service = MessageService(session)
    items, total = service.list_by_chat(chat_id, offset, limit)
    return {"total": total, "items": items}