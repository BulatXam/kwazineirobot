import math

from loguru import logger

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from sqlalchemy import select, func

from src.database.core import conn
from src.database.models.user import User

from src.utils import statistics as statistics_utils

from src.callbacks import ActionCallback, ActionDataCallback

from src.keyboards.admin import statistics as statistics_keyboards

from src.states import admin as admin_states


router = Router(name="statistics")

@router.callback_query(ActionDataCallback.filter(F.action == "paginator_user_statistic"))
async def statistics(call: CallbackQuery, callback_data: ActionDataCallback, state: FSMContext):
    await call.answer("")

    state_data = await state.get_data()

    logger.info(state_data)

    num_in_page = 4 # сколько юзеров в одной странице

    current_page = state_data.get("current_page")
    if not current_page:
        current_page = 1

    async with conn() as session:
        all_users_query = await session.execute(
            select(func.count()).select_from(User)
        )

        all_users_count = all_users_query.scalar()

        users_in_page_query = await session.execute(
            select(User).offset(current_page*num_in_page-num_in_page).limit(num_in_page)
        )

        users_in_page = users_in_page_query.scalars().all()

    pages_count = math.ceil(all_users_count/num_in_page)

    action = callback_data.data

    # делаем зацикливание страниц при их перелистывании
    if action == "next_page":
        if current_page < pages_count:
            current_page += 1
        else:
            current_page = 1
    elif action == "last_page":
        if current_page > 1:
            current_page -= 1
        else:
            current_page = pages_count

    await state.update_data(current_page=current_page)
    
    await call.message.edit_text(
        text=f"""
Страница: <b>{current_page}</b>
Всего страниц:<b>{pages_count}</b>

{await statistics_utils.get_statics_text()}
""",
        reply_markup=statistics_keyboards.paginator_users_statistic(
            users=users_in_page, current_page=current_page, num_in_page=num_in_page
        )
    )


@router.callback_query(ActionDataCallback.filter(F.action == "get_user_statistic"))
async def get_user_statistic(call: CallbackQuery, callback_data: ActionDataCallback, state: FSMContext):
    user__id_data = callback_data.data

    await state.set_state(None)

    if user__id_data == "None":
        state_data = await state.get_data()
        user__id = state_data.get("user__id")
    else:
        user__id = int(user__id_data)

    async with conn() as session:
        user_query = await session.execute(
            select(User).where(User.id == user__id)
        )

        user = user_query.scalars().one_or_none()
    
    await state.update_data(
        user__id=user.id
    )

    await call.message.edit_text(
        text=f"""
<b>Пользователь №{user.id}</b>

Осталось текстовых запросов: <b>{round(user.daily_text_limit)}</b>
Осталось запросов изображений: <b>{round(user.daily_image_limit)}</b>

{await statistics_utils.get_statics_text(user=user)}
""",
        reply_markup=statistics_keyboards.get_user_by_paginator_users_statistic
    )


@router.callback_query(ActionCallback.filter(F.action == "user_change_tokens_limit"))
async def user_change_tokens_limit(call: CallbackQuery):
    await call.message.edit_text(
        text="Выберите какой лимит изменить",
        reply_markup=statistics_keyboards.user_change_tokens_limit_image_or_text
    )


@router.callback_query(ActionDataCallback.filter(F.action == "user_change_tokens_limit_text_or_image"))
async def user_change_tokens_limit(call: CallbackQuery, callback_data: ActionDataCallback, state: FSMContext):
    state_data = await state.get_data()

    data = callback_data.data

    await state.update_data(
        text_or_image=data
    )

    user__id = state_data.get("user__id")
    async with conn() as session:
        user_query = await session.execute(
            select(User).where(User.id == user__id)
        )

        user = user_query.scalars().one_or_none()

    if data == "text":
        limit = user.const_daily_text_limit
        await state.set_state(admin_states.AdminMailingChange.limit)
    elif data == "image":
        limit = user.const_daily_image_limit
        await state.set_state(admin_states.AdminMailingChange.limit)

    await call.message.edit_text(
        text=f"Текущий лимит: <b>{limit}</b>\n\nВведите сколько вы хотите поставить:",
        reply_markup=statistics_keyboards.back_in_paginator_users_statistic
    )


@router.message(admin_states.AdminMailingChange.limit)
async def admin_mailing_change_limit(message: Message, state: FSMContext):
    state_data = await state.get_data()
    
    limit = message.text
    text_or_image = state_data.get("text_or_image")
    user__id = state_data.get("user__id")

    async with conn() as session:
        user_query = await session.execute(
            select(User).where(User.id == user__id)
        )

        user = user_query.scalars().one_or_none()

        if text_or_image == "text":
            last_limit = user.const_daily_text_limit

            user.const_daily_text_limit = int(limit)
        elif text_or_image == "image":
            last_limit = user.const_daily_image_limit

            user.const_daily_image_limit = int(limit)
        
        await session.commit()
        
    await message.answer(f"Вы успешнос сменили лимит токенов с {last_limit} на {limit}")
