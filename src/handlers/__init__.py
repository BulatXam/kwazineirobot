from .main import router as main_router
from .neiro import router as neiro_router
from .admin import router as admin_router


routers = [
    main_router,
    neiro_router,
    admin_router
]
