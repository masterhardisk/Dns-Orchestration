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

class CheckIPSyncUseCase:

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

                emit_event("ERROR", {
                    "scope": "provider",
                    "record_id": record_id,
                    "message": str(e)
                })
                continue

            if result == "updated":
                update_record(record_id, record["domain"], ip, "ok")
                updated.append(record["domain"])

            elif result == "no_change":
                update_record(record_id, record["domain"], ip, "up_to_date")

            elif result == "rate_limit":
                update_record(record_id, record["domain"], current_ip, "error")

                errors.append(record["domain"])

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