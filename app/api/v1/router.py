from fastapi import APIRouter

# from app.api.v1.endpoints.admin import router as admin_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.user import router as user_router
from app.api.v1.endpoints.engine import router as engine_router
from app.api.v1.endpoints.chat import router as chat_router

routers = APIRouter()
router_list = [
    # admin_router,
    auth_router,
    user_router,
    engine_router,
    chat_router
]

for router in router_list:
    # router.tags = routers.tags.append("v1")
    routers.include_router(router)
