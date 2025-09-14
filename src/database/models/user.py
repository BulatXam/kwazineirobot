from sqlalchemy import Column, String, BigInteger, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .core.base import BaseModel
from .core.crud import ModelCRUD


class User(BaseModel, ModelCRUD):
    __tablename__ = "users"

    user_id = Column(BigInteger, unique=True, index=True, nullable=False)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True)


class NeiroResponse(BaseModel, ModelCRUD):
    __tablename__ = "neiro_response"

    user_id = Column(
        Integer,
        ForeignKey("User.id", ondelete='CASCADE'),
        nullable=False,
        # no need to add index=True, all FKs have indexes
    )
    user = relationship('User', backref='clients')

    msg_type = Column(String, default="text") # text or img
    prompt = Column(String) # text or img
