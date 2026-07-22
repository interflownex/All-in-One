import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/riders": { target: "http://localhost:8100", changeOrigin: true },
      "/delivery": { target: "http://localhost:8100", changeOrigin: true },
      "/mobility": { target: "http://localhost:8100", changeOrigin: true },
      "/finance": { target: "http://localhost:8100", changeOrigin: true },
    },
  },
});
