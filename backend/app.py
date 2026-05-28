from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_redoc_html
from contextlib import asynccontextmanager
import threading

from backend.infrastructure.db.store import init_db
from backend.worker.engine import start_worker
from backend.infrastructure.providers.discovery import load_providers

import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()

    load_providers()

    worker_thread = threading.Thread(
        target=start_worker,
        daemon=True
    )
    worker_thread.start()

    yield


def create_app():
    app = FastAPI(
        title="DNS Orchestrator",
        description="Multi-provider DNS orchestration platform",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url=None,
        openapi_url="/openapi.json"
    )

    app.mount(
        "/static",
        StaticFiles(directory="frontend/static"),
        name="static"
    )

    @app.get("/")
    def root():
        from fastapi.responses import FileResponse
        return FileResponse("frontend/index.html")

    from backend.api.routes import router
    app.include_router(router, prefix="/api")

    @app.get("/redoc", include_in_schema=False)
    def redoc():
        return get_redoc_html(
            openapi_url=app.openapi_url,
            title="DNS Orchestrator",
            redoc_js_url="https://cdn.redoc.ly/redoc/v2.1.3/bundles/redoc.standalone.js"
        )

    return app


app = create_app()