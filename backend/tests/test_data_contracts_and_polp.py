import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.access_control.user_contexts import PREDEFINED_USERS, UserRole
from backend.app.harness.audit_logger import audit_ledger

client = TestClient(app)

def test_data_engineer_persona_registered():
    """Verify Data Engineer persona (Alex Wong) is registered with PoLP clearance"""
    assert "data_engineer" in PREDEFINED_USERS
    de = PREDEFINED_USERS["data_engineer"]
    assert de.role == UserRole.DATA_ENGINEER
    assert "Alex Wong" in de.name
    assert "view_bronze_raw" in de.allowed_actions
    assert "view_silver_masked" in de.allowed_actions
    assert "manage_pipeline_ingestion" in de.allowed_actions

def test_bronze_tier_po_lp_restriction_via_api():
    """Verify PoLP enforcement: non-engineers get 403 Forbidden on Bronze, Data Engineer gets 200 OK"""
    # 1. Unauthenticated or empty persona key -> 403
    res_no_auth = client.get("/api/medallion/tier/BRONZE")
    assert res_no_auth.status_code == 403
    assert "PoLP Data Governance" in res_no_auth.json()["detail"]

    # 2. Junior Analyst -> 403
    res_junior = client.get("/api/medallion/tier/BRONZE?user_persona_key=junior_analyst")
    assert res_junior.status_code == 403
    assert "lacks clearance" in res_junior.json()["detail"]

    # 3. Senior Wealth Advisor -> 403
    res_advisor = client.get("/api/medallion/tier/BRONZE?user_persona_key=wealth_advisor")
    assert res_advisor.status_code == 403

    # 4. Compliance Officer (auditor, not raw data engineer) -> 403
    res_compliance = client.get("/api/medallion/tier/BRONZE?user_persona_key=compliance_officer")
    assert res_compliance.status_code == 403

    # 5. Principal Data Platform Engineer (Alex Wong) -> 200 OK
    res_engineer = client.get("/api/medallion/tier/BRONZE?user_persona_key=data_engineer")
    assert res_engineer.status_code == 200
    records = res_engineer.json()
    assert isinstance(records, list)
    if len(records) > 0:
        # Check that Bronze contains raw unmasked field
        assert "sender_id_doc" in records[0]

def test_silver_and_quarantine_tiers_accessible_to_analysts():
    """Verify curated Silver and Quarantine are accessible to analysts without 403"""
    res_silver = client.get("/api/medallion/tier/SILVER?user_persona_key=junior_analyst")
    assert res_silver.status_code == 200
    silver_records = res_silver.json()
    assert isinstance(silver_records, list)

    res_quarantine = client.get("/api/medallion/tier/QUARANTINE?user_persona_key=junior_analyst")
    assert res_quarantine.status_code == 200
    quarantine_records = res_quarantine.json()
    assert isinstance(quarantine_records, list)

def test_policy_compilation_and_pending_approval():
    """Verify Policy Compiler produces a DataContract starting in PENDING_APPROVAL status"""
    compile_payload = {
        "policy_title": "MAS Notice 644 Cross-Border Fast Contract",
        "authority": "Monetary Authority of Singapore",
        "policy_text": "Financial institutions must ensure customer NRIC and payment IDs are pseudonymized before analytical processing."
    }
    res = client.post("/api/policies/compile", json=compile_payload)
    assert res.status_code == 200
    contract = res.json()

    assert contract["status"] == "PENDING_APPROVAL"
    assert contract["is_active"] is False
    assert len(contract["rules"]) > 0

def test_contract_approval_unauthorized_role_rejected():
    """Verify unauthorized personas cannot approve contracts under SOC 2 CC8.1 Change Management"""
    # Compile a contract first
    compile_payload = {
        "policy_title": "RBI DPDP Data Contract",
        "authority": "Reserve Bank of India",
        "policy_text": "Customer PAN documents must be masked with SHA256 cryptographic hashes."
    }
    compile_res = client.post("/api/policies/compile", json=compile_payload)
    assert compile_res.status_code == 200
    contract_id = compile_res.json()["contract_id"]

    # Junior Analyst tries to approve -> 403
    approve_junior = client.post(
        f"/api/policies/contracts/{contract_id}/approve",
        json={
            "reviewer_id": "usr_sg_014",
            "reviewer_name": "Rachel Lim",
            "reviewer_role": "JUNIOR_ANALYST",
            "remarks": "Attempting unauthorized approval"
        }
    )
    assert approve_junior.status_code == 403
    assert "lacks authority to approve data contracts" in approve_junior.json()["detail"]

    # Data Engineer tries to approve -> 403 (Separation of duties / 4-eyes)
    approve_engineer = client.post(
        f"/api/policies/contracts/{contract_id}/approve",
        json={
            "reviewer_id": "usr_sg_088",
            "reviewer_name": "Alex Wong",
            "reviewer_role": "DATA_ENGINEER",
            "remarks": "Engineering self-approval"
        }
    )
    assert approve_engineer.status_code == 403

def test_contract_approval_authorized_compliance_officer():
    """Verify Compliance Officer can approve and deploy data contracts with lifecycle telemetry and audit logging"""
    # Compile contract
    compile_payload = {
        "policy_title": "MAS & RBI Harmonized Core Contract",
        "authority": "MAS & RBI",
        "policy_text": "Full tokenization of identity docs and strict negative amount quarantine."
    }
    compile_res = client.post("/api/policies/compile", json=compile_payload)
    assert compile_res.status_code == 200
    contract_id = compile_res.json()["contract_id"]

    initial_audit_count = len(audit_ledger._chain)

    # Compliance Officer approves
    approve_res = client.post(
        f"/api/policies/contracts/{contract_id}/approve",
        json={
            "reviewer_id": "usr_sg_002",
            "reviewer_name": "Priya Sharma",
            "reviewer_role": "COMPLIANCE_OFFICER",
            "remarks": "Approved and validated against Singapore MAS Notice 644 standards."
        }
    )
    assert approve_res.status_code == 200
    approved_contract = approve_res.json()

    assert approved_contract["status"] == "ACTIVE_ENFORCING"
    assert approved_contract["is_active"] is True
    assert "Priya Sharma (COMPLIANCE_OFFICER)" in approved_contract["approved_by"]
    assert approved_contract["approved_at"] is not None

    # Verify lifecycle telemetry
    telemetry = approved_contract.get("lifecycle_telemetry")
    assert telemetry is not None
    assert telemetry["cycle_status"] == "SUCCESS"
    assert "pipeline_summary" in telemetry
    assert "gold_certified_metrics" in telemetry
    assert telemetry["compliance_remarks"] == "Approved and validated against Singapore MAS Notice 644 standards."

    # Verify audit ledger recorded the cryptographic deployment event
    assert len(audit_ledger._chain) > initial_audit_count
    latest_event = audit_ledger._chain[-1]
    assert latest_event.event_type == "DATA_CONTRACT_APPROVED_AND_DEPLOYED"
    assert latest_event.role == "COMPLIANCE_OFFICER"
    assert contract_id in latest_event.action_or_prompt
