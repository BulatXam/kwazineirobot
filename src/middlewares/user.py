from typing import Callable, Dict, Any, Awaitable

from datetime import timedelta

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from src.database.models.user import User


class LastActiveMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        user = await User.get_or_none(id=event.from_user.id)
        if user:
            if isinstance(event, Message):
                user.last_active = event.date
            elif isinstance(event, CallbackQuery):
                user.last_active = event.message.date
            await user.save()

        return await handler(event, data)
