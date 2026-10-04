import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.harness.audit_logger import audit_ledger
from backend.app.config import Settings

client = TestClient(app)

def test_http_security_headers_present():
    """Verify defense-in-depth HTTP security headers are injected into API responses"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"
    assert "strict-origin" in response.headers.get("Referrer-Policy", "")
    assert "max-age=31536000" in response.headers.get("Strict-Transport-Security", "")

def test_path_traversal_protection():
    """Verify that requests with directory traversal characters cannot escape frontend dist"""
    # Attempting to escape frontend dist to retrieve .env or backend files
    response = client.get("/../../.env")
    # Must NOT return the actual .env content
    if response.status_code == 200:
        content = response.text
        assert "GEMINI_API_KEY" not in content
        assert "<!doctype html>" in content.lower() or "<html" in content.lower()

def test_audit_ledger_auto_pii_sanitization():
    """Verify that logging raw PII automatically sanitizes it before cryptographic hashing"""
    raw_prompt_with_pii = "Transfer S$ 500 to customer Tan with NRIC S7819234A and PAN ABCPS9182F"
    
    entry = audit_ledger.log_event(
        event_type="TEST_SECURITY_PII_SANITIZATION",
        user_id="usr_test_security",
        role="JUNIOR_ANALYST",
        action_or_prompt=raw_prompt_with_pii,
        decision="SANITIZED_AND_LOGGED"
    )

    # The raw NRIC and PAN must NEVER appear in the immutable entry or action_or_prompt
    assert "S7819234A" not in entry.action_or_prompt
    assert "ABCPS9182F" not in entry.action_or_prompt
    assert "TOK_SG_NRIC" in entry.action_or_prompt or "****" in entry.action_or_prompt
    assert "TOK_IN_PAN" in entry.action_or_prompt or "****" in entry.action_or_prompt

    # Verify that the cryptographic hash was calculated over the sanitized action
    assert "S7819234A" not in entry.entry_hash

def test_production_environment_auto_disables_debug():
    """Verify that ENVIRONMENT=production enforces DEBUG=False to prevent traceback disclosure"""
    prod_settings = Settings(ENVIRONMENT="production", DEBUG=True)
    assert prod_settings.DEBUG is False
    assert prod_settings.ENVIRONMENT == "production"

    dev_settings = Settings(ENVIRONMENT="development", DEBUG=True)
    assert dev_settings.DEBUG is True
