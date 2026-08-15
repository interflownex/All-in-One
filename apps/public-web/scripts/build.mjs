import { copyFile, lstat, mkdir, readdir, realpath, rm } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const scriptPath = fileURLToPath(import.meta.url);
const defaultAppRoot = path.resolve(path.dirname(scriptPath), "..");
const defaultRepoRoot = path.resolve(defaultAppRoot, "../..");

export const publicDocs = [
  "overview.md",
  "architecture-public.md",
  "technical-operations-public.md",
  "modules.md",
  "roadmap-public.md",
  "privacy-and-security.md",
];

async function copyRegularTree(source, destination) {
  const metadata = await lstat(source);
  if (metadata.isSymbolicLink()) {
    throw new Error(`Link simbólico não permitido no conteúdo público: ${source}`);
  }
  if (metadata.isDirectory()) {
    await mkdir(destination, { recursive: true });
    const entries = await readdir(source);
    for (const entry of entries.sort()) {
      await copyRegularTree(path.join(source, entry), path.join(destination, entry));
    }
    return;
  }
  if (!metadata.isFile()) {
    throw new Error(`Tipo de arquivo não permitido no conteúdo público: ${source}`);
  }
  await mkdir(path.dirname(destination), { recursive: true });
  await copyFile(source, destination);
}

async function copyApprovedDocument(docsRoot, destination, document) {
  const source = path.join(docsRoot, document);
  const metadata = await lstat(source);
  if (metadata.isSymbolicLink()) {
    throw new Error(`Link simbólico não permitido na documentação pública: ${source}`);
  }
  if (!metadata.isFile()) {
    throw new Error(`Documento público não é um arquivo regular: ${source}`);
  }

  const resolvedDocsRoot = await realpath(docsRoot);
  const resolvedSource = await realpath(source);
  if (!resolvedSource.startsWith(`${resolvedDocsRoot}${path.sep}`)) {
    throw new Error(`Documento público fora do diretório aprovado: ${source}`);
  }
  await copyFile(resolvedSource, path.join(destination, "docs", document));
}

export async function build({ repoRoot = defaultRepoRoot, appRoot = defaultAppRoot } = {}) {
  const source = path.join(appRoot, "public");
  const destination = path.join(appRoot, "dist");
  const docsRoot = path.join(repoRoot, "docs");

  await rm(destination, { recursive: true, force: true });
  await mkdir(destination, { recursive: true });
  await copyRegularTree(source, destination);
  await mkdir(path.join(destination, "docs"), { recursive: true });

  for (const document of publicDocs) {
    await copyApprovedDocument(docsRoot, destination, document);
  }

  return destination;
}

if (process.argv[1] && path.resolve(process.argv[1]) === scriptPath) {
  const destination = await build();
  console.log(`Cloudflare Pages build concluída em ${destination}`);
}
