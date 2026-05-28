import httpx
import logging
from backend.infrastructure.providers.base import BaseDNSProvider
from backend.domain.providers.provider_result import ProviderResult

logger = logging.getLogger(__name__)

class StratoProvider(BaseDNSProvider, type="strato"):

    BASE_URL = "https://dyndns.strato.com/nic/update"

    def __init__(self, password: str):
        self.password = password

    def test_connection(self) -> bool:
        try:
            r = httpx.get(
                self.BASE_URL,
                auth=("test", self.password),
                params={
                    "hostname": "test.invalid",
                    "myip": "0.0.0.0"
                },
                timeout=10
            )
            return r.status_code in (200, 400, 401, 403)
        except Exception:
            return False

    def update_record(self, record: dict, ip: str) -> ProviderResult:
        domain = record["domain"]
        try:
            r = httpx.get(
                self.BASE_URL,
                auth=(domain, self.password),
                params={
                    "hostname": domain,
                    "myip": ip
                },
                timeout=10
            )

            body = r.text.strip().lower()

            logger.info("Strato response", extra={
                "domain": domain,
                "ip": ip,
                "status_code": r.status_code,
                "body": body
            })

            # -------------------------
            # SUCCESS UPDATED
            # -------------------------
            if body.startswith("good"):
                return ProviderResult.UPDATED

            # -------------------------
            # ALREADY IN SYNC
            # -------------------------
            if body.startswith("nochg"):
                return ProviderResult.NO_CHANGE

            # -------------------------
            # RATE LIMIT / ABUSE
            # -------------------------
            if body.startswith("abuse"):
                logger.error("Strato abuse response", extra={
                    "domain": domain,
                    "body": body
                })
                return ProviderResult.RATE_LIMIT

            # -------------------------
            # UNKNOWN ERROR
            # -------------------------
            logger.error("Unexpected Strato response", extra={
                "domain": domain,
                "status_code": r.status_code,
                "body": body
            })

            return ProviderResult.ERROR

        except Exception as e:
            logger.exception("Strato request failed", extra={
                "domain": domain,
                "ip": ip
            })
            return ProviderResult.ERROR
        
    def get_provider_schema(self):
        return {
            "fields": [
                {
                    "key": "password",
                    "type": "password",
                    "label_key": "strato.field_password",
                    "required": True
                }
            ]
        }
    
    def get_i18n(self):
        return {
            "es": {
                "strato.field_password": "Contraseña de Strato"
            },
            "en": {
                "strato.field_password": "Strato password"
            }
        }
