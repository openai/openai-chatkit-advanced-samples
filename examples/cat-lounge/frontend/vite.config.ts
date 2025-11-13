import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

const backendTarget = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5170,
    host: "0.0.0.0",
    proxy: {
      "/chatkit": {
        target: backendTarget,
        changeOrigin: true,
      },
      "/cats": {
        target: backendTarget,
        changeOrigin: true,
      },
    },
    // For production deployments, you need to add your public domains to this list
    allowedHosts: [
      // You can remove these examples added just to demonstrate how to configure the allowlist
      ".ngrok.io",
      ".trycloudflare.com",
    ],
  },
});
