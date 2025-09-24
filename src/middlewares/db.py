from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from src.database.core import conn


class DatabaseSessionMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message|CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        async with conn() as session:
            data["session"] = session
            return await handler(event, data)
