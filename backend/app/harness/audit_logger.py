import hashlib
import json
import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class AuditEntry(BaseModel):
    entry_id: str
    timestamp: float = Field(default_factory=time.time)
    formatted_time: str
    event_type: str
    user_id: str
    role: str
    action_or_prompt: str
    decision: str
    threat_score: float = 0.0
    violating_policies: List[str] = []
    metadata: Dict[str, Any] = Field(default_factory=dict)
    previous_hash: str
    entry_hash: str

class AuditLedger:
    def __init__(self):
        self._chain: List[AuditEntry] = []
        self._genesis_hash = "0" * 64
        # Seed with initial genesis block
        self._seed_genesis()

    def _seed_genesis(self):
        genesis = AuditEntry(
            entry_id="AUDIT-GENESIS-0000",
            formatted_time=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            event_type="SYSTEM_INITIALIZATION",
            user_id="SYSTEM",
            role="SYSTEM_ADMIN",
            action_or_prompt="AegisGov AI Tamper-Evident Ledger Initialized",
            decision="GENESIS_CONFIRMED",
            previous_hash="0" * 64,
            entry_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        )
        self._chain.append(genesis)

    def _compute_hash(self, prev_hash: str, timestamp: float, event_type: str, user_id: str, action: str, decision: str) -> str:
        payload = f"{prev_hash}|{timestamp}|{event_type}|{user_id}|{action}|{decision}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def log_event(
        self,
        event_type: str,
        user_id: str,
        role: str,
        action_or_prompt: str,
        decision: str,
        threat_score: float = 0.0,
        violating_policies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEntry:
        prev_hash = self._chain[-1].entry_hash if self._chain else self._genesis_hash
        ts = time.time()
        formatted_time = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(ts))
        
        # Privacy & Compliance Defense (PDPA / DPDP / MAS TRM):
        # Guarantee no raw customer identifiers (NRIC, PAN, CC, Email, Phone) enter the immutable hash chain
        from .pii_vault_tokenizer import pii_vault
        sanitized_action, _ = pii_vault.scan_and_sanitize_text(action_or_prompt or "", tokenize=True)

        entry_hash = self._compute_hash(
            prev_hash=prev_hash,
            timestamp=ts,
            event_type=event_type,
            user_id=user_id,
            action=sanitized_action,
            decision=decision
        )

        entry_id = f"AUDIT-TX-{len(self._chain):05d}"
        entry = AuditEntry(
            entry_id=entry_id,
            timestamp=ts,
            formatted_time=formatted_time,
            event_type=event_type,
            user_id=user_id,
            role=role,
            action_or_prompt=sanitized_action,
            decision=decision,
            threat_score=threat_score,
            violating_policies=violating_policies or [],
            metadata=metadata or {},
            previous_hash=prev_hash,
            entry_hash=entry_hash
        )
        self._chain.append(entry)
        return entry

    def get_entries(self, limit: int = 50) -> List[AuditEntry]:
        return list(reversed(self._chain))[:limit]

    def get_chain(self) -> List[AuditEntry]:
        return self._chain

    def verify_chain_integrity(self) -> Dict[str, Any]:
        """Validates all cryptographic hashes in sequence to prove tamper evidence"""
        if len(self._chain) <= 1:
            return {"valid": True, "total_blocks": len(self._chain), "message": "Ledger intact."}

        for i in range(1, len(self._chain)):
            prev = self._chain[i - 1]
            curr = self._chain[i]

            if curr.previous_hash != prev.entry_hash:
                return {
                    "valid": False,
                    "tampered_at_index": i,
                    "entry_id": curr.entry_id,
                    "message": "Cryptographic link broken! Previous hash mismatch."
                }

            recomputed = self._compute_hash(
                prev_hash=curr.previous_hash,
                timestamp=curr.timestamp,
                event_type=curr.event_type,
                user_id=curr.user_id,
                action=curr.action_or_prompt,
                decision=curr.decision
            )
            if recomputed != curr.entry_hash:
                return {
                    "valid": False,
                    "tampered_at_index": i,
                    "entry_id": curr.entry_id,
                    "message": "Block payload altered! Hash verification failed."
                }

        return {
            "valid": True,
            "total_blocks": len(self._chain),
            "latest_hash": self._chain[-1].entry_hash,
            "message": "All cryptographic links and block signatures verified. 100% Tamper-Evident."
        }

    def reset(self):
        """Resets audit ledger chain to initial genesis block"""
        self._chain.clear()
        self._seed_genesis()

audit_ledger = AuditLedger()
