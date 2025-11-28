from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.core.database import get_db
from app.models.models import (
    User,
    Conversation,
    Message,
    Document,
    ConversationDocument,
)
from app.api.schemas import (
    ConversationCreate,
    ConversationRead,
    ConversationListItem,
    MessageCreate,
    MessageRead,
)
from app.services.context_builder import build_message_history, build_rag_context
from app.services.llm_client import generate_reply

router = APIRouter(tags=["conversations"])

def get_user_or_404(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    return user


def get_conversation_or_404(db: Session, conversation_id: int) -> Conversation:
    conversation = (
        db.query(Conversation)
        .options(selectinload(Conversation.messages))
        .filter(Conversation.id == conversation_id)
        .first()
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with id {conversation_id} not found",
        )
    return conversation


def get_next_order_index(db: Session, conversation_id: int) -> int:
    count = (
        db.query(func.count(Message.id))
        .filter(Message.conversation_id == conversation_id)
        .scalar()
    )
    if not count:
        return 1
    return count + 1


def _maybe_generate_assistant_reply(
    db: Session,
    conversation: Conversation,
) -> Message:
    """
    Build context, call LLM, and persist the assistant's reply as the next message.
    """
  
    db.refresh(conversation)

    history = build_message_history(
        conversation,
        max_messages=settings.MAX_HISTORY_MESSAGES,
    )

    context_text: Optional[str] = None
    if conversation.mode.lower() in ("grounded", "rag"):
        context_text = build_rag_context(
            db,
            conversation,
            max_chars=settings.MAX_CONTEXT_CHARS,
        )

    system_prompt = (
        "You are a helpful assistant inside a backend conversation service. "
        "Always respond clearly and concisely."
    )
    if context_text:
        system_prompt += (
            " Use ONLY the information from the provided context when it is relevant. "
            "If the answer is not in the context, say you are unsure instead of guessing."
        )

    reply_text, usage = generate_reply(
        messages=history,
        system_prompt=system_prompt,
        context=context_text,
    )

    order_index = get_next_order_index(db, conversation.id)
    assistant_msg = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=reply_text,
        order_index=order_index,
        prompt_tokens=usage.get("prompt_tokens"),
        completion_tokens=usage.get("completion_tokens"),
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    return assistant_msg

@router.post(
    "/conversations",
    response_model=ConversationRead,
    status_code=status.HTTP_201_CREATED,
)
def create_conversation(
    payload: ConversationCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new conversation with the first user message.
    Automatically generates an assistant reply using the LLM.
    """
 
    user = get_user_or_404(db, payload.user_id)

    title = payload.title or payload.first_message[:80] 
    conversation = Conversation(
        user_id=user.id,
        mode=payload.mode,
        title=title,
    )
    db.add(conversation)
    db.flush() 

    first_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=payload.first_message,
        order_index=1,
    )
    db.add(first_msg)

    if payload.document_ids:
        for doc_id in payload.document_ids:
            document = db.get(Document, doc_id)
            if not document:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Document with id {doc_id} not found",
                )
            link = ConversationDocument(
                conversation_id=conversation.id,
                document_id=document.id,
            )
            db.add(link)

    db.commit()
    db.refresh(conversation)

    assistant_msg = _maybe_generate_assistant_reply(db, conversation)

    conversation = get_conversation_or_404(db, conversation.id)
    messages = [MessageRead.from_orm(m) for m in conversation.messages]

    return ConversationRead(
        id=conversation.id,
        user_id=conversation.user_id,
        mode=conversation.mode,
        title=conversation.title,
        is_archived=conversation.is_archived,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=messages,
    )


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=MessageRead,
    status_code=status.HTTP_201_CREATED,
)
def add_message_to_conversation(
    conversation_id: int,
    payload: MessageCreate,
    db: Session = Depends(get_db),
):
    """
    Add a new user message to an existing conversation and
    automatically append an assistant reply.
    """
    conversation = get_conversation_or_404(db, conversation_id)

    order_index = get_next_order_index(db, conversation.id)

    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=payload.content,
        order_index=order_index,
    )
    db.add(user_msg)
    db.commit()
    db.refresh(conversation)

    assistant_msg = _maybe_generate_assistant_reply(db, conversation)

    return MessageRead.from_orm(user_msg)


@router.get(
    "/users/{user_id}/conversations",
    response_model=List[ConversationListItem],
)
def list_conversations_for_user(
    user_id: int,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """
    List conversations for a given user with pagination.
    Sorted by most recently updated.
    """
    get_user_or_404(db, user_id)

    conversations = (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .filter(Conversation.is_archived == False) 
        .order_by(Conversation.updated_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    result: List[ConversationListItem] = []
    for conv in conversations:
        last_message_at: Optional[datetime] = (
            db.query(func.max(Message.created_at))
            .filter(Message.conversation_id == conv.id)
            .scalar()
        )

        result.append(
            ConversationListItem(
                id=conv.id,
                user_id=conv.user_id,
                mode=conv.mode,
                title=conv.title,
                is_archived=conv.is_archived,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                last_message_at=last_message_at,
            )
        )

    return result


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationRead,
)
def get_conversation_detail(
    conversation_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a single conversation with all its messages.
    """
    conversation = get_conversation_or_404(db, conversation_id)

    messages = [
        MessageRead.from_orm(m) for m in conversation.messages
    ]

    return ConversationRead(
        id=conversation.id,
        user_id=conversation.user_id,
        mode=conversation.mode,
        title=conversation.title,
        is_archived=conversation.is_archived,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=messages,
    )


@router.delete(
    "/conversations/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
):
    """
    Delete a conversation and all its messages.
    For the assignment, hard delete is OK.
    """
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with id {conversation_id} not found",
        )

    db.delete(conversation)
    db.commit()
    return None