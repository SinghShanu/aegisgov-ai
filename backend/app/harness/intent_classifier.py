import re
from typing import Optional
from pydantic import BaseModel
from ..engine.japac_currency import JAPACCurrencyEngine

class FinancialIntent(BaseModel):
    raw_amount: float = 0.0
    currency: str = "SGD"
    amount_sgd: float = 0.0
    amount_inr: float = 0.0
    target_action: str
    is_financial_transfer: bool = False

class FinancialIntentClassifier:
    """
    Deterministic intent and financial parameter extractor.
    Parses currency amounts, payment verbs, PII extraction probes,
    and fiduciary investment proposals across Singapore (SGD) and India (INR).
    """
    AMOUNT_PATTERN = re.compile(
        r'(?:(S\$|SGD|₹|INR|Rs|\$|USD)\s*([0-9,]+(?:\.[0-9]+)?))|([0-9,]+(?:\.[0-9]+)?)\s*(S\$|SGD|₹|INR|Rs|\$|USD)',
        re.I
    )
    TRANSFER_PATTERN = re.compile(
        r'\b(transfer|execute|pay|payout|disburse|disbursement|deposit|remit|send|wire|fund|clearing|lease\s+deposit|commercial\s+credit|rebalance)\b',
        re.I
    )
    PII_PATTERN = re.compile(
        r'(unmasked|reveal|display|export|extract).*(?:NRIC|PAN|Aadhaar|passport|bank\s*account|identity)|(?:NRIC|PAN|Aadhaar).*(unmasked|raw)',
        re.I
    )
    INVESTMENT_PATTERN = re.compile(
        r'\b(cryptocurrency|crypto|derivative|leveraged|speculative|portfolio|allocation|investment\s+plan)\b',
        re.I
    )

    @classmethod
    def classify(cls, prompt: str, target_action: Optional[str] = None) -> FinancialIntent:
        amt_match = cls.AMOUNT_PATTERN.search(prompt)
        is_financial_transfer = bool(cls.TRANSFER_PATTERN.search(prompt))

        raw_amt = 0.0
        curr = "SGD"
        amount_sgd = 0.0
        amount_inr = 0.0

        if amt_match:
            curr_symbol = (amt_match.group(1) or amt_match.group(4) or "").strip().upper()
            amt_str = (amt_match.group(2) or amt_match.group(3) or "").replace(',', '')
            try:
                raw_amt = float(amt_str)
            except ValueError:
                raw_amt = 0.0

            if any(x in curr_symbol for x in ['S$', 'SGD']):
                curr = "SGD"
            elif any(x in curr_symbol for x in ['₹', 'INR', 'RS']):
                curr = "INR"
            elif any(x in curr_symbol for x in ['$', 'USD']):
                curr = "USD"
            else:
                curr = "SGD"

            amount_sgd = raw_amt if curr == "SGD" else JAPACCurrencyEngine.to_sgd(raw_amt, curr)
            amount_inr = raw_amt if curr == "INR" else JAPACCurrencyEngine.to_inr(amount_sgd)

        if target_action is None:
            if is_financial_transfer and (raw_amt > 0.0 or any(w in prompt.lower() for w in ["deposit", "lease", "transfer", "disburse", "payout", "wire"])):
                target_action = "initiate_payment_order"
            elif cls.PII_PATTERN.search(prompt):
                target_action = "export_unmasked_pii"
            elif cls.INVESTMENT_PATTERN.search(prompt):
                target_action = "propose_investment_plan"
            else:
                target_action = "query_financial_sentinel_basic"

        return FinancialIntent(
            raw_amount=raw_amt,
            currency=curr,
            amount_sgd=amount_sgd,
            amount_inr=amount_inr,
            target_action=target_action,
            is_financial_transfer=is_financial_transfer
        )
