from typing import Dict, List, Optional, Tuple

from app.core.config import settings

def _estimate_tokens(text: str) -> int:
    """
    Very rough token estimate. Good enough for logging / cost awareness in this assignment.
    """
    if not text:
        return 0
    return max(1, len(text.split()))

def _build_prompt_text(
    messages: List[Dict[str, str]],
    system_prompt: Optional[str] = None,
    context: Optional[str] = None,
) -> str:
    parts: List[str] = []

    if system_prompt:
        parts.append(f"[SYSTEM]\n{system_prompt}")

    if context:
        parts.append(f"[CONTEXT]\n{context}")

    if messages:
        history_lines = []
        for m in messages:
            history_lines.append(f"[{m['role'].upper()}] {m['content']}")
        parts.append("\n".join(history_lines))

    return "\n\n".join(parts)

def _call_dummy_llm(
    messages: List[Dict[str, str]],
    system_prompt: Optional[str],
    context: Optional[str],
) -> Tuple[str, Dict[str, int]]:
    """
    Dummy LLM: does NOT call any external service.
    It just echoes the last user message and notes if RAG context exists.
    """

    last_user_message = ""
    for m in reversed(messages):
        if m["role"] == "user":
            last_user_message = m["content"]
            break

    reply_parts = [
        "This is a dummy LLM reply.",
        f"You said: {last_user_message!r}",
    ]

    if context:
        reply_parts.append(
            "Some retrieved context was provided, but since this is a dummy model, "
            "the answer is not actually grounded in that content."
        )

    reply_text = "\n\n".join(reply_parts)

    prompt_text = _build_prompt_text(messages, system_prompt=system_prompt, context=context)

    usage = {
        "prompt_tokens": _estimate_tokens(prompt_text),
        "completion_tokens": _estimate_tokens(reply_text),
    }

    return reply_text, usage

def generate_reply(
    messages: List[Dict[str, str]],
    system_prompt: Optional[str] = None,
    context: Optional[str] = None,
) -> Tuple[str, Dict[str, int]]:
    """
    Main entry point for the rest of the app.

    For this assignment we keep it simple:
    - If LLM_PROVIDER == "dummy": use the dummy echo-like model.
    - Otherwise: raise NotImplementedError (you can extend this later to call a real LLM).
    """
    provider = (settings.LLM_PROVIDER or "dummy").lower()

    if provider == "dummy":
        return _call_dummy_llm(messages, system_prompt=system_prompt, context=context)

    raise NotImplementedError(
        f"LLM provider '{settings.LLM_PROVIDER}' is not implemented yet. "
        "For this assignment, keep LLM_PROVIDER='dummy'."
    )