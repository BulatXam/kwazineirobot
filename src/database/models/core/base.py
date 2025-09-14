from typing import TypeVar, Generic, Sequence, Optional

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.orm import selectinload, load_only
from sqlalchemy.sql import select, update as sqlalchemy_update
from sqlalchemy.exc import NoResultFound


class BaseModel(DeclarativeBase):
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
