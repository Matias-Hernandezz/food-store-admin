import { defineConfig } from "vite";


// admin (Food-store-admin) — vite.config.ts
export default defineConfig({
  server: {
    host: "localhost",
    port: 5173,
    allowedHosts: ["admin.localtest.me"],
  },
});