from typing import List, Dict, Any
from fastapi import APIRouter
from ..harness.audit_logger import audit_ledger, AuditEntry

router = APIRouter(prefix="/api/audit", tags=["Audit Ledger & Threat Radar"])

@router.get("/ledger", response_model=List[AuditEntry])
async def get_audit_ledger(limit: int = 50):
    """Retrieve cryptographic hash-chained audit blocks"""
    return audit_ledger.get_entries(limit=limit)

@router.get("/verify")
async def verify_ledger_integrity() -> Dict[str, Any]:
    """Cryptographically verifies that no historical audit blocks have been tampered with"""
    return audit_ledger.verify_chain_integrity()

@router.get("/threat-radar")
async def get_threat_radar() -> Dict[str, Any]:
    """Real-time threat statistics for the dashboard radar"""
    entries = audit_ledger.get_entries(limit=100)
    attacks_blocked = sum(1 for e in entries if "ATTACK" in e.decision or "BLOCKED" in e.decision)
    hitl_escalated = sum(1 for e in entries if "HITL" in e.decision or "PENDING" in e.decision)
    granted = sum(1 for e in entries if "ALLOWED" in e.decision or "GRANTED" in e.decision)
    
    return {
        "attacks_blocked_count": attacks_blocked,
        "hitl_escalations_count": hitl_escalated,
        "authorized_transactions_count": granted,
        "total_audit_events": len(entries),
        "threat_status": "SECURE",
        "active_defenses": [
            "Direct Jailbreak Blocker",
            "Context Poisoning Filter",
            "JAPAC PII Dynamic Vault",
            "Four-Eyes Financial Circuit Breaker",
            "MAS FEAT Bias Verifier"
        ]
    }
