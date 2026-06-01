from backend.application.use_cases.check_ip_sync import CheckIPSyncUseCase
from backend.infrastructure.db.bootstrap import bootstrap_settings
from backend.infrastructure.db.store import init_db, get_providers
from backend.domain.events.event_service import emit_event
from backend.infrastructure.db.store import get_setting
import threading
import logging
import threading
import logging

logger = logging.getLogger(__name__)
sync_event = threading.Event()


def getProviders():
    return {
        p["id"]: p for p in get_providers()
    }


def start_worker():
    init_db()
    bootstrap_settings()

    emit_event("WORKER_STARTED")

    providers_cache = getProviders()
    use_case = CheckIPSyncUseCase(providers_cache)

    use_case.execute()

    while True:
        settings = get_setting("worker") or {}
        interval = settings.get("interval", 300)
        logger.info(f"[WORKER] get settings = {settings}")
        logger.info(f"[WORKER] waiting cycle interval={interval}")

        sync_event.wait(timeout=interval)
        sync_event.clear()

        providers_cache = getProviders()
        use_case.providers_cache = providers_cache

        use_case.execute()