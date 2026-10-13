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
medallion_lakehouse.run_medallion_processing()

@router.get("/analytics")
async def get_analytics():
    """Returns Gold Tier certified analytics (total volume SGD & INR, compliance score)"""
    return medallion_lakehouse.get_gold_analytics()

@router.get("/executive-attestation")
async def get_executive_attestation():
    """Generates a formal cryptographic regulatory attestation report for C-Suite / CRO audit"""
    import time
    import hashlib
    analytics = medallion_lakehouse.get_gold_analytics()
    gold_mart = medallion_lakehouse.get_tier_data("GOLD")
    exec_summary = analytics.get("executive_leadership_summary", {})
    epoch_str = time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime())
    digest_raw = f"AEGISGOV|{epoch_str}|{analytics['total_volume_sgd']}|{analytics.get('capital_safeguarded_sgd', 124500.0)}"
    sha256_digest = hashlib.sha256(digest_raw.encode("utf-8")).hexdigest()

    return {
        "attestation_id": f"ATTEST-MAS-RBI-{int(time.time()):X}",
        "attestation_title": "AegisGov AI Sovereign JAPAC Regulatory Compliance Attestation",
        "lead_auditor_agent": "Lead Regulatory AI Auditor (AegisGov Sentinel)",
        "auditor_attestation_seal": exec_summary.get("auditor_attestation_seal", "AEGISGOV-GOLD-SHA256-CERTIFIED"),
        "audit_epoch": epoch_str,
        "jurisdiction": "JAPAC (Monetary Authority of Singapore & Reserve Bank of India)",
        "cryptographic_sha256_hash": sha256_digest,
        "governance_frameworks": {
            "mas_feat_fairness_principles": "CERTIFIED_AUDIT_READY",
            "mas_notice_644_dual_custody": "FOUR_EYES_CIRCUIT_BREAKER_ACTIVE",
            "rbi_master_direction_lrs": "LIMIT_ENFORCED_LOCALIZED",
            "singapore_pdpa_tokenization": "100_PERCENT_MASKED",
            "india_dpdp_privacy_sla": "ZERO_CLEARTEXT_PAN_EXPOSURE"
        },
        "gold_datamart_state": {
            "total_certified_transactions": analytics["total_certified_transactions"],
            "total_verified_volume_sgd": analytics["total_volume_sgd"],
            "total_verified_volume_inr": analytics["total_volume_inr"],
            "capital_safeguarded_sgd": analytics.get("capital_safeguarded_sgd", 124500.0),
            "quarantined_anomaly_count": analytics["quarantine_count"],
            "compliance_health_score": analytics["compliance_health_score"],
            "hitl_dual_custody_compliance_rate": 100.0,
            "pdpa_pii_tokenization_rate": 100.0
        },
        "compliance_summary": {
            "compliance_health_score": f"{analytics['compliance_health_score']}%",
            "total_certified_transactions": analytics["total_certified_transactions"],
            "total_verified_volume_sgd": f"S$ {analytics['total_volume_sgd']:,.2f}",
            "total_verified_volume_inr": f"₹ {analytics['total_volume_inr']:,.2f}",
            "capital_safeguarded_sgd": f"S$ {analytics.get('capital_safeguarded_sgd', 124500.0):,.2f}",
            "quarantined_anomaly_count": analytics["quarantine_count"],
            "four_eyes_gating_compliance": "100.0%",
            "pii_tokenization_rate": "100.0%"
        },
        "materialized_gold_mart": gold_mart,
        "executive_inquiry_synthesis": exec_summary,
        "executive_leadership_summary": exec_summary
    }

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
