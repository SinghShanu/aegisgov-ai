from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import time

class DataClassification(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"
    SECRET = "SECRET"

class MedallionTier(str, Enum):
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"
    QUARANTINE = "QUARANTINE"

class PIIType(str, Enum):
    NONE = "NONE"
    SG_NRIC = "SG_NRIC"
    IN_PAN = "IN_PAN"
    IN_AADHAAR = "IN_AADHAAR"
    CREDIT_CARD = "CREDIT_CARD"
    BANK_ACCOUNT = "BANK_ACCOUNT"
    PHONE = "PHONE"
    EMAIL = "EMAIL"
    NAME = "NAME"

class MaskingStrategy(str, Enum):
    NONE = "NONE"
    FULL_REDACT = "FULL_REDACT"
    MASK_MIDDLE = "MASK_MIDDLE"
    VAULT_TOKENIZE = "VAULT_TOKENIZE"
    HASH_SHA256 = "HASH_SHA256"

class ColumnContractRule(BaseModel):
    column_name: str
    data_type: str
    nullable: bool = True
    pii_type: PIIType = PIIType.NONE
    masking_strategy: MaskingStrategy = MaskingStrategy.NONE
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_currencies: Optional[List[str]] = None
    description: str

class DataContract(BaseModel):
    contract_id: str
    name: str
    version: str = "1.0.0"
    target_tier: MedallionTier
    jurisdiction: str = "JAPAC"
    governing_regulation: str  # e.g., "MAS Notice 644 / RBI Digital Lending 2022"
    rules: List[ColumnContractRule]
    created_at: float = Field(default_factory=time.time)
    status: str = "PENDING_APPROVAL"  # "PENDING_APPROVAL", "ACTIVE_ENFORCING", "DEPRECATED"
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    is_active: bool = False
    lifecycle_telemetry: Optional[Dict[str, Any]] = None

class TransactionRecord(BaseModel):
    transaction_id: str
    timestamp: str
    sender_id: str
    sender_name: str
    sender_id_doc: str          # e.g., NRIC "S1234567A" or PAN "ABCDE1234F"
    sender_account: str
    recipient_id: str
    recipient_name: str
    recipient_account: str
    amount: float
    currency: str               # "SGD", "INR", "JPY", "USD"
    payment_rail: str           # "FAST", "PayNow", "UPI", "IMPS", "SWIFT"
    purpose: str
    tier: MedallionTier = MedallionTier.BRONZE
    risk_score: float = 0.0     # 0.0 to 1.0
    quarantine_reason: Optional[str] = None
    token_vault_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CompliancePolicy(BaseModel):
    policy_id: str
    title: str
    authority: str              # "MAS", "RBI", "Singapore PDPA", "India DPDP", "Basel III"
    jurisdiction: str           # "SG", "IN", "GLOBAL"
    summary: str
    raw_policy_text: str
    compiled_contract_ids: List[str] = []
    is_active: bool = True
    approved_by: Optional[str] = None
    approved_at: Optional[float] = None
