from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel


class UserBase(SQLModel):
    username: str
    email: str
    full_name: Optional[str] = None
    role: str = "user"
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    # created_at: datetime
    # updated_at: datetime

    # class Config:
    #     json_encoders = {
    #         datetime: lambda v: v.isoformat(),
    #     }


class UserPage(SQLModel):
    total: int
    items: List[UserRead]
