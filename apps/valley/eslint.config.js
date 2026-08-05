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
      "src/components/ProductFeed.tsx",
      "src/views/ProductViews.tsx",
      "src/views/JobsView.tsx",
      "src/views/OperationalViews.tsx",
    ],
    rules: {
      // Estas telas sincronizam observadores de viewport, hints de navegação e
      // respostas assíncronas. Os efeitos possuem dependências delimitadas e
      // atualizam estado somente para refletir eventos externos ou fallback.
      "react-hooks/set-state-in-effect": "off",
    },
  },
]);
