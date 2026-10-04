from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from ..gcp.gcp_provider import gcp_provider, GCPArchitectureOverview

router = APIRouter(prefix="/api/gcp", tags=["Google Cloud Architecture"])

class ModeUpdateRequest(BaseModel):
    mode: str  # "local" or "cloud"

@router.get("/architecture", response_model=GCPArchitectureOverview)
async def get_gcp_architecture():
    return gcp_provider.get_overview()

@router.post("/mode")
async def update_gcp_mode(req: ModeUpdateRequest):
    if req.mode in ["local", "cloud"]:
        gcp_provider.gcp_mode = req.mode
    return {
        "status": "UPDATED",
        "current_mode": gcp_provider.gcp_mode
    }
