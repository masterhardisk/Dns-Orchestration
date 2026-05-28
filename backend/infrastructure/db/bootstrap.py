import os
from backend.infrastructure.db.store import get_setting, set_setting

def bootstrap_settings():
    existing = get_setting("telegram")
    if existing:
        return
    set_setting("telegram", {
        "enabled": os.getenv("TELEGRAM_ENABLED", "false") == "true",
        "bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
        "chat_id": os.getenv("TELEGRAM_CHAT_ID", "")
    })