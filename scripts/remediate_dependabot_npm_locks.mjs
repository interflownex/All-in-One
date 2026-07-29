#!/usr/bin/env node

import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

const repositoryRoot = resolve(import.meta.dirname, "..");

const reactRouterLocks = [
  "apps/all-in-one-business/package-lock.json",
  "apps/all-in-one-user/package-lock.json",
  "apps/all-in-one/package-lock.json",
];

const postcssLocks = [
  ...reactRouterLocks,
  "apps/all-in-one-health/package-lock.json",
  "apps/all-in-one-mobility/package-lock.json",
  "apps/all-in-one-riders/package-lock.json",
  "apps/all-in-one-services/package-lock.json",
  "apps/valley/package-lock.json",
  "apps/valley_business/package-lock.json",
  "apps/valley_rider/package-lock.json",
  "desktop/valley-erp/package-lock.json",
];

const braceExpansionLocks = [
  ...reactRouterLocks,
  "apps/valley/package-lock.json",
  "apps/valley_business/package-lock.json",
  "apps/valley_rider/package-lock.json",
  "desktop/valley-erp/package-lock.json",
];

const reactRouter = {
  version: "7.18.2",
  resolved: "https://registry.npmjs.org/react-router/-/react-router-7.18.2.tgz",
  integrity:
    "sha512-aUVMjFm3GAPTTZL7oYr5E7ETiqfQCHRLH+B+5afnICvf0r7kkK4eR6SMuwbSTJw/7t+12khT/Kahij49fqOCIg==",
};

const reactRouterDom = {
  version: "7.18.2",
  resolved:
    "https://registry.npmjs.org/react-router-dom/-/react-router-dom-7.18.2.tgz",
  integrity:
    "sha512-AIKJ/jgGlFb3EbfCXk5Gzshiwt+l3mqbCrNjmEWMMjqQxNJ3svBa6bgzFyCC2Sw3RA0VWF1kg3uQf2OFhxb8hw==",
};

async function readJson(relativePath) {
  return JSON.parse(await readFile(resolve(repositoryRoot, relativePath), "utf8"));
}

async function writeJson(relativePath, value) {
  await writeFile(
    resolve(repositoryRoot, relativePath),
    `${JSON.stringify(value, null, 2)}\n`,
  );
}

function replacePackage(lock, packageName, replacement) {
  const key = `node_modules/${packageName}`;
  if (!lock.packages?.[key]) {
    throw new Error(`Pacote ausente no lockfile: ${packageName}`);
  }
  lock.packages[key] = structuredClone(replacement);
}

const adminLockPath = "apps/all-in-one-admin/package-lock.json";
const adminLock = await readJson(adminLockPath);
const businessLock = await readJson(reactRouterLocks[0]);

const canonicalPostcss = adminLock.packages["node_modules/postcss"];
const canonicalNanoid = adminLock.packages["node_modules/nanoid"];
const canonicalBraceExpansion =
  adminLock.packages["node_modules/brace-expansion"];

for (const relativePath of new Set(postcssLocks)) {
  const lock = await readJson(relativePath);
  replacePackage(lock, "postcss", canonicalPostcss);
  replacePackage(lock, "nanoid", canonicalNanoid);

  if (braceExpansionLocks.includes(relativePath)) {
    replacePackage(lock, "brace-expansion", canonicalBraceExpansion);
  }

  if (reactRouterLocks.includes(relativePath)) {
    Object.assign(lock.packages["node_modules/react-router"], reactRouter);
    Object.assign(
      lock.packages["node_modules/react-router-dom"],
      reactRouterDom,
      { dependencies: { "react-router": reactRouter.version } },
    );
  }

  await writeJson(relativePath, lock);
}

const vitePackageKeys = [
  "node_modules/vite",
  "node_modules/rolldown",
  "node_modules/@oxc-project/types",
  "node_modules/@rolldown/pluginutils",
  ...Object.keys(businessLock.packages).filter((key) =>
    key.startsWith("node_modules/@rolldown/binding-"),
  ),
];

for (const key of vitePackageKeys) {
  if (!businessLock.packages[key]) {
    throw new Error(`Dependência canônica do Vite ausente: ${key}`);
  }
  adminLock.packages[key] = structuredClone(businessLock.packages[key]);
}

adminLock.packages[""].devDependencies.vite = "8.0.16";
await writeJson(adminLockPath, adminLock);

const adminPackagePath = "apps/all-in-one-admin/package.json";
const adminPackage = await readJson(adminPackagePath);
adminPackage.devDependencies.vite = "8.0.16";
await writeJson(adminPackagePath, adminPackage);
