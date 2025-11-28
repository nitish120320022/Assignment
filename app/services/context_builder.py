from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.models import Conversation, ConversationDocument, Document, Message

def build_message_history(
    conversation: Conversation,
    max_messages: Optional[int] = None,
) -> List[Dict[str, str]]:
    """
    Build a list of {role, content} dicts for the last N messages of a conversation.
    """
    if max_messages is None:
        max_messages = settings.MAX_HISTORY_MESSAGES

    messages = conversation.messages[-max_messages:]

    history = []
    for m in messages:
        history.append(
            {
                "role": m.role,
                "content": m.content,
            }
        )
    return history

def _get_last_user_message(conversation: Conversation) -> Optional[str]:
    """
    Return content of last user message in the conversation.
    """
    for m in reversed(conversation.messages):
        if m.role == "user":
            return m.content
    return None

def build_rag_context(
    db: Session,
    conversation: Conversation,
    max_chars: Optional[int] = None,
) -> Optional[str]:
    """
    Build a simple RAG context string from documents linked to the conversation.

    Strategy (simple but reasonable for assignment):
    1. Get last user message as a "query".
    2. Fetch all linked documents.
    3. Score documents based on how many query words appear in raw_text.
    4. Sort by score and concatenate top docs.
    5. Truncate to max_chars.
    """
    if max_chars is None:
        max_chars = settings.MAX_CONTEXT_CHARS

    query_text = _get_last_user_message(conversation) or ""
    query_words = {
        w.lower()
        for w in query_text.split()
        if len(w) > 2
    }

    links = (
        db.query(ConversationDocument)
        .filter(ConversationDocument.conversation_id == conversation.id)
        .all()
    )

    if not links:
        return None

    doc_ids = [link.document_id for link in links]
    documents = (
        db.query(Document)
        .filter(Document.id.in_(doc_ids))
        .all()
    )

    scored_docs: List[tuple[int, Document]] = []
    for doc in documents:
        if not doc.raw_text:
            continue
        text = doc.raw_text.lower()
        score = sum(1 for w in query_words if w in text)
        scored_docs.append((score, doc))

    if not scored_docs:
        return None

    scored_docs.sort(key=lambda x: x[0], reverse=True)

    pieces: List[str] = []
    for score, doc in scored_docs:
        if doc.raw_text:
            header = f"Document: {doc.name} (score={score})"
            pieces.append(header)
            pieces.append(doc.raw_text)

    combined = "\n\n----- DOCUMENT SEPARATOR -----\n\n".join(pieces)

    if len(combined) > max_chars:
        combined = combined[:max_chars]

    return combined