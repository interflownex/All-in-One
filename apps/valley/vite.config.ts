import { defineConfig, type Plugin } from "vite";
import react from "@vitejs/plugin-react";

function flutterDemoRelease(): Plugin {
  const enabled = process.env.VITE_VALLEY_ALLOW_DEMO === "true";
  let transformed = false;
  const source =
    'import.meta.env.DEV && import.meta.env.VITE_VALLEY_ALLOW_DEMO === "true"';
  const target = 'import.meta.env.VITE_VALLEY_ALLOW_DEMO === "true"';

  return {
    name: "valley-flutter-demo-release",
    enforce: "pre",
    transform(code, id) {
      if (!enabled || !id.endsWith("/src/lib/valleyPlatform.ts")) return null;
      if (!code.includes(source)) {
        throw new Error("Contrato do modo demonstrativo Valley não encontrado.");
      }
      transformed = true;
      return code.replace(source, target);
    },
    buildEnd() {
      if (enabled && !transformed) {
        throw new Error("Build Flutter não habilitou o modo demonstrativo.");
      }
    },
  };
}

export default defineConfig({
  base: "./",
  plugins: [flutterDemoRelease(), react()],
  server: {
    proxy: {
      "/gateway": {
        target: "http://localhost:8100",
        changeOrigin: true,
      },
    },
  },
});
