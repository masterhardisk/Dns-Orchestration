import httpx
from backend.infrastructure.db.store import get_setting

def _get_telegram_config():
    config = get_setting("telegram")
    if not isinstance(config, dict):
        return None
    return config


def send_message(text: str):
    config = _get_telegram_config()

    print("send_message called", config)
    if not config:
        return

    if not config.get("enabled"):
        return

    token = config.get("bot_token")
    chat_id = config.get("chat_id")

    if not token or not chat_id:
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    try:
        httpx.post(
            url,
            json={
                "chat_id": chat_id,
                "text": text
            },
            timeout=10
        )
    except Exception:
        pass