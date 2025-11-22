import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

const backendTarget = process.env.BACKEND_URL ?? "http://127.0.0.1:8003";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: "0.0.0.0",
    proxy: {
      "/chatkit": {
        target: backendTarget,
        changeOrigin: true,
      },
    },
  },
});
