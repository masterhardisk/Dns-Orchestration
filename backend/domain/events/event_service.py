import json
from backend.infrastructure.db.store import add_event
from backend.domain.events.event_bus import publish


def emit_event(event_type: str, payload=None, domain: str | None = None):
    """
    Event dispatcher unificado:
    - persistencia
    - side effects
    - realtime UI
    """

    # -------------------------
    # NORMALIZACIÓN PAYLOAD
    # -------------------------
    if payload is None:
        payload = {}

    if isinstance(payload, str):
        payload = {
            "message": payload
        }

    if isinstance(domain, dict):
        domain = json.dumps(domain)

    # -------------------------
    # 1. DB (persistencia)
    # -------------------------
    add_event(
        event_type,
        domain,
        json.dumps(payload)
    )

    # -------------------------
    # 3. REALTIME UI (SSE)
    # -------------------------
    publish({
        "type": event_type,
        "payload": payload
    })