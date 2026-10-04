from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from ..hitl.hitl_schema import HITLTicket, HITLTicketStatus, HITLDecisionRequest
from ..hitl.hitl_manager import hitl_manager

router = APIRouter(prefix="/api/hitl", tags=["Human-in-the-Loop"])

@router.get("/tickets", response_model=List[HITLTicket])
async def list_tickets(status: Optional[HITLTicketStatus] = None):
    """Retrieve tickets in the HITL approval center queue"""
    return hitl_manager.list_tickets(status=status)

@router.post("/resolve", response_model=HITLTicket)
async def resolve_ticket(req: HITLDecisionRequest):
    """Authorize or reject an HITL ticket (enforcing Four-Eyes Principle)"""
    try:
        resolved = hitl_manager.resolve_ticket(req)
        return resolved
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.get("/summary")
async def get_hitl_summary() -> Dict[str, Any]:
    all_tickets = hitl_manager.list_tickets()
    pending = [t for t in all_tickets if t.status == HITLTicketStatus.PENDING]
    approved = [t for t in all_tickets if t.status == HITLTicketStatus.APPROVED]
    rejected = [t for t in all_tickets if t.status == HITLTicketStatus.REJECTED]
    return {
        "total_tickets": len(all_tickets),
        "pending_count": len(pending),
        "approved_count": len(approved),
        "rejected_count": len(rejected)
    }
