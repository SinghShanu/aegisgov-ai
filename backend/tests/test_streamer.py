import pytest
from backend.app.engine.transaction_streamer import transaction_streamer
from backend.app.engine.medallion_lakehouse import medallion_lakehouse
from backend.app.hitl.hitl_manager import hitl_manager
from backend.app.harness.audit_logger import audit_ledger
from backend.app.gcp.gcp_provider import gcp_provider

def test_streamer_compliant_transaction():
    initial_silver = medallion_lakehouse.get_gold_analytics()["total_certified_transactions"]
    ev = transaction_streamer.generate_single(force_category="COMPLIANT")
    assert ev["status"] == "SILVER_PROMOTED"
    assert ev["payment_rail"] in ["FAST", "PAYNOW", "UPI", "IMPS", "SWIFT"]
    new_silver = medallion_lakehouse.get_gold_analytics()["total_certified_transactions"]
    assert new_silver == initial_silver + 1

def test_streamer_high_value_hitl_trigger():
    initial_hitl = len(hitl_manager.list_tickets())
    ev = transaction_streamer.generate_single(force_category="HIGH_VALUE_HITL")
    assert ev["status"] == "HITL_TRIGGERED"
    assert "ticket_id" in ev
    new_hitl = len(hitl_manager.list_tickets())
    assert new_hitl == initial_hitl + 1

def test_streamer_malicious_quarantine_trigger():
    initial_quarantine = len(medallion_lakehouse.quarantine_vault)
    ev = transaction_streamer.generate_single(force_category="MALICIOUS_QUARANTINE")
    assert ev["status"] == "QUARANTINED"
    assert "threat_type" in ev
    new_quarantine = len(medallion_lakehouse.quarantine_vault)
    assert new_quarantine == initial_quarantine + 1

def test_streamer_burst_generation():
    prev_gen = transaction_streamer.total_generated
    burst = transaction_streamer.generate_burst(count=5)
    assert len(burst) == 5
    assert transaction_streamer.total_generated == prev_gen + 5

def test_gcp_architecture_matrix():
    overview = gcp_provider.get_overview()
    assert overview.project_id == "aegisgov-ai-2026"
    assert overview.region == "asia-southeast1"
    assert len(overview.services) >= 7
    service_names = [s.service_name for s in overview.services]
    assert any("Vertex AI" in s for s in service_names)
    assert any("BigQuery" in s for s in service_names)
    assert any("Pub/Sub" in s for s in service_names)
    assert any("DLP" in s for s in service_names)

def test_streamer_scenario_burst():
    mule_res = transaction_streamer.trigger_scenario_burst("MULE_FRAUD_SURGE")
    assert mule_res["scenario"] == "MULE_FRAUD_SURGE"
    assert "Scam Restitution" in mule_res["roi_impact"]
    assert mule_res["events_generated"] == 7

    lending_res = transaction_streamer.trigger_scenario_burst("HIGH_VALUE_LENDING")
    assert lending_res["scenario"] == "HIGH_VALUE_LENDING"
    assert "Dual-Control" in lending_res["roi_impact"]
    assert lending_res["events_generated"] == 5
