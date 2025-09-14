"""Логика чат-бота для обработки заказов с профессиональным общением"""

from typing import Optional, Literal, Union, List
from pydantic import BaseModel


class ProjectSchema(BaseModel):
    """Модель для хранения параметров проекта"""
    project_type: Optional[str] = None
    budget: Optional[str|int] = None
    deadline: Optional[str] = None
    status: Optional[
        Literal['suitable', 'unsuitable', 'requires_manager']
    ] = None
    call_up: Optional[str] = None
    description: Optional[str] = None


class MessageSchema(BaseModel):
    """Модель сообщения нейронки"""
    role: Literal['user', 'system', 'assistant']
    content: Optional[str] = ""
    file_ids: Optional[List[str|int]] = None



class DialogSchema(BaseModel):
    """Модель диалога нейронки с юзером"""
    messages: List[MessageSchema] = []
