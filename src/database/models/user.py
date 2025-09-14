from sqlalchemy import Column, String, BigInteger

from .core.base import BaseModel
from .core.crud import ModelCRUD


class User(BaseModel, ModelCRUD):
    __tablename__ = "users"

    user_id = Column(BigInteger, unique=True, index=True, nullable=False)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True)
