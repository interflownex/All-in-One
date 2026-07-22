export type CatalogField = {
  id: string;
  domain: string;
  logical_entity: string;
  logical_field: string;
  data_type: string;
  description: string;
  allowed_components: string[];
  mandatory_validations: string[];
  allowed_calculations: string[];
  sensitivity: string;
  unit?: string | null;
  status: string;
};

export type FieldBinding = {
  id: string;
  field_catalog_id: string;
  command: string;
  api: string;
  dto: string;
  logical_path: string;
  status: string;
};

export type BuilderBlock = {
  id: string;
  block_type: "section" | "group" | "tab" | "column";
  parent_block_id: string | null;
  display_order: number;
  title: string;
  description: string;
  width: number;
  collapsible: boolean;
  visibility_rule_id: string | null;
  repeatable: boolean;
  allowed_style: "default" | "compact" | "highlight" | "bordered";
};

export type BuilderField = {
  id: string;
  block_id: string;
  field_catalog_id: string;
  field_binding_id: string;
  component: string;
  label: string;
  help_text: string;
  placeholder: string;
  required: boolean;
  read_only: boolean;
  hidden: boolean;
  display_order: number;
  width: number;
  mask: string | null;
  format: string | null;
  default_value: unknown;
  value_source: "user" | "context" | "backend" | "calculation";
  unit: string | null;
  permissions: Record<string, unknown>;
  visibility_rule_id: string | null;
  validation_ids: string[];
  audit_policy: Record<string, unknown>;
};

export type BuilderValidation = {
  id: string;
  field_id: string;
  validation_type: string;
  parameters: Record<string, unknown>;
  message_pt_br: string;
  severity: "info" | "warning" | "error" | "blocking";
  condition: null;
  run_frontend: boolean;
  run_backend: boolean;
  status: "active";
  version: number;
};

export type BuilderDocument = {
  schemaVersion: 1;
  definitionId: string | null;
  versionId: string | null;
  name: string;
  moduleId: string;
  businessContext: string;
  status: "draft" | "editing" | "submitted" | "approved" | "published";
  versionNumber: number;
  blocks: BuilderBlock[];
  fields: BuilderField[];
  validations: BuilderValidation[];
  calculations: Record<string, unknown>[];
  visibility_rules: Record<string, unknown>[];
};

export type BuilderFeedback = { kind: "idle" | "loading" | "success" | "error"; message: string };
