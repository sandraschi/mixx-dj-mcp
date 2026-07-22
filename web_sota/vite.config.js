import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
export default defineConfig({
    plugins: [react(), tailwindcss()],
    server: {
        port: 11117,
        host: true,
        proxy: {
            "/api": {
                target: "http://127.0.0.1:11116",
                changeOrigin: true,
            },
            "/mcp": {
                target: "http://127.0.0.1:11116",
                changeOrigin: true,
                ws: true,
            },
        },
    },
    build: {
        outDir: "dist",
        sourcemap: true,
    },
});
