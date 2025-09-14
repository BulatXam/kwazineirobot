from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


gen_text_choice_model = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="gpt-4-turbo",
                callback_data="generate_text_gpt4"
            ),
        ],
        [
            InlineKeyboardButton(
                text="gpt-4",
                callback_data="generate_text_gpt4"
            ),
        ],
    ],
)
