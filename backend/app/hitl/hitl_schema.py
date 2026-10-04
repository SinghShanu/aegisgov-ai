from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import time

class HITLTicketStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    EXECUTED = "EXECUTED"
    REJECTED = "REJECTED"
    QUARANTINED = "QUARANTINED"

class HITLTriggerType(str, Enum):
    HIGH_VALUE_FINANCIAL_ACTION = "HIGH_VALUE_FINANCIAL_ACTION"
    EXTERNAL_INTERNET_EGRESS = "EXTERNAL_INTERNET_EGRESS"
    SENSITIVE_DATA_UNMASKING = "SENSITIVE_DATA_UNMASKING"
    ADVERSARIAL_THREAT_ESCALATION = "ADVERSARIAL_THREAT_ESCALATION"
    POLICY_COMPILATION_APPROVAL = "POLICY_COMPILATION_APPROVAL"

class HITLTicket(BaseModel):
    ticket_id: str
    created_at: float = Field(default_factory=time.time)
    formatted_time: str = ""
    trigger_type: HITLTriggerType
    requester_id: str
    requester_name: str
    requester_role: str
    requester_jurisdiction: str
    description: str
    proposed_action: str
    amount_sgd: float = 0.0
    amount_inr: float = 0.0
    payload: Dict[str, Any] = Field(default_factory=dict)
    risk_score: float = 0.0
    risk_summary: str
    status: HITLTicketStatus = HITLTicketStatus.PENDING
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[float] = None
    review_remarks: Optional[str] = None
    executed_at: Optional[float] = None
    settlement_ref: Optional[str] = None
    audit_entry_id: Optional[str] = None

class HITLDecisionRequest(BaseModel):
    ticket_id: str
    reviewer_id: str
    reviewer_name: str
    reviewer_role: str
    decision: HITLTicketStatus  # APPROVED or REJECTED
    remarks: str
