import { t } from "./i18n/locale.js";
import { connectEvents, subscribeEvents } from "./events.js";
import { router } from "./router.js";
import { loadDashboard } from "./views/dashboard.js";
import { loadProviders } from "./views/providers.js";
import { loadRecords } from "./views/records.js";
import { loadSettings } from "./views/settings.js";
import { icons } from "./utils/icons.js";

/* =========================
   SIDEBAR
========================= */

async function loadSidebar() {
    const res = await fetch("/static/layout/sidebar.html");
    let html = await res.text();

    html = html
        .replaceAll("{{dashboard}}", t("dashboard"))
        .replaceAll("{{providers}}", t("providers"))
        .replaceAll("{{records}}", t("records"))
        .replaceAll("{{settings}}", t("settings"));

    document.getElementById("sidebar").innerHTML = html;

    document.getElementById("iconDashboard").innerHTML = icons.dashboard();
    document.getElementById("iconProviders").innerHTML = icons.providers();
    document.getElementById("iconRecords").innerHTML = icons.records();
    document.getElementById("iconSettings").innerHTML = icons.settings();

    document.getElementById("sidebarToggleIcon").innerHTML = icons.sidebar();
    

    highlightActive();
    initSidebarToggle();
}
window.__rerenderSidebar = loadSidebar;

function initSidebarToggle() {
    const btn = document.getElementById("sidebarToggle");
    const sidebar = document.getElementById("sidebar");

    if (!btn || !sidebar) return;

    const state = localStorage.getItem("sidebar") || "open";

    if (state === "collapsed") {
        sidebar.classList.add("collapsed");
    }

    btn.onclick = () => {
        const isMobile = window.innerWidth <= 900;

        if (isMobile) {
            sidebar.classList.toggle("open");
        } else {
            sidebar.classList.toggle("collapsed");
        }
        const isCollapsed = sidebar.classList.contains("collapsed");
        localStorage.setItem("sidebar", isCollapsed ? "collapsed" : "open");
        updateSidebarLogo();
    };
    updateSidebarLogo();
}

document.addEventListener("DOMContentLoaded", initSidebarToggle);

function highlightActive() {
    const hash = window.location.hash || "#/dashboard";
    document.querySelectorAll(".nav-link").forEach(a => {
        a.classList.remove("active");
        if (a.getAttribute("href") === hash) {
            a.classList.add("active");
        }
    });
}

function updateSidebarLogo() {
    const sidebar = document.getElementById("sidebar");
    if (!sidebar) return;

    const isCollapsed = sidebar.classList.contains("collapsed");
    const theme = document.body.dataset.theme || "dark";

    const fullLogo = document.querySelector(".logo-full");
    const iconLogo = document.querySelector(".logo-icon");

    if (!fullLogo || !iconLogo) return;

    if (isCollapsed) {
        iconLogo.src = "/static/images/dnsO-onlylogo.png"
    } else {
        fullLogo.src =
            theme === "light"
                ? "/static/images/dnsO-logo.svg"
                : "/static/images/dnsO-logo-dark.svg";
    }
}
window.__rerenderSidebarLogo = updateSidebarLogo;

/* =========================
   TABBAR
========================= */
async function loadTabbar() {
    const res = await fetch("/static/layout/tabbar.html");
    let html = await res.text();

    html = html
        .replaceAll("{{dashboard}}", t("dashboard"))
        .replaceAll("{{providers}}", t("providers"))
        .replaceAll("{{records}}", t("records"))
        .replaceAll("{{settings}}", t("settings"));

    document.getElementById("mobile-tabbar").innerHTML = html;

    document.getElementById("tabbarDashboard").innerHTML = icons.dashboard();
    document.getElementById("tabbarProviders").innerHTML = icons.providers();
    document.getElementById("tabbarRecords").innerHTML = icons.records();
    document.getElementById("tabbarSettings").innerHTML = icons.settings();

    document.body.classList.add("has-mobile-tabbar");

    highlightActiveTabbar();
}
window.__rerenderSidebar = loadTabbar;

function highlightActiveTabbar() {
    const hash = window.location.hash || "#/dashboard";
    document.querySelectorAll(".mobile-tabbar .tab-item")
        .forEach(item => {
            item.classList.remove("active");
            if (item.getAttribute("href") === hash) {
                item.classList.add("active");
            }
        });
}
/* =========================
   EVENT HANDLER (REALTIME UI)
========================= */
function handleEvent(event) {
    console.log("event", event)
    switch (event.type) {
        // -------------------------
        // IP GLOBAL
        // -------------------------
        case "IP_CHANGED":
            window.__dashboardPatch?.ip({
                new_ip: event.payload.new_ip
            });
            break;
        // -------------------------
        // RECORD LIFECYCLE
        // -------------------------
        case "RECORD_CREATED":
            window.__dashboardPatch?.record(event.payload);
            window.__recordsPatch?.upsert(event.payload);
            break;

        case "RECORD_UPDATED":
            window.__dashboardPatch?.record(event.payload);
            window.__recordsPatch?.upsert(event.payload);
            break;

        case "RECORD_DELETED":
            window.__dashboardPatch?.delete({
                id: event.payload.id ?? event.payload.record_id
            });
             window.__recordsPatch?.upsert(event.payload);
            break;
        // -------------------------
        // ERROR (solo patch si hay record)
        // -------------------------
        case "ERROR":
            window.__dashboardPatch?.record(event.payload);
             window.__recordsPatch?.upsert(event.payload);
            break;
        default:
            break;
    }
}

export function formatInterval(sec) {

    let key;

    if (sec < 60) {
        key = sec === 1 ? "sec_one" : "sec_other";
        return `${sec} ${t(key)}`;
    }

    if (sec % 3600 === 0) {
        const value = sec / 3600;
        key = value === 1 ? "hour_one" : "hour_other";
        return `${value} ${t(key)}`;
    }

    const value = sec / 60;
    key = value === 1 ? "min_one" : "min_other";

    return `${value} ${t(key)}`;
}

export function formatProvider(p) {
    switch (p) {
        case "auto": return "Automatic";
        case "ipify": return "IPify";
        case "ipleak": return "IPLeak";
        default: return p;
    }
}
/* =========================
   ROUTER
========================= */

router.register("dashboard", loadDashboard);
router.register("providers", loadProviders);
router.register("records", loadRecords);
router.register("settings", loadSettings);

/* =========================
   BOOT
========================= */

await loadSidebar();
await loadTabbar();
router.init();

window.addEventListener("hashchange", () => {
    highlightActiveTabbar();
    highlightActive();
});

subscribeEvents(handleEvent);
connectEvents();
