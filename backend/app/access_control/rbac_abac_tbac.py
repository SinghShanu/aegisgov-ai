import time
from typing import Optional, List
from pydantic import BaseModel
from .user_contexts import UserContext, SecurityClearance, Jurisdiction, UserRole

CLEARANCE_HIERARCHY = {
    SecurityClearance.INTERNAL: 1,
    SecurityClearance.CONFIDENTIAL: 2,
    SecurityClearance.RESTRICTED: 3,
    SecurityClearance.SECRET: 4
}

class AccessDecision(BaseModel):
    allowed: bool
    status: str  # "GRANTED", "DENIED_RBAC", "DENIED_ABAC_CLEARANCE", "DENIED_ABAC_JURISDICTION", "DENIED_TBAC_EXPIRED", "DENIED_LIMIT_EXCEEDED"
    reason: str
    violating_policy: Optional[str] = None
    polp_enforced: bool = True
    audit_tags: List[str] = []

class AccessController:
    @staticmethod
    def evaluate_access(
        user: UserContext,
        action: str,
        resource_clearance: SecurityClearance = SecurityClearance.INTERNAL,
        resource_jurisdiction: Optional[Jurisdiction] = None,
        transaction_amount_sgd: float = 0.0,
        transaction_amount_inr: float = 0.0
    ) -> AccessDecision:
        audit_tags = [f"role:{user.role}", f"clearance:{user.clearance}", f"action:{action}"]

        # 1. TBAC Check (Time / Token Expiration)
        current_time = time.time()
        time_elapsed = current_time - user.token_issued_at
        if time_elapsed > user.token_ttl_seconds:
            return AccessDecision(
                allowed=False,
                status="DENIED_TBAC_EXPIRED",
                reason=f"Session token {user.session_token} expired ({int(time_elapsed)}s > {user.token_ttl_seconds}s). Re-authentication required under PoLP.",
                violating_policy="TBAC-SEC-004: Ephemeral Session Token TTL Exceeded",
                audit_tags=audit_tags + ["tbac_violation"]
            )

        # 2. RBAC Check (Role Entitlement)
        if action not in user.allowed_actions:
            return AccessDecision(
                allowed=False,
                status="DENIED_RBAC",
                reason=f"Role '{user.role}' lacks explicit privilege for action '{action}'. Enforcing Principle of Least Privilege.",
                violating_policy="RBAC-FIN-012: Unauthorized Action Privileges",
                audit_tags=audit_tags + ["rbac_denial"]
            )

        # 3. ABAC Check: Security Clearance
        user_clearance_score = CLEARANCE_HIERARCHY.get(user.clearance, 0)
        req_clearance_score = CLEARANCE_HIERARCHY.get(resource_clearance, 0)
        if user_clearance_score < req_clearance_score:
            return AccessDecision(
                allowed=False,
                status="DENIED_ABAC_CLEARANCE",
                reason=f"Insufficient security clearance ({user.clearance} < required {resource_clearance}). Access denied.",
                violating_policy="ABAC-DATA-007: Classification Clearance Mismatch",
                audit_tags=audit_tags + ["clearance_denial"]
            )

        # 4. ABAC Check: Jurisdiction Boundary (Cross-Border Data Restriction)
        if resource_jurisdiction and resource_jurisdiction != Jurisdiction.GLOBAL:
            if user.jurisdiction != Jurisdiction.GLOBAL and user.jurisdiction != resource_jurisdiction:
                return AccessDecision(
                    allowed=False,
                    status="DENIED_ABAC_JURISDICTION",
                    reason=f"Cross-border data protection violation: User jurisdiction '{user.jurisdiction}' cannot access '{resource_jurisdiction}' localized data under PDPA / DPDP guidelines.",
                    violating_policy="ABAC-GEO-003: Cross-Border Sovereignty Lock",
                    audit_tags=audit_tags + ["jurisdiction_denial"]
                )

        # 5. Financial Limit Verification (PoLP Threshold)
        if transaction_amount_sgd > user.max_transaction_limit_sgd:
            return AccessDecision(
                allowed=False,
                status="DENIED_LIMIT_EXCEEDED",
                reason=f"Transaction value S$ {transaction_amount_sgd:,.2f} exceeds user role limit of S$ {user.max_transaction_limit_sgd:,.2f}.",
                violating_policy="FIN-LIMIT-001: Role-Based Transaction Limit Exceeded",
                audit_tags=audit_tags + ["limit_exceeded"]
            )

        if transaction_amount_inr > user.max_transaction_limit_inr:
            return AccessDecision(
                allowed=False,
                status="DENIED_LIMIT_EXCEEDED",
                reason=f"Transaction value ₹ {transaction_amount_inr:,.2f} exceeds user role limit of ₹ {user.max_transaction_limit_inr:,.2f}.",
                violating_policy="FIN-LIMIT-002: Role-Based INR Transaction Limit Exceeded",
                audit_tags=audit_tags + ["limit_exceeded"]
            )

        return AccessDecision(
            allowed=True,
            status="GRANTED",
            reason="Access verified under RBAC/ABAC/TBAC policies and Principle of Least Privilege.",
            audit_tags=audit_tags + ["access_granted"]
        )
