from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from src.callbacks import ActionCallback, ActionDataCallback

menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Рассылка",
                callback_data=ActionCallback(
                    action="mailing"
                ).pack()
            )
        ],
        [
            InlineKeyboardButton(
                text="Статистика",
                callback_data=ActionDataCallback(
                    action="paginator_user_statistic",
                    data="current"
                ).pack()
            )
        ],
    ]
)
