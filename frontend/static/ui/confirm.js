export function confirm(message) {
    console.log("CONFIRM CALLED", message);

    const backdrop = document.getElementById("confirm-backdrop");
    const msg = document.getElementById("confirm-message");
    const ok = document.getElementById("confirm-ok");
    const cancel = document.getElementById("confirm-cancel");

    console.log("backdrop", backdrop);
    console.log("msg", msg);
    console.log("ok", ok);
    console.log("cancel", cancel);

    if (!backdrop || !msg || !ok || !cancel) {
        console.error("CONFIRM UI NOT MOUNTED PROPERLY");
        return Promise.resolve(false);
    }

    return new Promise((resolve) => {

        msg.textContent = message;
        backdrop.classList.remove("hidden");

        const cleanup = () => {
            backdrop.classList.add("hidden");
            ok.onclick = null;
            cancel.onclick = null;
        };

        ok.onclick = () => {
            cleanup();
            resolve(true);
        };

        cancel.onclick = () => {
            cleanup();
            resolve(false);
        };
    });
}