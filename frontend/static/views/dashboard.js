import { apiGet } from "../api.js";
import { t } from "../i18n/locale.js";
import { timeAgo } from "../utils/time.js";
import { formatStatus } from "../utils/status.js";

function formatDate(ts) {
    if (!ts) return "-";
    return new Date(ts * 1000).toLocaleString();
}

/* =========================================================
   STATE LOCAL
========================================================= */
let dashboardRecords = [];
let dashboardProviders = [];
let dashboardStatus = null;

/* =========================================================
   LOAD INITIAL
========================================================= */
export async function loadDashboard() {
    const [records, providers, status] = await Promise.all([
        apiGet("/api/records"),
        apiGet("api/providers"),
        apiGet("/api/system/ip")
    ]);

    dashboardRecords = Array.isArray(records) ? records : [];
    dashboardProviders= Array.isArray(providers) ? providers : [];
    dashboardStatus = status;

    renderDashboard();
}

/* =========================================================
   RENDER SHELL + TABLE CONTAINER
========================================================= */
function renderDashboard() {
    const publicIP = dashboardStatus?.current_ip ?? "-";
    const lastChange = dashboardStatus?.last_change_relative ?? "-";

    document.getElementById("view").innerHTML = `
        <div class="header">
            <h1>${t("dashboard")}</h1>
        </div>

        <div class="grid">
            <div class="stat-card">
                <div>${t("total_records")}</div>
                <div class="stat-value">${dashboardRecords.length}</div>
            </div>

            <div class="stat-card">
                <div>${t("public_ip")}</div>
                <div class="stat-value" id="stat-ip">${publicIP}</div>
            </div>

            <div class="stat-card">
                <div>${t("last_ip_update")}</div>
                <div class="stat-value">${ timeAgo(lastChange) }</div>
            </div>
        </div>

        <h2>${t("records")}</h2>

        <div class="list">
            <div class="row row-header row-dashboard">
                <div>${t("domain")}</div>
                <div>${t("provider")}</div>
                <div>${t("ip")}</div>
                <div>${t("status")}</div>
                <div>${t("updated")}</div>
            </div>
            <div id="records-list"></div>
        </div>
    `;

    renderList();
}

/* =========================================================
   TABLE RENDER
========================================================= */
function renderList() {
    const list = document.getElementById("records-list");
    list.innerHTML = dashboardRecords.length === 0
        ? `<div class="card muted">${t("no_records")}</div>`
        : dashboardRecords.map(r => {
            const provider = dashboardProviders.find(p => p.id === r.provider_id);
            return `
                <div class="row row-dashboard" data-id="${r.id}">
                    <div class="col domain">
                        <strong>${r.domain}</strong>
                    </div>
                    <div class="col provider">
                        <strong>${provider?.type ?? "-"}</strong>
                    </div>
                    <div class="col ip">
                        ${r.ip || "-"}
                    </div>
                    <div class="col status">
                        <span class="badge badge-${formatStatus(r.status).type}">
                            ${formatStatus(r.status).label}
                        </span>
                    </div>
                    <div class="col updated">
                        ${timeAgo(r.updated_at) ?? "-"}
                    </div>
                </div>
            `;
        }).join("");
}

/* =========================================================
   PATCH RECORD (CREATE / UPDATE / DELETE HANDLED)
========================================================= */
function patchRecord(record) {
    if (!record || !record.id) return;

    const id = String(record.id);

    const index = dashboardRecords.findIndex(r => String(r.id) === id);

    // -------------------------
    // CREATE
    // -------------------------
    if (index === -1) {
        dashboardRecords.unshift(record);

        const tbody = document.getElementById("records-tbody");
        if (!tbody) return;

        const tr = document.createElement("tr");
        tr.id = `row-${id}`;

        tr.innerHTML = `
            <td>${record.domain}</td>
            <td>${record.provider}</td>
            <td class="col-ip">${record.ip ?? "-"}</td>
            <td>
                <span class="badge badge-${formatStatus(record.status).type}">
                    ${formatStatus(record.status).label}
                </span>
            </td>
            <td>${record.updated_at ?? "-"}</td>
        `;

        tbody.prepend(tr);
        updateRecordCount();
        return;
    }

    // -------------------------
    // UPDATE STATE
    // -------------------------
    dashboardRecords[index] = {
        ...dashboardRecords[index],
        ...record,
        id
    };

    // -------------------------
    // UPDATE DOM
    // -------------------------
    const row = document.getElementById(`row-${id}`);
    if (!row) return;

    const ipEl = row.querySelector(".col-ip");
    if (ipEl) {
        ipEl.textContent = record.ip ?? "-";
    }

    const badge = row.querySelector(".badge");
    if (badge && record.status) {
        const formatted = formatStatus(record.status);
        badge.className = `badge badge-${formatted.type}`;
        badge.textContent = formatted.label;
    }
}

/* =========================================================
   DELETE PATCH
========================================================= */
function removeRecord(record) {
    const id = record.id ?? record.record_id;
    if (!id) return;

    dashboardRecords = dashboardRecords.filter(r => r.id !== id);

    document.getElementById(`row-${id}`)?.remove();

    updateRecordCount();
}

/* =========================================================
   IP PATCH
========================================================= */
function patchIP(event) {
    if (!dashboardStatus) return;

    dashboardStatus = {
        ...dashboardStatus,
        current_ip: event.new_ip,
        last_change_relative: "just now"
    };

    const ipEl = document.getElementById("stat-ip");
    if (ipEl) {
        ipEl.textContent = event.new_ip;
    }
}

/* =========================================================
   HELPERS
========================================================= */
function updateRecordCount() {
    const el = document.querySelector(".stat-value");
    if (el) {
        el.textContent = dashboardRecords.length;
    }
}

/* =========================================================
   PUBLIC API (EVENT BUS)
========================================================= */
window.__dashboardPatch = {
    record: patchRecord,
    ip: patchIP,
    delete: removeRecord
};