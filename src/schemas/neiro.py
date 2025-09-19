"""Логика чат-бота для обработки заказов с профессиональным общением"""

from typing import Optional, Literal, Union, List
from pydantic import BaseModel


class MessageSchema(BaseModel):
    """JSON Модель сообщения нейронки"""
    role: Literal['user', 'system', 'assistant']
    content: Optional[str] = ""


class DialogSchema(BaseModel):
    """JSON Модель диалога нейронки с юзером"""
    messages: List[MessageSchema] = []
