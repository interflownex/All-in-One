const API_HUB_URL = ((import.meta as any).env?.VITE_API_HUB_URL ?? "").replace(/\/$/, "");
const API_HUB_TOKEN = (import.meta as any).env?.VITE_API_HUB_TOKEN ?? "";
const BASE_PATH = "/stock/integrations";

export type StockProviderSlug = "cj_dropshipping" | "aliexpress";
export type StockProviderEnvironment = "sandbox" | "production";
export type StockSyncResource = "products" | "inventory" | "prices" | "orders" | "tracking";

export type StockProviderConfig = {
  provider: StockProviderSlug;
  enabled: boolean;
  environment: StockProviderEnvironment;
  api_base_url: string;
  authorization_url: string | null;
  token_url: string | null;
  refresh_url: string | null;
  callback_url: string | null;
  webhook_url: string | null;
  secret_env: Record<string, string>;
  auto_sync_products: boolean;
  auto_sync_inventory: boolean;
  auto_sync_prices: boolean;
  auto_sync_orders: boolean;
  auto_sync_tracking: boolean;
  auto_publish_products: boolean;
  schedule_minutes: number;
  timeout_seconds: number;
  retry_attempts: number;
  rate_limit_per_minute: number;
  max_products_per_run: number;
  source_currency: string;
  target_currency: string;
  default_country: string;
  default_warehouse: string | null;
  markup_percent: number;
  connection_test_path: string | null;
  mapping_rules: Record<string, string>;
  provider_options: Record<string, string | number | boolean>;
  updated_at: string;
  updated_by: string;
};

export type StockProviderState = {
  provider: StockProviderSlug;
  display_name: string;
  docs_url: string;
  auth_kind: string;
  capabilities: StockSyncResource[];
  endpoints: Record<string, string>;
  config: StockProviderConfig;
  secret_status: Record<string, boolean>;
  missing_requirements: string[];
  ready_for_connection: boolean;
  secrets_are_never_returned: true;
};

export type StockIntegrationRun = {
  id: string;
  provider: StockProviderSlug;
  kind: "connection_test" | "sync" | "webhook";
  status: string;
  dry_run?: boolean;
  resources?: StockSyncResource[];
  started_at: string;
  completed_at: string;
  actor: string;
  result: Record<string, unknown>;
};

export type StockIntegrationAudit = {
  id: string;
  actor: string;
  action: string;
  provider: StockProviderSlug;
  payload: Record<string, unknown>;
  created_at: string;
};

export type StockProviderSecrets = Partial<{
  api_key: string;
  app_key: string;
  app_secret: string;
  access_token: string;
  refresh_token: string;
  webhook_secret: string;
}>;

export type StockSyncInput = {
  resources: StockSyncResource[];
  dry_run: boolean;
  query?: string;
  product_id?: string;
  order_id?: string;
  tracking_number?: string;
  limit?: number;
};

export const stockIntegrationApiEnabled = Boolean(API_HUB_URL && API_HUB_TOKEN);

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  if (!stockIntegrationApiEnabled) {
    throw new Error(
      "API Hub não configurado. Defina VITE_API_HUB_URL e VITE_API_HUB_TOKEN no ambiente do painel.",
    );
  }

  const response = await fetch(`${API_HUB_URL}${BASE_PATH}${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${API_HUB_TOKEN}`,
      "Content-Type": "application/json",
      ...(init.headers ?? {}),
    },
  });

  if (!response.ok) {
    let detail = "";
    try {
      const body = await response.json();
      detail = typeof body?.detail === "string" ? body.detail : JSON.stringify(body);
    } catch {
      detail = await response.text();
    }
    throw new Error(detail || `API Hub retornou HTTP ${response.status}.`);
  }

  return response.json() as Promise<T>;
}

export async function listStockProviders() {
  const response = await request<{ providers: StockProviderState[] }>("/providers");
  return response.providers;
}

export async function getStockReadiness() {
  return request<{
    stock_supplier_integration_ready: boolean;
    enabled_provider_count: number;
    providers: StockProviderState[];
    required_server_settings: string[];
  }>("/readiness");
}

export async function updateStockProvider(
  provider: StockProviderSlug,
  patch: Partial<StockProviderConfig>,
) {
  return request<StockProviderState>(`/providers/${provider}`, {
    method: "PUT",
    body: JSON.stringify(patch),
  });
}

export async function saveStockProviderSecrets(
  provider: StockProviderSlug,
  secrets: StockProviderSecrets,
) {
  return request<StockProviderState>(`/providers/${provider}/secrets`, {
    method: "PUT",
    body: JSON.stringify(secrets),
  });
}

export async function clearStockProviderSecrets(
  provider: StockProviderSlug,
  names: string[],
) {
  return request<StockProviderState>(`/providers/${provider}/secrets`, {
    method: "DELETE",
    body: JSON.stringify({ names }),
  });
}

export async function testStockProvider(provider: StockProviderSlug) {
  return request<StockIntegrationRun>(`/providers/${provider}/test`, {
    method: "POST",
  });
}

export async function syncStockProvider(
  provider: StockProviderSlug,
  input: StockSyncInput,
) {
  return request<StockIntegrationRun>(`/providers/${provider}/sync`, {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export async function getAliExpressAuthorizeUrl() {
  return request<{ authorization_url: string }>("/providers/aliexpress/authorize-url");
}

export async function completeAliExpressOauth(code: string) {
  return request<StockProviderState>("/providers/aliexpress/oauth/callback", {
    method: "POST",
    body: JSON.stringify({ code }),
  });
}

export async function listStockIntegrationRuns(limit = 50) {
  const response = await request<{ runs: StockIntegrationRun[] }>(`/runs?limit=${limit}`);
  return response.runs;
}

export async function listStockIntegrationAudit(limit = 100) {
  const response = await request<{ audit: StockIntegrationAudit[] }>(`/audit?limit=${limit}`);
  return response.audit;
}
