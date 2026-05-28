from backend.infrastructure.telegram.telegram_service import send_message
from backend.infrastructure.telegram.telegram_formatter import format_message

INTERESTING_EVENTS = {
    "WORKER_STARTED",
    "SYNC_COMPLETED"
}


def handle_event(event: dict):
    event_type = event.get("type")
    payload = event.get("payload", {})

    print("handle event called", event_type)

    if event_type not in INTERESTING_EVENTS:
        return

    message = format_message(event_type, payload)
    send_message(message)