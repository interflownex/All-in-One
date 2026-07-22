import type { BuilderDocument, BuilderField, BuilderValidation, CatalogField, FieldBinding } from './types';

export const STORAGE_KEY = 'all-in-one:dynamic-form-builder:v1';

export const initialDocument = (): BuilderDocument => ({
  schemaVersion: 1,
  definitionId: null,
  versionId: null,
  name: 'Cadastro empresarial',
  moduleId: 'business',
  businessContext: 'company.onboarding',
  status: 'draft',
  versionNumber: 1,
  blocks: [{
    id: crypto.randomUUID(), block_type: 'section', parent_block_id: null, display_order: 0,
    title: 'Dados principais', description: 'Informações essenciais para o cadastro.', width: 12,
    collapsible: false, visibility_rule_id: null, repeatable: false, allowed_style: 'default',
  }],
  fields: [],
  validations: [],
  calculations: [],
  visibility_rules: [],
});

export const loadLocalDocument = (): BuilderDocument => {
  try {
    const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? 'null');
    return parsed?.schemaVersion === 1 ? parsed : initialDocument();
  } catch {
    return initialDocument();
  }
};

export const saveLocalDocument = (document: BuilderDocument) => localStorage.setItem(STORAGE_KEY, JSON.stringify(document));

const validationMessage: Record<string, string> = {
  required: 'Este campo é obrigatório.',
  max_length: 'O valor excede o tamanho permitido.',
  email: 'Informe um e-mail válido.',
  document_checksum: 'Documento inválido.',
};

export function createField(catalog: CatalogField, binding: FieldBinding, blockId: string, order: number) {
  const fieldId = crypto.randomUUID();
  const validations: BuilderValidation[] = catalog.mandatory_validations.map(type => ({
    id: crypto.randomUUID(), field_id: fieldId, validation_type: type, parameters: {},
    message_pt_br: validationMessage[type] ?? 'Valor inválido.', severity: type === 'required' ? 'blocking' : 'error',
    condition: null, run_frontend: true, run_backend: true, status: 'active', version: 1,
  }));
  const component = catalog.allowed_components[0] ?? 'text';
  const label = catalog.description || catalog.logical_field.replaceAll('_', ' ');
  const field: BuilderField = {
    id: fieldId, block_id: blockId, field_catalog_id: catalog.id, field_binding_id: binding.id,
    component, label, help_text: '', placeholder: '', required: catalog.mandatory_validations.includes('required'),
    read_only: false, hidden: false, display_order: order, width: 12, mask: null, format: null,
    default_value: null, value_source: 'user', unit: catalog.unit ?? null, permissions: {}, visibility_rule_id: null,
    validation_ids: validations.map(item => item.id), audit_policy: { sensitivity: catalog.sensitivity },
  };
  return { field, validations };
}

export const demoCatalog: CatalogField[] = [
  { id: 'demo-legal-name', domain: 'business', logical_entity: 'companies', logical_field: 'legal_name', data_type: 'string', description: 'Razão social', allowed_components: ['text'], mandatory_validations: ['required', 'max_length'], allowed_calculations: [], sensitivity: 'internal', status: 'active' },
  { id: 'demo-document', domain: 'business', logical_entity: 'companies', logical_field: 'document_number', data_type: 'string', description: 'CNPJ', allowed_components: ['text'], mandatory_validations: ['required', 'document_checksum'], allowed_calculations: [], sensitivity: 'personal', status: 'active' },
  { id: 'demo-email', domain: 'business', logical_entity: 'companies', logical_field: 'responsible_email', data_type: 'string', description: 'E-mail responsável', allowed_components: ['email'], mandatory_validations: ['required', 'email'], allowed_calculations: [], sensitivity: 'personal', status: 'active' },
  { id: 'demo-capital', domain: 'business', logical_entity: 'companies', logical_field: 'share_capital', data_type: 'decimal', description: 'Capital social', allowed_components: ['currency'], mandatory_validations: [], allowed_calculations: ['sum'], sensitivity: 'financial', unit: 'BRL', status: 'active' },
];

export const demoBindings: FieldBinding[] = demoCatalog.map(field => ({ id: `binding-${field.id}`, field_catalog_id: field.id, command: 'business.company.update', api: '/business/resources/companies', dto: 'CompanyPatch', logical_path: `payload.${field.logical_field}`, status: 'active' }));
