import asyncio

from loguru import logger

from typing import List
from datetime import datetime

from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    Message, 
    InlineKeyboardButton,
    ContentType
)
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.user import User

from src.utils import mailing as mailing_utils

from src.states import admin as admin_states

from src.callbacks import ActionCallback
from src.keyboards.admin import mailing as mailing_keyboards


router = Router()

# MARK: main

"""                                 main

Здесь находятся хендлеры, который выводят главное меню рассылки, а также
хендлеры регестрирующие кнопки назад, кнопка назад с очищением state и без.
"""


@router.callback_query(ActionCallback.filter(F.action == 'mailing'))
async def admin_mailing(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    try:
        message = await callback.message.edit_text(
            text='<tg-emoji emoji-id="5258215846450305872">💬</tg-emoji> <b>Отправьте сообщение, для рассылки.</b>',
            reply_markup=await mailing_keyboards.mailing_menu(),
            parse_mode="HTML",
        )
        await state.update_data(
            mailing_message_id=message.message_id
        )

    except TelegramBadRequest:
        await callback.message.delete()
        message = await callback.message.answer(
            text='<tg-emoji emoji-id="5258215846450305872">💬</tg-emoji> <b>Отправьте сообщение, для рассылки.</b>',
            reply_markup=await mailing_keyboards.mailing_menu(),
            parse_mode="HTML",
        )
        await state.update_data(
            mailing_message_id=message.message_id
        )
    await state.set_state(admin_states.AdminMailing.WAITING)
    await callback.answer()


# MARK: WAITING

"""                            WAITING

Хендлеры ожидающие, всевозможные контент для рассылки
"""

@router.message(admin_states.AdminMailing.WAITING)
async def mailing_text(message: Message, state: FSMContext):
    state_data = await state.get_data()
    text = message.html_text

    if not text:
        text = state_data.get("mailing_text")

    await state.update_data(mailing_text=text)

    await message.delete()
    try:
        await message.bot.delete_message(
            chat_id=message.chat.id,
            message_id=state_data.get("mailing_message_id")
        )
    except:
        pass

    if message.content_type == ContentType.TEXT:
        message = await message.answer(
            text=f'{text}',
            reply_markup=await mailing_keyboards.mailing_menu(),
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    elif message.content_type == ContentType.PHOTO:
        photo = message.photo[-1].file_id
        if text:
            await message.answer_photo(
                caption=text,
                photo=photo,
                reply_markup=await mailing_keyboards.mailing_menu(),
                parse_mode="HTML",
            )
        else:
            await message.answer_photo(
                photo=photo,
                reply_markup=await mailing_keyboards.mailing_menu(),
                parse_mode="HTML",
            )
        await state.update_data(mailing_photo=photo)

    elif message.content_type == ContentType.VIDEO:
        video = message.video.file_id
        if text:
            await message.answer_video(
                caption=text,
                video=video,
                reply_markup=await mailing_keyboards.mailing_menu(),
                parse_mode="HTML",
            )
        else:
            await message.answer_video(
                video=video,
                reply_markup=await mailing_keyboards.mailing_menu(),
                parse_mode="HTML",
            )
        await state.update_data(mailing_video=video)

    elif message.content_type == ContentType.DOCUMENT:
        document = message.document.file_id
        if text:
            await message.answer_document(
                caption=text,
                document=document,
                reply_markup=await mailing_keyboards.mailing_menu(),
                parse_mode="HTML",
            )
        else:
            await message.answer_document(
                document=document,
                reply_markup=await mailing_keyboards.mailing_menu(),
                parse_mode="HTML",
            )
        await state.update_data(mailing_document=document)

    elif message.content_type == ContentType.VOICE:
        voice = message.voice.file_id
        if text:
            await message.answer_voice(
                caption=text,
                voice=voice,
                reply_markup=await mailing_keyboards.mailing_menu(),
                parse_mode="HTML",
            )
        else:
            await message.answer_voice(
                voice=voice,
                reply_markup=await mailing_keyboards.mailing_menu(),
                parse_mode="HTML",
            )
        await state.update_data(mailing_voice=voice)

    elif message.content_type == ContentType.VIDEO_NOTE:
        video_note = message.video_note.file_id
        if text:
            await message.answer_video_note(
                caption=text,
                video_note=video_note,
                reply_markup=await mailing_keyboards.mailing_menu(),
                parse_mode="HTML",
            )
        else:
            await message.answer_video_note(
                video_note=video_note,
                reply_markup=await mailing_keyboards.mailing_menu(),
                parse_mode="HTML",
            )
        await state.update_data(mailing_videonote=video_note)

    await state.set_state(admin_states.AdminMailing.WAITING)
    await state.update_data(
        mailing_message_id=message.message_id
    )


# MARK: add link

"""                            add link

Хендлеры для создания клавиатуры ссылок в рассылке.
"""

@router.callback_query(
    ActionCallback.filter(F.action=='mailing_add_keyboard')
)
async def admin_mailing_always_cancel(
    callback: CallbackQuery, state: FSMContext
):
    await callback.message.delete()
    await callback.message.answer(
        "<b>➡️ Отправьте строку с кнопками</b>",
        reply_markup=await mailing_keyboards.send_mailing_keyboard(),
        parse_mode="HTML",
    )
    await state.set_state(None)
    await state.set_state(admin_states.AddMailingLink.link)


@router.message(admin_states.AddMailingLink.link)
async def i(message: Message, session: AsyncSession, state: FSMContext):
    link = message.text

    try:
        await state.update_data(
            keyboard=link
        )
    except ValueError:
        await message.answer(
            text="❌ Вы написали не верно",
            reply_markup=await mailing_keyboards.mailing_create_keyboard_retry()
        )
        return
    except TelegramBadRequest:
        await message.answer(
            text="❌ Вы написали не верно",
            reply_markup=await mailing_keyboards.mailing_create_keyboard_retry()
        )
        return

    await state.set_state(None)

    data = await state.get_data()
    text = data.get('mailing_text')
    photo = data.get('mailing_photo')
    video = data.get('mailing_video')
    document = data.get('mailing_doc')
    voice = data.get('mailing_voice')
    video_note = data.get('mailing_videonote')

    keyboard = await mailing_keyboards.build_inline_buttons_by_text(
        buttons_text=data.get("keyboard")
    ) if data.get("keyboard") else []

    reply_markup = await mailing_keyboards.mailing_next(
        keyboard=keyboard
    )
    
    user = await User.get(
        session=session,
        user_id=message.from_user.id
    )

    msg_text = f"<b>Ваше сообщение:</b> \n\n{text}" if text else ""

    try:
        await mailing_utils.send_mailing_message(
            bot=message.bot,
            user=user,
            reply_markup=reply_markup,
            text=msg_text,
            photo=photo,
            video=video,
            document=document,
            video_note=video_note,
            voice=voice,
            parse_mode="HTML",
        )
    except AttributeError:
        await message.answer("Добавьте текст, фото или медиа!")


@router.callback_query(ActionCallback.filter(F.action == 'mailing_next'))
async def mailing_next(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await state.set_state(None)
    await callback.message.delete()

    data = await state.get_data()
    text = data.get('mailing_text')
    photo = data.get('mailing_photo')
    video = data.get('mailing_video')
    document = data.get('mailing_doc')
    voice = data.get('mailing_voice')
    video_note = data.get('mailing_videonote')

    keyboard = await mailing_keyboards.build_inline_buttons_by_text(
        buttons_text=data.get("keyboard")
    ) if data.get("keyboard") else []

    reply_markup = await mailing_keyboards.mailing_next(
        keyboard=keyboard
    )

    user = await User.get(
        session=session,
        user_id=callback.from_user.id
    )


    msg_text = f"<b>Ваше сообщение:</b> \n\n{text}" if text else ""

    try:
        await mailing_utils.send_mailing_message(
            bot=callback.message.bot,
            user=user,
            reply_markup=reply_markup,
            text=msg_text,
            photo=photo,
            video=video,
            document=document,
            video_note=video_note,
            voice=voice,
            parse_mode="HTML",
        )
    except AttributeError:
        await callback.answer("Добавьте текст, фото или медиа!")


# MARK: mailing done

"""                            Mailing done

Хендлеры, срабатывающие когда сообщение рассылки готов и надо пройти дальше.
"""


@router.callback_query(ActionCallback.filter(F.action == 'admin_mailing_done'))
async def mailing_next(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await callback.answer(
        text='🚀 Запущена! Ожидайте отчёт.',
        parse_mode='HTML'
    )
    
    data = await state.get_data()
    text = data.get('mailing_text')
    photo = data.get('mailing_photo')
    video = data.get('mailing_video')
    document = data.get('mailing_doc')
    voice = data.get('mailing_voice')
    video_note = data.get('mailing_videonote')
    keyboard = await mailing_keyboards.build_inline_buttons_by_text(
        buttons_text=data.get("keyboard")
    ) if data.get("keyboard") else []
    
    all_users = await User.all(session=session)

    await state.update_data(
        mailing_stop_flag=False,
        mailing_complete_flag=False,
    )

    await asyncio.gather(
        mailing_message_progress_i(
            session=session,
            state=state, 
            text=text, 
            photo=photo, 
            video=video, 
            document=document, 
            voice=voice, 
            video_note=video_note, 
            keyboard=keyboard,
            message=callback,
            all_users=all_users
        ),
        mailing_message_progress_edit_text(
            state=state, callback=callback, session=session
        )
    )


# MARK: progress utils

"""                            progress utils

Утилиты и хенделеры для мониторинга протекания рассылки.
"""

async def mailing_message_progress_i(
    state: FSMContext,
    session: AsyncSession,
    text: str|None, 
    photo: str|None, 
    video: str|None, 
    document: str|None, 
    voice: str|None, 
    video_note: str|None, 
    keyboard: List[InlineKeyboardButton]|None,
    message: Message|CallbackQuery,
    all_users: List[User] = [],
):
    data = await state.get_data()

    if not all_users:
        all_users = User.all(session=session)

    bot = message.bot

    i = 0
    success_i = 0
    unsuccess_i = 0

    async for _, _, status in mailing_utils.send_mailing(
        bot=bot,
        text=text, 
        photo=photo, 
        video=video, 
        document=document, 
        voice=voice, 
        video_note=video_note, 
        keyboard=keyboard,
        all_users=all_users,
    ):
        data = await state.get_data()
        complete_flag = data.get("mailing_complete_flag") \
            if data.get("mailing_complete_flag") is not None else True
        if complete_flag:
            await state.clear()
            break

        i += 1

        if status:
            success_i += 1
        else:
            unsuccess_i += 1
    
        await state.update_data(mailing_i=i)
        await state.update_data(mailing_success_i=success_i)
        await state.update_data(mailing_unsuccess_i=unsuccess_i)

    if isinstance(message, CallbackQuery):
        await message.answer("Рассылка завершена!")
        message = message.message
    
    await state.update_data(mailing_complete_flag=True)


async def mailing_message_progress_edit_text(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    data = await state.get_data()
    message = callback.message

    all_user_count = await User.count(session=session)

    i = 0
    success_i =  0
    unsuccess_i = 0

    progress_bar_percent = i/all_user_count*100

    complete_flag = data.get("mailing_complete_flag") \
        if data.get("mailing_complete_flag") is not None else True
    
    progress_bar = lambda: \
    f" {'🟦'*round(progress_bar_percent/10)} "
    f"{round(progress_bar_percent, 1)} %"

    status = "Работает"

    text = lambda: f"""{progress_bar()} - {progress_bar_percent}%

{status}

<tg-emoji emoji-id="5258043150110301407">⬆️</tg-emoji> <b>Рассылка</b>

<tg-emoji emoji-id="5258115571848846212">✈️</tg-emoji> <b>Отправлено:</b> {i} <b>из</b> {all_user_count}

<tg-emoji emoji-id="5260416304224936047">✅</tg-emoji> <b>Успешно:</b> {success_i}
<tg-emoji emoji-id="5260342697075416641">❌</tg-emoji> <b>Заблокировали:</b> {unsuccess_i}

<tg-emoji emoji-id="5258258882022612173">⏲</tg-emoji> <b>Дата:</b> {datetime.now().strftime("%d.%m.%Y %H:%M")}
"""

    try: # Контрольная точка, при возникновение непонятного сценария
        await message.edit_text(
            text=text(),
            parse_mode="HTML",
        )
        await message.edit_reply_markup(
            reply_markup=await mailing_keyboards.mailing_progress()
        )
    except TelegramBadRequest:
        try:
            await message.delete()
        finally:
            message = await message.answer(
                text=text(),
                reply_markup=await mailing_keyboards.mailing_progress(),
                parse_mode="HTML",
            )

    while True:
        data = await state.get_data()

        i = data.get("mailing_i") \
            if data.get("mailing_i") is not None else 0
        success_i = data.get("mailing_success_i") \
            if data.get("mailing_success_i") is not None else 0
        unsuccess_i = data.get("mailing_unsuccess_i") \
            if data.get("mailing_unsuccess_i") is not None else 0
        complete_flag = data.get("mailing_complete_flag") \
            if data.get("mailing_complete_flag") is not None else True
        progress_bar_percent = i/all_user_count*100

        try:
            await message.edit_text(
                text=text(),
                reply_markup=await mailing_keyboards.mailing_progress(),
                parse_mode="HTML",
            )
        except TelegramBadRequest:
            pass

        await asyncio.sleep(0.1)

        if complete_flag:
            break

    if complete_flag:
        status = "Завершен"
        progress_bar_percent = 100
        await message.edit_text(
            text=text(),
            parse_mode="HTML",
        )
        await message.edit_reply_markup(
            reply_markup=await mailing_keyboards.progress_complete(),
            parse_mode="HTML",
        )

    await state.clear()


@router.callback_query(
    ActionCallback.filter(F.action == 'admin_mailing_complete')
)
async def mailing_next(callback: CallbackQuery, state: FSMContext):
    await state.update_data(mailing_complete_flag=True)

    await callback.answer("Рассылка завершена!")

# rulers 80
