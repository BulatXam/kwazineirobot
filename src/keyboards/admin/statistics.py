from typing import List

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from src.database.models.user import User
from src.database.models.neiro import NeiroResponse

from src.callbacks import ActionCallback, ActionDataCallback

def paginator_users_statistic(
    users: List[User], 
    current_page: int, 
    num_in_page: int = 4
):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            *[
                [
                    InlineKeyboardButton(
                        text=f"Пользователь #{user.id}",
                        callback_data=ActionDataCallback(
                            action="get_user_statistic",
                            data=user.id
                        ).pack()
                    )
                ] for user in users[:num_in_page]
            ],
            [
                InlineKeyboardButton(
                    text="<--",
                    callback_data=ActionDataCallback(
                        action="paginator_user_statistic",
                        data="last"
                    ).pack()
                ),
                InlineKeyboardButton(
                    text=f"{current_page}",
                    callback_data=ActionCallback(
                        action="None"
                    ).pack()
                ),
                InlineKeyboardButton(
                    text="-->",
                    callback_data=ActionDataCallback(
                        action="paginator_user_statistic",
                        data="next"
                    ).pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="Назад в главное меню",
                    callback_data=ActionCallback(
                        action="admin_menu"
                    ).pack()
                )
            ]
        ]
    )

back_in_paginator_users_statistic = InlineKeyboardMarkup(
    inline_keyboard=[
        [
                InlineKeyboardButton(
                text=f"Назад",
                callback_data=ActionDataCallback(
                    action="get_user_statistic",
                    data="None"
                ).pack()
            )
        ]
    ]
)

get_user_by_paginator_users_statistic = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Изменить лимит токенов",
                    callback_data=ActionCallback(
                        action="user_change_tokens_limit"
                    ).pack()
                ),
            ],
            [
                InlineKeyboardButton(
                    text="История запросов",
                    callback_data=ActionDataCallback(
                        action="paginator_user_history",
                        data="first"
                    ).pack()
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Назад",
                    callback_data=ActionDataCallback(
                        action="paginator_user_statistic",
                        data="None"
                    ).pack()
                ),
            ]
        ]
    )

user_change_tokens_limit_image_or_text = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Лимит на текста",
                callback_data=ActionDataCallback(
                    action="user_change_tokens_limit_text_or_image",
                    data="text"
                ).pack()
            ),   
        ],
        [
            InlineKeyboardButton(
                text="Лимит на изображения",
                callback_data=ActionDataCallback(
                    action="user_change_tokens_limit_text_or_image",
                    data="image"
                ).pack()
            ),   
        ],
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=ActionDataCallback(
                    action="get_user_statistic",
                    data="None"
                ).pack()
            ),
        ]
    ]
)


def paginator_user_history(
    neiro_responses: List[NeiroResponse], 
    current_page: int, 
    num_in_page: int = 4
):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            *[
                [
                    InlineKeyboardButton(
                        text=f"Запрос #{neiro_response.id}",
                        callback_data=ActionDataCallback(
                            action="get_user_neiro_response",
                            data=neiro_response.id
                        ).pack()
                    )
                ] for neiro_response in neiro_responses[:num_in_page]
            ],
            [
                InlineKeyboardButton(
                    text="<--",
                    callback_data=ActionDataCallback(
                        action="paginator_user_history",
                        data="last"
                    ).pack()
                ),
                InlineKeyboardButton(
                    text=f"{current_page}",
                    callback_data=ActionCallback(
                        action="None"
                    ).pack()
                ),
                InlineKeyboardButton(
                    text="-->",
                    callback_data=ActionDataCallback(
                        action="paginator_user_history",
                        data="next"
                    ).pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="Назад",
                    callback_data=ActionDataCallback(
                        action="get_user_statistic",
                        data="None"
                    ).pack()
                )
            ]
        ]
    )

back_in_paginator_user_history = InlineKeyboardMarkup(
    inline_keyboard=[
        [
                InlineKeyboardButton(
                text=f"Назад",
                callback_data=ActionDataCallback(
                    action="paginator_user_history",
                    data="None"
                ).pack()
            )
        ]
    ]
)
