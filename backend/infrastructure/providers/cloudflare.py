import httpx
import logging
import json

from backend.infrastructure.providers.base import BaseDNSProvider
from backend.domain.providers.provider_result import ProviderResult

logger = logging.getLogger(__name__)

class CloudflareProvider(BaseDNSProvider, type="cloudflare"):

    BASE_URL = "https://api.cloudflare.com/client/v4"

    def __init__(self, token: str):
        self.token = token

    # -------------------------------------------------
    # HEADERS
    # -------------------------------------------------
    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    # -------------------------------------------------
    # REQUIRED BY ABC
    # -------------------------------------------------
    def test_connection(self) -> bool:
        try:
            r = httpx.get(
                f"{self.BASE_URL}/user/tokens/verify",
                headers=self._headers(),
                timeout=10
            )
            return r.status_code == 200
        except Exception:
            return False

    # -------------------------------------------------
    # GET DNS RECORD
    # -------------------------------------------------
    def _get_record(self, domain: str, zone_id: str):
        try:
            r = httpx.get(
                f"{self.BASE_URL}/zones/{zone_id}/dns_records",
                headers=self._headers(),
                params={"type": "A", "name": domain},
                timeout=10
            )

            data = r.json()
            if not data.get("success"):
                return None

            results = data.get("result", [])
            return results[0] if results else None

        except Exception as e:
            logger.exception(e)
            return None

    # -------------------------------------------------
    # CREATE
    # -------------------------------------------------
    def _create_record(self, domain: str, ip: str, zone_id: str):
        try:
            r = httpx.post(
                f"{self.BASE_URL}/zones/{zone_id}/dns_records",
                headers=self._headers(),
                json={
                    "type": "A",
                    "name": domain,
                    "content": ip,
                    "ttl": 120,
                    "proxied": False
                },
                timeout=10
            )
            return r.json()
        except Exception:
            return None

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------
    def _update_record(self, record_id: str, domain: str, ip: str, zone_id: str):
        try:
            r = httpx.put(
                f"{self.BASE_URL}/zones/{zone_id}/dns_records/{record_id}",
                headers=self._headers(),
                json={
                    "type": "A",
                    "name": domain,
                    "content": ip,
                    "ttl": 120,
                    "proxied": False
                },
                timeout=10
            )
            return r.json()
        except Exception:
            return None

    # -------------------------------------------------
    # MAIN ENTRY (FIX IMPORTANTE)
    # -------------------------------------------------
    def update_record(self, record: dict, ip: str) -> ProviderResult:
        domain = record["domain"]
        payload = record.get("payload") or {}
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except Exception:
                payload = {}

        zone_id = payload["zone_id"]

        try:
            record = self._get_record(domain, zone_id)

            if not record:
                res = self._create_record(domain, ip, zone_id)
                return ProviderResult.UPDATED if res and res.get("success") else ProviderResult.ERROR

            record_id = record["id"]
            res = self._update_record(record_id, domain, ip, zone_id)

            return ProviderResult.UPDATED if res and res.get("success") else ProviderResult.ERROR

        except Exception:
            logger.exception("Cloudflare provider error")
            return ProviderResult.ERROR

    # -------------------------------------------------
    # SCHEMAS (CORRECTOS)
    # -------------------------------------------------
    def get_provider_schema(self):
        return {
            "fields": [
                {
                    "key": "token",
                    "type": "text",
                    "label_key": "cloudflare.field_api_token",
                    "required": True
                }
            ]
        }

    def get_record_schema(self):
        return {
            "fields": [
                {
                    "key": "zone_id",
                    "type": "text",
                    "label_key": "cloudflare.field_zone_id",
                    "required": True
                }
            ]
        }
    
    def get_i18n(self):
        return {
            "es": {
                "cloudflare.field_api_token": "Token de API de Cloudflare",
                "cloudflare.field_zone_id": "ID de zona"
            },
            "en": {
                "cloudflare.field_api_token": "Cloudflare API Token",
                "cloudflare.field_zone_id": "Zone ID"
            }
        }