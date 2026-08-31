"""
PROCUREX Backend - FastAPI Application Entry Point
SIH26100 - AI-Powered Integrated Bid Compliance Verification Platform
"""
import time
import uuid
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import init_db
from app.core.logging import configure_logging
from app.api import (
    auth,
    tenders,
    bidders,
    bids,
    documents,
    verification,
    compliance,
    risk,
    graph,
    policies,
    audit,
    decisions,
    demo,
    health,
    admin,
    dataset,
    processing,
    investigation,
)

configure_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("procurex_startup", version=settings.APP_VERSION, demo_mode=settings.ENABLE_DEMO_MODE)
    await init_db()
    yield
    logger.info("procurex_shutdown")


app = FastAPI(
    title="PROCUREX – Bid Compliance Verification Platform",
    description="SIH26100 · AI-Powered Integrated Bid Compliance Verification for GeM Procurement",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request ID + timing middleware ─────────────────────────────────────────────
@app.middleware("http")
async def request_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time"] = f"{duration_ms}ms"
    logger.debug(
        "http_request",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=duration_ms,
        request_id=request_id,
    )
    return response


# ── Global exception handler ───────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("unhandled_exception", error=str(exc), path=request.url.path, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "request_id": getattr(request.state, "request_id", None)},
    )


# ── API Routers ────────────────────────────────────────────────────────────────
prefix = "/api/v1"

app.include_router(auth.router, prefix=prefix, tags=["Authentication"])
app.include_router(tenders.router, prefix=prefix, tags=["Tenders"])
app.include_router(bidders.router, prefix=prefix, tags=["Bidders"])
app.include_router(bids.router, prefix=prefix, tags=["Bids"])
app.include_router(documents.router, prefix=prefix, tags=["Documents"])
app.include_router(processing.router, prefix=prefix, tags=["Processing Jobs"])
app.include_router(investigation.router, prefix=prefix, tags=["Officer Investigation"])
app.include_router(verification.router, prefix=prefix, tags=["Verification"])
app.include_router(compliance.router, prefix=prefix, tags=["Compliance"])
app.include_router(risk.router, prefix=prefix, tags=["Risk"])
app.include_router(graph.router, prefix=prefix, tags=["Graph"])
app.include_router(policies.router, prefix=prefix, tags=["Policies"])
app.include_router(audit.router, prefix=prefix, tags=["Audit"])
app.include_router(decisions.router, prefix=prefix, tags=["Decisions"])
app.include_router(demo.router, prefix=prefix, tags=["Demo"])
app.include_router(dataset.router, prefix=prefix, tags=["Dataset"])
app.include_router(admin.router, prefix=prefix, tags=["Administration"])
app.include_router(health.router, prefix="", tags=["Health"])


@app.get("/", include_in_schema=False)
async def root():
    return {
        "service": "PROCUREX",
        "tagline": "Verify. Explain. Detect. Decide.",
        "version": settings.APP_VERSION,
        "demo_mode": settings.ENABLE_DEMO_MODE,
        "docs": "/api/docs",
    }
