import asyncio

from typing import List

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramRetryAfter, TelegramBadRequest

from sqlalchemy import select

from src.database.core import conn
from src.database.models.user import User


"""                             send mailing

Утилиты для отправки сообщений юзерам по одному, циклом проходясь 
по всем юзерам и все что с этим связано.
"""

async def send_mailing_message(
    bot: Bot,
    user: User,
    reply_markup: InlineKeyboardMarkup,
    text: str = None,
    photo: str = None,
    video: str = None,
    document: str = None,
    video_note: str = None,
    voice: str = None,
    parse_mode: str = "HTML",
):
    user_id = user.user_id

    try:
        if photo:
            if text:
                msg = await bot.send_photo(
                    chat_id=user_id,
                    caption=text,
                    photo=photo,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode,
                )
            else:
                msg = await bot.send_photo(
                    chat_id=user_id,
                    photo=photo,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode,
                )
        elif video:
            if text:
                msg = await bot.send_video(
                    chat_id=user_id,
                    caption=text,
                    video=video,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode,
                )
            else:
                msg = await bot.send_video(
                    chat_id=user_id,
                    video=video,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode,
                )
        elif document:
            if text:
                msg = await bot.send_document(
                    chat_id=user_id,
                    caption=text,
                    document=document,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode,
                )
            else:
                msg = await bot.send_document(
                    chat_id=user_id,
                    document=document,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode,
                )
        elif video_note:
            msg = await bot.send_video_note(
                chat_id=user_id,
                video_note=video_note,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
            )
        elif voice:
            if text:
                msg = await bot.send_voice(
                    chat_id=user_id,
                    caption=text,
                    voice=voice,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode,
                )
            else:
                msg = await bot.send_voice(
                    chat_id=user_id,
                    voice=voice,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode,
                )
        else:
            msg = await bot.send_message(
                chat_id=user_id, # debug chat_id=user.user_id
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
                disable_web_page_preview=True,
            )

        return msg
    except TelegramRetryAfter:
        await asyncio.sleep(2)
        await send_mailing_message(
            bot=bot, user=user, reply_markup=reply_markup, text=text, photo=photo,
            video=video, document=document, video_note=video_note, voice=voice
        )


async def send_mailing(
    bot: Bot,
    text: str = None,
    photo: str = None,
    video: str = None,
    document: str = None,
    video_note: str = None,
    voice: str = None,
    username: str = None,
    keyboard: List[InlineKeyboardButton] = None,
    all_users: List[User] = [],
    return_message: bool = False,
):
    if not all_users:
        all_users = await User.find().to_list()

    if username:
        if username[0] == "@":
            username = username[1:]
        all_users = await User.find(username=username)

    if keyboard:
        reply_markup = InlineKeyboardMarkup(
            inline_keyboard=keyboard
        )
    else:
        reply_markup = None

    for num, user in enumerate(all_users):
        status = True
        try:
            msg = await send_mailing_message(
                bot=bot,
                user=user,
                reply_markup=reply_markup,
                text=text,
                photo=photo,
                video=video,
                document=document,
                video_note=video_note,
                voice=voice,
            )
        except TelegramRetryAfter:
            msg = None
            status = False
        except TelegramBadRequest:
            msg = None
            status = False

        if return_message:
            yield num, user, status, msg
        else:
            yield num, user, status
