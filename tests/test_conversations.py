from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def _create_user(email: str = "testuser@example.com"):
    resp = client.post(
        "/users",
        json={
            "email": email,
            "full_name": "Test User",
        },
    )
    assert resp.status_code in (200, 201, 400)
    if resp.status_code == 400:
        return 1
    return resp.json()["id"]


def test_create_conversation_and_llm_reply():
    user_id = _create_user()

    resp = client.post(
        "/conversations",
        json={
            "user_id": user_id,
            "mode": "open",
            "title": "Test conv",
            "first_message": "Hello from test",
            "document_ids": None,
        },
    )
    assert resp.status_code == 201
    data = resp.json()

    assert data["user_id"] == user_id
    assert len(data["messages"]) >= 2
    assert data["messages"][0]["role"] == "user"
    assert data["messages"][1]["role"] == "assistant"
    assert "dummy LLM reply" in data["messages"][1]["content"]


def test_append_message_to_conversation():
    user_id = _create_user(email="testuser2@example.com")

    resp = client.post(
        "/conversations",
        json={
            "user_id": user_id,
            "mode": "open",
            "title": "Test conv 2",
            "first_message": "Hi",
            "document_ids": None,
        },
    )
    assert resp.status_code == 201
    conv = resp.json()
    conv_id = conv["id"]

    resp2 = client.post(
        f"/conversations/{conv_id}/messages",
        json={"content": "Another message"},
    )
    assert resp2.status_code == 201
    msg = resp2.json()
    assert msg["role"] == "user"
    assert msg["content"] == "Another message"

    resp3 = client.get(f"/conversations/{conv_id}")
    assert resp3.status_code == 200
    conv_detail = resp3.json()
    roles = [m["role"] for m in conv_detail["messages"]]
    assert roles.count("assistant") >= 2
    assert roles.count("user") >= 2