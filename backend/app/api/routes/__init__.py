from fastapi import APIRouter

from app.api.routes.common import router as common_router

router = APIRouter()
router.include_router(common_router)

__all__ = ["router"]
