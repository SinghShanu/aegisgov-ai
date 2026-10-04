from fastapi import APIRouter
from ..agents.soc2_auditor_agent import SOC2AuditorAgent, SOC2ComplianceReport

router = APIRouter(prefix="/api/compliance", tags=["SOC 2 & Compliance Auditing"])

@router.get("/scan")
async def run_compliance_scan():
    """Trigger Agent 4 to perform a continuous compliance & pipeline health scan"""
    return SOC2AuditorAgent.execute_pipeline_scan()

@router.get("/report", response_model=SOC2ComplianceReport)
async def get_soc2_report():
    """Synthesize evidence-backed SOC 2 Type II and MAS/RBI compliance package for auditors"""
    return SOC2AuditorAgent.generate_soc2_report()
