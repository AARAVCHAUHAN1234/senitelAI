"""Settings configuration router."""

from fastapi import APIRouter, Body
from pydantic import BaseModel

from ..core.settings import settings

router = APIRouter(prefix="/api/settings", tags=["settings"])


class SettingsUpdate(BaseModel):
    voyagesim_url: str = "http://localhost:8001"
    enabled_modules: str = "all"


@router.get("")
def get_settings():
    """Retrieve platform runtime configuration."""
    return {
        "voyagesim_url": settings.VOYAGESIM_URL,
        "database_url": settings.DATABASE_URL,
        "enabled_modules": settings.enabled_module_list,
        "gemini_configured": bool(settings.GEMINI_API_KEY),
        "mode": "DEMO / SIMULATED",
        "live_testing": False,
        "safe_sandbox": True
    }


@router.put("")
def update_settings(req: SettingsUpdate = Body(...)):
    """Update runtime configuration."""
    settings.VOYAGESIM_URL = req.voyagesim_url
    settings.ENABLED_MODULES = req.enabled_modules
    return {"status": "updated", "settings": get_settings()}
