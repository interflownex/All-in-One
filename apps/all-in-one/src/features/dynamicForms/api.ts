import type { BuilderDocument, CatalogField, FieldBinding } from './types';

const API_HUB_URL = (import.meta as any).env?.VITE_API_HUB_URL ?? '';
const API_HUB_TOKEN = (import.meta as any).env?.VITE_API_HUB_TOKEN ?? '';
const TENANT_ID = (import.meta as any).env?.VITE_TENANT_ID ?? '00000000-0000-4000-8000-000000000101';
const ACTOR_ID = (import.meta as any).env?.VITE_ACTOR_USER_ID ?? '00000000-0000-4000-8000-000000000102';
const BASE = `${API_HUB_URL}/dynamic_forms`;

const requestHeaders = (idempotencyKey?: string) => ({
  'Content-Type': 'application/json',
  'X-Tenant-Id': TENANT_ID,
  ...(API_HUB_TOKEN
    ? { Authorization: `Bearer ${API_HUB_TOKEN}` }
    : {
        'X-Actor-User-Id': ACTOR_ID,
        'X-Actor-Roles': 'owner,form_designer',
        'X-Actor-Scopes': 'forms:read,forms:write,forms:review,forms:publish,forms:submit',
        'X-MFA-Verified': 'true',
        'X-Business-Id': TENANT_ID,
        'X-Business-Status': 'active',
      }),
  ...(idempotencyKey ? { 'X-Idempotency-Key': idempotencyKey } : {}),
});

async function request<T>(path: string, init?: RequestInit, idempotencyKey?: string): Promise<T> {
  const response = await fetch(`${BASE}${path}`, { ...init, headers: { ...requestHeaders(idempotencyKey), ...init?.headers } });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.detail ?? 'Não foi possível concluir a operação no backend.');
  return payload as T;
}

export async function loadCatalog(): Promise<{ catalog: CatalogField[]; bindings: FieldBinding[] }> {
  const catalog = await request<CatalogField[]>('/catalog');
  if (!catalog.length) return { catalog, bindings: [] };
  const query = new URLSearchParams();
  catalog.forEach(field => query.append('catalog_ids', field.id));
  const bindings = await request<FieldBinding[]>(`/catalog/bindings?${query.toString()}`);
  return { catalog, bindings };
}

export async function saveDocument(document: BuilderDocument): Promise<{ definitionId: string; versionId: string }> {
  let definitionId = document.definitionId;
  let versionId = document.versionId;
  if (!definitionId || !versionId) {
    const created = await request<any>(
      '/definitions',
      {
        method: 'POST',
        body: JSON.stringify({
          module_id: document.moduleId,
          business_context: document.businessContext,
          name: document.name,
          change_summary: 'Versão inicial criada pelo builder web',
        }),
      },
      `form-definition-${crypto.randomUUID()}`,
    );
    definitionId = created.definition.id;
    versionId = created.version.id;
  }
  if (!definitionId || !versionId) throw new Error('Backend não retornou os identificadores do formulário.');
  await request(
    `/versions/${versionId}/blueprint`,
    {
      method: 'PUT',
      body: JSON.stringify({
        blocks: document.blocks,
        fields: document.fields,
        calculations: document.calculations,
        validations: document.validations,
        visibility_rules: document.visibility_rules,
      }),
    },
  );
  return { definitionId, versionId };
}

export async function requestHomologation(versionId: string): Promise<void> {
  await request(
    `/versions/${versionId}/homologations`,
    { method: 'POST', body: JSON.stringify({ checklist: { blueprint_validated: true, preview_reviewed: true, no_physical_binding: true } }) },
    `homologation-${versionId}`,
  );
}
