from backend.infrastructure.network.public_ip import get_public_ip
from backend.domain.events.event_service import emit_event
from backend.infrastructure.db.store import (
    get_records,
    update_record,
    add_ip_history,
    get_current_ip_status,
    get_providers
)
from backend.infrastructure.providers.factory import build_provider
from time import time
import logging

logger = logging.getLogger(__name__)
COOLDOWN = 300

class CheckIPSyncUseCase:
    rate_limit_cache = {}
    

    def __init__(self, providers_cache):
        self.providers_cache = providers_cache

    def execute(self):
        ip = get_public_ip()

        if not ip:
            emit_event("ERROR", {
                "scope": "system",
                "message": "Cannot resolve public IP"
            })
            return

        changed, old_ip = self._update_ip_if_changed(ip)

        if changed:
            emit_event(
                "IP_CHANGED",
                {
                    "old_ip": old_ip,
                    "new_ip": ip
                },
                domain="system"
            )

        if not self.providers_cache:
            self.providers_cache.update({
                p["id"]: p for p in get_providers()
            })

        updated, errors = self._run_sync_cycle(ip)

        if updated or errors:
            emit_event(
                "SYNC_COMPLETED",
                {
                    "ip": ip,
                    "updated": updated,
                    "errors": errors
                },
                domain="system"
            )

        return ip

    # -------------------------
    # INTERNAL METHODS
    # -------------------------
    def _update_ip_if_changed(self, new_ip: str):
        current = get_current_ip_status()
        old_ip = current["current_ip"] if current else None

        if current and current["current_ip"] == new_ip:
            return False, old_ip

        add_ip_history(new_ip, old_ip)
        return True, old_ip

    def _run_sync_cycle(self, ip):
        records = get_records()

        updated = []
        errors = []

        for record in records:
            record_id = record["id"]
            provider_row = self.providers_cache.get(record["provider_id"])

            if not provider_row:
                errors.append(record["domain"])

                emit_event("ERROR", {
                    "scope": "system",
                    "record_id": record_id,
                    "message": "Provider not found"
                })
                continue

            provider = build_provider(provider_row)

            current_ip = record.get("ip")

            if current_ip == ip:
                if record.get("status") != "up_to_date":
                    update_record(
                        record_id=record_id,
                        domain=record["domain"],
                        ip=ip,
                        status="up_to_date"
                    )

                    record["ip"] = ip
                    record["status"] = "up_to_date"
                    self.send_record_event("RECORD_UPDATED", record)
                continue

            try:
                result = provider.update_record(record=record, ip=ip)
            except Exception as e:
                update_record(
                    record_id=record_id,
                    domain=record["domain"],
                    ip=current_ip,
                    status="error"
                )

                errors.append(record["domain"])

                record["ip"] = record_id
                record["status"] = "error"
                self.send_record_event("RECORD_UPDATED", record)

                emit_event("ERROR", {
                    "scope": "provider",
                    "record_id": record_id,
                    "message": str(e)
                })
                continue

            if result == "updated":
                update_record(record_id, record["domain"], ip, "ok")
                record["ip"] = ip
                record["status"] = "ok"
                self.send_record_event("RECORD_UPDATE", record)
                updated.append(record["domain"])

            elif result == "no_change":
                update_record(record_id, record["domain"], ip, "up_to_date")
                record["ip"] = ip
                record["status"] = "up_to_date"
                self.send_record_event("RECORD_UPDATED", record)
            elif result == "rate_limit":
                now = time()
                last = self.rate_limit_cache.get(record_id, 0)
                delta = now - last
                logger.warning(
                    "[RATE_LIMIT] detected",
                    extra={
                        "record_id": record_id,
                        "domain": record["domain"],
                        "last_seen": last,
                        "now": now,
                        "delta_seconds": delta,
                        "cooldown": COOLDOWN,
                        "blocked": delta < COOLDOWN
                    }
                )
                if delta < COOLDOWN:
                    logger.info(
                        "[RATE_LIMIT] suppressed (cooldown active)",
                        extra={
                            "record_id": record_id,
                            "remaining_seconds": COOLDOWN - delta
                        }
                    )
                    update_record(record_id, record["domain"], current_ip, "error")
                    continue
                logger.info(
                    "[RATE_LIMIT] allowed after cooldown",
                    extra={
                        "record_id": record_id,
                        "cooldown_elapsed": delta
                    }
                )
                self.rate_limit_cache[record_id] = now
                update_record(record_id, record["domain"], current_ip, "error")
                errors.append(record["domain"])
                record["ip"] = current_ip
                record["status"] = "error"
                self.send_record_event("RECORD_UPDATED", record)
                emit_event("ERROR", {
                    "scope": "provider",
                    "record_id": record_id,
                    "message": "Rate limit"
                })

            else:
                update_record(record_id, record["domain"], current_ip, "error")

                errors.append(record["domain"])

                emit_event("ERROR", {
                    "scope": "provider",
                    "record_id": record_id,
                    "message": "Unknown provider result"
                })

        return updated, errors
    
    def send_record_event(self, event_type: str, record: dict):
        emit_event(
            event_type,
            payload={
                "id": record["id"],
                "provider_id": record["provider_id"],
                "domain": record.get("domain"),
                "ip": record.get("ip"),
                "status": record.get("status")
            }
        )