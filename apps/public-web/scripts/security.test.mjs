import assert from "node:assert/strict";
import { mkdtemp, mkdir, readFile, readdir, rm, symlink, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";

import { build } from "./build.mjs";

const docs = [
  "overview.md",
  "architecture-public.md",
  "technical-operations-public.md",
  "modules.md",
  "roadmap-public.md",
  "privacy-and-security.md",
];

async function makeFixture() {
  const root = await mkdtemp(path.join(os.tmpdir(), "aio-pages-security-"));
  const appRoot = path.join(root, "apps", "public-web");
  await mkdir(path.join(appRoot, "public"), { recursive: true });
  await mkdir(path.join(root, "docs"), { recursive: true });

  const publicFiles = {
    "index.html": '<html lang="pt-BR"><title>All-in-One + Valley</title><body>Organizar empresas por dentro.</body></html>',
    "styles.css": "body { color: white; }\n",
    "_headers": "/*\n  Content-Security-Policy: default-src 'self'\n  X-Content-Type-Options: nosniff\n",
    "_redirects": "/documentacao /#documentacao 302\n",
  };

  await Promise.all(
    Object.entries(publicFiles).map(([name, content]) =>
      writeFile(path.join(appRoot, "public", name), content, "utf8"),
    ),
  );
  await Promise.all(
    docs.map((name) => writeFile(path.join(root, "docs", name), `# ${name}\n`, "utf8")),
  );

  return { root, appRoot };
}

async function rejectsPublicSymlink() {
  const fixture = await makeFixture();
  const sentinel = path.join(fixture.root, "sentinel.txt");
  await writeFile(sentinel, "nao-publicar", "utf8");
  await symlink(sentinel, path.join(fixture.appRoot, "public", "leak.txt"));

  try {
    await assert.rejects(
      build({ repoRoot: fixture.root, appRoot: fixture.appRoot }),
      /link simbólico/i,
      "o build deve recusar links dentro de public/",
    );
  } finally {
    await rm(fixture.root, { recursive: true, force: true });
  }
}

async function rejectsAllowlistedDocumentSymlink() {
  const fixture = await makeFixture();
  const sentinel = path.join(fixture.root, "sentinel.txt");
  await writeFile(sentinel, "nao-publicar", "utf8");
  await rm(path.join(fixture.root, "docs", "overview.md"));
  await symlink(sentinel, path.join(fixture.root, "docs", "overview.md"));

  try {
    await assert.rejects(
      build({ repoRoot: fixture.root, appRoot: fixture.appRoot }),
      /link simbólico/i,
      "o build deve recusar links nos documentos allowlisted",
    );
  } finally {
    await rm(fixture.root, { recursive: true, force: true });
  }
}

async function copiesOnlyApprovedRegularFiles() {
  const fixture = await makeFixture();

  try {
    const dist = await build({ repoRoot: fixture.root, appRoot: fixture.appRoot });
    const rootFiles = (await readdir(dist)).sort();
    const copiedDocs = (await readdir(path.join(dist, "docs"))).sort();

    assert.deepEqual(rootFiles, ["_headers", "_redirects", "docs", "index.html", "styles.css"]);
    assert.deepEqual(copiedDocs, [...docs].sort());
    assert.equal(await readFile(path.join(dist, "docs", "overview.md"), "utf8"), "# overview.md\n");
  } finally {
    await rm(fixture.root, { recursive: true, force: true });
  }
}

await rejectsPublicSymlink();
await rejectsAllowlistedDocumentSymlink();
await copiesOnlyApprovedRegularFiles();
console.log("Regressões de segurança do build aprovadas.");
