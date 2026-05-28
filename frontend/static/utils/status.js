import { t } from "../i18n/locale.js";

export function formatStatus(status) {
    switch (status) {
        case "ok":
            return { label: t("status_ok"), type: "success" };
        case "up_to_date":
            return { label: t("status_up_to_date"), type: "success" };
        case "error":
            return { label: t("status_error"), type: "error" };
        case "pending":
            return {label: t("status_pending"), type: "warning"};
        default:
            return { label: status || "-", type: "muted" };
    }
}