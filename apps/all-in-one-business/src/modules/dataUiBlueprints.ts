export type DataSurfaceKind = 'overview' | 'report' | 'list' | 'form';

export type DataUiBlueprint = {
  moduleSlug: string;
  entity: string;
  titlePtBr: string;
  surface: DataSurfaceKind;
  requiredBlocks: string[];
  requiredFields?: string[];
  requiredStates: string[];
  primaryActionPtBr: string;
  auditEvent: string;
};

const states = [
  'carregamento',
  'vazio_inicial',
  'vazio_apos_filtro',
  'erro_recuperavel',
  'sem_permissao',
  'sucesso',
  'somente_leitura',
  'dados_desatualizados',
];

export const dataUiBlueprints: DataUiBlueprint[] = [
  {
    moduleSlug: 'business',
    entity: 'companies',
    titlePtBr: 'Empresas',
    surface: 'form',
    requiredBlocks: ['dados essenciais', 'endereco', 'documentos', 'classificacao', 'modulos recomendados', 'revisao'],
    requiredFields: ['cnpj', 'razaoSocial', 'nomeFantasia', 'cnaePrincipal', 'porte', 'telefone', 'email', 'cep', 'uf', 'municipio'],
    requiredStates: states,
    primaryActionPtBr: 'Concluir cadastro da empresa',
    auditEvent: 'business.company.submitted',
  },
  {
    moduleSlug: 'marketplace',
    entity: 'products',
    titlePtBr: 'Produtos',
    surface: 'form',
    requiredBlocks: ['identificacao', 'precos', 'estoque', 'imagens', 'tributacao', 'canais', 'revisao'],
    requiredFields: ['nome', 'sku', 'categoria', 'preco', 'custo', 'estoqueAtual', 'unidade', 'peso', 'dimensoes', 'ncm'],
    requiredStates: states,
    primaryActionPtBr: 'Salvar produto',
    auditEvent: 'marketplace.product.created',
  },
  {
    moduleSlug: 'finance',
    entity: 'receivables',
    titlePtBr: 'Contas a receber',
    surface: 'list',
    requiredBlocks: ['busca', 'filtros', 'tabela', 'acoes em massa', 'resumo financeiro', 'exportacao'],
    requiredStates: states,
    primaryActionPtBr: 'Registrar recebimento',
    auditEvent: 'erp.receivable.reconciled',
  },
  {
    moduleSlug: 'erp',
    entity: 'fiscal_documents',
    titlePtBr: 'Documentos fiscais',
    surface: 'report',
    requiredBlocks: ['periodo', 'status fiscal', 'rejeicoes', 'valores', 'tabela equivalente', 'exportacao'],
    requiredStates: states,
    primaryActionPtBr: 'Emitir documento fiscal',
    auditEvent: 'erp.invoice.submitted',
  },
  {
    moduleSlug: 'wms',
    entity: 'inventory',
    titlePtBr: 'Inventario',
    surface: 'overview',
    requiredBlocks: ['estoque atual', 'baixo estoque', 'rupturas', 'giro', 'proximas acoes', 'origem dos dados'],
    requiredStates: states,
    primaryActionPtBr: 'Ajustar inventario',
    auditEvent: 'wms.inventory.received',
  },
  {
    moduleSlug: 'tms',
    entity: 'freights',
    titlePtBr: 'Fretes',
    surface: 'overview',
    requiredBlocks: ['em andamento', 'atrasados', 'custo por rota', 'prova de entrega', 'ocorrencias', 'origem dos dados'],
    requiredStates: states,
    primaryActionPtBr: 'Criar frete',
    auditEvent: 'tms.freight.created',
  },
  {
    moduleSlug: 'crm',
    entity: 'leads',
    titlePtBr: 'Leads',
    surface: 'list',
    requiredBlocks: ['busca', 'funil', 'filtros', 'tabela', 'atividades', 'proxima acao'],
    requiredStates: states,
    primaryActionPtBr: 'Cadastrar lead',
    auditEvent: 'crm.lead.created',
  },
  {
    moduleSlug: 'jobs',
    entity: 'job_postings',
    titlePtBr: 'Vagas',
    surface: 'form',
    requiredBlocks: ['cargo', 'contrato', 'local', 'remuneracao', 'requisitos', 'etapas', 'responsaveis', 'publicacao'],
    requiredFields: ['cargo', 'regime', 'localTrabalho', 'faixaSalarial', 'requisitos', 'prazo', 'responsavel'],
    requiredStates: states,
    primaryActionPtBr: 'Publicar vaga',
    auditEvent: 'jobs.job_posting.published',
  },
  {
    moduleSlug: 'services',
    entity: 'providers',
    titlePtBr: 'Prestadores',
    surface: 'form',
    requiredBlocks: ['dados do prestador', 'area de atendimento', 'servicos', 'agenda', 'precos', 'evidencias', 'revisao'],
    requiredFields: ['nome', 'documento', 'telefone', 'categoria', 'areaAtendimento', 'precoBase', 'disponibilidade'],
    requiredStates: states,
    primaryActionPtBr: 'Ativar prestador',
    auditEvent: 'services.visit.created',
  },
  {
    moduleSlug: 'health',
    entity: 'appointments',
    titlePtBr: 'Consultas',
    surface: 'form',
    requiredBlocks: ['paciente', 'profissional', 'agenda', 'consentimento', 'documentos', 'confirmacao'],
    requiredFields: ['paciente', 'profissional', 'especialidade', 'data', 'horario', 'consentimento'],
    requiredStates: states,
    primaryActionPtBr: 'Agendar consulta',
    auditEvent: 'health.appointment.created',
  },
];

export function getBlueprintsByModule(moduleSlug: string) {
  return dataUiBlueprints.filter(blueprint => blueprint.moduleSlug === moduleSlug);
}
