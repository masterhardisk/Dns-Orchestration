import { apiGet, apiPost } from "../api.js";
import { t, setLocale, getLocale } from "../i18n/locale.js";
import { icons } from "../utils/icons.js";
import { ui } from "../ui/index.js";

/* =========================
   STATE
========================= */
let settingsState = {
    theme: localStorage.getItem("theme") || "dark",
    language: localStorage.getItem("language") || getLocale?.() || "es",
    telegram: {
        enabled: false,
        bot_token: "",
        chat_id: ""
    }
};

/* =========================
   LOAD
========================= */
export async function loadSettings() {

    try {
        const remote = await apiGet("/api/settings/telegram");

        settingsState.telegram = {
            enabled: remote?.enabled ?? false,
            bot_token: remote?.bot_token ?? "",
            chat_id: remote?.chat_id ?? ""
        };

    } catch (e) {
        console.error("settings load failed", e);
    }

    renderSettings();
    bindEvents();
}

/* =========================
   RENDER
========================= */

function renderSettings() {

    document.getElementById("view").innerHTML = `
        <div class="header">
            <h1>${t("settings")}</h1>
        </div>

        <div class="card">

            <h2>${t("appearance")}</h2>

            <div class="settings-group">

                <label>${t("language")}</label>

                <select id="language">
                    <option value="es" ${settingsState.language === "es" ? "selected" : ""}>
                        Español
                    </option>

                    <option value="en" ${settingsState.language === "en" ? "selected" : ""}>
                        English
                    </option>
                </select>

                <label>${t("theme")}</label>

                <select id="theme">
                    <option value="dark" ${settingsState.theme === "dark" ? "selected" : ""}>
                        ${t("dark_mode")}
                    </option>

                    <option value="light" ${settingsState.theme === "light" ? "selected" : ""}>
                        ${t("light_mode")}
                    </option>
                </select>

            </div>
        </div>

        <div class="card">
            <h2>Telegram</h2>
            <div class="settings-group">
                <label class="switch-row">
                    <span>${t("enable_telegram")}</span>
                    <input
                        type="checkbox"
                        id="telegram_enabled"
                        ${settingsState.telegram.enabled ? "checked" : ""}
                    />
                </label>
                <label>${t("telegram_bot_token")}</label>
                <div class="input-with-toggle">
                    <input
                        type="password"
                        id="telegram_bot_token"
                        value="${settingsState.telegram.bot_token || ""}"
                    />
                
                    <button class="toggle-visibility" data-target="telegram_bot_token">
                        ${icons.eye()}
                    </button>
                </div>

                <label>${t("telegram_chat_id")}</label>
                <input
                    type="text"
                    id="telegram_chat_id"
                    value="${settingsState.telegram.chat_id || ""}"
                />

            </div>

            <div class="settings-actions">
                <button class="default" id="saveSettings">
                    ${t("save")}
                </button>
            </div>
        </div>
    `;

    document.querySelectorAll(".toggle-visibility").forEach(btn => {
            btn.onclick = () => {
                const target = document.getElementById(btn.dataset.target);
                if (!target) return;

                const hidden = target.type === "password";
                target.type = hidden ? "text" : "password";

                btn.innerHTML = hidden ? icons.eyeOff() : icons.eye();
            };
        });
}

/* =========================
   EVENTS
========================= */

function bindEvents() {

    const language = document.getElementById("language");
    const theme = document.getElementById("theme");
    const save = document.getElementById("saveSettings");

    language.onchange = () => {
        settingsState.language = language.value;

        localStorage.setItem("language", language.value);

        if (setLocale) {
            setLocale(language.value);
        }
        window.__rerenderSidebar?.();
        renderSettings();
        bindEvents();
    };

    theme.onchange = () => {
        settingsState.theme = theme.value;
        localStorage.setItem("theme", theme.value);
        applyTheme(theme.value);
        window.__rerenderSidebarLogo?.();
    };
    save.onclick = saveSettings;
}

/* =========================
   SAVE
========================= */

async function saveSettings() {
    settingsState.telegram.enabled =
        document.getElementById("telegram_enabled")?.checked || false;
    settingsState.telegram.bot_token =
        document.getElementById("telegram_bot_token")?.value?.trim() || "";
    settingsState.telegram.chat_id =
        document.getElementById("telegram_chat_id")?.value?.trim() || "";
    try {
        await apiPost("/api/settings/telegram", settingsState.telegram);
        ui.alert(t("telegram_settings_saved"));
    } catch (e) {
        console.error(e);
        ui.alert(t("telegram_save_failed"));
    }
}

/* =========================
   APPLY THEME
========================= */
function applyTheme(theme) {
    document.body.dataset.theme = theme;
    localStorage.setItem("theme", theme);
}

/* =========================
   INIT THEME
========================= */
applyTheme(settingsState.theme);