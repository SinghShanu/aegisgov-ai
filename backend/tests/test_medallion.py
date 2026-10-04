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
