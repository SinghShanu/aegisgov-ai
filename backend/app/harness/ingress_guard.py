import re
from typing import List, Dict, Any
from pydantic import BaseModel
from .pii_vault_tokenizer import pii_vault

class IngressInspectionResult(BaseModel):
    allowed: bool
    threat_score: float  # 0.0 (clean) to 1.0 (critical threat)
    threat_level: str    # "CLEAN", "SUSPICIOUS_HITL_REQUIRED", "BLOCKED_CRITICAL_ATTACK"
    attack_indicators: List[str]
    sanitized_prompt: str
    detected_pii: List[Dict[str, str]]
    escalate_to_hitl: bool = False
    rejection_reason: str = ""

class IngressGuard:
    # Known adversarial heuristics & jailbreak vectors
    INJECTION_PATTERNS = [
        (re.compile(r'(ignore|disregard|forget)\s+(all\s+)?(previous|prior|initial|system)\s+(instructions|prompts|rules|policies|guardrails|safety|security|directives)', re.IGNORECASE), "DIRECT_JAILBREAK_OVERRIDE", 0.85),
        (re.compile(r'system\s+override|admin\s+override|sudo\s+mode|elevate\s+privilege', re.IGNORECASE), "PRIVILEGE_ESCALATION_OVERRIDE", 0.85),
        (re.compile(r'you\s+are\s+now\s+(DAN|unrestricted|godmode|jailbroken|developer\s+mode)', re.IGNORECASE), "ROLEPLAY_JAILBREAK", 0.85),
        (re.compile(r'dump\s+(all\s+)?(tables|schemas|passwords|database|secrets|credentials)', re.IGNORECASE), "DATABASE_EXFILTRATION_ATTACK", 0.85),
        (re.compile(r'(reveal|show|display|print|output|repeat|tell\s+me|what\s+(is|are))\s+(your\s+)?(system\s+prompt|developer\s+instructions|system\s+instructions|hidden\s+rules|internal\s+guidelines|meta\s+prompt)', re.IGNORECASE), "SYSTEM_PROMPT_EXTRACTION", 0.85),
        (re.compile(r'repeat\s+(everything|all|the\s+text|the\s+words)\s+(above|before|previously)', re.IGNORECASE), "SYSTEM_PROMPT_EXTRACTION", 0.85),
        (re.compile(r'bypass\s+(all\s+)?(compliance|guardrails|safety|mas|rbi|controls)', re.IGNORECASE), "COMPLIANCE_BYPASS_ATTACK", 0.85),
        (re.compile(r'base64\s+decode|execute\s+script|<\s*script\s*>', re.IGNORECASE), "CODE_INJECTION_VECTOR", 0.50)
    ]

    @classmethod
    def inspect(cls, raw_prompt: str) -> IngressInspectionResult:
        attack_indicators = []
        threat_score = 0.0

        # 1. Adversarial Pattern Check
        for regex, tag, weight in cls.INJECTION_PATTERNS:
            if regex.search(raw_prompt):
                attack_indicators.append(tag)
                threat_score += weight

        # 2. Heuristic checks for payload anomalies (Context Poisoning / Delimiter Abuse)
        if raw_prompt.count("```") > 4 or raw_prompt.count("<|im_start|>") > 0:
            attack_indicators.append("CONTEXT_DELIMITER_POISONING")
            threat_score += 0.35

        # 3. PII Detection and Tokenization
        sanitized_prompt, pii_detected = pii_vault.scan_and_sanitize_text(raw_prompt, tokenize=True)
        if len(pii_detected) > 3:
            attack_indicators.append("BULK_PII_PROBING")
            threat_score += 0.25

        threat_score = min(threat_score, 1.0)

        # 4. Determine Action Gate
        if threat_score >= 0.8:
            return IngressInspectionResult(
                allowed=False,
                threat_score=threat_score,
                threat_level="BLOCKED_CRITICAL_ATTACK",
                attack_indicators=attack_indicators,
                sanitized_prompt=sanitized_prompt,
                detected_pii=pii_detected,
                escalate_to_hitl=True,
                rejection_reason=f"Security Harness Block: Malicious prompt injection or jailbreak detected ({', '.join(attack_indicators)})."
            )
        elif threat_score >= 0.4:
            return IngressInspectionResult(
                allowed=True,
                threat_score=threat_score,
                threat_level="SUSPICIOUS_HITL_REQUIRED",
                attack_indicators=attack_indicators,
                sanitized_prompt=sanitized_prompt,
                detected_pii=pii_detected,
                escalate_to_hitl=True,
                rejection_reason="Prompt exhibits suspicious injection signals. Routing to Human-in-the-Loop review."
            )
        else:
            return IngressInspectionResult(
                allowed=True,
                threat_score=threat_score,
                threat_level="CLEAN",
                attack_indicators=[],
                sanitized_prompt=sanitized_prompt,
                detected_pii=pii_detected,
                escalate_to_hitl=False,
                rejection_reason=""
            )
