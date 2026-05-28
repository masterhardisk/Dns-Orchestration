let source = null;
let listeners = new Set();

export function connectEvents() {
    console.log("connectEvents");
    if (source) return;

    source = new EventSource("/api/events/stream");
    source.onmessage = (e) => {
        try {
            const event = JSON.parse(e.data);
            notify(event);
        } catch (err) {
            console.log("Invalid event", e.data);
        }
    };

    source.onerror = (err) => {
        console.log("SSE error", err);
    };
}

function notify(event) {
    for (const cb of listeners) {
        try { cb(event); } catch {}
    }
}

export function subscribeEvents(cb) {
    listeners.add(cb);
    return () => listeners.delete(cb);
}