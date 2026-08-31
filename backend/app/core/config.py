"""
PROCUREX Core Configuration
All settings loaded from environment variables with sensible defaults.
"""
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ────────────────────────────────────────────────────────────
    APP_NAME: str = "PROCUREX"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # ── Demo / Simulation ──────────────────────────────────────────────────────
    ENABLE_DEMO_MODE: bool = True
    DEMO_SEED: int = 42

    # ── Security ───────────────────────────────────────────────────────────────
    SECRET_KEY: str = "CHANGE-ME-IN-PRODUCTION-USE-STRONG-RANDOM-KEY"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── Database ───────────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://procurex:procurex@localhost:5432/procurex"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # ── Redis ──────────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # ── Object Storage ─────────────────────────────────────────────────────────
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "procurex"
    MINIO_SECRET_KEY: str = "procurex123"
    MINIO_BUCKET_DOCUMENTS: str = "procurex-documents"
    MINIO_BUCKET_DEMO: str = "procurex-demo"
    MINIO_SECURE: bool = False

    # ── AI Provider ────────────────────────────────────────────────────────────
    AI_PROVIDER: str = "mock"  # "gemini" | "openai" | "ollama" | "mock"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_BASE_URL: Optional[str] = None  # For OpenAI-compatible endpoints
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"

    # ── Embedding ──────────────────────────────────────────────────────────────
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_PROVIDER: str = "sentence_transformers"  # "sentence_transformers" | "openai" | "gemini"
    VECTOR_DIMENSION: int = 384

    # ── Document Processing ────────────────────────────────────────────────────
    MAX_UPLOAD_SIZE_MB: int = 50
    MAX_PAGES_PER_DOCUMENT: int = 500
    OCR_CONFIDENCE_THRESHOLD: float = 0.7
    OCR_ENGINE: str = "pymupdf"  # "pymupdf" | "paddleocr" | "tesseract"
    ENABLE_MALWARE_SCAN: bool = False
    MALWARE_SCAN_ENDPOINT: Optional[str] = None

    # ── Rate Limiting ──────────────────────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 100
    AUTH_RATE_LIMIT_PER_MINUTE: int = 10

    # ── CORS ───────────────────────────────────────────────────────────────────
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:80",
        "http://frontend:3000",
    ]

    # ── Compliance Engine ──────────────────────────────────────────────────────
    DEFAULT_COMPLIANCE_WEIGHTS: dict = {
        "compliance": 0.30,
        "document_integrity": 0.15,
        "verification": 0.15,
        "graph": 0.25,
        "behaviour": 0.15,
    }

    # ── Government Adapters ────────────────────────────────────────────────────
    GST_API_KEY: Optional[str] = None
    GST_API_URL: Optional[str] = None
    MCA_API_KEY: Optional[str] = None
    MCA_API_URL: Optional[str] = None
    UDYAM_API_KEY: Optional[str] = None
    UDYAM_API_URL: Optional[str] = None
    PAN_API_KEY: Optional[str] = None
    PAN_API_URL: Optional[str] = None
    EPFO_API_KEY: Optional[str] = None
    ESIC_API_KEY: Optional[str] = None
    DIGILOCKER_CLIENT_ID: Optional[str] = None
    DIGILOCKER_CLIENT_SECRET: Optional[str] = None
    GEM_API_KEY: Optional[str] = None
    BIS_API_KEY: Optional[str] = None

    # ── Logging ────────────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # "json" | "console"


settings = Settings()
