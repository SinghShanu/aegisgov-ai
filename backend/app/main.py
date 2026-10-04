import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

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
    return response

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
        if target_path.startswith(frontend_dist_path) and os.path.isfile(target_path):
            return FileResponse(target_path)
        return FileResponse(os.path.join(frontend_dist_path, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
