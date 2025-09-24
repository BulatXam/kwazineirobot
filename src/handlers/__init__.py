from src.handlers.main import router as main_router
from src.handlers.neiro import router as neiro_router
from src.handlers.admin import router as admin_router


routers = [
    main_router,
    neiro_router,
    admin_router
]
