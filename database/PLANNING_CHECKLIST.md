# 📑 CHECKLIST MESTRE DE PLANEJAMENTO - ALL-IN-ONE

Este documento é a fonte da verdade para a orquestração técnica e evolução do projeto. Atualizado incrementalmente a cada ciclo.

---

## 🏗️ [FRENTE 1] PERSISTÊNCIA DE DADOS (POSTGRESQL LOCAL AGORA, ALLOYDB DEPOIS, MONGODB DE APOIO)

- [ ] **Tarefa: Migração de Stores SQLite para PostgreSQL local compativel com AlloyDB**
  - **Critério de Aceite:** Todos os 25 módulos utilizando `BasePostgresStore` com sucesso em ambiente local/homologação sem dependência obrigatória de Google Cloud.
  - **Dependência:** Docker Compose local, DSNs PostgreSQL e manutenção de compatibilidade futura com AlloyDB via mesmas migrations e contratos.
  - **Módulo Afetado:** `modules/*/store.py`, `infra/terraform`.

- [ ] **Tarefa: Tipagem Forte de Stores Prioritários (Risco 1-5)**
  - **Critério de Aceite:** Stores de `finance`, `identity`, `business`, `api_hub` e `marketplace` com schemas tipados e validação de constraints.
  - **Dependência:** Fase 2 do Plano de Execução.
  - **Módulo Afetado:** `modules/{finance,identity,business,api_hub,marketplace}`.

- [ ] **Tarefa: Validação de Auditoria Append-Only e Outbox**
  - **Critério de Aceite:** Logs de auditoria gravados no Postgres e eventos publicados no RabbitMQ para todos os fluxos de mutação.
  - **Dependência:** Fase 3 do Plano de Execução.
  - **Módulo Afetado:** `workers/outbox_dispatcher`, `modules/*/main.py`.

---

## 🚢 [FRENTE 2] ORQUESTRAÇÃO E RUNTIME KUBERNETES (GKE)

- [x] **Tarefa: Validação de Disponibilidade no Artifact Registry** (2026-06-08)
  - **Critério de Aceite:** Script de check confirma as 27 imagens com tag `:latest` disponíveis para pull.
  - **Dependência:** Conclusão do build `eb8a5547-16ab-4ee4-919e-a4b62212921a`.
  - **Módulo Afetado:** `scripts/check_artifact_registry.py`.

- [x] **Tarefa: Configuração de Segredos Reais** (2026-06-08)
  - **Critério de Aceite:** DSNs e chaves JWT/Documentos disponíveis no Cloud Secret Manager.
  - **Status:** Finalizado via `scripts/setup_cloud_secrets.py`.
  - **Módulo Afetado:** `scripts/setup_cloud_secrets.py`.

- [x] **Tarefa: Bucket de Estado do Terraform** (2026-06-08)
  - **Critério de Aceite:** Bucket `gs://all-in-one-tfstate` criado na região `us-central1`.
  - **Status:** Finalizado.

- [ ] **Tarefa: Deploy Total (Infraestrutura + Apps)**
  - **Critério de Aceite:** Ambiente operacional na GCP com Ingress acessível.
  - **Status:** Reiniciado em 2026-06-08 (Cloud Build ID: 52026ef6-0869-42b7-a363-228795908e2d - em execução).
  - **Módulo Afetado:** `infra/ci-cd/cloudbuild-deploy.yaml`.

- [x] **Tarefa: Manifestos de Deploy K8s para o Core, Negócios, Logística e Verticais** (2026-06-08)
  - **Critério de Aceite:** Toda a malha de 25 módulos declarada no GKE com Ingress centralizado.
  - **Status:** Finalizado.
  - **Dependência:** Terraform concluído.
  - **Módulo Afetado:** `infra/kubernetes/`.

---

## 🌐 [FRENTE 3] GOVERNANÇA DE APIS (APIGEE & STITCH FRONTEND)

- [x] **Tarefa: Proxy de Borda para Identity no Apigee** (2026-06-08)
  - **Critério de Aceite:** Endpoints de Login/KYC protegidos por Spike Arrest e VerifyOAuthV2.
  - **Status:** Proxy Bundle base criado em `config/apigee/proxies/identity/`.
  - **Dependência:** Módulo Identity rodando em GKE ou Cloud Run.
  - **Módulo Afetado:** `config/apigee/proxies/identity/`.

- [ ] **Tarefa: Manifestos de Deploy K8s para Negócios**
  - **Critério de Aceite:** `finance` e `marketplace` rodando no GKE.
  - **Status:** Manifestos de `finance` e `marketplace` criados em `infra/kubernetes/business/`.
  - **Dependência:** Terraform concluído.
  - **Módulo Afetado:** `infra/kubernetes/business/`.

- [ ] **Tarefa: Substituição de Mock Data nas 320+ Telas**
  - **Critério de Aceite:** Chamadas `fetch` no frontend apontando para o Gateway Apigee com dados reais do Hub.
  - **Dependência:** Deploy do API Hub.
  - **Módulo Afetado:** `apps/all-in-one/src/pages/`.

---

## 🔐 [FRENTE 4] SEGURANÇA E GERENCIAMENTO DE SEGREDOS (SECRET MANAGER)

- [ ] **Tarefa: Centralização de Segredos no Cloud Secret Manager**
  - **Critério de Aceite:** Nenhuma variável de ambiente sensível (DSNs, API Keys) injetada manualmente; uso de Secret Manager.
  - **Dependência:** Configuração de Workload Identity no GKE.
  - **Módulo Afetado:** `infra/ci-cd/`, `shared/runtime.py`.

- [ ] **Tarefa: Cifragem de Documentos Privados (Jobs/CTPS)**
  - **Critério de Aceite:** PDFs da CTPS Digital cifrados com chaves do KMS/Secret Manager antes do storage.
  - **Dependência:** Módulo Jobs funcional.
  - **Módulo Afetado:** `modules/jobs/`.

- [x] **Tarefa: Manifestos de Deploy K8s para Logística** (2026-06-08)
  - **Critério de Aceite:** `delivery`, `wms` e `tms` rodando no GKE.
  - **Status:** Manifestos de Logística concluídos e integrados ao Ingress global.
  - **Dependência:** Terraform concluído.
  - **Módulo Afetado:** `infra/kubernetes/logistics/`.

- [ ] **Tarefa: Homologação do Verificador de CTPS Digital**
  - **Critério de Aceite:** Integração com o provedor oficial (ou adapter de alta fidelidade) para validação de procedência do PDF.
  - **Dependência:** Roadmap Fase 5.
  - **Módulo Afetado:** `modules/jobs/integration_adapters.py`.

- [ ] **Tarefa: Fluxo Completo de Recrutamento B2B**
  - **Critério de Aceite:** Triagem, agendamento de entrevista e logs de acesso auditáveis operacionais.
  - **Dependência:** UI de Jobs finalizada.
  - **Módulo Afetado:** `apps/all-in-one/src/pages/jobs/`.

---

## 🔄 REGRAS DE ATUALIZAÇÃO

1. **Conclusão:** Alterne `[ ]` para `[X]` e adicione a data da conclusão.
2. **Priorização:** Itens no topo de cada frente são bloqueadores imediatos.
3. **Persistência:** Commitar este arquivo após cada atualização significativa de estado.
