from typing import Dict, Any, Optional
from pydantic import BaseModel
from ..config import settings
from ..engine.japac_currency import JAPACCurrencyEngine

class CircuitBreakerEvaluation(BaseModel):
    triggered: bool
    requires_hitl: bool
    hard_blocked: bool
    risk_level: str  # "LOW", "MEDIUM", "HIGH_VALUE_ACTION", "UNAUTHORIZED_EGRESS"
    reason: str
    amount_sgd: float = 0.0
    action_type: str = "READ_ONLY"

class CircuitBreaker:
    @staticmethod
    def evaluate_tool_call(
        tool_name: str,
        arguments: Dict[str, Any],
        user_role: str
    ) -> CircuitBreakerEvaluation:
        # 1. External Network Egress Check
        if tool_name in ["external_http_request", "send_external_webhook", "query_public_internet"]:
            return CircuitBreakerEvaluation(
                triggered=True,
                requires_hitl=True,
                hard_blocked=False,
                risk_level="UNAUTHORIZED_EGRESS",
                reason="Attempted external internet communication. Restricted under BFSI data sovereignty regulations.",
                action_type="EXTERNAL_EGRESS"
            )

        # 2. Financial Transaction Evaluation
        if tool_name in ["execute_funds_transfer", "initiate_payment_order", "approve_loan_disbursement"]:
            raw_amount = float(arguments.get("amount", 0.0))
            currency = str(arguments.get("currency", "SGD")).upper()
            amount_in_sgd = JAPACCurrencyEngine.to_sgd(raw_amount, currency)

            # High-Value Threshold Check (SGD 10,000 or INR 5,00,000)
            if amount_in_sgd >= settings.HIGH_VALUE_THRESHOLD_SGD:
                return CircuitBreakerEvaluation(
                    triggered=True,
                    requires_hitl=True,
                    hard_blocked=False,
                    risk_level="HIGH_VALUE_ACTION",
                    reason=f"Financial action value {JAPACCurrencyEngine.format(raw_amount, currency)} (equivalent to S$ {amount_in_sgd:,.2f}) exceeds single-agent autonomous limit (S$ {settings.HIGH_VALUE_THRESHOLD_SGD:,.2f}). Four-Eyes Principle approval mandated.",
                    amount_sgd=amount_in_sgd,
                    action_type="FINANCIAL_TRANSFER"
                )

        # 3. Bulk Data Export / Decryption Check
        if tool_name in ["export_raw_pii", "bulk_download_kyc"]:
            return CircuitBreakerEvaluation(
                triggered=True,
                requires_hitl=True,
                hard_blocked=True,
                risk_level="HIGH_RISK_DATA_EXFILTRATION",
                reason="Bulk export of unmasked PII/KYC is prohibited by policy PDPA-SG-009 / DPDP-IN-2023.",
                action_type="DATA_ACCESS"
            )

        return CircuitBreakerEvaluation(
            triggered=False,
            requires_hitl=False,
            hard_blocked=False,
            risk_level="LOW",
            reason="Action within safe autonomous operational boundaries.",
            action_type="INTERNAL_QUERY"
        )
