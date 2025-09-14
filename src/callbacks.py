from aiogram.filters.callback_data import CallbackData


class ActionCallback(CallbackData, prefix="menu"):
    """Келлбек для главного меню и в целом для всех базовых действий."""
    action: str


class ActionDataCallback(CallbackData, prefix="menu_d"):
    """Келлбек для главного меню и в целом для всех базовых действий.
    
    + дополнительно есть поле data"""
    action: str
    data: str|int
