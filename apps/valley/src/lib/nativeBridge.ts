export const API_HUB_URL =
  (import.meta.env.VITE_API_HUB_URL?.trim() || 'https://all-in-one-api-hub.web.app').replace(/\/$/, '');

type NativeResponse = { id: string; ok: boolean; status: number; body: unknown; headers?: Record<string, string>; error?: string };
type PendingRequest = { resolve: (value: NativeResponse) => void; reject: (reason?: unknown) => void; timeout: number };
type SerializedBody = { body: string | null; bodyBase64: string | null };
declare global { interface Window { ValleyNative?: { postMessage: (message: string) => void }; __valleyNativeResolve?: (id: string, response: NativeResponse) => void } }
const pending = new Map<string, PendingRequest>();
const RESPONSE_SIGNATURE_MAX_AGE_SECONDS = 300;
let responseSigningKeyPromise: Promise<{ keyId: string; key: CryptoKey }> | null = null;

function requestId() { return window.crypto?.randomUUID?.() ?? `valley-${Date.now()}-${Math.random().toString(36).slice(2)}`; }
window.__valleyNativeResolve = (id, response) => { const request = pending.get(id); if (!request) return; window.clearTimeout(request.timeout); pending.delete(id); request.resolve(response); };

function bytesToBase64(bytes: Uint8Array) {
  const chunkSize = 0x8000;
  let binary = '';
  for (let offset = 0; offset < bytes.length; offset += chunkSize) {
    binary += String.fromCharCode(...bytes.subarray(offset, offset + chunkSize));
  }
  return window.btoa(binary);
}

async function serializeBody(body: BodyInit | null | undefined): Promise<SerializedBody> {
  if (body == null) return { body: null, bodyBase64: null };
  if (typeof body === 'string') return { body, bodyBase64: null };
  if (body instanceof URLSearchParams) return { body: body.toString(), bodyBase64: null };
  if (body instanceof Blob) return { body: null, bodyBase64: bytesToBase64(new Uint8Array(await body.arrayBuffer())) };
  if (body instanceof ArrayBuffer) return { body: null, bodyBase64: bytesToBase64(new Uint8Array(body)) };
  if (ArrayBuffer.isView(body)) return { body: null, bodyBase64: bytesToBase64(new Uint8Array(body.buffer, body.byteOffset, body.byteLength)) };
  throw new Error('Formato de corpo não suportado pela ponte Android.');
}

async function requestThroughNative(path: string, init: RequestInit, token?: string): Promise<NativeResponse> {
  const bridge = window.ValleyNative;
  if (!bridge) throw new Error('Ponte Android indisponível.');
  const id = requestId();
  const serialized = await serializeBody(init.body);
  const message = {
    id,
    path,
    method: (init.method ?? 'GET').toUpperCase(),
    token: token ?? null,
    headers: Object.fromEntries(new Headers(init.headers).entries()),
    body: serialized.body,
    bodyBase64: serialized.bodyBase64,
  };
  return new Promise((resolve, reject) => {
    const timeout = window.setTimeout(() => {
      pending.delete(id);
      reject(new Error('O servidor demorou demais para responder.'));
    }, 45000);
    pending.set(id, { resolve, reject, timeout });
    bridge.postMessage(JSON.stringify(message));
  });
}

export async function apiRequest<T>(path: string, init: RequestInit = {}, token?: string): Promise<{ body: T; status: number; headers: Headers }> {
  if (!path.startsWith('/')) throw new Error('Caminho de API inválido.');
  let nativeResponse: NativeResponse;
  if (window.ValleyNative) {
    nativeResponse = await requestThroughNative(path, init, token);
  } else {
    const headers = new Headers(init.headers);
    headers.set('Accept', 'application/json');
    headers.set('X-Valley-Api-Version', '1');
    if (token) headers.set('Authorization', `Bearer ${token}`);
    const response = await fetch(`${API_HUB_URL}${path}`, { ...init, headers });
    const contentType = response.headers.get('content-type') ?? '';
    const body = contentType.includes('application/json') ? await response.json().catch(() => ({})) : await response.arrayBuffer();
    nativeResponse = { id: 'web', ok: response.ok, status: response.status, body, headers: Object.fromEntries(response.headers.entries()) };
  }
  if (!nativeResponse.ok) {
    const detail = typeof (nativeResponse.body as { detail?: unknown })?.detail === 'string'
      ? (nativeResponse.body as { detail: string }).detail
      : nativeResponse.error || `Falha HTTP ${nativeResponse.status}`;
    throw new Error(detail);
  }
  const responseHeaders = new Headers(nativeResponse.headers ?? {});
  if (isCriticalResponse(path, init.method)) await verifyCriticalResponse(nativeResponse.body, responseHeaders);
  return { body: nativeResponse.body as T, status: nativeResponse.status, headers: responseHeaders };
}

function isCriticalResponse(path: string, method?: string) {
  if (path.startsWith('/gateway/catalog/offers?')) return true;
  if ((method ?? 'GET').toUpperCase() === 'GET') return false;
  return path === '/gateway/catalog/actions' || path === '/gateway/payments/sandbox/authorize';
}

async function verifyCriticalResponse(payload: unknown, headers: Headers) {
  const algorithm = headers.get('X-Valley-Signature-Algorithm');
  const keyId = headers.get('X-Valley-Signature-Key-Id');
  const timestamp = headers.get('X-Valley-Signature-Timestamp');
  const signature = headers.get('X-Valley-Response-Signature');
  if (algorithm !== 'Ed25519' || !keyId || !timestamp || !signature) throw new Error('Resposta crítica sem assinatura válida.');
  const timestampNumber = Number(timestamp);
  const nowSeconds = Math.floor(Date.now() / 1000);
  if (!Number.isSafeInteger(timestampNumber) || Math.abs(nowSeconds - timestampNumber) > RESPONSE_SIGNATURE_MAX_AGE_SECONDS) throw new Error('Resposta crítica expirada ou com horário inválido.');
  const signingKey = await getResponseSigningKey();
  if (signingKey.keyId !== keyId) throw new Error('Resposta crítica assinada por chave desconhecida.');
  const digest = await window.crypto.subtle.digest('SHA-256', new TextEncoder().encode(stableStringify(payload)));
  const digestHex = Array.from(new Uint8Array(digest), byte => byte.toString(16).padStart(2, '0')).join('');
  const canonical = new TextEncoder().encode(`${timestamp}\n${digestHex}`);
  if (!await window.crypto.subtle.verify('Ed25519', signingKey.key, decodeBase64(signature), canonical)) throw new Error('Assinatura da resposta crítica não confere.');
}

async function getResponseSigningKey() {
  if (!responseSigningKeyPromise) {
    responseSigningKeyPromise = apiRequest<{ algorithm: string; key_id: string; public_key_b64: string }>('/gateway/security/response-signing-key')
      .then(async ({ body }) => {
        if (body.algorithm !== 'Ed25519' || !body.key_id || !body.public_key_b64) throw new Error('Contrato de chave pública inválido.');
        const key = await window.crypto.subtle.importKey('raw', decodeBase64(body.public_key_b64), 'Ed25519', false, ['verify']);
        return { keyId: body.key_id, key };
      })
      .catch(error => {
        responseSigningKeyPromise = null;
        throw error;
      });
  }
  return responseSigningKeyPromise;
}

function stableStringify(value: unknown): string {
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(stableStringify).join(',')}]`;
  const record = value as Record<string, unknown>;
  return `{${Object.keys(record).sort().map(key => `${JSON.stringify(key)}:${stableStringify(record[key])}`).join(',')}}`;
}

function decodeBase64(value: string): ArrayBuffer {
  const binary = window.atob(value);
  const bytes = Uint8Array.from(binary, character => character.charCodeAt(0));
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength) as ArrayBuffer;
}

let nativeFetchInstalled = false;
export function installNativeFetchBridge() {
  if (nativeFetchInstalled || !window.ValleyNative) return;
  nativeFetchInstalled = true;
  const originalFetch = window.fetch.bind(window);
  window.fetch = async (input: RequestInfo | URL, init: RequestInit = {}) => {
    const request = input instanceof Request ? input : null;
    const rawUrl = request?.url ?? input.toString();
    const resolved = new URL(rawUrl, window.location.href);
    const apiOrigin = new URL(API_HUB_URL).origin;
    const isRelativeApiPath = rawUrl.startsWith('/') && !rawUrl.startsWith('//');
    const isApiHubUrl = resolved.origin === apiOrigin;
    if (!isRelativeApiPath && !isApiHubUrl) return originalFetch(input, init);
    const headers = new Headers(request?.headers ?? init.headers);
    const authorization = headers.get('Authorization');
    const token = authorization?.startsWith('Bearer ') ? authorization.slice(7) : undefined;
    headers.delete('Authorization');
    const method = init.method ?? request?.method ?? 'GET';
    const body = init.body ?? (request && method !== 'GET' && method !== 'HEAD' ? await request.clone().arrayBuffer() : null);
    const response = await requestThroughNative(`${resolved.pathname}${resolved.search}`, { ...init, method, headers, body }, token);
    return new Response(JSON.stringify(response.body ?? {}), {
      status: response.status || (response.ok ? 200 : 500),
      headers: { 'Content-Type': 'application/json', ...(response.headers ?? {}) },
    });
  };
}
