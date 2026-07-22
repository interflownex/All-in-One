import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/gateway": {
        target: "http://localhost:8100",
        changeOrigin: true,
      },
    },
  },
});
