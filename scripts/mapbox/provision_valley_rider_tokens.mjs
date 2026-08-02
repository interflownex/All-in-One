#!/usr/bin/env node

import { chmod, mkdir, writeFile } from "node:fs/promises";
import path from "node:path";

const API_ROOT = "https://api.mapbox.com/tokens/v2";
const PUBLIC_SCOPES = ["styles:read", "fonts:read"];
const DEFAULT_ENVIRONMENTS = ["staging", "production"];

function required(name) {
  const value = String(process.env[name] || "").trim();
  if (!value) throw new Error(`Variável obrigatória ausente: ${name}`);
  return value;
}

function parseCsv(value) {
  return String(value || "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function parseEnvironments() {
  const values = parseCsv(process.env.MAPBOX_ENVIRONMENTS || DEFAULT_ENVIRONMENTS.join(","));
  const allowed = new Set(["development", "staging", "production"]);
  if (!values.length || values.some((value) => !allowed.has(value))) {
    throw new Error("MAPBOX_ENVIRONMENTS deve conter development, staging e/ou production.");
  }
  return [...new Set(values)];
}

function validateAllowedUrls(environment, urls) {
  if (!urls.length) throw new Error(`Nenhuma URL permitida foi informada para ${environment}.`);
  return urls.map((raw) => {
    let parsed;
    try {
      parsed = new URL(raw);
    } catch {
      throw new Error(`URL inválida em ${environment}: ${raw}`);
    }
    if (environment !== "development" && parsed.protocol !== "https:") {
      throw new Error(`Somente HTTPS é aceito fora de development: ${raw}`);
    }
    if (environment === "production" && ["localhost", "127.0.0.1"].includes(parsed.hostname)) {
      throw new Error(`localhost não pode ser autorizado no token de produção: ${raw}`);
    }
    return raw;
  });
}

function sanitize(message, secret) {
  return String(message || "Erro Mapbox").split(secret).join("[REDACTED]");
}

async function requestMapbox(username, adminToken, pathname, init) {
  const url = `${API_ROOT}/${encodeURIComponent(username)}${pathname}?access_token=${encodeURIComponent(adminToken)}`;
  const response = await fetch(url, {
    ...init,
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
  });
  const text = await response.text();
  let body;
  try {
    body = text ? JSON.parse(text) : null;
  } catch {
    body = { message: text };
  }
  if (!response.ok) {
    const detail = body?.message || body?.code || `HTTP ${response.status}`;
    throw new Error(sanitize(`Mapbox Tokens API: ${detail}`, adminToken));
  }
  return body;
}

async function createToken(username, adminToken, { note, allowedUrls }) {
  const payload = {
    note,
    scopes: PUBLIC_SCOPES,
    ...(allowedUrls ? { allowedUrls } : {}),
  };
  const created = await requestMapbox(username, adminToken, "", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  if (!created?.id || !created?.token || !String(created.token).startsWith("pk.")) {
    throw new Error(`A Mapbox não devolveu um token público válido para ${note}.`);
  }
  return created;
}

async function deleteToken(username, adminToken, tokenId) {
  await requestMapbox(username, adminToken, `/${encodeURIComponent(tokenId)}`, { method: "DELETE" });
}

async function writeSecure(filePath, content) {
  await writeFile(filePath, content, { encoding: "utf8", mode: 0o600 });
  await chmod(filePath, 0o600);
}

async function main() {
  const username = required("MAPBOX_USERNAME");
  const adminToken = required("MAPBOX_ADMIN_TOKEN");
  if (!adminToken.startsWith("sk.")) {
    throw new Error("MAPBOX_ADMIN_TOKEN deve ser um token secreto sk. com tokens:write e os escopos públicos solicitados.");
  }

  const environments = parseEnvironments();
  const outputDir = path.resolve(process.env.MAPBOX_OUTPUT_DIR || "tmp/mapbox-secrets");
  const createMobile = String(process.env.MAPBOX_CREATE_MOBILE_TOKENS || "true").toLowerCase() !== "false";
  const created = [];
  const manifest = {
    generatedAt: new Date().toISOString(),
    username,
    scopes: PUBLIC_SCOPES,
    tokens: [],
  };

  await mkdir(outputDir, { recursive: true, mode: 0o700 });

  try {
    for (const environment of environments) {
      const envSuffix = environment.toUpperCase();
      const allowedUrls = validateAllowedUrls(
        environment,
        parseCsv(process.env[`MAPBOX_WEB_ALLOWED_URLS_${envSuffix}`]),
      );

      const web = await createToken(username, adminToken, {
        note: `Valley Rider Web ${environment}`,
        allowedUrls,
      });
      created.push(web.id);
      manifest.tokens.push({
        environment,
        platform: "web",
        id: web.id,
        note: web.note,
        scopes: web.scopes,
        allowedUrls: web.allowedUrls || allowedUrls,
      });

      let mobile = null;
      if (createMobile) {
        mobile = await createToken(username, adminToken, {
          note: `Valley Rider Mobile ${environment}`,
        });
        created.push(mobile.id);
        manifest.tokens.push({
          environment,
          platform: "mobile",
          id: mobile.id,
          note: mobile.note,
          scopes: mobile.scopes,
          allowedUrls: [],
        });
      }

      const envFile = [
        `# Gerado localmente em ${new Date().toISOString()}`,
        "# NÃO VERSIONAR. O diretório tmp/ já é ignorado pelo Git.",
        `VITE_MAPBOX_ACCESS_TOKEN=${web.token}`,
        "VITE_MAPBOX_GL_JS_VERSION=3.25.0",
        "VITE_MAPBOX_STYLE_DAY=mapbox://styles/mapbox/navigation-day-v1",
        "VITE_MAPBOX_STYLE_NIGHT=mapbox://styles/mapbox/navigation-night-v1",
        "VITE_MAPBOX_NAVIGATION_MODE=auto",
        ...(mobile ? [`MAPBOX_MOBILE_ACCESS_TOKEN=${mobile.token}`] : []),
        "",
      ].join("\n");
      await writeSecure(path.join(outputDir, `.env.mapbox.${environment}.local`), envFile);
    }

    await writeSecure(
      path.join(outputDir, "mapbox-token-manifest.json"),
      `${JSON.stringify(manifest, null, 2)}\n`,
    );

    console.log("Provisionamento Mapbox concluído sem expor tokens no terminal.");
    console.log(`Ambientes: ${environments.join(", ")}`);
    console.log(`Arquivos protegidos: ${outputDir}`);
    console.log(`IDs criados: ${created.join(", ")}`);
  } catch (error) {
    const rollbackFailures = [];
    for (const tokenId of [...created].reverse()) {
      try {
        await deleteToken(username, adminToken, tokenId);
      } catch (rollbackError) {
        rollbackFailures.push(`${tokenId}: ${sanitize(rollbackError?.message, adminToken)}`);
      }
    }
    const rollbackText = rollbackFailures.length
      ? ` Rollback incompleto: ${rollbackFailures.join("; ")}`
      : " Todos os tokens criados nesta execução foram revogados.";
    throw new Error(`${sanitize(error?.message, adminToken)}${rollbackText}`);
  }
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : "Falha desconhecida no provisionamento Mapbox.");
  process.exitCode = 1;
});
