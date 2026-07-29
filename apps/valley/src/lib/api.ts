import { apiRequest } from './nativeBridge';

export type JsonRecord = Record<string, unknown>;
export type ViewKey = 'home' | 'commerce' | 'services' | 'delivery' | 'mobility' | 'life' | 'account' | 'settings';
export type Session = { accessToken: string; refreshToken: string; userId: string; sessionId: string; email: string; expiresAt: string; refreshExpiresAt: string };
export type Offer = { offer_id: string; title: string; short_description?: string; description?: string; price_amount?: string | null; consumer_category: string; offer_type_label: string; source_module: string; source_entity_id?: string; provider_label: string; region_label: string; distance_km?: number | null; consumer_action: 'buy' | 'book' | 'hire' | 'request' | 'view' | 'coming_soon'; primary_action_label: string; verified_seller?: boolean; metadata?: { image_url?: string; video_url?: string } };
export type CatalogResponse = { data: Offer[]; total: number; partial?: boolean };
export type ApiItem = { id: string; status?: string; payload?: JsonRecord; created_at?: string; updated_at?: string };
export type Order = { id: string; kind?: string; title?: string; status?: string; amount_brl?: string | null; scheduled_at?: string | null; created_at?: string };
export type ViewProps = { session: Session; setNotice: (message: string) => void };

const SESSION_KEY = 'valley.production.session.v1';
const DEVICE_KEY = 'valley.production.device.v1';

export function deviceFingerprint() {
  let value = window.localStorage.getItem(DEVICE_KEY);
  if (!value) { value = window.crypto.randomUUID(); window.localStorage.setItem(DEVICE_KEY, value); }
  return value;
}
export function loadSession(): Session | null {
  const raw = window.localStorage.getItem(SESSION_KEY);
  if (!raw) return null;
  try { return JSON.parse(raw) as Session; } catch { window.localStorage.removeItem(SESSION_KEY); return null; }
}
export function saveSession(session: Session | null) {
  if (session) window.localStorage.setItem(SESSION_KEY, JSON.stringify(session)); else window.localStorage.removeItem(SESSION_KEY);
}
export async function request<T = JsonRecord>(path: string, method = 'GET', body?: unknown, token?: string) {
  const headers: Record<string, string> = { 'X-Device-Fingerprint': deviceFingerprint() };
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  return (await apiRequest<T>(path, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) }, token)).body;
}
export function errorMessage(error: unknown) { return error instanceof Error ? error.message : 'Não foi possível concluir a operação.'; }
export function formatMoney(value?: string | null) { return value ? Number(value).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) : 'Sob orçamento'; }
export function itemTitle(item: ApiItem) { const p = item.payload ?? {}; return String(p.title ?? p.name ?? p.subject ?? p.specialty ?? p.origin ?? item.id); }
export function itemSubtitle(item: ApiItem) { const p = item.payload ?? {}; return String(p.description ?? p.destination ?? p.note ?? p.status ?? item.status ?? 'Registro sincronizado'); }
