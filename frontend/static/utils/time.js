import { t } from "../i18n/locale.js";

export function timeAgo(seconds) {
    let value = seconds;
    let unit = "second";
    if (seconds >= 86400) {
        value = Math.floor(seconds / 86400);
        unit = "day";
    } else if (seconds >= 3600) {
        value = Math.floor(seconds / 3600);
        unit = "hour";
    } else if (seconds >= 60) {
        value = Math.floor(seconds / 60);
        unit = "minute";
    }
    const unitLabel = t(`unit_${unit}`);
    const plural = value !== 1 ? t("plural_s") : "";
    return t("time_ago")
        .replace("{{n}}", value)
        .replace("{{unit}}", unitLabel + plural);
}