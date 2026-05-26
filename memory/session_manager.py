"""
Session memory manager — tracks conversation history per user session.
Short-term: last N messages (in-context window).
Long-term: session summary stored per session_id (could be persisted to DB in v2).
"""
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Message:
    role: str           # "user" | "assistant"
    content: str
    agent: str = "routing"
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))


@dataclass
class Session:
    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    user_name: str = "User"
    user_role: str = "Executive"
    messages: list[Message] = field(default_factory=list)
    token_estimate: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))

    def add_user_message(self, content: str) -> None:
        self.messages.append(Message(role="user", content=content))
        self.token_estimate += self._estimate_tokens(content)

    def add_assistant_message(self, content: str, agent: str = "routing") -> None:
        self.messages.append(Message(role="assistant", content=content, agent=agent))
        self.token_estimate += self._estimate_tokens(content)

    def get_history(self, last_n: int = 8) -> list[dict[str, str]]:
        """Returns last N messages in Anthropic messages API format."""
        window = self.messages[-last_n:] if len(self.messages) > last_n else self.messages
        return [{"role": m.role, "content": m.content} for m in window]

    def within_token_limit(self, limit: int) -> bool:
        return self.token_estimate < limit

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        return max(1, int(len(text.split()) * 1.35))

    def summary(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "user": f"{self.user_name} ({self.user_role})",
            "messages": len(self.messages),
            "token_estimate": self.token_estimate,
            "started": self.created_at,
        }


class SessionManager:
    """Singleton-style in-memory session store. Replace with Redis/DB for production."""

    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    def create(self, user_name: str, user_role: str) -> Session:
        s = Session(user_name=user_name, user_role=user_role)
        self._sessions[s.session_id] = s
        return s

    def get(self, session_id: str) -> Session | None:
        return self._sessions.get(session_id)

    def reset(self, session_id: str, user_name: str, user_role: str) -> Session:
        s = Session(session_id=session_id, user_name=user_name, user_role=user_role)
        self._sessions[session_id] = s
        return s

    def delete(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)
