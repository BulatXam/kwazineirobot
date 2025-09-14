import os

from typing import Union, Dict, Any

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from src.database.models.user import User


class UserFilter(BaseFilter):
    async def __call__(self, message: Message|CallbackQuery) -> Union[bool, Dict[str, Any]]:
        user = await User.get_or_none(
            user_id=message.from_user.id
        )
        if user:
            return True
        else:
            if isinstance(message, Message):
                if message.text[:6] == "/start":
                    return True
            await message.answer(
                "❌ Чтобы продолжить пользоваться ботом, введите /start! ❌"
            )
