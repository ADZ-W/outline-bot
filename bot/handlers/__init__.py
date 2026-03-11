"""Handlers package exports."""

from aiogram import Router

from .common import router as common_router
from .keys import router as keys_router
from .servers import router as servers_router


def get_root_router() -> Router:
    """Build root router with nested feature routers."""
    router = Router(name="root")
    router.include_router(common_router)
    router.include_router(servers_router)
    router.include_router(keys_router)
    return router


__all__ = ["get_root_router"]
