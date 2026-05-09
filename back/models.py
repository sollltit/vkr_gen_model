from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import Text
from sqlalchemy import DateTime

from sqlalchemy.orm import relationship

from datetime import datetime

from back.database import Base


# =========================
# USERS
# =========================
class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True
    )

    email = Column(
        String,
        unique=True,
        nullable=False
    )

    password_hash = Column(
        String,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    chats = relationship(
        "Chat",
        back_populates="user"
    )


# =========================
# CHATS
# =========================
class Chat(Base):

    __tablename__ = "chats"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # 🔹 Владелец чата
    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    # ДОБАВИТЬ ЭТО
    user = relationship(
        "User",
        back_populates="chats"
    )

    messages = relationship(
        "Message",
        back_populates="chat"
    )

# =========================
# MESSAGES
# =========================
class Message(Base):

    __tablename__ = "messages"

    id = Column(
        Integer,
        primary_key=True
    )

    chat_id = Column(
        Integer,
        ForeignKey("chats.id")
    )

    role = Column(String)

    content = Column(Text)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    chat = relationship(
        "Chat",
        back_populates="messages"
    )