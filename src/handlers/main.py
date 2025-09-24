from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.core import conn
from src.database.models.user import User

from src.filters.user import UserFilter

from src.keyboards import menu as main_keyboards
from src.callbacks import ActionCallback

from src.texts import start as start_texts


router = Router(name="main")

router.message.filter(UserFilter())
router.callback_query.filter(UserFilter())

@router.message(
    F.text == "/start"
)
async def start(message: Message, session: AsyncSession):
    user = await User.get(
        session=session,
        user_id=message.from_user.id
    )

    if not user:
        user: User = await User.create(
            session=session,
            user_id=message.from_user.id,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username,
        )
        
    await message.answer(
        text=start_texts.start(user_id=user.id),
        reply_markup=main_keyboards.menu,
    )


@router.callback_query(
    ActionCallback.filter(F.action == "start")
)
async def start(call: CallbackQuery, session: AsyncSession, state: FSMContext):
    await state.clear()
    user = await User.get(
        session=session,
        user_id=call.from_user.id
    )

    if not user:
        user: User = await User.create(
            session=session,
            user_id=call.from_user.id,
            first_name=call.from_user.first_name,
            last_name=call.from_user.last_name,
            username=call.from_user.username,
        )
    try:
        await call.message.edit_text(
            text=start_texts.start(user_id=user.id),
            reply_markup=main_keyboards.menu,
        )
    except TelegramBadRequest:
        await call.message.delete()
        await call.message.answer(
            text=start_texts.start(user_id=user.id),
            reply_markup=main_keyboards.menu,
        )


@router.message(
    F.text == "/help"
)
async def help(message: Message):
    await message.answer(
        text=start_texts.help,
    )


# rulers 80
