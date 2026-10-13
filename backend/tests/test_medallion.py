import pytest
from backend.app.engine.medallion_lakehouse import medallion_lakehouse
from backend.app.engine.contracts import DataContract, MedallionTier

def test_medallion_pipeline_execution():
    test_records = [
        {
            "transaction_id": "TX-TEST-001",
            "timestamp": "2026-09-20T10:00:00Z",
            "sender_id": "SND-1",
            "sender_name": "Test User",
            "sender_id_doc": "S1234567A",
            "sender_account": "DBS-1111",
            "recipient_id": "REC-1",
            "recipient_name": "Test Recipient",
            "recipient_account": "OCBC-2222",
            "amount": 250.0,
            "currency": "SGD",
            "payment_rail": "PayNow",
            "purpose": "Test"
        },
        {
            "transaction_id": "TX-TEST-BAD-002",
            "timestamp": "2026-09-20T10:00:00Z",
            "sender_id": "SND-2",
            "sender_name": "Bad User",
            "sender_id_doc": "BAD-DOC",
            "sender_account": "ACC-000",
            "recipient_id": "REC-2",
            "recipient_name": "Bad Rec",
            "recipient_account": "ACC-999",
            "amount": -100.0,  # Negative! Should be quarantined
            "currency": "SGD",
            "payment_rail": "FAST",
            "purpose": "Bad Amount"
        }
    ]

    medallion_lakehouse.ingest_bronze(test_records)
    summary = medallion_lakehouse.run_medallion_processing()

    assert summary["status"] == "COMPLETED"
    assert summary["quarantined"] >= 1
    assert summary["silver_promoted"] >= 1

    silver_data = medallion_lakehouse.get_tier_data("SILVER")
    # Verify NRIC is masked
    matched = [r for r in silver_data if r["transaction_id"] == "TX-TEST-001"]
    assert len(matched) == 1
    assert matched[0]["sender_id_doc_masked"] != "S1234567A"
    assert "****" in matched[0]["sender_id_doc_masked"]

    gold_analytics = medallion_lakehouse.get_gold_analytics()
    assert gold_analytics["total_certified_transactions"] >= 1
    assert gold_analytics["total_volume_sgd"] > 0
    assert gold_analytics["capital_safeguarded_sgd"] > 0
    assert gold_analytics["hitl_dual_custody_compliance_rate"] == 100.0
    assert "executive_leadership_summary" in gold_analytics


def test_gold_tier_datamart_and_executive_attestation():
    from fastapi.testclient import TestClient
    from backend.app.main import app

    client = TestClient(app)

    # 1. Test GET /api/medallion/tier/GOLD
    gold_res = client.get("/api/medallion/tier/GOLD")
    assert gold_res.status_code == 200
    marts = gold_res.json()
    assert isinstance(marts, list)
    assert len(marts) >= 1
    first_mart = marts[0]
    assert "payment_rail" in first_mart
    assert "rail_volume_sgd" in first_mart
    assert "mas_compliance_status" in first_mart
    assert "rbi_compliance_status" in first_mart
    assert "pii_protection_sla" in first_mart

    # 2. Test GET /api/medallion/executive-attestation
    attest_res = client.get("/api/medallion/executive-attestation")
    assert attest_res.status_code == 200
    attest_data = attest_res.json()
    assert "attestation_id" in attest_data
    assert attest_data["auditor_attestation_seal"] == "AEGISGOV-GOLD-SHA256-CERTIFIED"
    assert len(attest_data["cryptographic_sha256_hash"]) == 64
    assert "governance_frameworks" in attest_data
    assert attest_data["governance_frameworks"]["mas_feat_fairness_principles"] == "CERTIFIED_AUDIT_READY"
    assert attest_data["gold_datamart_state"]["hitl_dual_custody_compliance_rate"] == 100.0

