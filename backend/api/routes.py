from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from backend.infrastructure.providers.base import BaseDNSProvider
from backend.worker.engine import sync_event
from backend.domain.events.event_bus import subscribe, unsubscribe
from backend.domain.events.event_service import emit_event

import asyncio
import json

from backend.infrastructure.db.store import (
    get_status,
    get_records,
    get_record,
    update_record,
    delete_record,
    get_events,
    get_providers,
    create_provider,
    delete_provider, 
    provider_has_records,
    create_record,
    get_current_ip_status,
    get_setting,
    set_setting
)

router = APIRouter()

@router.get("/status")
def status():
    return get_status()


@router.get("/records")
def records():
    return get_records()


@router.post("/records")
async def add_record(request: Request):
    data = await request.json()
    record = create_record(
        provider_id=data["provider_id"],
        domain = data["domain"],
        payload=data.get("payload", {}),
        status=data.get("status", "pending")
    )

    emit_event(
        "RECORD_CREATED",
        payload={
            "id": record["id"],
            "provider_id": record["provider_id"],
            "domain": record["domain"] if record else None,
            "ip": record.get("ip") if record else None,
            "status": record["status"] if record else None
        }
    )

    sync_event.set()
    return {"status": "ok"}

@router.put("/records/{record_id}")
async def update_record_route(record_id: int, request: Request):
    data = await request.json()
    update_record(
        record_id=record_id,
        domain= data.get("domain"),
        ip=data.get("ip"),
        status=data.get("status"),
        payload=data.get("payload")
    )
    record = get_record(record_id)    
    emit_event(
        "RECORD_UPDATED",
        payload={
            "id": record_id,
            "provider_id": record["provider_id"],
            "domain": record["domain"] if record else None,
            "ip": record.get("ip") if record else None,
            "status": record["status"] if record else None
        }
    )
    sync_event.set()
    return {"status": "ok"}

@router.delete("/records/{record_id}")
async def delete_record_route(record_id: int):
    record = get_record(record_id)
    delete_record(record_id)
    emit_event(
        "RECORD_DELETED",
        payload={
            "id": record_id,
            "domain": record["domain"] if record else None,
            "ip": record.get("ip") if record else None
        }
    )
    sync_event.set()
    return {"status": "deleted"}

@router.get("/providers")
def providers():
    return get_providers()

@router.post("/providers")
async def add_provider(request: Request):
    data = await request.json()
    create_provider(
        name=data["name"],
        type_=data["type"],
        credentials=data["credentials"]
    )
    return {"status": "ok"}

@router.delete("/providers/{provider_id}")
def remove_provider(provider_id: int):
    # 🔥 regla de negocio: no borrar si tiene records asociados
    if provider_has_records(provider_id):
        raise HTTPException(
            status_code=409,
            detail="Provider has associated records"
        )
    deleted = delete_provider(provider_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Provider not found"
        )
    return {"status": "ok"}

@router.get("/providers/types")
def get_provider_types():
    result = []

    for type_, cls in BaseDNSProvider.registry.items():
        try:
            # instancia real pero sin dependencias externas
            instance = cls.__new__(cls)

            provider_schema = getattr(instance, "get_provider_schema", lambda: {"fields": []})()
            record_schema = getattr(instance, "get_record_schema", lambda: {"fields": []})()
            i18n = getattr(instance, "get_i18n", lambda: {"fields": []})()

            result.append({
                "type": type_,
                "provider_schema": provider_schema,
                "record_schema": record_schema, 
                "i18n": i18n,
            })

        except Exception:
            print(f"Provider type error: {type_} {e}")
            continue

    return result


@router.get("/events")
def events(limit: int = 50):
    return get_events(limit)

@router.get("/settings/telegram")
def get_telegram_settings():
    data = get_setting("telegram")
    return data or {
        "enabled": False,
        "bot_token": "",
        "chat_id": ""
    }

@router.post("/settings/telegram")
async def update_telegram_settings(request: Request):
    payload = await request.json()
    normalized = {
        "enabled": bool(payload.get("enabled", False)),
        "bot_token": payload.get("bot_token", ""),
        "chat_id": payload.get("chat_id", "")
    }
    set_setting("telegram", normalized)
    sync_event.set()
    return {"status": "ok"}

@router.get("/system/ip")
def system_ip():
    return get_current_ip_status()

@router.get("/events/stream")
async def events_stream():
    queue = subscribe()
    async def generator():
        try:
            while True:
                try:
                    event = await asyncio.to_thread(queue.get, timeout=30)
                    yield f"data: {json.dumps(event)}\n\n"
                except Exception:
                    # keep-alive para evitar cortes
                    yield ": ping\n\n"
        except asyncio.CancelledError:
            unsubscribe(queue)
    return StreamingResponse(
        generator(),
        media_type="text/event-stream"
    )