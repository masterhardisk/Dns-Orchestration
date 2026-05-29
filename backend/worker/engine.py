from backend.application.use_cases.check_ip_sync import CheckIPSyncUseCase
from backend.infrastructure.db.bootstrap import bootstrap_settings
from backend.infrastructure.db.store import init_db, get_providers
from backend.domain.events.event_service import emit_event
import threading
import logging
import threading
import logging

logger = logging.getLogger(__name__)

CHECK_INTERVAL = 60
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
        sync_event.wait(timeout=CHECK_INTERVAL)
        sync_event.clear()

        providers_cache = getProviders()
        use_case.providers_cache = providers_cache

        use_case.execute()