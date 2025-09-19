from typing import Union, Dict, Any

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from sqlalchemy import select, exists
from src.database.core import conn
from src.database.models.user import User


class UserFilter(BaseFilter):
    async def __call__(self, message: Message|CallbackQuery) -> Union[bool, Dict[str, Any]]:
        async with conn() as session:
            user_query = await session.execute(
                select(User).where(User.user_id == message.from_user.id)
            )

            user = user_query.scalars().one_or_none()

        if user:
            return True
        else:
            if isinstance(message, Message):
                if message.text[:6] == "/start":
                    return True
            await message.answer(
                "❌ Чтобы продолжить пользоваться ботом, введите /start! ❌"
            )
