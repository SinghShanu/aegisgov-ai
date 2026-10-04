import json
import os
import time
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..engine.contracts import CompliancePolicy, DataContract
from ..agents.policy_compiler import PolicyCompilerAgent
from ..agents.medallion_inspector import MedallionInspectorAgent
from ..harness.audit_logger import audit_ledger

router = APIRouter(prefix="/api/policies", tags=["Policies"])

POLICIES_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "japac_regulatory_policies.json")

def load_policies() -> List[Dict[str, Any]]:
    if os.path.exists(POLICIES_PATH):
        with open(POLICIES_PATH, "r") as f:
            return json.load(f)
    return []

ACTIVE_CONTRACTS: Dict[str, DataContract] = {}

class PolicyCompileRequest(BaseModel):
    policy_title: str
    authority: str
    policy_text: str

class ContractApproveRequest(BaseModel):
    reviewer_id: str
    reviewer_name: str
    reviewer_role: str
    remarks: Optional[str] = "Approved and deployed to Medallion Lakehouse pipeline."

@router.get("", response_model=List[Dict[str, Any]])
async def get_policies():
    """Retrieve all loaded JAPAC BFSI compliance policies (MAS, RBI, PDPA/DPDP)"""
    return load_policies()

@router.post("/compile", response_model=DataContract)
async def compile_policy(req: PolicyCompileRequest):
    """Trigger Agent 1 (PolicyCompilerAgent) to translate natural language into Policy-as-Code"""
    contract = await PolicyCompilerAgent.compile_policy_to_contracts(
        policy_title=req.policy_title,
        authority=req.authority,
        policy_text=req.policy_text
    )
    # Compiled contract starts in PENDING_APPROVAL state pending governance signoff
    contract.status = "PENDING_APPROVAL"
    contract.is_active = False
    ACTIVE_CONTRACTS[contract.contract_id] = contract
    return contract

@router.post("/contracts/{contract_id}/approve", response_model=DataContract)
async def approve_contract(contract_id: str, req: ContractApproveRequest):
    """
    Dual-Persona Governance Approval:
    Allows Compliance Officers or Risk Officers to approve a compiled Data Contract
    and deploy it to the live Medallion Lakehouse pipeline.
    """
    contract = ACTIVE_CONTRACTS.get(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail=f"Contract '{contract_id}' not found.")

    # Validate reviewer authority under SOC 2 CC8.1 Change Management
    if req.reviewer_role not in ["COMPLIANCE_OFFICER", "RISK_OFFICER", "SYSTEM_ADMIN"]:
        raise HTTPException(
            status_code=403,
            detail=f"Access Denied: Role '{req.reviewer_role}' lacks authority to approve data contracts under SOC 2 CC8.1 Change Management. Requires Compliance Officer or Risk Officer."
        )

    # Approve and activate contract
    contract.status = "ACTIVE_ENFORCING"
    contract.is_active = True
    contract.approved_by = f"{req.reviewer_name} ({req.reviewer_role})"
    contract.approved_at = time.strftime("%Y-%m-%d %H:%M:%SZ")

    # Run inspection cycle on Medallion Lakehouse using this active contract
    inspection_result = MedallionInspectorAgent.execute_inspection_cycle(contract)

    # Capture lifecycle enforcement telemetry
    contract.lifecycle_telemetry = {
        "cycle_status": inspection_result.get("cycle_status", "SUCCESS"),
        "pipeline_summary": inspection_result.get("pipeline_summary", {}),
        "gold_certified_metrics": inspection_result.get("gold_certified_metrics", {}),
        "deployed_at": time.strftime("%Y-%m-%d %H:%M:%SZ"),
        "compliance_remarks": req.remarks
    }

    # Log to cryptographic audit ledger
    audit_ledger.log_event(
        event_type="DATA_CONTRACT_APPROVED_AND_DEPLOYED",
        user_id=req.reviewer_id,
        role=req.reviewer_role,
        action_or_prompt=f"Approved Data Contract {contract.contract_id} ({contract.name}) for Medallion pipeline enforcement",
        decision="APPROVED",
        metadata={
            "contract_id": contract.contract_id,
            "governing_regulation": contract.governing_regulation,
            "target_tier": contract.target_tier.value if hasattr(contract.target_tier, "value") else str(contract.target_tier),
            "rules_count": len(contract.rules),
            "compliance_health_score": contract.lifecycle_telemetry["gold_certified_metrics"].get("compliance_health_score", 0.0)
        }
    )

    ACTIVE_CONTRACTS[contract_id] = contract
    return contract

@router.get("/contracts", response_model=List[DataContract])
async def list_contracts():
    return list(ACTIVE_CONTRACTS.values())
