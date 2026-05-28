class Router {
    constructor() {
        this.routes = new Map();
    }

    register(name, handler) {
        this.routes.set(name, handler);
    }

    async navigate(route) {
        const handler = this.routes.get(route);

        if (!handler) {
            console.error("Route not found:", route);
            return;
        }

        await handler();
    }

    init() {
        const route = location.hash.replace("#/", "") || "dashboard";

        window.addEventListener("hashchange", () => {
            const r = location.hash.replace("#/", "") || "dashboard";
            this.navigate(r);
        });

        this.navigate(route);
    }
}

export const router = new Router();