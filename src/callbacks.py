from aiogram.filters.callback_data import CallbackData


class ActionCallback(CallbackData, prefix="menu"):
    """Келлбек для главного меню и в целом для всех базовых действий."""
    action: str
    data: str|int|None = None
