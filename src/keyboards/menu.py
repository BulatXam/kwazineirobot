from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from src.callbacks import ActionCallback


menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📝 Сгенерировать текст",
                callback_data=ActionCallback(action="generate_text").pack()
            ),
        ],
        [
            InlineKeyboardButton(
                text="🖼️ Сгенерировать изображение",
                callback_data=ActionCallback(action="generate_image").pack()
            ),
        ],
    ],
)


# rulers 80
