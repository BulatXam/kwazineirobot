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
                callback_data=ActionCallback(
                    action="generate_text_choice_model"
                ).pack()
            ),
        ],
        [
            InlineKeyboardButton(
                text="🖼️ Сгенерировать изображение",
                callback_data=ActionCallback(
                    action="generate_image_choice_model"
                ).pack()
            ),
        ],
    ],
)


back_in_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Назад в главное меню",
                callback_data=ActionCallback(
                    action="start"
                ).pack()
            )
        ]
    ]
)


# rulers 80
