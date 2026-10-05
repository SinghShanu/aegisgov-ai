import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from .pii_vault_tokenizer import pii_vault

class EgressInspectionResult(BaseModel):
    passed: bool
    sanitized_output: str
    hallucination_detected: bool
    grounding_score: float  # 0.0 to 1.0 (1.0 = fully grounded in Gold data)
    bias_or_policy_violations: List[str]
    leaked_secrets_intercepted: List[str]
    audit_notes: str

class EgressGuard:
    SECRET_PATTERNS = [
        (re.compile(r'AIza[0-9A-Za-z-_]{35}'), "GOOGLE_API_KEY"),
        (re.compile(r'sk-[a-zA-Z0-9]{32,}'), "OPENAI_OR_SERVICE_KEY"),
        (re.compile(r'-----BEGIN\s+PRIVATE\s+KEY-----'), "RSA_PRIVATE_KEY"),
        (re.compile(r'postgres://|mysql://|mongodb(\+srv)?://[^\s]+'), "DATABASE_CONNECTION_STRING"),
    ]

    SYSTEM_PROMPT_CANARY_PATTERNS = [
        (re.compile(r'CONFIDENTIALITY\s*&\s*SECURITY\s*DIRECTIVES', re.IGNORECASE), "SYSTEM_PROMPT_DIRECTIVES_LEAK"),
        (re.compile(r'Ground\s+Truth\s+Certified\s+Gold\s+Metrics:', re.IGNORECASE), "INTERNAL_PROMPT_CANARY_LEAK"),
        (re.compile(r'You\s+are\s+AegisGov\s+Copilot,\s+an\s+enterprise\s+financial\s+assistant', re.IGNORECASE), "SYSTEM_PERSONA_INSTRUCTION_LEAK"),
        (re.compile(r'system\s+instruction(s)?:', re.IGNORECASE), "SYSTEM_INSTRUCTION_PREFIX_LEAK"),
    ]

    UNLICENSED_ADVICE_TRIGGERS = [
        (re.compile(r'I\s+guarantee\s+you\s+will\s+make\s+\d+%', re.IGNORECASE), "GUARANTEED_RETURN_PROHIBITED"),
        (re.compile(r'you\s+must\s+immediately\s+invest\s+all\s+your\s+funds', re.IGNORECASE), "UNSUITABLE_FINANCIAL_ADVICE"),
        (re.compile(r'exclude\s+applicants\s+based\s+on\s+(race|gender|nationality|religion)', re.IGNORECASE), "MAS_FEAT_BIAS_VIOLATION"),
    ]

    @classmethod
    def inspect(cls, raw_output: str, certified_facts: Optional[List[str]] = None) -> EgressInspectionResult:
        sanitized = raw_output
        violations = []
        leaks = []

        # 1. Secret & Key Leak Interception
        for regex, tag in cls.SECRET_PATTERNS:
            if regex.search(sanitized):
                leaks.append(tag)
                sanitized = regex.sub("[REDACTED_CREDENTIAL_KEY]", sanitized)

        # 1b. System Prompt Leak & Canary Interception
        for regex, tag in cls.SYSTEM_PROMPT_CANARY_PATTERNS:
            if regex.search(sanitized):
                leaks.append(tag)
                sanitized = regex.sub("[REDACTED_SYSTEM_INSTRUCTION]", sanitized)

        # 2. PII Interception
        sanitized, pii_detected = pii_vault.scan_and_sanitize_text(sanitized, tokenize=False)
        if pii_detected:
            violations.append(f"Unmasked PII detected in output ({len(pii_detected)} occurrences masked)")

        # 3. MAS FEAT & Regulatory Advice Check
        for regex, violation_tag in cls.UNLICENSED_ADVICE_TRIGGERS:
            if regex.search(sanitized):
                violations.append(violation_tag)

        # 4. Grounding & Hallucination Assessment
        grounding_score = 0.95
        hallucination_detected = False
        if certified_facts:
            # Check overlap with certified gold facts
            grounded_count = sum(1 for fact in certified_facts if fact.lower() in sanitized.lower())
            if len(certified_facts) > 0 and grounded_count == 0:
                grounding_score = 0.40
                hallucination_detected = True
                violations.append("LOW_FACTUAL_GROUNDING: Output lacks alignment with verified Gold facts")

        passed = len(leaks) == 0 and not any("BIAS_VIOLATION" in v for v in violations)

        return EgressInspectionResult(
            passed=passed,
            sanitized_output=sanitized,
            hallucination_detected=hallucination_detected,
            grounding_score=grounding_score,
            bias_or_policy_violations=violations,
            leaked_secrets_intercepted=leaks,
            audit_notes="Egress inspection completed under MAS FEAT and privacy guardrails."
        )
