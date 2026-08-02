export type MapboxNavigationMode = "auto" | "day" | "night";
export type MapboxTokenStatus = "missing" | "invalid" | "ready";

const DEFAULT_GL_JS_VERSION = "3.25.0";
const DEFAULT_DAY_STYLE = "mapbox://styles/mapbox/navigation-day-v1";
const DEFAULT_NIGHT_STYLE = "mapbox://styles/mapbox/navigation-night-v1";

function env(name: string, fallback = "") {
  const value = (import.meta.env as Record<string, unknown>)[name];
  return typeof value === "string" && value.trim() ? value.trim() : fallback;
}

export const MAPBOX_GL_JS_VERSION = /^\d+\.\d+\.\d+$/.test(env("VITE_MAPBOX_GL_JS_VERSION", DEFAULT_GL_JS_VERSION))
  ? env("VITE_MAPBOX_GL_JS_VERSION", DEFAULT_GL_JS_VERSION)
  : DEFAULT_GL_JS_VERSION;

export const MAPBOX_STYLE_DAY = env("VITE_MAPBOX_STYLE_DAY", DEFAULT_DAY_STYLE);
export const MAPBOX_STYLE_NIGHT = env("VITE_MAPBOX_STYLE_NIGHT", DEFAULT_NIGHT_STYLE);
export const MAPBOX_NAVIGATION_MODE = (["auto", "day", "night"].includes(env("VITE_MAPBOX_NAVIGATION_MODE", "auto"))
  ? env("VITE_MAPBOX_NAVIGATION_MODE", "auto")
  : "auto") as MapboxNavigationMode;

export const MAPBOX_COLORS = Object.freeze({
  route: "#20C8F3",
  routeCasing: "#06111F",
  rider: "#20C8F3",
  pickup: "#F2A93B",
  destination: "#22B86B",
  danger: "#E45B6A",
});

export function tokenStatus(token: string): MapboxTokenStatus {
  const normalized = token.trim();
  if (!normalized) return "missing";
  return normalized.startsWith("pk.") ? "ready" : "invalid";
}

export function resolveNavigationStyleUri(mode: MapboxNavigationMode = MAPBOX_NAVIGATION_MODE, now = new Date()) {
  if (mode === "day") return MAPBOX_STYLE_DAY;
  if (mode === "night") return MAPBOX_STYLE_NIGHT;

  const hour = now.getHours();
  const prefersDark = typeof window !== "undefined" && window.matchMedia?.("(prefers-color-scheme: dark)").matches;
  return hour < 6 || hour >= 18 || prefersDark ? MAPBOX_STYLE_NIGHT : MAPBOX_STYLE_DAY;
}

export function mapboxCredentialMessage(token: string) {
  const status = tokenStatus(token);
  if (status === "missing") {
    return "Mapbox aguardando token público restrito. Defina VITE_MAPBOX_ACCESS_TOKEN.";
  }
  if (status === "invalid") {
    return "Credencial Mapbox inválida. O aplicativo aceita somente token público iniciado por pk..";
  }
  return "";
}
