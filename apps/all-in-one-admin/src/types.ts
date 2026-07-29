export type ScreenId =
  | "overview"
  | "approvals"
  | "companies"
  | "modules"
  | "operations"
  | "security"
  | "reports"
  | "settings";

export type NavItem = {
  id: ScreenId;
  label: string;
  shortLabel: string;
  icon: IconName;
};

export type IconName =
  | "home"
  | "check"
  | "building"
  | "grid"
  | "pulse"
  | "shield"
  | "chart"
  | "settings"
  | "search"
  | "bell"
  | "menu"
  | "arrow"
  | "more"
  | "trend"
  | "users"
  | "orders"
  | "money";

export type Approval = {
  id: string;
  title: string;
  subtitle: string;
  type: "Empresa" | "Documento" | "Módulo" | "Financeiro";
  priority: "Alta" | "Média" | "Normal";
  age: string;
  status: "Pendente" | "Em análise" | "Aprovado";
};

export type ModuleStatus = "Ativo" | "Homologação" | "Bloqueado" | "Planejado";

export type ModuleRecord = {
  slug: string;
  name: string;
  audience: "B2C" | "B2B" | "Ambos" | "Equipe técnica";
  status: ModuleStatus;
  health: number;
  incidents: number;
  enabled: boolean;
};
