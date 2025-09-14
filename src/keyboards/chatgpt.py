from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton
)

from src.callbacks import ActionDataCallback


gen_text_choice_model = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="gpt-4-turbo",
                callback_data=ActionDataCallback(
                    action="generate_text",
                    data="gpt-4-turbo"
                ).pack()
            ),
        ],
        [
            InlineKeyboardButton(
                text="gpt-4",
                callback_data=ActionDataCallback(
                    action="generate_text",
                    data="gpt-4"
                ).pack()
            ),
        ],
    ],
)


stop_chat = ReplyKeyboardMarkup(
    keyboard=[[
        KeyboardButton(
            text="Остановить"
        )
    ]]
)

gen_img_choice_model = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="hydro-gemini",
                callback_data=ActionDataCallback(
                    action="generate_image",
                    data="hydro-gemini"
                ).pack()
            ),
        ],
        [
            InlineKeyboardButton(
                text="flux.1-schnell",
                callback_data=ActionDataCallback(
                    action="generate_image",
                    data="flux.1-schnell"
                ).pack()
            ),
        ],
    ],
)

