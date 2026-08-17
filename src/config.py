"""
Application Settings — multi-agent-framework-api
=================================================
All configuration is loaded from environment variables (or a .env file in
development). Import `get_settings()` anywhere in the codebase instead of
reading os.environ directly.

Usage:
    from config import get_settings
    settings = get_settings()
    print(settings.llm_provider)
"""
from functools import lru_cache
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── Server ────────────────────────────────────────────────────────────────
    app_env: str = "development"
    """Runtime environment: development | staging | production"""

    api_host: str = "0.0.0.0"
    api_port: int = 8001

    allowed_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://ai-platform-lllm-ui-24286129227.us-central1.run.app"
    ]
    """Comma-separated CORS allowed origins (or a JSON list in the env var)."""

    log_level: str = "info"
    """Uvicorn / Python log level: debug | info | warning | error | critical"""

    # ── Database ──────────────────────────────────────────────────────────────
    database_url: str = "sqlite+aiosqlite:///:memory:"
    """
    SQLAlchemy-compatible async connection string.
    Examples:
      sqlite+aiosqlite:///:memory:                    (default, in-memory async)
      sqlite+aiosqlite:///./data/app.db               (file-based async)
      postgresql+psycopg://user:pass@host:5432/db      (production)
    """

    db_pool_size: int = 10
    db_pool_max_overflow: int = 20
    db_echo_sql: bool = False
    """Set True in development to log all SQL statements."""

    # ── Vector Store ──────────────────────────────────────────────────────────
    vector_store_type: str = "memory"
    """
    Active vector store backend.
    Options: memory | chroma | pinecone | weaviate
    """

    # Chroma (self-hosted)
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    chroma_collection: str = "documents"

    # Pinecone
    pinecone_api_key: str = ""
    pinecone_environment: str = ""
    pinecone_index_name: str = ""

    # Weaviate
    weaviate_url: str = ""
    weaviate_api_key: str = ""
    weaviate_class_name: str = "Document"

    # ── LLM / Agent API Keys ──────────────────────────────────────────────────
    llm_provider: str = "stub"
    """
    Active LLM provider.
    Options: stub | ollama | openai | anthropic | gemini
    """

    # Ollama (local)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_base_url: str = ""
    """Override for Azure OpenAI or compatible endpoints."""

    # Anthropic
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-sonnet-20241022"

    # Google Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    # External LLM service (generic HTTP API)
    external_llm_url: str = ""
    external_llm_api_key: str = ""

    # Embedding model (used by RAG agent)
    embedding_provider: str = "stub"
    """Options: stub | openai | ollama | sentence-transformers"""
    embedding_model: str = "text-embedding-3-small"

    # ── File Upload ───────────────────────────────────────────────────────────
    upload_dir: str = "./data/uploads"
    max_upload_size_mb: int = 50

    # ── Agent Orchestration ───────────────────────────────────────────────────
    agent_timeout_seconds: int = 120
    max_concurrent_agents: int = 5
    session_ttl_seconds: int = 86400
    """How long inactive sessions are retained in the store (seconds)."""

    # ── Observability ─────────────────────────────────────────────────────────
    enable_metrics: bool = False
    """Expose /metrics (Prometheus) when True."""

    sentry_dsn: str = ""
    """Leave empty to disable Sentry error tracking."""

    # ─────────────────────────────────────────────────────────────────────────

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("app_env")
    @classmethod
    def validate_env(cls, v: str) -> str:
        allowed = {"development", "staging", "production"}
        if v not in allowed:
            raise ValueError(f"app_env must be one of {allowed}, got '{v}'")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = {"debug", "info", "warning", "error", "critical"}
        if v.lower() not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return v.lower()

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Returns the cached Settings singleton.
    The cache is invalidated only on process restart — use `get_settings.cache_clear()`
    in tests to reset between test cases.
    """
    return Settings()
