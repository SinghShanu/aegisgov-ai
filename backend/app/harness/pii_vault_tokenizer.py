import re
import uuid
from typing import Dict, Tuple, List, Optional
from ..engine.contracts import PIIType, MaskingStrategy

class PIITokenVault:
    def __init__(self):
        # Vault structure: token_id -> (original_value, pii_type, timestamp)
        self._vault: Dict[str, Dict[str, str]] = {}

    # Regex patterns for JAPAC and BFSI Identifiers
    PATTERNS = {
        PIIType.SG_NRIC: re.compile(r'\b[STFGM]\d{7}[A-Z]\b', re.IGNORECASE),
        PIIType.IN_PAN: re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', re.IGNORECASE),
        PIIType.IN_AADHAAR: re.compile(r'\b\d{4}\s?\d{4}\s?\d{4}\b'),
        PIIType.CREDIT_CARD: re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
        PIIType.PHONE: re.compile(r'\b(?:\+?(?:65|91)[-\s]?)?[689]\d{7}\b|\b(?:\+?91[-\s]?)?[6789]\d{9}\b'),
        PIIType.EMAIL: re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'),
    }

    def mask_string(self, value: str, strategy: MaskingStrategy, pii_type: PIIType) -> str:
        if not value or strategy == MaskingStrategy.NONE:
            return value

        clean_val = str(value).strip()

        if strategy == MaskingStrategy.FULL_REDACT:
            return f"[REDACTED_{pii_type.value}]"

        elif strategy == MaskingStrategy.MASK_MIDDLE:
            if len(clean_val) <= 4:
                return "****"
            # Keep first 1-2 and last 2-3 characters
            prefix = clean_val[:2]
            suffix = clean_val[-2:]
            return f"{prefix}{'*' * (len(clean_val) - 4)}{suffix}"

        elif strategy == MaskingStrategy.VAULT_TOKENIZE:
            token_id = f"TOK_{pii_type.value}_{uuid.uuid4().hex[:8].upper()}"
            self._vault[token_id] = {
                "original": clean_val,
                "type": pii_type.value
            }
            return f"[{token_id}]"

        return clean_val

    def scan_and_sanitize_text(self, text: str, tokenize: bool = True) -> Tuple[str, List[Dict[str, str]]]:
        """
        Scans free text (e.g. employee prompt or LLM response), replaces detected JAPAC PII
        with vault tokens or masks, and returns the sanitized text + detected entities.
        """
        sanitized = text
        detections = []

        for pii_type, regex in self.PATTERNS.items():
            for match in regex.finditer(text):
                original = match.group(0)
                strategy = MaskingStrategy.VAULT_TOKENIZE if tokenize else MaskingStrategy.MASK_MIDDLE
                masked = self.mask_string(original, strategy, pii_type)
                sanitized = sanitized.replace(original, masked)
                detections.append({
                    "pii_type": pii_type.value,
                    "masked_token": masked
                })

        return sanitized, detections

    def detokenize(self, token_id: str, authorized: bool = False) -> Optional[str]:
        """Detokenization requires explicit security clearance and HITL verification"""
        if not authorized:
            raise PermissionError("Detokenization denied: Unauthorized caller under PoLP.")
        entry = self._vault.get(token_id)
        return entry["original"] if entry else None

pii_vault = PIITokenVault()
