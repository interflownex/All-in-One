import type { BusinessClassificationInput, ModuleRecommendation } from './moduleRecommendationRules';

const API_HUB_URL = (import.meta as any).env?.VITE_API_HUB_URL ?? '';
const API_HUB_TOKEN = (import.meta as any).env?.VITE_API_HUB_TOKEN ?? '';
const BUSINESS_MODULES_BASE = '/business-modules';

export type CompanyModuleSetting = {
  id: string;
  company_id: string;
  module_slug: string;
  title_pt_br: string;
  state: ModuleRecommendation['state'];
  visibility: 'visible' | 'hidden';
  source: 'automatic' | 'manual';
  recommendation_score: number;
  recommendation_reason: string;
  dependencies: string[];
  can_disable: boolean;
  updated_at: string;
  updated_by: string;
};

export type ModuleSettingsResponse = {
  company_id: string;
  classification: unknown;
  modules: CompanyModuleSetting[];
  audit: Array<{ id: string; action: string; payload: unknown; created_at: string }>;
};

export const businessModulesApiEnabled = Boolean(API_HUB_URL && API_HUB_TOKEN);

function toBackendClassification(input: BusinessClassificationInput) {
  return {
    businessKind: input.businessKind,
    cnaePrimary: input.cnaePrimary,
    cnaeSecondary: input.cnaeSecondary ?? [],
    hasPhysicalStock: Boolean(input.hasPhysicalStock),
    sellsOnline: Boolean(input.sellsOnline),
    performsDelivery: Boolean(input.performsDelivery),
    hiresPeople: Boolean(input.hiresPeople),
    issuesFiscalDocuments: Boolean(input.issuesFiscalDocuments),
    operatesFleet: Boolean(input.operatesFleet),
    hasWarehouse: Boolean(input.hasWarehouse),
  };
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  if (!businessModulesApiEnabled) {
    throw new Error('API Hub nao configurado para modulos empresariais.');
  }
  const response = await fetch(`${API_HUB_URL}${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${API_HUB_TOKEN}`,
      'Content-Type': 'application/json',
      ...(init.headers ?? {}),
    },
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `API Hub retornou HTTP ${response.status}.`);
  }
  return response.json() as Promise<T>;
}

export async function previewBusinessModuleRecommendations(input: BusinessClassificationInput) {
  return request<ModuleRecommendation[]>(`${BUSINESS_MODULES_BASE}/recommendations`, {
    method: 'POST',
    body: JSON.stringify(toBackendClassification(input)),
  });
}

export async function applyBusinessModuleRecommendations(companyId: string, input: BusinessClassificationInput) {
  return request<ModuleSettingsResponse>(`${BUSINESS_MODULES_BASE}/companies/${companyId}/apply-recommendations`, {
    method: 'POST',
    body: JSON.stringify({ classification: toBackendClassification(input), actor_id: 'business-shell' }),
  });
}

export async function loadCompanyModules(companyId: string) {
  return request<ModuleSettingsResponse>(`${BUSINESS_MODULES_BASE}/companies/${companyId}/modules`);
}

export async function patchCompanyModule(companyId: string, moduleSlug: string, state: ModuleRecommendation['state'], reason: string) {
  return request<CompanyModuleSetting>(`${BUSINESS_MODULES_BASE}/companies/${companyId}/modules/${moduleSlug}`, {
    method: 'PATCH',
    body: JSON.stringify({ state, reason }),
  });
}

export async function getCompanyModuleChangeImpact(companyId: string, moduleSlug: string, nextState: ModuleRecommendation['state']) {
  return request<Record<string, unknown>>(`${BUSINESS_MODULES_BASE}/companies/${companyId}/modules/${moduleSlug}/change-impact?next_state=${nextState}`);
}
