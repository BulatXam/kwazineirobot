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
                text="hydra-gemini",
                callback_data=ActionDataCallback(
                    action="generate_text",
                    data="hydra-gemini"
                ).pack()
            ),
        ],
        [
            InlineKeyboardButton(
                text="gpt-4-turbo",
                callback_data=ActionDataCallback(
                    action="generate_text",
                    data="gpt-4-turbo"
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
                text="flux.1-schnell",
                callback_data=ActionDataCallback(
                    action="generate_image",
                    data="flux.1-schnell"
                ).pack()
            ),
        ],
        [
            InlineKeyboardButton(
                text="dall-e-3",
                callback_data=ActionDataCallback(
                    action="generate_image",
                    data="dall-e-3"
                ).pack()
            ),
        ],
    ],
)

