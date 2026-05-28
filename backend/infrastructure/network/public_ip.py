import httpx
import logging

logger = logging.getLogger(__name__)


def get_public_ip() -> str | None:
    urls = [
        "https://api.ipify.org?format=json",
        "https://ipv4.ipleak.net/json"
    ]

    for url in urls:
        try:
            r = httpx.get(url, timeout=5)

            if r.status_code != 200:
                continue

            data = r.json()

            ip = data.get("ip")

            if ip:
                ip = ip.strip()
                logger.info("Public IP resolved", extra={
                    "source": url,
                    "ip": ip
                })
                return ip

        except Exception as e:
            logger.warning("IP resolver failed", extra={
                "url": url,
                "error": str(e)
            })
            continue

    return None