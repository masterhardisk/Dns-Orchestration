import sqlite3
import os
import json
import time
from datetime import datetime, timezone

DB_PATH = os.getenv("DATA_DIR", "/data") + "/app.db"


# =====================
# CONNECTION
# =====================

def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# =====================
# INIT DB
# =====================

def init_db():
    conn = _conn()
    c = conn.cursor()

    # PROVIDERS
    c.execute("""
    CREATE TABLE IF NOT EXISTS providers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        type TEXT,
        credentials TEXT,
        enabled INTEGER DEFAULT 1,
        created_at TEXT
    )
    """)

    # RECORDS (config + last known state per domain)
    c.execute("""
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY,
        provider_id INTEGER,
        domain TEXT,
        payload TEXT,
        ip TEXT,
        status TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    """)

    # EVENTS
    c.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        domain TEXT,
        message TEXT,
        created_at TEXT
    )
    """)

    # IP HISTORY (global state)
    c.execute("""
    CREATE TABLE IF NOT EXISTS ip_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT,
        previous_ip TEXT,
        created_at TEXT
    )
    """)

    # SYSTEM SETTINGS (global config: telegram, etc.)
    c.execute("""
    CREATE TABLE IF NOT EXISTS system_settings (
        key TEXT PRIMARY KEY,
        value TEXT,
        updated_at TEXT
    )
    """)

    conn.commit()
    conn.close()


# =====================
# STATUS
# =====================

def get_status():
    conn = _conn()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) as total FROM records")
    total = c.fetchone()["total"]

    conn.close()

    return {
        "service": "ok",
        "records": total
    }


# =====================
# RECORDS
# =====================

def get_records():
    conn = _conn()
    c = conn.cursor()

    c.execute("""
        SELECT r.*, p.name as provider_name, p.type as provider_type
        FROM records r
        JOIN providers p ON p.id = r.provider_id
        ORDER BY r.id DESC
    """)

    rows = [dict(r) for r in c.fetchall()]
    conn.close()

    for row in rows:
        ua = datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00"))
        ca = datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))

        now = datetime.now(timezone.utc)
        seconds = int((now - ua).total_seconds())
        
        row['created_at'] = ca.strftime("%d/%m/%Y %H:%M")
        row["updated_at"] = seconds

    return rows

def get_record(record_id: int):
    conn = _conn()
    c = conn.cursor()
    c.execute("""
        SELECT *
        FROM records
        WHERE id = ?
    """, (record_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def update_record(record_id: int, domain=None, ip=None, status=None, payload=None):
    conn = _conn()
    c = conn.cursor()

    fields = []
    values = []

    if domain is not None:
        fields.append("domain = ?")
        values.append(domain)

    if ip is not None:
        fields.append("ip = ?")
        values.append(ip)

    if status is not None:
        fields.append("status = ?")
        values.append(status)

    if payload is not None:
        fields.append("payload = ?")
        values.append(json.dumps(payload))

    fields.append("updated_at = ?")
    values.append(datetime.now(timezone.utc).isoformat())

    if len(fields) == 1:
        conn.close()
        return

    values.append(record_id)

    query = f"""
        UPDATE records
        SET {", ".join(fields)}
        WHERE id = ?
    """

    c.execute(query, values)
    conn.commit()
    conn.close()


def create_record(provider_id: int, domain: str, payload: dict, status: str = "pending"):
    conn = _conn()
    c = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    c.execute("""
        INSERT INTO records (provider_id, domain, payload, ip, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        provider_id,
        domain,
        json.dumps(payload),
        None,
        status,
        now,
        now
    ))

    record_id = c.lastrowid
    
    conn.commit()
    conn.close()

    return {
        "id": record_id,
        "provider_id": provider_id,
        "domain": domain,
        "ip": None,
        "payload": payload,
        "status": status
    }

def delete_record(record_id: int):
    conn = _conn()
    c = conn.cursor()
    c.execute("""
        DELETE FROM records
        WHERE id = ?
    """, (record_id,))
    conn.commit()
    conn.close()


# =====================
# PROVIDERS
# =====================

def get_providers():
    conn = _conn()
    c = conn.cursor()

    c.execute("SELECT * FROM providers ORDER BY id DESC")
    rows = c.fetchall()

    conn.close()

    return [
        {
            **dict(r),
            "credentials": json.loads(r["credentials"]) if r["credentials"] else {}
        }
        for r in rows
    ]


def create_provider(name: str, type_: str, credentials: dict):
    conn = _conn()
    c = conn.cursor()

    c.execute("""
        INSERT INTO providers (name, type, credentials, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        name,
        type_,
        json.dumps(credentials),
        datetime.now(timezone.utc).isoformat()
    ))

    conn.commit()
    conn.close()

def provider_has_records(provider_id: int) -> bool:
    conn = _conn()
    c = conn.cursor()
    c.execute("""
        SELECT 1
        FROM records
        WHERE provider_id = ?
        LIMIT 1
    """, (provider_id,))
    result = c.fetchone()
    conn.close()
    return result is not None

def delete_provider(provider_id: int):
    conn = _conn()
    c = conn.cursor()
    c.execute("DELETE FROM providers WHERE id = ?", (provider_id,))
    conn.commit()
    deleted = c.rowcount > 0
    conn.close()
    return deleted

# =====================
# EVENTS
# =====================

def get_events(limit=50):
    conn = _conn()
    c = conn.cursor()

    c.execute("""
        SELECT * FROM events
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def add_event(event_type, domain, message):
    conn = _conn()
    c = conn.cursor()

    c.execute("""
        INSERT INTO events (type, domain, message, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        event_type,
        domain,
        message,
        datetime.now(timezone.utc).isoformat()
    ))

    conn.commit()
    conn.close()

# =====================
# SETTINGS
# =====================
def get_setting(key: str):
    conn = _conn()
    c = conn.cursor()

    c.execute("""
        SELECT value
        FROM system_settings
        WHERE key = ?
    """, (key,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    try:
        return json.loads(row["value"])
    except Exception:
        return row["value"]

def set_setting(key: str, value):
    conn = _conn()
    c = conn.cursor()

    if not isinstance(value, str):
        value = json.dumps(value)

    c.execute("""
        INSERT INTO system_settings (key, value, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(key) DO UPDATE SET
            value = excluded.value,
            updated_at = excluded.updated_at
    """, (
        key,
        value,
        time.strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

# =====================
# IP HISTORY (GLOBAL STATE)
# =====================

def add_ip_history(ip: str, previous_ip: str = None):
    conn = _conn()
    c = conn.cursor()

    c.execute("""
        INSERT INTO ip_history (ip, previous_ip, created_at)
        VALUES (?, ?, ?)
    """, (
        ip,
        previous_ip,
        datetime.now(timezone.utc).isoformat()
    ))

    conn.commit()
    conn.close()


def get_current_ip_status():
    conn = _conn()
    c = conn.cursor()

    c.execute("""
        SELECT ip, previous_ip, created_at
        FROM ip_history
        ORDER BY id DESC
        LIMIT 1
    """)

    row = c.fetchone()
    conn.close()

    if not row:
        return {
            "current_ip": None,
            "last_change": None,
            "last_change_relative": None
        }

    dt = datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    seconds = int((now - dt).total_seconds())
    return {
        "current_ip": row["ip"],
        "last_change": dt.strftime("%d/%m/%Y %H:%M"),
        "last_change_relative": seconds
    }

def time_ago(dt: datetime) -> str:
    now = datetime.now(timezone.utc)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    seconds = int((now - dt).total_seconds())

    if seconds < 60:
        return f"Hace {seconds} segundo" + ("s" if seconds != 1 else "")

    minutes = seconds // 60
    if minutes < 60:
        return f"Hace {minutes} minuto" + ("s" if minutes != 1 else "")

    hours = minutes // 60
    if hours < 24:
        return f"Hace {hours} hora" + ("s" if hours != 1 else "")

    days = hours // 24
    return f"Hace {days} día" + ("s" if days != 1 else "")