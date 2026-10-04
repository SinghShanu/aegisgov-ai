from fastapi import APIRouter, Query, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from ..engine.transaction_streamer import transaction_streamer

router = APIRouter(prefix="/api/stream", tags=["Transaction Streamer"])

class StreamControlRequest(BaseModel):
    interval_seconds: Optional[float] = Field(default=2.5, ge=0.5, le=10.0)

class BurstRequest(BaseModel):
    count: Optional[int] = Field(default=10, ge=1, le=50)

@router.post("/start")
async def start_stream(req: Optional[StreamControlRequest] = None):
    interval = req.interval_seconds if req else 2.5
    transaction_streamer.start(interval_seconds=interval)
    return {
        "status": "STREAM_ACTIVE",
        "interval_seconds": transaction_streamer.interval_seconds,
        "is_running": transaction_streamer.is_running
    }

@router.post("/stop")
async def stop_stream():
    transaction_streamer.stop()
    return {
        "status": "STREAM_STOPPED",
        "is_running": transaction_streamer.is_running
    }

class ScenarioBurstRequest(BaseModel):
    scenario_type: str = Field(default="MULE_FRAUD_SURGE")

@router.post("/burst")
async def burst_stream(req: Optional[BurstRequest] = None):
    count = req.count if req else 10
    burst_results = transaction_streamer.generate_burst(count=count)
    return {
        "status": "BURST_COMPLETED",
        "count_generated": len(burst_results),
        "results": burst_results,
        "current_status": transaction_streamer.get_status()
    }

@router.post("/scenario")
async def trigger_scenario(req: ScenarioBurstRequest):
    result = transaction_streamer.trigger_scenario_burst(scenario_type=req.scenario_type)
    return {
        "status": "SCENARIO_EXECUTED",
        "scenario": req.scenario_type,
        "summary": result["summary"],
        "roi_impact": result["roi_impact"],
        "events_generated": result["events_generated"],
        "current_status": transaction_streamer.get_status()
    }

@router.get("/status")
async def get_stream_status():
    return transaction_streamer.get_status()

@router.get("/events")
async def get_stream_events():
    return {
        "is_running": transaction_streamer.is_running,
        "recent_events": transaction_streamer.recent_events
    }
