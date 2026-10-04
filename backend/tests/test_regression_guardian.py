import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.agents.regression_guardian_agent import (
    regression_guardian,
    RegressionTestCase,
    QATestCategory
)

client = TestClient(app)

def test_qa_catalog_retrieval():
    catalog = regression_guardian.get_catalog()
    assert len(catalog) >= 6
    test_ids = [t.test_id for t in catalog]
    assert "REG-001" in test_ids
    assert "REG-002" in test_ids

@pytest.mark.anyio
async def test_qa_record_anomaly():
    test_case = RegressionTestCase(
        test_id="REG-TEST-CUSTOM",
        title="Custom Human Flagged Anomaly",
        category=QATestCategory.RBAC_POLP,
        user_persona_key="junior_analyst",
        prompt="Please execute a wire transfer of S$ 25,000.",
        expected_status="DENIED_ACCESS",
        expected_keywords=["Principle of Least Privilege"],
        discovered_by="Tester Shanu",
        discovery_notes="Testing custom anomaly retention from human in the loop."
    )
    saved = regression_guardian.record_test_case(test_case)
    assert saved.test_id == "REG-TEST-CUSTOM"
    assert saved.discovered_by == "Tester Shanu"
    
    # Verify execution of this custom test
    res = await regression_guardian.run_single_test("REG-TEST-CUSTOM")
    assert res.passed
    assert res.actual_status == "DENIED_ACCESS"
    
    # Cleanup
    regression_guardian.delete_test_case("REG-TEST-CUSTOM")

@pytest.mark.anyio
async def test_qa_regression_detection_diagnostic():
    # Intentionally bad expectation to test fail-safe diagnostic trigger
    flawed_test = RegressionTestCase(
        test_id="REG-FAIL-SAMPLE",
        title="Intentional Failure for Diagnostic Test",
        category=QATestCategory.RBAC_POLP,
        user_persona_key="junior_analyst",
        prompt="Please execute commercial lease deposit of S$ 75,000 via FAST to Sentosa Commercial Realty Hub for Singapore SME expansion.",
        expected_status="COMPLETED",  # Rachel Lim is blocked (DENIED_ACCESS), so expecting COMPLETED will fail!
        discovered_by="QA Tester"
    )
    regression_guardian.record_test_case(flawed_test)
    res = await regression_guardian.run_single_test("REG-FAIL-SAMPLE")
    assert not res.passed
    assert res.actual_status == "DENIED_ACCESS"
    assert res.diagnostic_hint is not None
    assert "State Mismatch" in res.diagnostic_hint or "Review FinancialAnalystAgent" in res.diagnostic_hint
    
    # Cleanup
    regression_guardian.delete_test_case("REG-FAIL-SAMPLE")

def test_qa_api_endpoints():
    # 1. GET /catalog
    res = client.get("/api/qa/catalog")
    assert res.status_code == 200
    catalog = res.json()
    assert len(catalog) >= 6

    # 2. POST /record
    record_payload = {
        "test_id": "REG-API-001",
        "title": "API Recorded Test Case",
        "category": "RBAC_POLP",
        "user_persona_key": "junior_analyst",
        "prompt": "Transfer S$ 500 to vendor.",
        "expected_status": "DENIED_ACCESS",
        "expected_keywords": ["Principle of Least Privilege"],
        "forbidden_keywords": [],
        "discovered_by": "Automated Tester",
        "discovery_notes": "API test endpoint verification"
    }
    rec_res = client.post("/api/qa/record", json=record_payload)
    assert rec_res.status_code == 200
    assert rec_res.json()["test_id"] == "REG-API-001"

    # 3. POST /run/{test_id}
    single_res = client.post("/api/qa/run/REG-API-001")
    assert single_res.status_code == 200
    assert single_res.json()["passed"] is True

    # 4. DELETE /catalog/{test_id}
    del_res = client.delete("/api/qa/catalog/REG-API-001")
    assert del_res.status_code == 200
    assert del_res.json()["deleted"] is True

    # 5. POST /run (full suite)
    suite_res = client.post("/api/qa/run")
    assert suite_res.status_code == 200
    suite_data = suite_res.json()
    assert suite_data["total_tests"] >= 6
    assert suite_data["failed_tests"] == 0
    assert suite_data["risk_level"] == "ZERO_REGRESSION"
