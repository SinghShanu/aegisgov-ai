import pytest
from backend.app.hitl.hitl_manager import hitl_manager
from backend.app.hitl.hitl_schema import HITLTriggerType, HITLTicketStatus, HITLDecisionRequest

def test_hitl_ticket_creation():
    ticket = hitl_manager.create_ticket(
        trigger_type=HITLTriggerType.HIGH_VALUE_FINANCIAL_ACTION,
        requester_id="usr_test_01",
        requester_name="Test Banker",
        requester_role="WEALTH_ADVISOR",
        requester_jurisdiction="SG",
        description="High value test transfer",
        proposed_action="Transfer S$ 30,000 via FAST",
        amount_sgd=30000.0,
        risk_score=0.75
    )
    assert ticket.ticket_id.startswith("HITL-SG-")
    assert ticket.status == HITLTicketStatus.PENDING

def test_hitl_resolution_unauthorized_role():
    # Junior Analyst cannot approve HITL ticket
    req = HITLDecisionRequest(
        ticket_id="HITL-SG-1092",
        reviewer_id="usr_junior",
        reviewer_name="Junior Staff",
        reviewer_role="JUNIOR_ANALYST",
        decision=HITLTicketStatus.APPROVED,
        remarks="Approved by junior"
    )
    with pytest.raises(PermissionError):
        hitl_manager.resolve_ticket(req)

def test_hitl_resolution_authorized_risk_officer():
    req = HITLDecisionRequest(
        ticket_id="HITL-SG-1092",
        reviewer_id="usr_risk_01",
        reviewer_name="Kenji Sato",
        reviewer_role="RISK_OFFICER",
        decision=HITLTicketStatus.APPROVED,
        remarks="Verified against customer corporate credit line."
    )
    resolved = hitl_manager.resolve_ticket(req)
    assert resolved.status == HITLTicketStatus.APPROVED
    assert "Kenji Sato" in resolved.reviewed_by

@pytest.mark.anyio
async def test_hitl_dual_authorized_settlement_and_replay_protection():
    from backend.app.access_control.user_contexts import PREDEFINED_USERS
    from backend.app.agents.financial_analyst_agent import FinancialAnalystAgent

    vikram = PREDEFINED_USERS["wealth_advisor"]
    priya = PREDEFINED_USERS["compliance_officer"]
    prompt = "Please execute commercial lease deposit of S$ 75,000 via FAST to Sentosa Commercial Realty Hub for Singapore SME expansion."

    # 1. Initial attempt triggers HITL ticket
    resp1 = await FinancialAnalystAgent.process_prompt(vikram, prompt)
    assert resp1.status == "PENDING_HITL_APPROVAL"
    ticket_id = resp1.hitl_ticket_id
    assert ticket_id is not None

    # 2. Immediate retry while still pending (deduplication)
    resp2 = await FinancialAnalystAgent.process_prompt(vikram, prompt)
    assert resp2.status == "PENDING_HITL_APPROVAL"
    assert "ALREADY pending review" in resp2.reply
    assert resp2.hitl_ticket_id == ticket_id

    # 3. Compliance Officer approves ticket
    hitl_manager.resolve_ticket(HITLDecisionRequest(
        ticket_id=ticket_id,
        reviewer_id=priya.user_id,
        reviewer_name=priya.name,
        reviewer_role=priya.role.value,
        decision=HITLTicketStatus.APPROVED,
        remarks="Approved under MAS Notice 644."
    ))

    # 4. Wealth Advisor retries prompt after approval -> SETTLED & COMPLETED!
    resp3 = await FinancialAnalystAgent.process_prompt(vikram, prompt)
    assert resp3.status == "COMPLETED"
    assert "Dual-Authorization Verified" in resp3.reply
    assert "SETTLED" in resp3.reply
    assert ticket_id in resp3.reply

    # 5. Re-executing settled transaction triggers Replay Protection
    resp4 = await FinancialAnalystAgent.process_prompt(vikram, prompt)
    assert resp4.status == "COMPLETED"
    assert "Replay Protection Active" in resp4.reply

    # Cleanup ticket
    hitl_manager._tickets.pop(ticket_id, None)
