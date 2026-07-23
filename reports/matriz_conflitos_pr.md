# Matriz de Conflitos e Validação Pós-Merge

Esta matriz identifica os arquivos que sofreram conflitos durante a integração dos Pull Requests #8, #10 e #12, e mapeia a validação necessária para cada um, conforme o Bloco 2 do plano de ação.

| Arquivo Alterado                                       | PR de Origem (Conflito) | Houve Conflito | Gate Responsável                  | Validação Necessária                                        |
| ------------------------------------------------------ | ----------------------- | :------------: | --------------------------------- | ----------------------------------------------------------- |
| **CI/CD**                                              |                         |                |                                   |                                                             |
| `.github/workflows/security.yml`                       | #8, #10, #12            |       Sim      | CI/CD Workflow                    | Análise manual da sintaxe e lógica do workflow.             |
| **Configuração VS Code**                               |                         |                |                                   |                                                             |
| `.vscode/settings.json`                                | #8, #10                 |       Sim      | Configuração do Ambiente          | Verificação de consistência das configurações do editor.    |
| `.vscode/extensions.json`                              | #10                     |       Sim      | Configuração do Ambiente          | Verificação da lista de extensões recomendadas.             |
| `.vscode/tasks.json`                                   | #12                     |       Sim      | Configuração do Ambiente          | Verificação das tarefas automatizadas.                      |
| **Documentação e Status**                              |                         |                |                                   |                                                             |
| `STATUS.md`                                            | #8, #12                 |       Sim      | Documentação                      | Leitura e verificação da consistência do status.            |
| `apps/all-in-one-business/STATUS.md`                   | #12                     |       Sim      | Documentação                      | Leitura e verificação da consistência do status.            |
| `apps/all-in-one-health/README.md`                     | #12                     |       Sim      | Documentação                      | Leitura e verificação da consistência.                      |
| `apps/all-in-one-health/STATUS.md`                     | #12                     |       Sim      | Documentação                      | Leitura e verificação da consistência.                      |
| `apps/all-in-one-mobility/README.md`                   | #12                     |       Sim      | Documentação                      | Leitura e verificação da consistência.                      |
| `apps/all-in-one-mobility/STATUS.md`                   | #12                     |       Sim      | Documentação                      | Leitura e verificação da consistência.                      |
| `apps/all-in-one-services/README.md`                   | #12                     |       Sim      | Documentação                      | Leitura e verificação da consistência.                      |
| `apps/all-in-one-services/STATUS.md`                   | #12                     |       Sim      | Documentação                      | Leitura e verificação da consistência.                      |
| `apps/all-in-one-user/STATUS.md`                       | #12                     |       Sim      | Documentação                      | Leitura e verificação da consistência.                      |
| `docs/COMPLIANCE.md`                                   | #12                     |       Sim      | Documentação                      | Leitura e verificação da consistência.                      |
| `docs/EXECUTION_PLAN.md`                               | #12                     |       Sim      | Documentação                      | Leitura e verificação da consistência.                      |
| `docs/OPERATIONS.md`                                   | #12                     |       Sim      | Documentação                      | Leitura e verificação da consistência.                      |
| `docs/REQUIREMENTS_TRACEABILITY.md`                    | #12                     |       Sim      | Documentação                      | Leitura e verificação da consistência.                      |
| **Banco de Dados**                                     |                         |                |                                   |                                                             |
| `database/postgres/migrations/016_performance_indexes.sql` | #8, #10                 |       Sim      | Migrations (SQL)                  | Validar ordem e conteúdo da migração. Testar em DB limpo.  |
| `database/postgres/migrations/021_valley_reviews.sql`    | #10                     |       Sim      | Migrations (SQL)                  | Validar ordem e conteúdo da migração. Testar em DB limpo.  |
| `database/postgres/migrations/022_marketplace_disputes_support.sql` | #10                     |       Sim      | Migrations (SQL)                  | Validar ordem e conteúdo da migração. Testar em DB limpo.  |
| **Infraestrutura (Kubernetes)**                        |                         |                |                                   |                                                             |
| `infra/kubernetes/base/outbox-alerting.yaml`           | #12                     |       Sim      | Infra as Code (IaC)               | Validação de sintaxe do manifesto Kubernetes.               |
| **Módulos (Backend Python)**                           |                         |                |                                   |                                                             |
| `modules/shared/erp_postgres_store.py`                 | #8                      |       Sim      | Testes, Lint, Tipagem, Segurança  | `pytest`, `ruff`, `mypy`, `bandit`                          |
| `modules/api_hub/main.py`                              | #12                     |       Sim      | Testes, Lint, Tipagem, Segurança  | `pytest`, `ruff`, `mypy`, `bandit`                          |
| `modules/identity/kyc_mfa_models.py`                   | #12                     |       Sim      | Testes, Lint, Tipagem, Segurança  | `pytest`, `ruff`, `mypy`, `bandit`                          |
| `modules/identity/main.py`                             | #12                     |       Sim      | Testes, Lint, Tipagem, Segurança  | `pytest`, `ruff`, `mypy`, `bandit`                          |
| `modules/shared/domain_rules.py`                       | #12                     |       Sim      | Testes, Lint, Tipagem, Segurança  | `pytest`, `ruff`, `mypy`, `bandit`                          |
| `modules/shared/finance_postgres_store.py`             | #12                     |       Sim      | Testes, Lint, Tipagem, Segurança  | `pytest`, `ruff`, `mypy`, `bandit`                          |
| `modules/shared/logging_utils.py`                      | #12                     |       Sim      | Testes, Lint, Tipagem, Segurança  | `pytest`, `ruff`, `mypy`, `bandit`                          |
| `modules/shared/postgres_store.py`                     | #12                     |       Sim      | Testes, Lint, Tipagem, Segurança  | `pytest`, `ruff`, `mypy`, `bandit`                          |
| `modules/shared/runtime.py`                            | #12                     |       Sim      | Testes, Lint, Tipagem, Segurança  | `pytest`, `ruff`, `mypy`, `bandit`                          |
| **Aplicações (Frontend)**                              |                         |                |                                   |                                                             |
| `apps/valley_business/src/TelemetryDashboard.tsx`      | #8, #12                 |       Sim      | Build, Lint (Frontend)            | `npm run lint`, `npm run build` no app correspondente.      |
| `apps/all-in-one-business/src/App.tsx`                 | #12                     |       Sim      | Build, Lint (Frontend)            | `npm run lint`, `npm run build` no app correspondente.      |
| `apps/all-in-one-business/src/components/SmartCRUD.tsx`| #12                     |       Sim      | Build, Lint (Frontend)            | `npm run lint`, `npm run build` no app correspondente.      |
| `apps/all-in-one-health/*`                             | #12                     |       Sim      | Build, Lint (Frontend)            | `npm ci`, `npm run lint`, `npm run build` no app.           |
| `apps/all-in-one-mobility/*`                             | #12                     |       Sim      | Build, Lint (Frontend)            | `npm ci`, `npm run lint`, `npm run build` no app.           |
| `apps/all-in-one-riders/*`                               | #12                     |       Sim      | Build, Lint (Frontend)            | `npm ci`, `npm run lint`, `npm run build` no app.           |
| `apps/all-in-one-services/*`                             | #12                     |       Sim      | Build, Lint (Frontend)            | `npm ci`, `npm run lint`, `npm run build` no app.           |
| `apps/all-in-one/src/App.tsx`                          | #12                     |       Sim      | Build, Lint (Frontend)            | `npm run lint`, `npm run build` no app correspondente.      |
| `apps/all-in-one/src/components/SmartCRUD.tsx`         | #12                     |       Sim      | Build, Lint (Frontend)            | `npm run lint`, `npm run build` no app correspondente.      |
| `apps/valley_business/src/App.tsx`                     | #12                     |       Sim      | Build, Lint (Frontend)            | `npm run lint`, `npm run build` no app correspondente.      |
| `apps/valley_rider/src/App.tsx`                        | #12                     |       Sim      | Build, Lint (Frontend)            | `npm run lint`, `npm run build` no app correspondente.      |
| **Configuração**                                       |                         |                |                                   |                                                             |
| `config/module_catalog.json`                           | #12                     |       Sim      | Configuração                      | Auditoria de catálogo (`scripts/audit_confirmation_v7.py`). |
| `config/observability/outbox_alerts.json`              | #12                     |       Sim      | Configuração                      | Verificação de sintaxe JSON.                                |
| `config/observability/outbox_dashboard.json`           | #12                     |       Sim      | Configuração                      | Verificação de sintaxe JSON.                                |
| **Scripts e Testes**                                   |                         |                |                                   |                                                             |
| `requirements-dev.txt`                                 | #8, #10                 |       Sim      | Dependências                      | `pip-audit`.                                                |
| `scripts/validate_repository.py`                       | #8, #10, #12            |       Sim      | Scripts, Testes                   | Execução do script e `pytest` se houver testes para ele.    |
| `scripts/docker_gcp_push.py`                           | #10                     |       Sim      | Scripts                           | Análise estática (`ruff`, `mypy`).                          |
| `scripts/generate_kubernetes_manifests.py`             | #12                     |       Sim      | Scripts                           | Análise estática (`ruff`, `mypy`).                          |
| `tests/*`                                              | #10, #12                |       Sim      | Testes                            | `pytest`.                                                   |

**Nota:** A lista de arquivos para o PR #12 foi massiva. A matriz acima prioriza a identificação das áreas de maior risco e os gates de validação correspondentes, agrupando arquivos de front-end por aplicação para maior clareza.
