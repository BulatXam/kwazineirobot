from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, BigInteger, DateTime, func


class BaseModel(DeclarativeBase):
    id = Column(BigInteger, primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
