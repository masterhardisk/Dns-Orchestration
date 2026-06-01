import httpx
import logging

from backend.infrastructure.db.store import get_setting
from backend.application.constants.public_ip import IP_PROVIDERS

logger = logging.getLogger(__name__)


def get_public_ip() -> str | None:
    """
    Resolve public IP using configured provider.
    Falls back to first available provider chain if config is invalid.
    """

    logger.info("[IP] resolver start")

    settings = get_setting("public_ip") or {}
    provider_name = settings.get("provider", "ipify")

    logger.info("[IP] selected provider=%s", provider_name)

    sources = IP_PROVIDERS.get(provider_name)

    if not sources:
        logger.warning(
            "[IP] invalid provider, falling back to default provider=%s",
            provider_name
        )

        # fallback: first provider in dict (no "auto" concept anymore)
        fallback_provider = next(iter(IP_PROVIDERS.keys()))
        sources = IP_PROVIDERS[fallback_provider]

    with httpx.Client(timeout=5) as client:
        for url, mode in sources:
            try:
                logger.info("[IP] trying provider url=%s mode=%s", url, mode)

                r = client.get(url)

                if r.status_code != 200:
                    logger.warning(
                        "[IP] provider failed status url=%s status=%s",
                        url,
                        r.status_code
                    )
                    continue

                # -------------------------
                # JSON mode: json:field
                # -------------------------
                if mode.startswith("json:"):
                    try:
                        data = r.json()
                    except Exception as e:
                        logger.warning(
                            "[IP] invalid json response url=%s error=%s",
                            url,
                            e
                        )
                        continue

                    field = mode.split(":", 1)[1]
                    ip = data.get(field)

                    if not ip:
                        logger.warning(
                            "[IP] missing field in response url=%s field=%s",
                            url,
                            field
                        )
                        continue

                # -------------------------
                # TEXT mode: raw response
                # -------------------------
                elif mode == "text":
                    ip = r.text

                else:
                    logger.warning(
                        "[IP] unknown mode url=%s mode=%s",
                        url,
                        mode
                    )
                    continue

                ip = ip.strip()

                logger.info(
                    "[IP] resolved OK ip=%s source=%s",
                    ip,
                    url
                )

                return ip

            except Exception as e:
                logger.warning(
                    "[IP] provider exception url=%s error=%s",
                    url,
                    e
                )
                continue

    logger.error("[IP] all providers failed")
    return None