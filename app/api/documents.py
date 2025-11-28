from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Document, User
from app.api.schemas import DocumentCreate, DocumentRead

router = APIRouter(tags=["documents"])


def get_user_or_404(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    return user


@router.post(
    "/documents",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_document(
    payload: DocumentCreate,
    db: Session = Depends(get_db),
):
    """
    Create a document for a user.
    For this assignment, we accept only raw_text (no real file upload).
    """
 
    get_user_or_404(db, payload.user_id)

    document = Document(
        user_id=payload.user_id,
        name=payload.name,
        source_type=payload.source_type or "upload",
        raw_text=payload.raw_text,
        storage_path=None, 
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.get(
    "/documents",
    response_model=List[DocumentRead],
)
def list_documents(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    List all documents for a user.
    """
    get_user_or_404(db, user_id)

    docs = (
        db.query(Document)
        .filter(Document.user_id == user_id)
        .order_by(Document.created_at.desc())
        .all()
    )
    return docs


@router.get(
    "/documents/{document_id}",
    response_model=DocumentRead,
)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a single document by id.
    """
    doc = db.get(Document, document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id {document_id} not found",
        )
    return doc