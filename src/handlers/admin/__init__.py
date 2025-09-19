from aiogram import Router

from src.filters.admin import AdminFilter

from .menu import router as menu_router
from .mailing import router as mailing_router
from .statistics import router as statistics_router

router = Router(name="admin")

router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())

router.include_routers(
    menu_router,
    mailing_router,
    statistics_router
)
