import os
import time
from collections import defaultdict
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from .config import settings
from .routers import (
    policy_router,
    medallion_router,
    harness_router,
    hitl_router,
    audit_router,
    compliance_router,
    stream_router,
    gcp_router,
    qa_router
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="JAPAC BFSI Policy-as-Code, Medallion Guardrails & Agentic AI Safety Harness Platform"
)

# ----------------------------------------------------
# Defense-in-Depth: HTTP Security Headers Middleware
# ----------------------------------------------------
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Server"] = "AegisGov-Secure-Gateway"
    return response

# ----------------------------------------------------
# Defense-in-Depth: In-Memory Rate Limiting & Abuse Prevention
# ----------------------------------------------------
# Protects public Cloud Run endpoint against:
# 1. DDoS / automated billing drain on Gemini API
# 2. Oversized payload memory exhaustion (CWE-400)
RATE_LIMIT_STORE: dict[str, list[float]] = defaultdict(list)
MAX_PAYLOAD_BYTES = 1 * 1024 * 1024  # 1 MB

@app.middleware("http")
async def rate_limit_and_abuse_guard(request: Request, call_next):
    # 1. Payload size guard (CWE-400 / Memory Exhaustion defense)
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > MAX_PAYLOAD_BYTES:
                return JSONResponse(
                    status_code=413,
                    content={"detail": "Payload Too Large. Maximum allowed request size is 1MB."},
                    headers={"Server": "AegisGov-Secure-Gateway"}
                )
        except ValueError:
            pass

    # 2. Rate limiting guard (Bypass for internal pytest test runs unless explicitly tested)
    is_test_client = (
        (not request.client or request.client.host == "testclient")
        and "x-test-rate-limit" not in request.headers
    )

    if not is_test_client:
        forwarded_for = request.headers.get("x-forwarded-for")
        client_ip = forwarded_for.split(",")[0].strip() if forwarded_for else (request.client.host if request.client else "unknown")
        now = time.time()
        path = request.url.path

        # Determine rate limit quota per window (60s)
        if path.startswith("/api/harness/run") or path.startswith("/api/policy/compile"):
            limit = 30  # Heavy AI operations
        elif path.startswith("/api/harness/reset"):
            limit = 10  # State reset
        elif path.startswith("/api/"):
            limit = 120 # General API endpoints
        else:
            limit = None # Static assets

        if limit is not None:
            key = f"{client_ip}:{path.split('?')[0]}"
            timestamps = [t for t in RATE_LIMIT_STORE[key] if now - t < 60.0]
            if len(timestamps) >= limit:
                return JSONResponse(
                    status_code=429,
                    content={"detail": f"Rate limit exceeded. Maximum {limit} requests per minute. Please retry shortly."},
                    headers={"Retry-After": "60", "Server": "AegisGov-Secure-Gateway"}
                )
            timestamps.append(now)
            RATE_LIMIT_STORE[key] = timestamps

            # Memory safety: periodic prune if store grows large
            if len(RATE_LIMIT_STORE) > 2000:
                for k in list(RATE_LIMIT_STORE.keys()):
                    valid = [t for t in RATE_LIMIT_STORE[k] if now - t < 60.0]
                    if valid:
                        RATE_LIMIT_STORE[k] = valid
                    else:
                        del RATE_LIMIT_STORE[k]

    return await call_next(request)

# ----------------------------------------------------
# Hardened CORS Configuration
# ----------------------------------------------------
# In production on Cloud Run, the static SPA and API are co-located on the same origin.
# For local development, allow explicit localhost dev servers.
DEFAULT_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:8088",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:8088",
]

env_origins = os.getenv("CORS_ORIGINS", "").strip()
allowed_origins = [o.strip() for o in env_origins.split(",") if o.strip()] if env_origins else DEFAULT_CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(policy_router.router)
app.include_router(medallion_router.router)
app.include_router(harness_router.router)
app.include_router(hitl_router.router)
app.include_router(audit_router.router)
app.include_router(compliance_router.router)
app.include_router(stream_router.router)
app.include_router(gcp_router.router)
app.include_router(qa_router.router)

@app.get("/api/health")
async def health_check():
    return {
        "status": "HEALTHY",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "base_currency": settings.BASE_CURRENCY,
        "environment": settings.ENVIRONMENT,
        "gemini_model_flash": settings.GEMINI_MODEL_FLASH,
        "gemini_model_pro": settings.GEMINI_MODEL_PRO,
        "gemini_api_configured": bool(settings.GEMINI_API_KEY)
    }

# ----------------------------------------------------
# Production Static SPA Serving with Path Traversal Defense (CWE-22)
# ----------------------------------------------------
frontend_dist_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
if os.path.exists(frontend_dist_path):
    assets_path = os.path.join(frontend_dist_path, "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Resolve target canonical path and prevent directory traversal
        target_path = os.path.abspath(os.path.join(frontend_dist_path, full_path))
        if os.path.normcase(target_path).startswith(os.path.normcase(frontend_dist_path)) and os.path.isfile(target_path):
            return FileResponse(target_path)
        return FileResponse(os.path.join(frontend_dist_path, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
