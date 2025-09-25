import math

from loguru import logger

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database.models.user import User
from src.database.models.neiro import NeiroResponse

from src.utils import statistics as statistics_utils

from src.callbacks import ActionCallback, ActionDataCallback

from src.keyboards.admin import statistics as statistics_keyboards

from src.states import admin as admin_states

from src.texts import statistics as statistics_texts


router = Router(name="statistics")

@router.callback_query(ActionDataCallback.filter(F.action == "paginator_user_statistic"))
async def statistics(call: CallbackQuery, session: AsyncSession, callback_data: ActionDataCallback, state: FSMContext):
    await call.answer("")

    state_data = await state.get_data()

    num_in_page = 4 # сколько юзеров в одной странице

    current_page = state_data.get("current_page")
    if not current_page:
        current_page = 1

    action = callback_data.data

    all_users_count = await User.count(session=session)

    pages_count = math.ceil(all_users_count/num_in_page)

    # делаем зацикливание страниц при их перелистывании
    if action == "next":
        if current_page < pages_count:
            current_page += 1
        else:
            current_page = 1
    elif action == "last":
        if current_page > 1:
            current_page -= 1
        else:
            current_page = pages_count

    await state.update_data(current_page=current_page)

    users_in_page_query = await session.execute(
        select(User).offset(current_page*num_in_page-num_in_page).limit(num_in_page)
    )

    users_in_page = users_in_page_query.scalars().all()
    
    await call.message.edit_text(
        text=f"""
Страница: <b>{current_page}</b>
Всего страниц:<b>{pages_count}</b>

{await statistics_utils.get_statics_text(session=session)}
""",
        reply_markup=statistics_keyboards.paginator_users_statistic(
            users=users_in_page, current_page=current_page, num_in_page=num_in_page
        )
    )


@router.callback_query(ActionDataCallback.filter(F.action == "get_user_statistic"))
async def get_user_statistic(call: CallbackQuery, callback_data: ActionDataCallback, state: FSMContext, session: AsyncSession):
    user__id_data = callback_data.data

    await state.set_state(None)

    if user__id_data == "None":
        state_data = await state.get_data()
        user__id = state_data.get("user__id")
    else:
        user__id = int(user__id_data)

    user: User = await User.get(
        session=session,
        id=user__id
    )
    
    await state.update_data(
        user__id=user.id
    )

    await call.message.edit_text(
        text=statistics_texts.user_statistic(
            user=user,
            statistic_text=await statistics_utils.get_statics_text(
                session=session,
                user=user
            )
        ),
        reply_markup=statistics_keyboards.get_user_by_paginator_users_statistic
    )


@router.callback_query(ActionCallback.filter(F.action == "user_change_tokens_limit"))
async def user_change_tokens_limit(call: CallbackQuery):
    await call.message.edit_text(
        text="Выберите какой лимит изменить",
        reply_markup=statistics_keyboards.user_change_tokens_limit_image_or_text
    )


@router.callback_query(ActionDataCallback.filter(F.action == "user_change_tokens_limit_text_or_image"))
async def user_change_tokens_limit(call: CallbackQuery, callback_data: ActionDataCallback, state: FSMContext, session: AsyncSession):
    state_data = await state.get_data()

    data = callback_data.data

    await state.update_data(
        text_or_image=data
    )

    user__id = state_data.get("user__id")
    
    user = await User.get(
        session=session,
        id=user__id
    )

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
async def admin_mailing_change_limit(message: Message, state: FSMContext, session: AsyncSession):
    state_data = await state.get_data()
    
    limit = message.text
    text_or_image = state_data.get("text_or_image")
    user__id = state_data.get("user__id")

    user: User = await User.get(
        session=session,
        id=user__id,
    )

    if text_or_image == "text":
        last_limit = user.const_daily_text_limit

        user.const_daily_text_limit = int(limit)
    elif text_or_image == "image":
        last_limit = user.const_daily_image_limit

        user.const_daily_image_limit = int(limit)
    
    await session.commit()
    await session.refresh(user)
        
    await message.answer(f"Вы успешнос сменили лимит токенов с {last_limit} на {limit}")


@router.callback_query(ActionDataCallback.filter(F.action == "paginator_user_history"))
async def user_history(call: CallbackQuery, callback_data: ActionDataCallback, state: FSMContext, session: AsyncSession):
    await call.answer("")

    state_data = await state.get_data()

    num_in_page = 4 # сколько юзеров в одной странице

    current_page = state_data.get("user_history_current_page")

    if not current_page:
        current_page = 1

    action = callback_data.data

    all_neiro_responses_count = await NeiroResponse.count(session=session)
    pages_count = math.ceil(all_neiro_responses_count / num_in_page)

    # делаем зацикливание страниц при их перелистывании
    if action == "next":
        if current_page < pages_count:
            current_page += 1
        else:
            current_page = 1
    elif action == "last":
        if current_page > 1:
            current_page -= 1
        else:
            current_page = pages_count
    

    # Получаем нужные объекты NeiroResponse для текущей страницы
    offset = (current_page - 1) * num_in_page
    logger.info(f"offset:{offset} current_page:{current_page}")

    neiro_responses_in_page_query = await session.execute(
        select(NeiroResponse).order_by(NeiroResponse.id).offset(offset).limit(num_in_page)
    )
    neiro_responses_in_page = neiro_responses_in_page_query.scalars().all()

    await state.update_data(user_history_current_page=current_page)

    await call.message.edit_text(
        text=statistics_texts.user_history(
            current_page=current_page,
            pages_count=pages_count,
            neiro_responses_in_page_len=len(neiro_responses_in_page),
            all_neiro_responses_count=all_neiro_responses_count
        ),
        reply_markup=statistics_keyboards.paginator_user_history(
            neiro_responses=neiro_responses_in_page,
            current_page=current_page,
            num_in_page=num_in_page
        )
    )


@router.callback_query(ActionDataCallback.filter(F.action == "get_user_neiro_response"))
async def get_user_neiro_response(call: CallbackQuery, callback_data: ActionDataCallback, state: FSMContext, session: AsyncSession):
    neiro_response__id_data = callback_data.data

    await state.set_state(None)

    if neiro_response__id_data == "None":
        state_data = await state.get_data()
        neiro_response__id = state_data.get("user__id")
    else:
        neiro_response__id = int(neiro_response__id_data)

    neiro_response: NeiroResponse = await NeiroResponse.get(
        session=session,
        id=neiro_response__id
    )
    
    await state.update_data(
        neiro_response__id=neiro_response.id
    )

    await call.message.edit_text(
        text=statistics_texts.user_history_response(neiro_response=neiro_response),
        reply_markup=statistics_keyboards.back_in_paginator_user_history
    )
