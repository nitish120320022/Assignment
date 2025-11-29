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

---

## ⚙ 3. Installation & Setup

```bash
git clone https://github.com/nitish120320022/Assignment.git
cd Assignment

conda create -n bot_env python=3.12
conda activate bot_env

pip install -r requirements.txt
```

---

## ▶ 4. Running the Application

```bash
uvicorn main:app --reload
```

🔗 Swagger UI → http://127.0.0.1:8000/docs  
🔗 Health → http://127.0.0.1:8000/health  

---

# 🔥 5. API ROUTES (with JSON Schemas & Examples)

---

### 🧍 USER ROUTES

📌 **Create User** — `POST /users`

#### Request:
```json
{
  "email": "user@mail.com",
  "full_name": "John Wick"
}
```

#### Response:
```json
{
  "id": 1,
  "email": "user@mail.com",
  "full_name": "John Wick",
  "created_at": "2025-01-01T12:10:00"
}
```

📌 **Get User** — `GET /users/{user_id}`

---

### 📄 DOCUMENT ROUTES (for RAG)

📌 **Upload Document** — `POST /documents`

#### Request:
```json
{
  "user_id": 1,
  "name": "Python Guide",
  "source_type": "upload",
  "raw_text": "Python is a programming language..."
}
```

#### Response:
```json
{
  "id": 11,
  "user_id": 1,
  "name": "Python Guide",
  "source_type": "upload",
  "created_at": "2025-01-01T10:22:33"
}
```

📌 **Get All Documents for User** — `GET /documents?user_id=1`

📌 **Fetch Single Document** — `GET /documents/{document_id}`

---

### 💬 CONVERSATION ROUTES

📌 **Create Conversation (with first LLM reply)** — `POST /conversations`

#### Request:
```json
{
  "user_id": 1,
  "mode": "grounded",
  "title": "Ask Python",
  "first_message": "What is Python?",
  "document_ids": [11]
}
```

#### Response:
```json
{
  "id": 7,
  "user_id": 1,
  "title": "Ask Python",
  "messages": [
    {"role": "user", "content": "What is Python?"},
    {"role": "assistant", "content": "Python is ... (dummy LLM reply)"}
  ]
}
```

📌 **List Conversations for User** —  
`GET /users/{user_id}/conversations?limit=10&offset=0`

📌 **Fetch Full Chat History** —  
`GET /conversations/{conversation_id}`

---

### 🗨 MESSAGE ROUTE

📌 Add Message to Conversation — `POST /conversations/{id}/messages`

#### Request:
```json
{
  "content": "Explain Python lists."
}
```

📌 Response (assistant reply is auto-stored):
```json
{
  "role": "user",
  "content": "Explain Python lists."
}
```

---

## 🧪 6. Testing

```bash
pytest
```

Runs:

| Test | Validates |
|---|---|
| test_health | API readiness |
| test_conversations | Full LLM chat flow |

All tests passing ✔

---

## 🐳 7. Docker Deployment

```bash
docker build -t conversation-backend .
docker run -p 8000:8000 conversation-backend
```

Then open: http://localhost:8000/docs

---

## 🔁 8. GitHub CI Setup

Located at:

```
.github/workflows/ci.yml
```

| Stage | Status |
|---|---|
| Install dependencies | ✔ |
| Run tests | ✔ |
| Validate build | ✔ |

---

## 🚀 Future Enhancements

| Upgrade | Value |
|---|---|
| Replace Dummy LLM with OpenAI/Groq/Azure | Real AI responses |
| Vector DB + embeddings | Proper Semantic RAG |
| JWT Auth & Authorization | Secure multi-user access |
| WebSockets | Live chat streaming |
| Token billing UI | Usage cost dashboards |

---

### 📍 Final