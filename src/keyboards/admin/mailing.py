from typing import List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.callbacks import ActionCallback, ActionDataCallback


def _is_valid_text_for_convert_buttons(text: str) -> bool:
    """
    Проверяет, соответствует ли текст формату для создания кнопок.
    Формат: текст-ссылка или текст-ссылка|текст-ссылка...
    
    Args:
        text (str): Текст для проверки
        
    Returns:
        bool: True если текст валиден, False если нет
    """
    lines = text.split('\n')
    for line in lines:
        buttons = line.split('|')
        for button in buttons:
            parts = button.strip().split('-')
            if len(parts) != 2:
                return False
            if not parts[0].strip() or not parts[1].strip():
                return False
    return True


async def build_inline_buttons_by_text(
    buttons_text: str
) -> List[InlineKeyboardButton]:
    """
    Создает инлайн-клавиатуру из текста с кнопками.
    
    Args:
        button_text (str): Текст в формате "текст-ссылка" или "текст-ссылка|текст-ссылка..."
        
    Returns:
        InlineKeyboardMarkup: Готовая клавиатура
        
    Raises:
        ValueError: Если текст не соответствует формату
    """
    if not _is_valid_text_for_convert_buttons(buttons_text):
        raise ValueError("Invalid button text format")
    
    keyboard = []
    lines = buttons_text.split('\n')
    
    for line in lines:
        row_buttons = []
        buttons = line.split('|')
        
        for button in buttons:
            text, link = map(str.strip, button.split('-'))
            
            if link == "{random}":
                row_buttons.append(InlineKeyboardButton(text=text, callback_data="random"))
            else:
                row_buttons.append(InlineKeyboardButton(text=text, url=link))
        
        if row_buttons:
            keyboard.append(row_buttons)
    
    return keyboard


async def mailing_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            # [
            #     InlineKeyboardButton(
            #         text='Добавить кнопки', 
            #         callback_data=ActionCallback(
            #             action='Action_mailing_add_keyboard'
            #         ).pack()
            #     ),
            # ],
            [
                InlineKeyboardButton(
                    text='⚫ Отменить', 
                    callback_data=ActionCallback(
                        action='admin_menu'
                    ).pack()
                ),
                InlineKeyboardButton(
                    text='Продолжить ➡️', 
                    callback_data=ActionCallback(
                        action='mailing_add_keyboard'
                    ).pack()
                )
            ]
        ]
    )


async def back_in_mailing():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data=ActionCallback(
                        action="mailing"
                    ).pack()
                ),
            ],
        ]
    )


async def mailing_next(keyboard: List[List[InlineKeyboardButton]]):
    if not keyboard:
        keyboard = []

    return InlineKeyboardMarkup(
        inline_keyboard=[
            *keyboard,
            [
                InlineKeyboardButton(
                    text="↗️ Запустить",
                    callback_data=ActionCallback(
                        action="admin_mailing_done"
                    ).pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data=ActionCallback(
                        action="mailing"
                    ).pack()
                )
            ]
        ]
    )


async def mailing_progress():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Завершить",
                    callback_data=ActionCallback(
                        action="admin_mailing_complete"
                    ).pack()
                ),
            ]
        ]
    )


async def progress_stop():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Редактировать",
                    callback_data=ActionCallback(
                        action="admin_mailing"
                    ).pack()
                ),
                InlineKeyboardButton(
                    text="Завершить",
                    callback_data=ActionCallback(
                        action="admin_mailing_complete"
                    ).pack()
                ),
            ]
        ]
    ) 


async def progress_complete():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Вернуться в меню рассылки",
                    callback_data=ActionCallback(
                        action="mailing"
                    ).pack()
                ),
            ],
        ]
    )


async def send_mailing_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data=ActionCallback(
                        action="mailing"
                    ).pack()
                ),
                InlineKeyboardButton(
                    text="➡️ Пропустить",
                    callback_data=ActionCallback(
                        action="mailing_next"
                    ).pack()
                )
            ]
        ]
    )


async def mailing_create_keyboard_retry():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔄️️ Попробовать снова", 
                    callback_data=ActionCallback(
                        action="admin_mailing_add_keyboard"
                    ).pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад", 
                    callback_data=ActionCallback(
                        action="mailing"
                    ).pack()
                ),
                InlineKeyboardButton(
                    text="🏠 Меню", 
                    callback_data=ActionCallback(
                        action="menu"
                    ).pack()
                )

            ]
        ]
    )


async def mailing_free_or_all():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Отправить рассылку",
                    callback_data=ActionDataCallback(
                        action="mailing_next",
                        data="all"
                    ).pack()
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data=ActionCallback(
                        action="admin_mailing_add_keyboard"
                    ).pack()
                )
            ]
        ]
    )
