from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .groups import router as groups_router
from .info_categories import router as info_categories_router
from .articles import router as articles_router
from .proposals import router as proposals_router
from .statistics import router as statistics_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(groups_router, prefix="/groups", tags=["groups"])
api_router.include_router(info_categories_router, prefix="/info-categories", tags=["info-categories"])
api_router.include_router(articles_router, prefix="/articles", tags=["articles"])
api_router.include_router(proposals_router, prefix="/proposals", tags=["proposals"])
api_router.include_router(statistics_router, prefix="/statistics", tags=["statistics"])