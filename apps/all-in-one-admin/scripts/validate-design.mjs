import { readFile } from "node:fs/promises";
import { resolve } from "node:path";

const root = process.cwd();
const tokens = JSON.parse(await readFile(resolve(root, "design/figma.tokens.json"), "utf8"));
const manifest = JSON.parse(await readFile(resolve(root, "design/figma-screen-manifest.json"), "utf8"));

const requiredCollections = ["color", "spacing", "radius", "typography", "shadow", "motion"];
for (const collection of requiredCollections) {
  if (!tokens[collection] || typeof tokens[collection] !== "object") {
    throw new Error(`Coleção de tokens ausente: ${collection}`);
  }
}

const requiredPlatforms = new Set(["web", "mobile"]);
for (const platform of manifest.platforms ?? []) {
  requiredPlatforms.delete(platform.id);
  if (!Array.isArray(platform.frames) || platform.frames.length < 6) {
    throw new Error(`Manifesto insuficiente para ${platform.id}.`);
  }
}
if (requiredPlatforms.size > 0) {
  throw new Error(`Plataformas ausentes: ${[...requiredPlatforms].join(", ")}`);
}

const requiredComponents = ["AppShell", "Navigation", "MetricCard", "DataTable", "ApprovalQueue", "BottomNav"];
for (const component of requiredComponents) {
  if (!(manifest.components ?? []).some((item) => item.name === component)) {
    throw new Error(`Componente Figma obrigatório ausente: ${component}`);
  }
}

console.log("Tokens e manifesto Figma validados.");
