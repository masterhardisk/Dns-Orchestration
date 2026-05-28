import { apiGet, apiPost } from "../api.js";
import { t, registerProviderI18n } from "../i18n/locale.js";
import { icons } from "../utils/icons.js";
import { ui } from "../ui/index.js";

let providers = [];
let providerSchemas = {};
let recordsCountMap = {};
let records = [];
let editingProviderId = null;

export async function loadProviders() {
    providers = await apiGet("/api/providers");
    records = await apiGet("/api/records");
    const types = await apiGet("/api/providers/types");

    types.forEach(type => {
        registerProviderI18n(type.i18n);
    });

    providerSchemas = Object.fromEntries(
        types.map(t => [t.type, t])
    );

    recordsCountMap = records.reduce((acc, r) => {
        acc[r.provider_id] = (acc[r.provider_id] || 0) + 1;
        return acc;
    }, {});

    document.getElementById("view").innerHTML = `
        <div class="header">
            <h1>${t("providers")}</h1>
            <button class="fab" id="openModal">+</button>
        </div>

        <div class="list">
            ${providers.length === 0
                ? `<div class="card muted">${t("no_providers")}</div>`
                : providers.map(p => `
                    <div class="row row-providers" data-id="${p.id}">
                        <div class="col">
                            <strong>${p.name}</strong>
                            <div class="muted">${p.type}</div>
                        </div>

                        <div class="row-actions">
                            <button class="icon-btn edit" data-id="${p.id}">
                                ${icons.edit()}
                            </button>

                            <button
                                class="icon-btn delete"
                                data-id="${p.id}"
                            >
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
   MODAL
========================= */

function modal() {
    return `
        <div id="modal" class="modal hidden">
            <div class="modal-content">

                <h2 id="modalTitle">${t("new_provider")}</h2>

                <label>${t("type")}</label>
                <select id="type"></select>

                <label>${t("name")}</label>
                <input id="provider_name" type="text">

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
    if (!modal) return;

    editingProviderId = null;

    modal.classList.remove("hidden");

    document.getElementById("cancel").onclick = closeModal;
    document.getElementById("submit").onclick = submit;

    const typeSelect = document.getElementById("type");

    const providerTypes = Object.keys(providerSchemas);

    typeSelect.innerHTML = providerTypes
        .map(type => `<option value="${type}">${type}</option>`)
        .join("");

    if (providerTypes.length > 0) {
        typeSelect.value = providerTypes[0];
    }

    typeSelect.onchange = () => {
        renderFields();
        validateForm();
    };

    document.getElementById("provider_name").oninput = validateForm;

    renderFields();
    validateForm();
}

/* =========================
   OPEN EDIT
========================= */

function openEdit(id) {
    const provider = providers.find(p => String(p.id) === String(id));
    if (!provider) return;

    editingProviderId = id;

    const modal = document.getElementById("modal");
    modal.classList.remove("hidden");

    document.getElementById("cancel").onclick = closeModal;
    document.getElementById("submit").onclick = submit;

    document.getElementById("modalTitle").textContent = t("edit_provider");
    document.getElementById("submit").textContent = t("save");

    const typeSelect = document.getElementById("type");

    const providerTypes = Object.keys(providerSchemas);

    typeSelect.innerHTML = providerTypes
        .map(type => `<option value="${type}">${type}</option>`)
        .join("");

    typeSelect.value = provider.type;

    document.getElementById("provider_name").value = provider.name;

    typeSelect.onchange = () => {
        renderFields();
        validateForm();
    };

    renderFields();

    let credentials = {};
    try {
        credentials = provider.credentials || {};
    } catch {
        credentials = {};
    }

    requestAnimationFrame(() => {
        Object.entries(credentials).forEach(([key, value]) => {
            const el = document.getElementById(key);
            if (el) el.value = value;
        });
        validateForm();
    });

    document.getElementById("provider_name").oninput = validateForm;
}

/* =========================
   FIELDS + TOGGLE PASSWORD
========================= */
function renderFields() {
    const type = document.getElementById("type").value;
    const container = document.getElementById("fields");

    const schema = providerSchemas[type]?.provider_schema;

    if (!schema?.fields?.length) {
        container.innerHTML = "";
        return;
    }

    container.innerHTML = schema.fields.map(f => {
        const id = f.key;

        if (f.type === "password") {
            return `
                <div>
                    <label>${t(f.label_key)}</label>
                </div>

                <div class="input-with-toggle">
                    <input id="${id}" type="password" class="field-input">

                    <button class="toggle-visibility" data-target="${id}">
                        ${icons.eye()}
                    </button>
                </div>
            `;
        }

        return `
            <label>${t(f.label_key)}</label>
            <input id="${id}" type="text">
        `;
    }).join("");

    setTimeout(() => {
        document.querySelectorAll("#fields input").forEach(el => {
            el.oninput = validateForm;
        });

        document.querySelectorAll(".toggle-visibility").forEach(btn => {
            btn.onclick = () => {
                const target = document.getElementById(btn.dataset.target);
                if (!target) return;

                const hidden = target.type === "password";
                target.type = hidden ? "text" : "password";

                btn.innerHTML = hidden ? icons.eyeOff() : icons.eye();
            };
        });
    }, 0);
}

/* =========================
   VALIDATION
========================= */

function validateForm() {
    const submit = document.getElementById("submit");

    const name = document.getElementById("provider_name")?.value?.trim();
    const type = document.getElementById("type")?.value;

    const schema = providerSchemas[type]?.provider_schema;

    let valid = !!name;

    if (schema) {
        for (const f of schema.fields) {
            const el = document.getElementById(f.key);
            if (!el || !el.value?.toString().trim()) {
                valid = false;
            }
        }
    }

    submit.disabled = !valid;
}

/* =========================
   BUILD
========================= */

function buildCredentials(type) {
    const schema = providerSchemas[type]?.provider_schema;

    const credentials = {};

    if (!schema) return credentials;

    schema.fields.forEach(f => {
        const el = document.getElementById(f.key);
        if (!el) return;

        credentials[f.key] = el.value;
    });

    return credentials;
}

/* =========================
   SUBMIT (CREATE / UPDATE)
========================= */

async function submit() {
    const type = document.getElementById("type").value;
    const name = document.getElementById("provider_name").value?.trim();
    if (!name) return;

    const credentials = buildCredentials(type);

    if (editingProviderId) {
        await fetch(`/api/providers/${editingProviderId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, type, credentials })
        });
    } else {
        await apiPost("/api/providers", {
            name,
            type,
            credentials
        });
    }

    closeModal();
    loadProviders();
}

/* =========================
   DELETE
========================= */

async function handleDelete(id) {

    const ok = await ui.confirm(t("confirm_delete_provider"));
    if (!ok) return;

    const res = await fetch(`/api/providers/${id}`, {
        method: "DELETE"
    });

    if (res.status === 409) {
        const data = await res.json().catch(() => ({}));

        ui.alert(
            data.message ||
            t("cannot_delete_provider_has_records")
        );
        return;
    }

    if (!res.ok) {
        ui.alert(t("delete_failed"));
        return;
    }

    loadProviders();
}

function closeModal() {
    const modal = document.getElementById("modal");
    if (modal) modal.classList.add("hidden");
    editingProviderId = null;
}

