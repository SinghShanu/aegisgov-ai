import pytest
from backend.app.agents.soc2_auditor_agent import SOC2AuditorAgent

def test_soc2_pipeline_scan():
    scan_result = SOC2AuditorAgent.execute_pipeline_scan()
    assert "scan_timestamp" in scan_result
    assert scan_result["status"] in ["HEALTHY", "DRIFT_DETECTED"]
    assert scan_result["silver_unmasked_leaks"] == 0  # No unmasked PII leaks in silver
    assert scan_result["compliance_health_score"] >= 0.0

def test_soc2_report_generation():
    report = SOC2AuditorAgent.generate_soc2_report()
    assert report.report_id.startswith("SOC2-REPORT-")
    assert report.overall_status == "SOC2_TYPE_II_AUDIT_READY"
    assert report.compliance_score > 90.0
    assert len(report.evidence_controls) >= 5

    # Verify essential Trust Services Criteria are covered
    control_ids = [c.control_id for c in report.evidence_controls]
    assert "CC6.1" in control_ids          # Access control (RBAC/ABAC/TBAC & PoLP)
    assert "CC7.2" in control_ids          # Threat monitoring & Ingress guard
    assert "PI1.1" in control_ids          # Processing integrity & Medallion lakehouse
    assert "C1.1" in control_ids           # JAPAC PII Confidentiality
    assert "MAS-FEAT-4.1" in control_ids   # Four-Eyes Principle / High-Value Gate
    assert "CC8.1" in control_ids          # Cryptographic auditability

    # Verify all controls are evaluated as EFFECTIVE
    for c in report.evidence_controls:
        assert c.status == "EFFECTIVE"

    # Verify cryptographic integrity verification is included
    assert report.cryptographic_chain_proof["valid"] is True
