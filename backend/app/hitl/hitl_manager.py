import time
from typing import Dict, List, Optional
from .hitl_schema import HITLTicket, HITLTicketStatus, HITLTriggerType, HITLDecisionRequest
from ..harness.audit_logger import audit_ledger
from ..engine.japac_currency import JAPACCurrencyEngine

class HITLManager:
    def __init__(self):
        self._tickets: Dict[str, HITLTicket] = {}
        self._counter: int = 1094
        self._seed_sample_tickets()

    def _seed_sample_tickets(self):
        t1 = HITLTicket(
            ticket_id="HITL-SG-1092",
            created_at=time.time() - 300,
            formatted_time=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(time.time() - 300)),
            trigger_type=HITLTriggerType.HIGH_VALUE_FINANCIAL_ACTION,
            requester_id="usr_in_082",
            requester_name="Vikram Mehta",
            requester_role="WEALTH_ADVISOR",
            requester_jurisdiction="SG",
            description="Autonomous agent requested cross-border payment exceeding single-agent operational limits.",
            proposed_action="Execute corporate supplier FAST transfer of S$ 45,000.00 to DBS Account SG-88192",
            amount_sgd=45000.00,
            amount_inr=JAPACCurrencyEngine.to_inr(45000.00),
            payload={
                "beneficiary": "Apex Maritime Logistics Pte Ltd",
                "bank_code": "DBS-SG-01",
                "payment_rail": "FAST",
                "currency": "SGD",
                "purpose": "Commercial Invoice #INV-2026-8819"
            },
            risk_score=0.78,
            risk_summary="Amount exceeds autonomous threshold (S$ 10,000). Mandates Four-Eyes Principle approval under MAS Notice 644.",
            status=HITLTicketStatus.PENDING
        )

        t2 = HITLTicket(
            ticket_id="HITL-IN-1093",
            created_at=time.time() - 120,
            formatted_time=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(time.time() - 120)),
            trigger_type=HITLTriggerType.SENSITIVE_DATA_UNMASKING,
            requester_id="usr_sg_014",
            requester_name="Rachel Lim",
            requester_role="JUNIOR_ANALYST",
            requester_jurisdiction="IN",
            description="Attempt to unmask and export Aadhaar and PAN documents for retail borrowers.",
            proposed_action="Export unmasked KYC records for loan cohort IN-Q3-2026",
            amount_sgd=0.0,
            amount_inr=0.0,
            payload={
                "target_table": "borrower_kyc_silver",
                "columns_requested": ["full_name", "aadhaar_number", "pan_card", "annual_income"],
                "export_format": "CSV"
            },
            risk_score=0.92,
            risk_summary="Direct PII unmasking violation under India DPDP Act 2023 & RBI Digital Lending Guidelines. Requires Compliance Officer sign-off.",
            status=HITLTicketStatus.PENDING
        )

        self._tickets[t1.ticket_id] = t1
        self._tickets[t2.ticket_id] = t2

    def create_ticket(
        self,
        trigger_type: HITLTriggerType,
        requester_id: str,
        requester_name: str,
        requester_role: str,
        requester_jurisdiction: str,
        description: str,
        proposed_action: str,
        amount_sgd: float = 0.0,
        amount_inr: float = 0.0,
        payload: Optional[Dict] = None,
        risk_score: float = 0.5,
        risk_summary: str = ""
    ) -> HITLTicket:
        ticket_id = f"HITL-{requester_jurisdiction.upper()}-{self._counter}"
        self._counter += 1
        ts = time.time()
        ticket = HITLTicket(
            ticket_id=ticket_id,
            created_at=ts,
            formatted_time=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(ts)),
            trigger_type=trigger_type,
            requester_id=requester_id,
            requester_name=requester_name,
            requester_role=requester_role,
            requester_jurisdiction=requester_jurisdiction,
            description=description,
            proposed_action=proposed_action,
            amount_sgd=amount_sgd,
            amount_inr=amount_inr or JAPACCurrencyEngine.to_inr(amount_sgd),
            payload=payload or {},
            risk_score=risk_score,
            risk_summary=risk_summary,
            status=HITLTicketStatus.PENDING
        )
        self._tickets[ticket_id] = ticket

        # Log to tamper-evident audit ledger
        audit_entry = audit_ledger.log_event(
            event_type="HITL_TICKET_GENERATED",
            user_id=requester_id,
            role=requester_role,
            action_or_prompt=proposed_action,
            decision="PENDING_HUMAN_APPROVAL",
            threat_score=risk_score,
            violating_policies=["HITL-GATE-001: Four-Eyes Principle Mandate"],
            metadata={"ticket_id": ticket_id, "trigger_type": trigger_type.value}
        )
        ticket.audit_entry_id = audit_entry.entry_id
        return ticket

    def list_tickets(self, status: Optional[HITLTicketStatus] = None) -> List[HITLTicket]:
        tickets = list(self._tickets.values())
        if status:
            tickets = [t for t in tickets if t.status == status]
        return sorted(tickets, key=lambda x: x.created_at, reverse=True)

    def resolve_ticket(self, decision_req: HITLDecisionRequest) -> HITLTicket:
        ticket = self._tickets.get(decision_req.ticket_id)
        if not ticket:
            raise KeyError(f"Ticket {decision_req.ticket_id} not found.")

        # Enforce that only Compliance or Risk Officer can approve HITL tickets
        if decision_req.reviewer_role not in ["COMPLIANCE_OFFICER", "RISK_OFFICER", "SYSTEM_ADMIN"]:
            raise PermissionError(f"Role '{decision_req.reviewer_role}' unauthorized to resolve HITL tickets. Four-Eyes violation.")

        ticket.status = decision_req.decision
        ticket.reviewed_by = f"{decision_req.reviewer_name} ({decision_req.reviewer_role})"
        ticket.reviewed_at = time.time()
        ticket.review_remarks = decision_req.remarks

        # Log resolution to audit ledger
        audit_ledger.log_event(
            event_type="HITL_TICKET_RESOLVED",
            user_id=decision_req.reviewer_id,
            role=decision_req.reviewer_role,
            action_or_prompt=f"Ticket {ticket.ticket_id} marked as {decision_req.decision.value}",
            decision=decision_req.decision.value,
            metadata={
                "ticket_id": ticket.ticket_id,
                "remarks": decision_req.remarks,
                "original_action": ticket.proposed_action
            }
        )
        return ticket

    def find_approved_ticket(
        self,
        requester_id: str,
        amount_sgd: float,
        tolerance: float = 1.0
    ) -> Optional[HITLTicket]:
        """Finds an unconsumed APPROVED ticket matching requester and amount"""
        for t in reversed(list(self._tickets.values())):
            if t.status == HITLTicketStatus.APPROVED and t.requester_id == requester_id:
                if abs(t.amount_sgd - amount_sgd) <= tolerance:
                    return t
        return None

    def find_executed_ticket(
        self,
        requester_id: str,
        amount_sgd: float,
        tolerance: float = 1.0
    ) -> Optional[HITLTicket]:
        """Finds an already EXECUTED/settled ticket to enforce replay/double-spending protection"""
        for t in reversed(list(self._tickets.values())):
            if t.status == HITLTicketStatus.EXECUTED and t.requester_id == requester_id:
                if abs(t.amount_sgd - amount_sgd) <= tolerance:
                    return t
        return None

    def find_pending_ticket(
        self,
        requester_id: str,
        amount_sgd: float,
        tolerance: float = 1.0
    ) -> Optional[HITLTicket]:
        """Finds an active PENDING ticket to prevent duplicate tickets on repeated user prompts"""
        for t in reversed(list(self._tickets.values())):
            if t.status == HITLTicketStatus.PENDING and t.requester_id == requester_id:
                if abs(t.amount_sgd - amount_sgd) <= tolerance:
                    return t
        return None

    def consume_approved_ticket(
        self,
        ticket_id: str,
        executed_by: str
    ) -> HITLTicket:
        """Transitions APPROVED ticket to EXECUTED upon actual payment disbursement"""
        ticket = self._tickets.get(ticket_id)
        if not ticket:
            raise KeyError(f"Ticket {ticket_id} not found.")

        ticket.status = HITLTicketStatus.EXECUTED
        ticket.executed_at = time.time()
        ticket.settlement_ref = f"SETTLE-FAST-{int(time.time()*1000) % 1000000}"

        audit_ledger.log_event(
            event_type="HITL_TICKET_EXECUTED_SETTLED",
            user_id=ticket.requester_id,
            role=ticket.requester_role,
            action_or_prompt=f"Ticket {ticket.ticket_id} executed and settled via FAST rail",
            decision="SETTLED",
            metadata={
                "ticket_id": ticket.ticket_id,
                "approved_by": ticket.reviewed_by,
                "settlement_ref": ticket.settlement_ref,
                "executed_by": executed_by,
                "amount_sgd": ticket.amount_sgd
            }
        )
        return ticket

    def reset(self):
        """Resets all HITL tickets to initial pristine state with baseline demo seeds"""
        self._tickets.clear()
        self._counter = 1094
        self._seed_sample_tickets()

hitl_manager = HITLManager()
