from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import time

class UserRole(str, Enum):
    JUNIOR_ANALYST = "JUNIOR_ANALYST"
    WEALTH_ADVISOR = "WEALTH_ADVISOR"
    COMPLIANCE_OFFICER = "COMPLIANCE_OFFICER"
    RISK_OFFICER = "RISK_OFFICER"
    DATA_ENGINEER = "DATA_ENGINEER"
    SYSTEM_ADMIN = "SYSTEM_ADMIN"

class SecurityClearance(str, Enum):
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"
    SECRET = "SECRET"

class Jurisdiction(str, Enum):
    SG = "SG"       # Singapore
    IN = "IN"       # India
    JP = "JP"       # Japan
    GLOBAL = "GLOBAL"

class UserContext(BaseModel):
    user_id: str
    name: str
    role: UserRole
    clearance: SecurityClearance
    jurisdiction: Jurisdiction
    allowed_actions: List[str]
    max_transaction_limit_sgd: float
    max_transaction_limit_inr: float
    can_approve_hitl: bool = False
    session_token: str
    token_issued_at: float = Field(default_factory=time.time)
    token_ttl_seconds: int = 28800  # 8 hours standard enterprise workday session (TBAC)

# Pre-defined enterprise personas for demo & testing
PREDEFINED_USERS: Dict[str, UserContext] = {
    "junior_analyst": UserContext(
        user_id="usr_sg_014",
        name="Rachel Lim (Junior Analyst)",
        role=UserRole.JUNIOR_ANALYST,
        clearance=SecurityClearance.INTERNAL,
        jurisdiction=Jurisdiction.SG,
        allowed_actions=[
            "view_gold_metrics",
            "view_silver_masked",
            "query_financial_sentinel_basic",
            "query_financial_copilot_basic"
        ],
        max_transaction_limit_sgd=1000.00,
        max_transaction_limit_inr=50000.00,
        can_approve_hitl=False,
        session_token="tbac_tok_rachel_lim_9921",
        token_ttl_seconds=28800
    ),
    "wealth_advisor": UserContext(
        user_id="usr_in_082",
        name="Vikram Mehta (Senior Wealth Advisor)",
        role=UserRole.WEALTH_ADVISOR,
        clearance=SecurityClearance.CONFIDENTIAL,
        jurisdiction=Jurisdiction.IN,
        allowed_actions=[
            "view_gold_metrics",
            "view_silver_masked",
            "view_portfolio_aggregates",
            "propose_investment_plan",
            "initiate_payment_order",
            "query_financial_sentinel_basic",
            "query_financial_copilot_basic"
        ],
        max_transaction_limit_sgd=10000.00,
        max_transaction_limit_inr=500000.00,
        can_approve_hitl=False,
        session_token="tbac_tok_vikram_mehta_4418",
        token_ttl_seconds=28800
    ),
    "compliance_officer": UserContext(
        user_id="usr_sg_002",
        name="Priya Sharma (Principal Compliance Auditor)",
        role=UserRole.COMPLIANCE_OFFICER,
        clearance=SecurityClearance.SECRET,
        jurisdiction=Jurisdiction.GLOBAL,
        allowed_actions=[
            "view_gold_metrics",
            "view_silver_masked",
            "view_audit_ledger",
            "inspect_quarantine",
            "approve_policy_as_code",
            "approve_hitl_ticket",
            "review_threat_radar",
            "query_financial_sentinel_basic",
            "query_financial_copilot_basic"
        ],
        max_transaction_limit_sgd=0.00,
        max_transaction_limit_inr=0.00,
        can_approve_hitl=True,
        session_token="tbac_tok_priya_sharma_0012",
        token_ttl_seconds=28800
    ),
    "risk_officer": UserContext(
        user_id="usr_sg_005",
        name="Kenji Sato (Director of Model & Financial Risk)",
        role=UserRole.RISK_OFFICER,
        clearance=SecurityClearance.SECRET,
        jurisdiction=Jurisdiction.GLOBAL,
        allowed_actions=[
            "view_gold_metrics",
            "view_silver_masked",
            "view_audit_ledger",
            "approve_hitl_ticket",
            "override_circuit_breaker",
            "review_threat_radar",
            "query_financial_sentinel_basic",
            "query_financial_copilot_basic"
        ],
        max_transaction_limit_sgd=1000000.00,
        max_transaction_limit_inr=50000000.00,
        can_approve_hitl=True,
        session_token="tbac_tok_kenji_sato_7781",
        token_ttl_seconds=28800
    ),
    "data_engineer": UserContext(
        user_id="usr_sg_088",
        name="Alex Wong (Principal Data Platform Engineer)",
        role=UserRole.DATA_ENGINEER,
        clearance=SecurityClearance.CONFIDENTIAL,
        jurisdiction=Jurisdiction.SG,
        allowed_actions=[
            "view_bronze_raw",
            "view_silver_masked",
            "view_gold_metrics",
            "manage_pipeline_ingestion",
            "query_financial_sentinel_basic",
            "query_financial_copilot_basic"
        ],
        max_transaction_limit_sgd=0.00,
        max_transaction_limit_inr=0.00,
        can_approve_hitl=False,
        session_token="tbac_tok_alex_wong_7719",
        token_ttl_seconds=28800
    )
}
