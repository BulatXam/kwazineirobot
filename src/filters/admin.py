from typing import Union, Dict, Any

from loguru import logger

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from src.config import cnf

class AdminFilter(BaseFilter):
    async def __call__(self, message: Message|CallbackQuery) -> Union[bool, Dict[str, Any]]:
        if message.from_user.id in cnf.bot.ADMINS:
            return True
        else:
            await message.answer(
                "❌ Вы не имеете прав администратора! ❌"
            )
