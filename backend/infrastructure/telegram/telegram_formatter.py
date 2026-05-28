from backend.infrastructure.db.store import get_setting


def get_language():
    settings = get_setting("app") or {}
    return settings.get("language", "es")


def tr(key: str, lang: str):
    translations = {
        "es": {
            "record_updated": "🔄 Actualización de registro",
            "domain": "🌐 Dominio",
            "status": "📌 Estado",
            "pending": "🕒 Pendiente",
            "ok": "✅ Actualizado",
            "up_to_date": "☑️ Sin cambios",
            "error": "❌ Error",

            "ip_changed": "🌍 IP pública actualizada",
            "old_ip": "📤 IP anterior",
            "new_ip": "📥 Nueva IP",

            "worker_started":
                "🫡 DNS Orchestrator\n"
                "🟢 Activo\n"
                "⚙️ v1.0.0"
        },

        "en": {
            "record_updated": "🔄 Record updated",
            "domain": "🌐 Domain",
            "status": "📌 Status",
            "pending": "🕒 Pending",
            "ok": "✅ Updated",
            "up_to_date": "☑️ No changes",
            "error": "❌ Error",

            "ip_changed": "🌍 Public IP updated",
            "old_ip": "📤 Previous IP",
            "new_ip": "📥 New IP",

            "worker_started":
                "🫡 DNS Orchestrator\n"
                "🟢 Running\n"
                "⚙️ v1.0.0"
        }
    }

    return translations.get(lang, translations["es"]).get(key, key)


def format_message(event_type: str, payload: dict):
    lang = get_language()

    # -----------------------------------
    # RECORD UPDATED
    # -----------------------------------
    if event_type == "RECORD_UPDATED":

        domain = payload.get("domain", "-")
        status = payload.get("status", "unknown")

        return (
            f"{tr('record_updated', lang)}\n\n"
            f"{tr('domain', lang)}: {domain}\n"
            f"{tr('status', lang)}: {tr(status, lang) if status in ['ok','error','up_to_date','pending'] else status}"
        )

    # -----------------------------------
    # IP CHANGED
    # -----------------------------------
    if event_type == "IP_CHANGED":

        old_ip = payload.get("old_ip")
        new_ip = payload.get("new_ip", "-")

        lines = [
            f"{tr('ip_changed', lang)}",
            ""
        ]

        # solo mostrar old_ip si existe y es válido
        if old_ip:
            lines.append(f"{tr('old_ip', lang)}: {old_ip}")

        lines.append(f"{tr('new_ip', lang)}: {new_ip}")

        return "\n".join(lines)

    # -----------------------------------
    # WORKER STARTED
    # -----------------------------------
    if event_type == "WORKER_STARTED":
        return tr("worker_started", lang)
    
    if event_type == "SYNC_COMPLETED":
        ip = payload.get("ip", "-")
        updated = payload.get("updated", [])
        errors = payload.get("errors", [])

        lines = [
            f"🌍 IP actualizada: {ip}",
        ]

        # -------------------------
        # SOLO SI HAY DOMINIOS
        # -------------------------
        if updated:
            lines += [
                "",
                "🔄 Dominios sincronizados:",
                *[f"✅ {d}" for d in updated]
            ]

        # -------------------------
        # SOLO SI HAY ERRORES
        # -------------------------
        if errors:
            lines += [
                "",
                f"❌ Errores: {len(errors)}",
                "",
                "🚨 Fallos:",
                *[f"• {e}" for e in errors]
            ]

        return "\n".join(lines)

    # -----------------------------------
    # FALLBACK
    # -----------------------------------
    return f"📢 {event_type}\n\n{payload}"