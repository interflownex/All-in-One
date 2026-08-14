import { cp, mkdir, rm } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const repository = path.resolve(root, "../..");
const source = path.join(root, "public");
const destination = path.join(root, "dist");
const publicDocs = [
  "overview.md",
  "architecture-public.md",
  "technical-operations-public.md",
  "modules.md",
  "roadmap-public.md",
  "privacy-and-security.md",
];

await rm(destination, { recursive: true, force: true });
await mkdir(destination, { recursive: true });
await cp(source, destination, { recursive: true });
await mkdir(path.join(destination, "docs"), { recursive: true });

for (const document of publicDocs) {
  await cp(
    path.join(repository, "docs", document),
    path.join(destination, "docs", document),
  );
}

console.log(`Cloudflare Pages build concluída em ${destination}`);
