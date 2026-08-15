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
  "dist/docs/architecture-public.md",
  "dist/docs/technical-operations-public.md",
  "dist/docs/modules.md",
  "dist/docs/roadmap-public.md",
  "dist/docs/privacy-and-security.md",
  "wrangler.jsonc",
];

for (const relative of required) {
  await access(path.join(root, relative));
}

const html = await readFile(path.join(root, "dist/index.html"), "utf8");
const headers = await readFile(path.join(root, "dist/_headers"), "utf8");
const config = JSON.parse(await readFile(path.join(root, "wrangler.jsonc"), "utf8"));
const pipeline = await readFile(path.resolve(root, "..", "..", "azure-pipelines.cloudflare.yml"), "utf8");
const prPipeline = await readFile(path.resolve(root, "..", "..", "azure-pipelines.pr.yml"), "utf8");

const checks = [
  [html.includes("<html lang=\"pt-BR\">"), "idioma pt-BR"],
  [html.includes("<title>All-in-One + Valley</title>"), "título público"],
  [html.includes("Organizar empresas por dentro."), "mensagem principal"],
  [
    headers.includes(
      "Content-Security-Policy: default-src 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'none'; form-action 'self'; img-src 'self' data:; script-src 'self'; style-src 'self'; connect-src 'self'; upgrade-insecure-requests",
    ),
    "CSP restritiva",
  ],
  [headers.includes("X-Content-Type-Options: nosniff"), "nosniff"],
  [config.name === "all-in-one-web", "projeto Pages"],
  [config.pages_build_output_dir === "./dist", "diretório de saída"],
  [
    /condition:\s*and\(succeeded\(\),\s*ne\(variables\['Build\.Reason'\],\s*'PullRequest'\),\s*eq\(variables\['Build\.SourceBranch'\],\s*'refs\/heads\/main'\)\)/.test(pipeline),
    "deploy restrito a main fora de PullRequest",
  ],
  [
    !/SYSTEM_PULLREQUEST_SOURCEBRANCH|refs\/pull\//.test(pipeline),
    "deploy sem destino derivado de metadados da PR",
  ],
  [/pr:\s*none/.test(pipeline), "pipeline privilegiado sem gatilho de PR"],
  [
    !/CLOUDFLARE_|wrangler\s+pages\s+deploy/.test(prPipeline),
    "pipeline de PR sem credenciais nem deploy",
  ],
];

const failed = checks.filter(([ok]) => !ok).map(([, label]) => label);
if (failed.length) {
  throw new Error(`Validação Cloudflare falhou: ${failed.join(", ")}`);
}

console.log("Integração Cloudflare Pages validada com sucesso.");
