from .main import router as main_router
from .chatgpt import router as chatgpt_router


routers = [
    main_router,
    chatgpt_router,
]
