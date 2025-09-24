from aiogram import Router

from src.filters.admin import AdminFilter

from src.handlers.admin.menu import router as menu_router
from src.handlers.admin.mailing import router as mailing_router
from src.handlers.admin.statistics import router as statistics_router

router = Router(name="admin")

router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())

router.include_routers(
    menu_router,
    mailing_router,
    statistics_router
)
