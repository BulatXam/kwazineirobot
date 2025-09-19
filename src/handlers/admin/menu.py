from loguru import logger

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from sqlalchemy import select

from src.database.core import conn
from src.database.models.user import User

from src.callbacks import ActionCallback

from src.keyboards.admin import menu as menu_keyboards


router = Router(name="admin")

@router.message(F.text == "/admin")
async def start_admin(message: Message):
    await message.answer(
        "Привет, админ!",
        reply_markup=menu_keyboards.menu
    )


@router.callback_query(ActionCallback.filter(F.action == "admin_menu"))
async def start_admin(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer(
        "Привет, админ!",
        reply_markup=menu_keyboards.menu
    )
