from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.domain.user.service import UserService
from app.domain.user.schemas import UserCreate, UserRead, UserPage

router = APIRouter(prefix="/user", tags=["user"])

def get_service(session: Session = Depends(get_session)) -> UserService:
    return UserService(session)

@router.get("", response_model=UserPage)
def list_user(offset: int = 0, limit: int = 50, svc: UserService = Depends(get_service)):
    items, total = svc.list_with_total(offset=offset, limit=limit)
    return UserPage(total=total, items=items)

@router.post("", response_model=UserRead)
def create_user(payload: UserCreate, svc: UserService = Depends(get_service)):
    return svc.create(payload)
