# Mapa de Fontes de Verdade e Propriedade de Dados

Este documento define a propriedade de cada entidade de negócio (fonte de verdade) dentro do ecossistema All-in-One + Valley. A análise é baseada na estrutura `MODULE_ENTITIES` encontrada em `modules/shared/domain_rules.py`, que funciona como o contrato de propriedade de dados entre os módulos.

## Princípio da Fonte Única de Verdade

Conforme a diretriz do "MEMORANDO MESTRE", cada dado deve possuir uma fonte oficial de verdade. O módulo proprietário é o único responsável por escrever e validar os dados de suas entidades. Outros módulos podem ler esses dados (via APIs) ou reagir a mudanças (via eventos), mas não devem modificar diretamente dados que não possuem.

## Matriz de Propriedade: Módulo vs. Entidades

A tabela a seguir detalha qual módulo é o proprietário (a fonte de verdade) de cada conjunto de entidades de dados.

| Módulo Proprietário | Entidades Gerenciadas |
| :--- | :--- |
| `identity` | `users`, `documents`, `biometrics`, `sessions`, `identity_verifications`, `consent_records` |
| `business` | `companies`, `branches`, `company_documents`, `user_company_memberships`, `catalog_offers` |
| `permissions`| `roles`, `permissions`, `user_roles`, `access_policies`, `approval_limits` |
| `finance` | `wallets`, `ledger_entries`, `escrows`, `splits`, `invoices`, `valley_gold_ledger_entries` |
| `marketplace`| `stores`, `products`, `carts`, `orders`, `reviews`, `disputes`, `pepita_grants` |
| `stock` | `suppliers`, `catalog_products`, `price_rules`, `supplier_orders`, `discount_quotes` |
| `delivery` | `delivery_requests`, `quotes`, `assignments`, `proofs`, `insurance_options` |
| `riders` | `rider_profiles`, `rider_documents`, `vehicles`, `rider_reviews` |
| `services` | `providers`, `visits`, `quotes`, `service_contracts`, `evidence` |
| `mobility` | `rides`, `routes`, `stops`, `tickets`, `fare_rules` |
| `jobs` | `resumes`, `employment_records`, `resume_documents`, `job_postings`, `applications`, `resume_access_logs` |
| `erp` | `accounts`, `payables`, `receivables`, `cost_centers`, `fiscal_documents` |
| `wms` | `warehouses`, `bins`, `inventory`, `picking_waves`, `shipments` |
| `tms` | `carriers`, `freights`, `routes`, `proofs_of_delivery`, `freight_audits` |
| `crm` | `leads`, `opportunities`, `activities`, `campaigns` |
| `bpm` | `processes`, `workflow_instances`, `tasks`, `sla_policies` |
| `document` | `folders`, `documents`, `versions`, `retention_policies` |
| `hr` | `employees`, `payroll_runs`, `candidates`, `courses`, `occupational_records` |
| `health` | `patients`, `appointments`, `medical_records`, `prescriptions`, `beds` |
| `vision` | `devices`, `streams`, `recordings`, `motion_alerts` |
| `legal` | `cases`, `deadlines`, `hearings`, `legal_contracts` |
| `property` | `properties`, `units`, `leases`, `assemblies`, `maintenance_orders` |
| `bi` | `datasets`, `dashboards`, `indicators`, `exports` |
| `ai_core` | `ai_memories`, `moderation_decisions`, `model_runs` |
| `api_hub` | `api_clients`, `api_keys`, `webhooks`, `integration_runs` |

Este mapa de propriedade é fundamental para as próximas fases do projeto, garantindo que a análise de cada campo, a construção de APIs e a modelagem de formulários respeitem os limites de cada domínio.
