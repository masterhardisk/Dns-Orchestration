import queue
import threading
from backend.infrastructure.subscribers.telegram_subscriber import handle_event

_subscribers = set()
_lock = threading.Lock()


def subscribe():
    q = queue.Queue()
    with _lock:
        _subscribers.add(q)
    return q


def unsubscribe(q):
    with _lock:
        _subscribers.discard(q)


def publish(event: dict):
    with _lock:
        subscribers = list(_subscribers)

    for q in subscribers:
        try:
            q.put_nowait(event)
        except Exception:
            pass
        
    try:
        handle_event(event)
    except Exception:
        pass