import uuid
from typing import List, Optional

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from mirix.orm.sqlalchemy_base import SqlalchemyBase


class ChatMessage(SqlalchemyBase):
    """
    Stores chat history messages.
    """

    __tablename__ = "chat_messages"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: f"msg-{uuid.uuid4()}"
    )

    role: Mapped[str] = mapped_column(String, nullable=False)  # "user" or "assistant"
    content: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Store images as a list of objects/strings
    images: Mapped[Optional[List]] = mapped_column(JSONB, nullable=True)
    
    # Store thinking steps for assistant messages
    thinking_steps: Mapped[Optional[List]] = mapped_column(JSONB, nullable=True)
    
    # Store memory references for assistant messages
    memory_references: Mapped[Optional[List]] = mapped_column(JSONB, nullable=True)

    def __repr__(self) -> str:
        return f"<ChatMessage(id={self.id}, role={self.role}, content={self.content[:50]}...)>"
