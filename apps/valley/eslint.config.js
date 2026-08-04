import js from "@eslint/js";
import globals from "globals";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import tseslint from "typescript-eslint";
import { defineConfig, globalIgnores } from "eslint/config";

export default defineConfig([
  globalIgnores(["dist"]),
  {
    files: ["**/*.{ts,tsx}"],
    extends: [
      js.configs.recommended,
      tseslint.configs.recommended,
      reactHooks.configs.flat.recommended,
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      globals: globals.browser,
    },
  },
  {
    files: [
      "src/views/ProductViews.tsx",
      "src/views/JobsView.tsx",
      "src/views/OperationalViews.tsx",
    ],
    rules: {
      // Estas telas sincronizam hints de navegação e respostas assíncronas do servidor.
      // Os efeitos possuem dependências delimitadas e não atualizam a própria dependência.
      "react-hooks/set-state-in-effect": "off",
    },
  },
]);
