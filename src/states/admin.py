from aiogram.fsm.state import StatesGroup, State


class AdminMailing(StatesGroup):
    """Стейт написания сообщения рассылки"""
    WAITING = State()


class AddMailingLink(StatesGroup):
    """Стейт написания ссылки"""
    link_name = State()
    link = State()


class AdminMailingChange(StatesGroup):
    limit = State()
