import pytest
import time
from backend.app.access_control.user_contexts import PREDEFINED_USERS, UserContext, UserRole, SecurityClearance, Jurisdiction
from backend.app.access_control.rbac_abac_tbac import AccessController

def test_junior_analyst_polp_rbac_denial():
    user = PREDEFINED_USERS["junior_analyst"]
    # Action not in allowed_actions
    decision = AccessController.evaluate_access(user, action="execute_funds_transfer")
    assert not decision.allowed
    assert decision.status == "DENIED_RBAC"
    assert "RBAC-FIN-012" in decision.violating_policy

def test_wealth_advisor_financial_limit_exceeded():
    user = PREDEFINED_USERS["wealth_advisor"]
    # Limit is S$ 10,000, requesting S$ 25,000
    decision = AccessController.evaluate_access(
        user,
        action="initiate_payment_order",
        transaction_amount_sgd=25000.00
    )
    assert not decision.allowed
    assert decision.status == "DENIED_LIMIT_EXCEEDED"

def test_abac_jurisdiction_mismatch():
    user = PREDEFINED_USERS["wealth_advisor"]  # Jurisdiction: IN
    # Requesting SG-locked data
    decision = AccessController.evaluate_access(
        user,
        action="view_gold_metrics",
        resource_jurisdiction=Jurisdiction.SG
    )
    assert not decision.allowed
    assert decision.status == "DENIED_ABAC_JURISDICTION"

def test_tbac_session_expiration():
    expired_user = UserContext(
        user_id="usr_test_expired",
        name="Expired User",
        role=UserRole.JUNIOR_ANALYST,
        clearance=SecurityClearance.INTERNAL,
        jurisdiction=Jurisdiction.SG,
        allowed_actions=["view_gold_metrics"],
        max_transaction_limit_sgd=100.0,
        max_transaction_limit_inr=5000.0,
        session_token="tok_expired",
        token_issued_at=time.time() - 3600,  # 1 hour ago
        token_ttl_seconds=1800               # 30 mins TTL
    )
    decision = AccessController.evaluate_access(expired_user, action="view_gold_metrics")
    assert not decision.allowed
    assert decision.status == "DENIED_TBAC_EXPIRED"
