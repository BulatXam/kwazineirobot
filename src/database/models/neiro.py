from sqlalchemy import Column, String, BigInteger, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .base import BaseModel
from .user import User


class NeiroMessage(BaseModel):
    __tablename__ = "neiro_message"

    user_id = Column(
        BigInteger,
        ForeignKey(User.id, ondelete='CASCADE'),
        nullable=False,
        # no need to add index=True, all FKs have indexes
    )
    user = relationship(User, backref='clients')

    role = Column(String(length=10)) # system or user or assistent
    
    content = Column(String) # text or img


class NeiroResponse(BaseModel):
    __tablename__ = "neiro_text_response"

    user_id = Column(
        BigInteger,
        ForeignKey(User.id, ondelete='CASCADE'),
        nullable=False,
        # no need to add index=True, all FKs have indexes
    )
    model = Column(
        String, default="hydra-gemini"
    )

    user = relationship(User, backref='responses')

    type = Column(String(length=10)) # text or image

    prompt = Column(String) # text prompt or img prompt
    content = Column(String) # text answer or img url
    total_tokens = Column(Integer) # total tokens used in request
