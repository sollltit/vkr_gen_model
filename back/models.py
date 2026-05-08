from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import Text

from sqlalchemy.orm import relationship

from back.database import Base

class Chat(Base):

    __tablename__ = "chats"

    id = Column(Integer, primary_key=True)

    title = Column(String)

    messages = relationship(
        "Message",
        back_populates="chat"
    )

class Message(Base):

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)

    chat_id = Column(
        Integer,
        ForeignKey("chats.id")
    )

    role = Column(String)

    content = Column(Text)

    chat = relationship(
        "Chat",
        back_populates="messages"
    )