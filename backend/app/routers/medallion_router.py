import json
import os
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query
from ..engine.medallion_lakehouse import medallion_lakehouse
from ..agents.medallion_inspector import MedallionInspectorAgent
from ..agents.policy_compiler import PolicyCompilerAgent
from ..access_control.user_contexts import PREDEFINED_USERS, UserRole

router = APIRouter(prefix="/api/medallion", tags=["Medallion Lakehouse"])

SAMPLE_TX_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sample_japac_transactions.json")

def initialize_bronze_data():
    if os.path.exists(SAMPLE_TX_PATH):
        with open(SAMPLE_TX_PATH, "r", encoding="utf-8") as f:
            records = json.load(f)
            medallion_lakehouse.ingest_bronze(records)

# Seed on load
initialize_bronze_data()

@router.get("/analytics")
async def get_analytics():
    """Returns Gold Tier certified analytics (total volume SGD & INR, compliance score)"""
    return medallion_lakehouse.get_gold_analytics()

@router.get("/lineage")
async def get_lineage():
    """Returns nodes and edges for the React Flow lineage graph"""
    return medallion_lakehouse.get_lineage_graph()

@router.get("/tier/{tier_name}")
async def get_tier_records(
    tier_name: str,
    limit: int = 50,
    user_persona_key: Optional[str] = Query(None, description="Active user persona key for PoLP enforcement")
):
    """
    Retrieve records from Bronze, Silver, or Quarantine with PoLP tier-gating.
    Principle of Least Privilege: Raw Bronze tier contains unmasked customer PII and raw account numbers.
    Access is restricted exclusively to Principal Data Platform Engineers (Alex Wong).
    """
    tier_upper = tier_name.upper()

    if tier_upper == "BRONZE":
        user = PREDEFINED_USERS.get(user_persona_key) if user_persona_key else None
        if not user or user.role != UserRole.DATA_ENGINEER:
            role_label = user.role.value if user else "UNAUTHENTICATED"
            raise HTTPException(
                status_code=403,
                detail=f"Access Denied (PoLP Data Governance): Raw Bronze tier contains unmasked customer PII and unverified payment ingestion streams. Role '{role_label}' lacks clearance. Access is restricted exclusively to Principal Data Platform Engineers (Alex Wong)."
            )

    return medallion_lakehouse.get_tier_data(tier_upper, limit=limit)

@router.post("/run-pipeline")
async def run_pipeline():
    """Trigger Agent 2 to enforce data contracts across the Medallion architecture"""
    # Compile default contract
    contract = await PolicyCompilerAgent.compile_policy_to_contracts(
        policy_title="MAS FEAT & RBI Harmonized Contract",
        authority="MAS & RBI",
        policy_text="Automated tokenization for NRIC/PAN and transaction validation."
    )
    result = MedallionInspectorAgent.execute_inspection_cycle(contract)
    return result
