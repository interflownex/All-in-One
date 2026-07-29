import type { Approval, ModuleRecord, NavItem } from "./types";

export const navigation: NavItem[] = [
  { id: "overview", label: "Visão geral", shortLabel: "Início", icon: "home" },
  { id: "approvals", label: "Aprovações", shortLabel: "Aprovar", icon: "check" },
  { id: "companies", label: "Empresas", shortLabel: "Empresas", icon: "building" },
  { id: "modules", label: "Módulos", shortLabel: "Módulos", icon: "grid" },
  { id: "operations", label: "Operações", shortLabel: "Operação", icon: "pulse" },
  { id: "security", label: "Segurança", shortLabel: "Segurança", icon: "shield" },
  { id: "reports", label: "Relatórios", shortLabel: "Relatórios", icon: "chart" },
  { id: "settings", label: "Configurações", shortLabel: "Mais", icon: "settings" },
];

export const approvals: Approval[] = [
  {
    id: "APR-1048",
    title: "Cadastro da empresa Horizonte Logística",
    subtitle: "CNPJ e representante legal aguardam validação final.",
    type: "Empresa",
    priority: "Alta",
    age: "há 18 min",
    status: "Pendente",
  },
  {
    id: "APR-1047",
    title: "Ativação do módulo Marketplace",
    subtitle: "Solicitação vinculada ao plano Business Essencial.",
    type: "Módulo",
    priority: "Média",
    age: "há 36 min",
    status: "Em análise",
  },
  {
    id: "APR-1046",
    title: "Revisão de documento KYB",
    subtitle: "Documento societário reenviado após correção.",
    type: "Documento",
    priority: "Normal",
    age: "há 1 h",
    status: "Pendente",
  },
  {
    id: "APR-1045",
    title: "Limite operacional temporário",
    subtitle: "Solicitação auditada para operação de teste.",
    type: "Financeiro",
    priority: "Alta",
    age: "há 2 h",
    status: "Pendente",
  },
];

export const modules: ModuleRecord[] = [
  { slug: "identity", name: "Identity", audience: "Ambos", status: "Ativo", health: 99, incidents: 0, enabled: true },
  { slug: "business", name: "Business", audience: "B2B", status: "Ativo", health: 98, incidents: 0, enabled: true },
  { slug: "marketplace", name: "Marketplace", audience: "Ambos", status: "Homologação", health: 94, incidents: 1, enabled: true },
  { slug: "stock", name: "Stock", audience: "B2B", status: "Planejado", health: 72, incidents: 0, enabled: false },
  { slug: "delivery", name: "Delivery", audience: "Ambos", status: "Planejado", health: 68, incidents: 0, enabled: false },
  { slug: "riders", name: "Valley Riders", audience: "B2C", status: "Homologação", health: 91, incidents: 1, enabled: true },
  { slug: "finance", name: "Finance", audience: "Ambos", status: "Bloqueado", health: 84, incidents: 2, enabled: false },
  { slug: "jobs", name: "Jobs", audience: "Ambos", status: "Ativo", health: 97, incidents: 0, enabled: true },
  { slug: "health", name: "Health", audience: "B2C", status: "Planejado", health: 61, incidents: 0, enabled: false },
  { slug: "api_hub", name: "API Hub", audience: "Equipe técnica", status: "Ativo", health: 99, incidents: 0, enabled: true },
];

export const activity = [
  { title: "PR #65 integrada", detail: "Marketplace Fase 1", time: "agora", tone: "success" },
  { title: "Gate de segurança aprovado", detail: "Python, Android e containers", time: "há 4 min", tone: "success" },
  { title: "Empresa enviada para análise", detail: "Horizonte Logística", time: "há 18 min", tone: "info" },
  { title: "Alerta de observabilidade", detail: "Finance com latência elevada", time: "há 31 min", tone: "warning" },
];
