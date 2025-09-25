from sqlalchemy import Column, String, BigInteger, Float

from src.config import cnf

from src.database.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    user_id = Column(BigInteger, unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True)
    username = Column(String(100), nullable=True)

    daily_text_limit = Column(Float, default=cnf.openai.TEXTS_LIMIT)
    daily_image_limit = Column(Float, default=cnf.openai.IMAGES_LIMIT)

    # константы сколько лимит должен быть на след день
    const_daily_text_limit = Column(Float, default=cnf.openai.TEXTS_LIMIT)    
    const_daily_image_limit = Column(Float, default=cnf.openai.IMAGES_LIMIT)
