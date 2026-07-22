import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/services": { target: "http://localhost:8100", changeOrigin: true },
      "/finance": { target: "http://localhost:8100", changeOrigin: true },
      "/document": { target: "http://localhost:8100", changeOrigin: true },
    },
  },
});
