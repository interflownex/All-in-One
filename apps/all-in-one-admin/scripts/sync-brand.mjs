import { copyFile, mkdir } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const appRoot = resolve(here, "..");
const source = resolve(appRoot, "../../assets/brand/all-in-one-logo-official.png");
const target = resolve(appRoot, "public/brand/all-in-one-logo-official.png");

await mkdir(dirname(target), { recursive: true });
try {
  await copyFile(source, target);
  console.log("Marca oficial sincronizada a partir do ativo canônico.");
} catch (error) {
  console.error(`Não foi possível sincronizar a marca oficial: ${error.message}`);
  process.exitCode = 1;
}
