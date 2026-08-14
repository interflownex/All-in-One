import { access, readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const required = [
  "dist/index.html",
  "dist/styles.css",
  "dist/_headers",
  "dist/_redirects",
  "dist/docs/overview.md",
  "dist/docs/privacy-and-security.md",
  "wrangler.jsonc",
];

for (const relative of required) {
  await access(path.join(root, relative));
}

const html = await readFile(path.join(root, "dist/index.html"), "utf8");
const headers = await readFile(path.join(root, "dist/_headers"), "utf8");
const config = JSON.parse(await readFile(path.join(root, "wrangler.jsonc"), "utf8"));

const checks = [
  [html.includes("<html lang=\"pt-BR\">"), "idioma pt-BR"],
  [html.includes("<title>All-in-One + Valley</title>"), "título público"],
  [html.includes("Organizar empresas por dentro."), "mensagem principal"],
  [headers.includes("Content-Security-Policy:"), "CSP"],
  [headers.includes("X-Content-Type-Options: nosniff"), "nosniff"],
  [config.name === "all-in-one-web", "projeto Pages"],
  [config.pages_build_output_dir === "./dist", "diretório de saída"],
];

const failed = checks.filter(([ok]) => !ok).map(([, label]) => label);
if (failed.length) {
  throw new Error(`Validação Cloudflare falhou: ${failed.join(", ")}`);
}

console.log("Integração Cloudflare Pages validada com sucesso.");
