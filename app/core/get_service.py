"""
-------------------------------------------------------------------------
Generic FastAPI dependency factory for injecting domain service classes.
-------------------------------------------------------------------------
"""

from typing import Type, TypeVar, Callable
from fastapi import Depends
from sqlmodel import Session
from app.core.database import get_session

T = TypeVar("T")


def get_service(service_class: Type[T]) -> Callable[[Session], T]:
    """
    Generic dependency factory for injecting domain services into FastAPI endpoints.

    This allows any service class that depends on a database session
    (or any shared resource) to be automatically provided by FastAPI.

    Example:
        from app.domain.document.service import DocumentService
        from app.core.services import get_service

        get_document_service = get_service(DocumentService)

        @router.post("", response_model=DocumentRead)
        def create_document(
            payload: DocumentCreate,
            svc: DocumentService = Depends(get_document_service)
        ):
            return svc.create(payload)
    """

    def _get_service(session: Session = Depends(get_session)) -> T:
        # Instantiate the service with the active DB session
        return service_class(session)

    return _get_service
