from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..agents.regression_guardian_agent import (
    regression_guardian,
    RegressionTestCase,
    RegressionTestResult,
    RegressionSuiteReport
)

router = APIRouter(prefix="/api/qa", tags=["Regression Guardian & HITL QA Testing"])

@router.get("/catalog", response_model=List[RegressionTestCase])
async def get_test_catalog():
    """Returns all cataloged HITL test cases (baseline + human-flagged anomalies)"""
    return regression_guardian.get_catalog()

@router.post("/record", response_model=RegressionTestCase)
async def record_test_case(test_case: RegressionTestCase):
    """Records an anomaly or edge-case scenario flagged by a human tester"""
    return regression_guardian.record_test_case(test_case)

@router.post("/run", response_model=RegressionSuiteReport)
async def run_full_regression_suite():
    """Executes all cataloged regression tests against the live Sentinel engine and generates a scorecard"""
    return await regression_guardian.run_full_suite()

@router.post("/run/{test_id}", response_model=RegressionTestResult)
async def run_single_test(test_id: str):
    """Executes an individual test case and returns assertion results with diagnostic hints"""
    try:
        return await regression_guardian.run_single_test(test_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/catalog/{test_id}")
async def delete_test_case(test_id: str):
    """Removes a test case from the regression catalog"""
    success = regression_guardian.delete_test_case(test_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Test case '{test_id}' not found.")
    return {"message": f"Test case '{test_id}' deleted successfully.", "deleted": True}

@router.post("/reset", response_model=List[RegressionTestCase])
async def reset_catalog_to_baseline():
    """Resets the catalog to certified enterprise baseline scenarios"""
    return regression_guardian.reset_to_baseline()

@router.get("/history", response_model=List[RegressionSuiteReport])
async def get_test_history():
    """Returns historical regression suite run reports"""
    return regression_guardian.get_history()
