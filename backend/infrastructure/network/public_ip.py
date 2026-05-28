import httpx
import logging

logger = logging.getLogger(__name__)

SOURCES = [
    ("https://api.ipify.org?format=json", "ip"),
    ("https://ipv4.ipleak.net/json", "query"),
]


def get_public_ip() -> str | None:
    with httpx.Client(timeout=5) as client:
        for url, field in SOURCES:
            try:
                r = client.get(url)

                if r.status_code != 200:
                    continue

                data = r.json()
                ip = data.get(field)

                if ip:
                    return ip.strip()

            except Exception:
                continue

    return None