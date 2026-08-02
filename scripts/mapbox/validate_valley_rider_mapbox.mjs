#!/usr/bin/env node

const token = String(process.env.VITE_MAPBOX_ACCESS_TOKEN || "").trim();
const referer = String(process.env.MAPBOX_TEST_REFERER || "").trim();
const styleUri = String(
  process.env.VITE_MAPBOX_STYLE_NIGHT || "mapbox://styles/mapbox/navigation-night-v1",
).trim();

function fail(message) {
  console.error(message);
  process.exitCode = 1;
}

function styleEndpoint(uri) {
  const match = /^mapbox:\/\/styles\/([^/]+)\/(.+)$/.exec(uri);
  if (!match) throw new Error(`Style URI inválida: ${uri}`);
  return `https://api.mapbox.com/styles/v1/${encodeURIComponent(match[1])}/${encodeURIComponent(match[2])}`;
}

async function check(name, url) {
  const response = await fetch(`${url}${url.includes("?") ? "&" : "?"}access_token=${encodeURIComponent(token)}`, {
    headers: {
      Accept: "application/json",
      Referer: referer,
      "User-Agent": "Valley-Rider-Mapbox-Validator/1.0",
    },
  });
  const body = await response.text();
  if (!response.ok) {
    const detail = body.slice(0, 220).replaceAll(token, "[REDACTED]");
    throw new Error(`${name}: HTTP ${response.status} ${detail}`.trim());
  }
  return { name, status: response.status, bytes: Buffer.byteLength(body) };
}

async function main() {
  if (!token.startsWith("pk.")) throw new Error("VITE_MAPBOX_ACCESS_TOKEN deve ser um token público pk..");
  if (!referer) throw new Error("MAPBOX_TEST_REFERER é obrigatório para validar token com restrição de URL.");
  new URL(referer);

  const origin = "-44.1987,-19.9673";
  const destination = "-44.1881,-19.9558";
  const results = [];
  results.push(await check("style", styleEndpoint(styleUri)));
  results.push(
    await check(
      "directions",
      `https://api.mapbox.com/directions/v5/mapbox/driving-traffic/${origin};${destination}?alternatives=false&geometries=geojson&overview=full&steps=true&language=pt-BR`,
    ),
  );
  results.push(
    await check(
      "geocoding",
      "https://api.mapbox.com/geocoding/v5/mapbox.places/Betim%20MG.json?country=BR&language=pt-BR&limit=1",
    ),
  );

  console.log(
    JSON.stringify(
      {
        validatedAt: new Date().toISOString(),
        referer,
        tokenType: "public",
        tokenPreview: `${token.slice(0, 5)}…${token.slice(-4)}`,
        checks: results,
      },
      null,
      2,
    ),
  );
}

main().catch((error) => fail(error instanceof Error ? error.message : "Falha desconhecida na validação Mapbox."));
