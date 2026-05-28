import { translations } from "./i18n.js";

const STORAGE_KEY = "locale";

let currentLocale = localStorage.getItem(STORAGE_KEY) || "es";

/* =========================
   PROVIDER I18N REGISTRY
========================= */
let providerI18n = {
    es: {},
    en: {}
};

export function registerProviderI18n(i18n) {
    if (!i18n) return;

    for (const lang of Object.keys(providerI18n)) {
        if (i18n[lang]) {
            Object.assign(providerI18n[lang], i18n[lang]);
        }
    }
}

/* =========================
   LOCALE CONTROL
========================= */
export function getLocale() {
    return currentLocale;
}

export function setLocale(locale) {
    currentLocale = locale;
    localStorage.setItem(STORAGE_KEY, locale);
}

/* =========================
   TRANSLATION ENGINE
========================= */
export function t(key) {
    const dict = translations[currentLocale] || translations.en;
    const providerDict = providerI18n[currentLocale] || {};

    return dict[key] || providerDict[key] || key;
}