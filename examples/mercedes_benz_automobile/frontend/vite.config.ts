import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const backendTarget = process.env.BACKEND_URL ?? "http://127.0.0.1:8004";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174,
    host: "0.0.0.0",
    proxy: {
      "/mercedes": {
        target: backendTarget,
        changeOrigin: true,
      },
    },
    allowedHosts: [
      ".ngrok.io",
      ".trycloudflare.com",
    ],
  },
});
