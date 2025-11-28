# Conversation Backend Service

Backend service for the **Associate Engineer – Case Study**.

It exposes REST APIs to:

- Manage **users**, **conversations**, **messages**, and **documents**
- Support two chat modes:
  - **Open chat** – standard LLM conversation
  - **Grounded chat (RAG)** – conversation grounded on uploaded documents
- Handle **conversation history**, **LLM integration**, **basic RAG**, and **cost/context management hooks**

---

## 1. Tech Stack

- **Language**: Python 3.12
- **Framework**: FastAPI
- **DB**: SQLite (via SQLAlchemy)
- **LLM**: Pluggable client, currently a **dummy provider** (no external API needed)
- **Testing**: pytest
- **Containerization**: Docker
- **CI**: GitHub Actions (pytest on each push / PR)

---

## 2. Project Structure

```text
.
├─ app/
│  ├─ api/
│  │  ├─ conversations.py      # Conversation + message APIs
│  │  ├─ users.py              # Simple user APIs (create/get)
│  │  ├─ documents.py          # Document APIs (for RAG)
│  │  └─ schemas.py            # Pydantic models (request/response)
│  ├─ core/
│  │  ├─ config.py             # App & env configuration
│  │  ├─ database.py           # SQLAlchemy engine, session, Base
│  │  ├─ logging_config.py     # Logging setup
│  │  └─ error_handlers.py     # Global exception handlers
│  ├─ models/
│  │  └─ models.py             # ORM models (User, Conversation, Message, Document, etc.)
│  └─ services/
│     ├─ llm_client.py         # LLM client abstraction (dummy provider)
│     └─ context_builder.py    # Conversation history + RAG context builder
├─ tests/
│  ├─ test_health.py           # Health endpoint test
│  └─ test_conversations.py    # Conversation + LLM flow tests
├─ docs/
│  └─ ARCHITECTURE.md          # Detailed design / case-study writeup
├─ main.py               # FastAPI app entrypoint
├─ requirements.txt
├─ app.db
├─ README.md
├─ Dockerfile
├─ .gitignore
├─ pytest.ini
└─ .env