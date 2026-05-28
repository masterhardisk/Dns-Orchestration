import { apiGet, apiPost } from "../api.js";
import { t } from "../i18n/locale.js";
import { registerProviderI18n } from "../i18n/locale.js";
import { formatStatus } from "../utils/status.js";
import { icons } from "../utils/icons.js";
import { ui } from "../ui/index.js";

let providers = [];
let providerMap = {};
let editingRecordId = null;

/* =========================
   LOCAL STATE (para PATCH)
========================= */

let recordsState = [];

/* =========================
   LOAD
========================= */

export async function loadRecords() {
    const records = await apiGet("/api/records");
    providers = await apiGet("/api/providers");
    const status = await apiGet("/api/status");

    const types = await apiGet("/api/providers/types");

    const typeMap = Object.fromEntries(
        types.map(t => [t.type, t])
    );

    types.forEach(type => {
        registerProviderI18n(type.i18n);
    });

    providerMap = Object.fromEntries(
        providers.map(p => [
            p.id,
            {
                ...p,
                schema: typeMap[p.type]
            }
        ])
    );

    recordsState = Array.isArray(records) ? records : [];
    window.__recordsCache = recordsState;

    document.getElementById("view").innerHTML = `
        <div class="header">
            <h1>${t("records")}</h1>
            <button class="fab" id="openModal" ${providers.length === 0 ? "disabled" : ""}>+</button>
        </div>

        <div class="list">
            ${recordsState.length === 0
                ? `<div class="card muted">${t("no_records")}</div>`
                : recordsState.map(r => `
                    <div class="row row-records" data-id="${r.id}">
                        <div class="col domain">
                            <strong>${r.domain}</strong>
                        </div>

                        <div class="col provider">
                            ${ providers.find(p => p.id === r.provider_id).type }
                        </div>

                        <div class="col ip">
                            ${r.ip || "-"}
                        </div>

                        <div class="col status">
                            <span class="badge badge-${formatStatus(r.status).type}">
                             ${formatStatus(r.status).label}
                            </span>
                        </div>

                        <div class="row-actions">
                            <button class="icon-btn edit" data-id="${r.id}">
                                ${icons.edit()}
                            </button>

                            <button class="icon-btn delete" data-id="${r.id}">
                                ${icons.delete()}
                            </button>
                        </div>
                    </div>
                `).join("")
            }
        </div>

        ${modal()}
    `;

    document.getElementById("openModal").onclick = openModal;

    document.querySelectorAll(".edit").forEach(btn => {
        btn.onclick = () => openEdit(btn.dataset.id);
    });

    document.querySelectorAll(".delete").forEach(btn => {
        btn.onclick = () => handleDelete(btn.dataset.id);
    });
}

/* =========================
   SSE PATCH API (igual que dashboard)
========================= */

window.__recordsPatch = {
    upsert: upsertRecord,
    remove: removeRecord
};

/* =========================
   UPSERT (CREATE / UPDATE)
========================= */

function upsertRecord(record) {
    if (!record || !record.id) return;

    const id = String(record.id);
    const index = recordsState.findIndex(r => String(r.id) === id);

    if (index === -1) {
        recordsState.unshift(record);

        const list = document.querySelector(".list");
        if (!list) return;

        const wrapper = document.createElement("div");
        wrapper.innerHTML = rowHTML(record);

        const row = wrapper.firstElementChild;
        list.prepend(row);

        bindRow(record.id);
        return;
    }

    recordsState[index] = {
        ...recordsState[index],
        ...record
    };

    const row = document.querySelector(`.row[data-id="${id}"]`);
    if (!row) return;

    const domainEl = row.querySelector(".col.domain strong");
    if (record.domain && domainEl) domainEl.textContent = record.domain;

    const ipEl = row.querySelector(".col.ip");
    if (ipEl && record.ip !== undefined) {
        ipEl.textContent = record.ip ?? "-";
    }

    const badge = row.querySelector(".badge");
    if (badge && record.status) {
        const s = formatStatus(record.status);
        badge.className = `badge badge-${s.type}`;
        badge.textContent = s.label;
    }
}

/* =========================
   REMOVE
========================= */

function removeRecord(payload) {
    const id = payload?.id ?? payload?.record_id;
    if (!id) return;

    recordsState = recordsState.filter(r => r.id !== id);

    const row = document.querySelector(`.row[data-id="${id}"]`);
    if (row) row.remove();
}

/* =========================
   ROW HTML (TU UI ORIGINAL)
========================= */

function rowHTML(r) {
    const s = formatStatus(r.status);

    return `
        <div class="row" data-id="${r.id}">
            <div class="col domain">
                <strong>${r.domain}</strong>
            </div>

            <div class="col ip">
                ${r.ip || "-"}
            </div>

            <div class="col status">
                <span class="badge badge-${s.type}">
                    ${s.label}
                </span>
            </div>

            <div class="row-actions">
                <button class="icon-btn edit" data-id="${r.id}">
                    ${icons.edit()}
                </button>

                <button class="icon-btn delete" data-id="${r.id}">
                    ${icons.delete()}
                </button>
            </div>
        </div>
    `;
}

/* =========================
   BIND ROW EVENTS
========================= */

function bindRow(id) {
    const row = document.querySelector(`.row[data-id="${id}"]`);
    if (!row) return;

    const edit = row.querySelector(".edit");
    const del = row.querySelector(".delete");

    if (edit) edit.onclick = () => openEdit(id);
    if (del) del.onclick = () => handleDelete(id);
}

/* =========================
   MODAL
========================= */

function modal() {
    return `
        <div id="modal" class="modal hidden">
            <div class="modal-content">

                <h2 id="modalTitle">${t("new_record")}</h2>

                <label>${t("provider")}</label>
                <select id="provider_id">
                    <option value="">${t("select_provider")}</option>
                    ${providers.map(p => `
                        <option value="${p.id}">
                            ${p.name}
                        </option>
                    `).join("")}
                </select>

                <label>${t("domain")}</label>
                <input id="domain" type="text">

                <div id="fields"></div>

                <div class="modal-actions">
                    <button class="cancel" id="cancel">${t("cancel")}</button>
                    <button class="default" id="submit" disabled>${t("create")}</button>
                </div>

            </div>
        </div>
    `;
}

/* =========================
   OPEN CREATE
========================= */

function openModal() {
    const modal = document.getElementById("modal");
    if (!modal || providers.length === 0) return;

    editingRecordId = null;

    modal.classList.remove("hidden");

    document.getElementById("modalTitle").textContent = t("new_record");
    document.getElementById("submit").textContent = t("create");

    document.getElementById("provider_id").value = "";
    document.getElementById("domain").value = "";

    document.getElementById("provider_id").onchange = () => {
        renderFields();
        validate();
    };

    document.getElementById("domain").oninput = validate;

    document.getElementById("cancel").onclick = closeModal;
    document.getElementById("submit").onclick = submitRecord;

    renderFields();
    validate();
}

/* =========================
   OPEN EDIT
========================= */

function openEdit(id) {
    const records = window.__recordsCache || [];
    const record = records.find(r => String(r.id) === String(id));
    if (!record) return;

    editingRecordId = id;

    const modal = document.getElementById("modal");
    modal.classList.remove("hidden");

    document.getElementById("modalTitle").textContent = t("edit_record");
    document.getElementById("submit").textContent = t("save");

    document.getElementById("provider_id").value = record.provider_id;
    document.getElementById("domain").value = record.domain;

    renderFields();

    let payload = {};
    try {
        payload = typeof record.payload === "string"
            ? JSON.parse(record.payload)
            : (record.payload || {});
    } catch {
        payload = {};
    }

    requestAnimationFrame(() => {
        for (const key in payload) {
            const el = document.getElementById(key);
            if (el) el.value = payload[key];
        }
        validate();
    });

    document.getElementById("provider_id").onchange = () => {
        renderFields();
        validate();
    };

    document.getElementById("domain").oninput = validate;
    document.getElementById("cancel").onclick = closeModal;
    document.getElementById("submit").onclick = submitRecord;
}

/* =========================
   RENDER FIELDS / VALIDATION / PAYLOAD
========================= */

function renderFields() {
    const providerId = document.getElementById("provider_id").value;
    const container = document.getElementById("fields");

    const provider = providerMap[providerId];
    const schema = provider?.schema?.record_schema;

    if (!schema?.fields?.length) {
        container.innerHTML = "";
        return;
    }

    container.innerHTML = schema.fields.map(f => {
        const type = f.type === "password" ? "password" : "text";

        return `
            <label>${t(f.label_key)}</label>
            <input id="${f.key}" type="${type}">
        `;
    }).join("");

    setTimeout(() => {
        document.querySelectorAll("#fields input").forEach(el => {
            el.oninput = validate;
        });
    }, 0);
}

function validate() {
    const submit = document.getElementById("submit");
    const providerId = document.getElementById("provider_id").value;
    const domain = document.getElementById("domain").value?.trim();

    const provider = providerMap[providerId];
    const schema = provider?.schema?.record_schema;

    let valid = !!providerId && !!domain;

    if (schema?.fields?.length) {
        for (const f of schema.fields) {
            const el = document.getElementById(f.key);
            if (!el || !el.value?.trim()) valid = false;
        }
    }

    submit.disabled = !valid;
}

function buildPayload(providerId) {
    const provider = providerMap[providerId];
    const schema = provider?.schema?.record_schema;

    const payload = {};

    if (!schema?.fields) return payload;

    schema.fields.forEach(f => {
        const el = document.getElementById(f.key);
        if (el) payload[f.key] = el.value;
    });

    return payload;
}

async function submitRecord() {
    const providerId = document.getElementById("provider_id").value;
    const domain = document.getElementById("domain").value?.trim();

    const payload = buildPayload(providerId);


    if (editingRecordId) {
        await fetch(`/api/records/${editingRecordId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                domain,
                payload
            })
        });
    } else {
        await apiPost("/api/records", {
            provider_id: providerId,
            domain,
            payload,
            status: "pending"
        });
    }

    closeModal();
    loadRecords();
}

async function handleDelete(id) {
    const ok = await ui.confirm(t("confirm_delete_record"));
    if (!ok) return;

    await fetch(`/api/records/${id}`, { method: "DELETE" });

    loadRecords();
}

function closeModal() {
    const modal = document.getElementById("modal");
    if (modal) modal.classList.add("hidden");

    editingRecordId = null;
}

/* =========================
   ICONS
========================= */

function iconEdit() {
    return `
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
        <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25z" fill="currentColor"/>
        <path d="M20.71 7.04a1.003 1.003 0 0 0 0-1.42L18.37 3.29a1.003 1.003 0 0 0-1.42 0l-1.83 1.83 3.75 3.75 1.84-1.83z" fill="currentColor"/>
    </svg>`;
}

function iconDelete() {
    return `
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
        <path d="M6 7h12l-1 14H7L6 7z" fill="currentColor"/>
        <path d="M9 4h6l1 2H8l1-2z" fill="currentColor"/>
    </svg>`;
}