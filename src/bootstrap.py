"""Application bootstrap and factory for the Multi-Agent Framework API."""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from config import get_settings
from db.session import init_db
from routers.v1 import router as v1_router


def configure_logging(settings):
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.getLogger("uvicorn").setLevel(level)


def configure_sentry(settings):
    if settings.sentry_dsn:
        try:
            import sentry_sdk

            sentry_sdk.init(dsn=settings.sentry_dsn)
            logging.getLogger("bootstrap").info("Sentry initialized")
        except Exception:
            logging.getLogger("bootstrap").exception("Failed to initialize Sentry")


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings)
    configure_sentry(settings)

    app = FastAPI(
        title="Multi-Agent Framework API",
        description="Gateway API for the Local LLM Multi-Agent Orchestration Framework",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://ai-platform-lllm-ui-24286129227.us-central1.run.app"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(v1_router, prefix="/v1")

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        return JSONResponse({"detail": exc.errors()}, status_code=422)

    @app.on_event("startup")
    async def on_startup():
        logging.getLogger("bootstrap").info("Starting multi-agent-framework-api (env=%s)", settings.app_env)
        await init_db()

    @app.on_event("shutdown")
    async def on_shutdown():
        logging.getLogger("bootstrap").info("Shutting down multi-agent-framework-api")

    return app


app = create_app()
