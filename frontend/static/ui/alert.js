export function alert(message) {
    return new Promise((resolve) => {
        const backdrop = document.getElementById("confirm-backdrop");
        const msg = document.getElementById("confirm-message");
        const ok = document.getElementById("confirm-ok");
        const cancel = document.getElementById("confirm-cancel");

        msg.textContent = message;

        // adaptar UI a modo alert
        cancel.style.display = "none";
        ok.textContent = "OK";
        ok.classList.remove("cancel");
        ok.classList.add("default");

        backdrop.classList.remove("hidden");

        const cleanup = () => {
            backdrop.classList.add("hidden");

            // restaurar estado original (IMPORTANTE)
            cancel.style.display = "";
            ok.textContent = "Eliminar";
            ok.classList.remove("default");
            ok.classList.add("cancel");

            ok.onclick = null;
        };

        ok.onclick = () => {
            cleanup();
            resolve();
        };
    });
}