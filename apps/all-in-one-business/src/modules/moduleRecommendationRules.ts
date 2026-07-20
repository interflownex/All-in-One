export type BusinessKind =
  | 'physical_store'
  | 'ecommerce'
  | 'dropshipping'
  | 'restaurant'
  | 'services_provider'
  | 'carrier'
  | 'clinic'
  | 'industry'
  | 'office'
  | 'autonomous'
  | 'rider'
  | 'driver_partner';

export type ModuleState = 'mandatory' | 'active' | 'recommended' | 'optional' | 'hidden' | 'disabled' | 'blocked_by_plan';

export type ModuleRecommendation = {
  moduleSlug: string;
  titlePtBr: string;
  state: ModuleState;
  score: number;
  reasonCodes: string[];
  explanationPtBr: string;
  dependencies: string[];
  canDisable: boolean;
};

export type BusinessClassificationInput = {
  businessKind: BusinessKind;
  cnaePrimary?: string;
  cnaeSecondary?: string[];
  hasPhysicalStock?: boolean;
  sellsOnline?: boolean;
  performsDelivery?: boolean;
  hiresPeople?: boolean;
  issuesFiscalDocuments?: boolean;
  operatesFleet?: boolean;
  hasWarehouse?: boolean;
};

type Preset = {
  mandatory: string[];
  active: string[];
  recommended: string[];
  hidden: string[];
};

const moduleNames: Record<string, string> = {
  identity: 'Identidade',
  business: 'Empresas',
  permissions: 'Permissões',
  finance: 'Financeiro',
  marketplace: 'Marketplace',
  stock: 'Estoque',
  delivery: 'Entregas',
  riders: 'Entregadores e motoristas',
  services: 'Serviços',
  mobility: 'Mobilidade',
  jobs: 'Vagas e candidatos',
  erp: 'ERP',
  wms: 'Gestão de armazéns',
  tms: 'Gestão de transportes',
  crm: 'Relacionamento com clientes',
  bpm: 'Fluxos de trabalho',
  document: 'Documentos',
  hr: 'Recursos humanos',
  health: 'Saúde',
  bi: 'Análises e indicadores',
  api_hub: 'Integrações e APIs',
};

const presets: Record<BusinessKind, Preset> = {
  physical_store: {
    mandatory: ['identity', 'business', 'permissions'],
    active: ['marketplace', 'finance', 'crm'],
    recommended: ['stock', 'bi'],
    hidden: ['health', 'mobility', 'tms', 'wms'],
  },
  ecommerce: {
    mandatory: ['identity', 'business', 'permissions'],
    active: ['marketplace', 'finance', 'stock', 'delivery', 'crm'],
    recommended: ['bi', 'document'],
    hidden: ['health', 'mobility', 'tms'],
  },
  dropshipping: {
    mandatory: ['identity', 'business', 'permissions'],
    active: ['marketplace', 'finance', 'stock', 'crm'],
    recommended: ['tms', 'bi', 'document'],
    hidden: ['health', 'mobility', 'jobs'],
  },
  restaurant: {
    mandatory: ['identity', 'business', 'permissions'],
    active: ['marketplace', 'delivery', 'finance', 'crm'],
    recommended: ['stock', 'bi'],
    hidden: ['health', 'tms', 'wms', 'jobs'],
  },
  services_provider: {
    mandatory: ['identity', 'business', 'permissions'],
    active: ['services', 'finance', 'crm'],
    recommended: ['document', 'jobs', 'bi'],
    hidden: ['marketplace', 'wms', 'tms'],
  },
  carrier: {
    mandatory: ['identity', 'business', 'permissions'],
    active: ['tms', 'finance', 'document'],
    recommended: ['wms', 'bi', 'hr'],
    hidden: ['health', 'marketplace', 'services'],
  },
  clinic: {
    mandatory: ['identity', 'business', 'permissions'],
    active: ['health', 'document', 'finance'],
    recommended: ['crm', 'hr', 'bi'],
    hidden: ['marketplace', 'tms', 'wms'],
  },
  industry: {
    mandatory: ['identity', 'business', 'permissions'],
    active: ['erp', 'finance', 'wms'],
    recommended: ['tms', 'bpm', 'bi', 'hr'],
    hidden: ['health', 'mobility', 'services'],
  },
  office: {
    mandatory: ['identity', 'business', 'permissions'],
    active: ['crm', 'finance', 'document'],
    recommended: ['hr', 'bi', 'bpm'],
    hidden: ['wms', 'tms', 'health'],
  },
  autonomous: {
    mandatory: ['identity'],
    active: ['services', 'finance'],
    recommended: ['document', 'crm'],
    hidden: ['erp', 'wms', 'tms', 'health'],
  },
  rider: {
    mandatory: ['identity'],
    active: ['riders', 'delivery', 'finance'],
    recommended: ['document'],
    hidden: ['erp', 'wms', 'health', 'crm'],
  },
  driver_partner: {
    mandatory: ['identity'],
    active: ['riders', 'mobility', 'finance'],
    recommended: ['document'],
    hidden: ['erp', 'wms', 'health', 'marketplace'],
  },
};

function unique(values: string[]) {
  return [...new Set(values)];
}

export function recommendBusinessModules(input: BusinessClassificationInput): ModuleRecommendation[] {
  const preset = presets[input.businessKind];
  const dynamicRecommended = [
    ...(input.hasPhysicalStock ? ['stock'] : []),
    ...(input.hasWarehouse ? ['wms'] : []),
    ...(input.performsDelivery ? ['delivery'] : []),
    ...(input.operatesFleet ? ['tms'] : []),
    ...(input.hiresPeople ? ['jobs', 'hr'] : []),
    ...(input.issuesFiscalDocuments ? ['erp'] : []),
    ...(input.sellsOnline ? ['marketplace'] : []),
  ];

  const mandatory = unique(preset.mandatory);
  const active = unique([...preset.active, ...dynamicRecommended.filter(moduleSlug => !mandatory.includes(moduleSlug))]);
  const recommended = unique(preset.recommended).filter(moduleSlug => !mandatory.includes(moduleSlug) && !active.includes(moduleSlug));
  const hidden = unique(preset.hidden).filter(moduleSlug => !mandatory.includes(moduleSlug) && !active.includes(moduleSlug) && !recommended.includes(moduleSlug));

  const entries = [
    ...mandatory.map(moduleSlug => ({ moduleSlug, state: 'mandatory' as const, score: 1, canDisable: false })),
    ...active.map(moduleSlug => ({ moduleSlug, state: 'active' as const, score: 0.94, canDisable: true })),
    ...recommended.map(moduleSlug => ({ moduleSlug, state: 'recommended' as const, score: 0.82, canDisable: true })),
    ...hidden.map(moduleSlug => ({ moduleSlug, state: 'hidden' as const, score: 0.25, canDisable: true })),
  ];

  return entries.map(entry => ({
    ...entry,
    titlePtBr: moduleNames[entry.moduleSlug] ?? entry.moduleSlug,
    reasonCodes: [`BUSINESS_KIND_${input.businessKind.toUpperCase()}`],
    explanationPtBr: buildExplanation(entry.moduleSlug, entry.state, input.businessKind),
    dependencies: entry.moduleSlug === 'business' ? ['identity'] : entry.moduleSlug === 'permissions' ? ['identity', 'business'] : ['identity', 'business', 'permissions'].filter(dep => dep !== entry.moduleSlug),
  }));
}

function buildExplanation(moduleSlug: string, state: ModuleState, businessKind: BusinessKind) {
  const moduleName = moduleNames[moduleSlug] ?? moduleSlug;
  if (state === 'mandatory') return `${moduleName} é obrigatório para garantir identidade, empresa, permissões e auditoria da operação.`;
  if (state === 'active') return `${moduleName} foi ativado automaticamente porque combina com o perfil operacional ${businessKind}.`;
  if (state === 'recommended') return `${moduleName} é recomendado, mas pode aguardar configuração manual pela empresa.`;
  if (state === 'hidden') return `${moduleName} ficará oculto na navegação inicial para reduzir complexidade sem apagar dados.`;
  return `${moduleName} depende de plano, permissão, configuração ou revisão administrativa.`;
}
