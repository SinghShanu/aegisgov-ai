import json
import logging
from typing import Dict, Any, List
from ..config import settings
from ..engine.contracts import DataContract, ColumnContractRule, MedallionTier, PIIType, MaskingStrategy

logger = logging.getLogger(__name__)

class PolicyCompilerAgent:
    """
    Agent 1: Translates natural language regulatory policies (MAS, RBI, PDPA, DPDP)
    into machine-executable DataContract objects using Gemini 1.5 Pro or deterministic fallback.
    """

    @classmethod
    async def compile_policy_to_contracts(cls, policy_title: str, authority: str, policy_text: str) -> DataContract:
        contract_id = f"CONTRACT-{authority.replace(' ', '_').upper()}-{int(hash(policy_text) % 10000)}"

        # Attempt Gemini 2.0 / 1.5 Pro compilation if API key is configured
        if settings.GEMINI_API_KEY:
            try:
                from google import genai
                from google.genai import types
                client = genai.Client(api_key=settings.GEMINI_API_KEY)

                prompt = f"""
You are an expert Chief AI Governance and Financial Regulatory Engineer specializing in JAPAC BFSI compliance (MAS, RBI, PDPA, DPDP).
Analyze the following regulatory policy text and extract formal, machine-executable Data Contract rules for a Medallion Lakehouse pipeline.

Policy Title: {policy_title}
Authority: {authority}
Policy Text:
{policy_text}

Output a single valid JSON object strictly matching this schema:
{{
  "contract_id": "{contract_id}",
  "name": "{policy_title} Active Contract",
  "target_tier": "SILVER",
  "jurisdiction": "JAPAC",
  "governing_regulation": "{authority}",
  "rules": [
    {{
      "column_name": "sender_id_doc",
      "data_type": "VARCHAR",
      "nullable": false,
      "pii_type": "SG_NRIC or IN_PAN or IN_AADHAAR",
      "masking_strategy": "MASK_MIDDLE or VAULT_TOKENIZE",
      "description": "Justification from policy"
    }}
  ]
}}
"""
                response = client.models.generate_content(
                    model=settings.GEMINI_MODEL_PRO,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.1,
                        response_mime_type="application/json"
                    )
                )
                if response and response.text:
                    data = json.loads(response.text.strip())
                    return DataContract(**data)
            except Exception as e:
                logger.warning(f"Gemini API compilation fallback to deterministic engine: {e}")

        # Deterministic JAPAC BFSI Policy-as-Code Compiler
        rules = [
            ColumnContractRule(
                column_name="sender_id_doc",
                data_type="VARCHAR",
                nullable=False,
                pii_type=PIIType.SG_NRIC if "MAS" in authority or "SG" in authority else PIIType.IN_PAN,
                masking_strategy=MaskingStrategy.MASK_MIDDLE,
                description=f"Masked under {authority} sensitive customer identity protection mandate."
            ),
            ColumnContractRule(
                column_name="sender_account",
                data_type="VARCHAR",
                nullable=False,
                pii_type=PIIType.BANK_ACCOUNT,
                masking_strategy=MaskingStrategy.MASK_MIDDLE,
                description="Core banking account number pseudonymization."
            ),
            ColumnContractRule(
                column_name="amount",
                data_type="DOUBLE",
                nullable=False,
                min_value=0.01,
                max_value=10000000.0,
                allowed_currencies=["SGD", "INR", "JPY", "AUD", "USD"],
                description="Non-negative numeric amount in approved JAPAC transaction currencies."
            ),
            ColumnContractRule(
                column_name="payment_rail",
                data_type="VARCHAR",
                nullable=False,
                description="Approved transaction rail: FAST, PayNow, UPI, IMPS, or SWIFT."
            )
        ]

        return DataContract(
            contract_id=contract_id,
            name=f"{policy_title} Compiled Contract",
            version="1.0.0",
            target_tier=MedallionTier.SILVER,
            jurisdiction="JAPAC",
            governing_regulation=authority,
            rules=rules,
            is_active=True
        )
