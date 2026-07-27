# Tarefas da IA Desenvolvedora

**Versão:** 1.3  
**Data da entrega:** 27/07/2026  
**Hora da entrega:** 01:55:20  
**Fuso horário:** `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch de execução:** `fix/cicd-governanca-v2-8-2026-07-27`  
**Commit-base:** `77fa6fab5f1c881ba6289dc288dc64e20421614a`  
**Issue de orquestração:** `#49`  
**Pull request:** `#50`  
**Destino:** Codex e demais IAs desenvolvedoras autorizadas

## 1. Objetivo desta versão

Executar o plano de ação v2.8 para restaurar uma linha de integração confiável, corrigir os gates de CI/CD e segurança, reduzir PRs concorrentes e preservar uma retomada auditável.

## 2. Estado confirmado

### Concluído neste ciclo

- branch limpa criada diretamente da `main`;
- issue `#49` criada e atribuída ao mantenedor;
- PR em rascunho `#50` aberta;
- PR `#34` encerrada sem merge por ter sido substituída pela `#37`;
- confirmado que o repositório ainda permite `merge commit`, `rebase merge` e `squash merge` simultaneamente;
- workflow Python alterado para auditar `requirements-dev.txt`, evitando auditar ferramentas internas do runner;
- workflow temporária de regeneração protegida criada;
- workflow de evidências diagnósticas criada;
- nenhuma credencial adicionada;
- nenhum push direto na `main`;
- nenhum merge executado.

### Em execução

- regeneração de artefatos a partir de `scripts/scaffold_modules.py`;
- regeneração de `config/events/domain_event_fixtures.json`;
- coleta versionada das saídas de validação Android, `pip-audit` e Trivy Jobs;
- nova execução dos gates Continuous Integration, Security e Docker Compose Health Gate.

### Pendente

- confirmar commit automático dos artefatos gerados;
- executar `scripts/check_generated_artifacts.py` numa árvore limpa;
- corrigir falhas restantes de `validate_openapi.py` e `validate_repository.py`;
- avaliar o relatório Trivy da imagem Jobs;
- corrigir o contrato ou build Android conforme evidência real;
- corrigir Docker Compose e healthchecks HTTP;
- remover workflows temporárias após cumprirem sua função;
- criar matriz final de destino das PRs `#36`, `#37`, `#38`, `#40`, `#46` e `#48`;
- impor administrativamente uso exclusivo de Squash and Merge;
- atualizar pendências e relatório v2.8 no repositório;
- manter PR `#50` em rascunho até todos os gates obrigatórios ficarem verdes.

## 3. Fontes de verdade

Consultar nesta ordem:

1. `AGENTS.md`;
2. este `tarefas.md`;
3. issue `#49`;
4. PR `#50`;
5. `docs/Pendências Do desenvolvedor.md`;
6. relatórios de pendências mais recentes;
7. `docs/relatorios/execucao-v2.8/`, quando criado pelas workflows;
8. logs dos workflows do commit atual;
9. PRs `#36`, `#37`, `#38`, `#40`, `#46` e `#48`.

## 4. Regras mandatórias

1. Não realizar push direto na `main`.
2. Não realizar merge com gate vermelho.
3. Integração final somente por Squash and Merge.
4. Não usar `merge commit` ou `rebase merge`.
5. Não inserir secrets, tokens, senhas, chaves ou certificados.
6. Não reativar o módulo Vision.
7. Não alterar logomarcas oficiais.
8. Não excluir arquivos em massa sem inventário e justificativa.
9. Não declarar Health Watch + SafeZone funcional com base apenas em documentação.
10. Não converter falha de scanner em sucesso por supressão genérica.
11. Atualizar esta passagem antes de encerrar ou transferir o ciclo.

## 5. Ordem de retomada

### Prioridade 1: artefatos gerados

- verificar o head atual da PR `#50`;
- confirmar se existe commit `fix(ci): sincronizar artefatos gerados`;
- executar ou consultar:

```bash
python scripts/scaffold_modules.py --check
python scripts/generate_domain_event_fixtures.py --check
python scripts/check_generated_artifacts.py
```

- revisar qualquer alteração antes de aceitar;
- rejeitar exclusões ou caminhos fora do escopo aprovado.

### Prioridade 2: evidências diagnósticas

Ler:

- `docs/relatorios/execucao-v2.8/android-validation.txt`;
- `docs/relatorios/execucao-v2.8/python-audit.json`;
- `docs/relatorios/execucao-v2.8/python-audit.stderr.txt`;
- `docs/relatorios/execucao-v2.8/jobs-image-build.txt`;
- `docs/relatorios/execucao-v2.8/jobs-trivy.json`.

Corrigir somente causas reproduzidas nesses arquivos.

### Prioridade 3: Docker Compose

- consultar o job `Docker Compose Health Gate` do head atual;
- identificar se a falha ocorre em `docker compose config`, build, inicialização ou `/health`;
- preservar logs dos serviços pendentes;
- não aumentar timeout ou retry sem evidência de lentidão legítima.

### Prioridade 4: governança de PRs

Produzir matriz obrigatória:

| PR | Estado | Base | Mergeável | Sobreposição | Ação recomendada | Justificativa |
|---|---|---|---|---|---|---|
| #36 | aberta | verificar | verificar | verificar | rebase, reconstruir ou encerrar | pendente |
| #37 | rascunho | antiga | falso no início do ciclo | substitui #34 | dividir ou reconstruir | 474 arquivos e 117 commits |
| #38 | aberta | verificar | verificar | verificar | rebase, reconstruir ou encerrar | pendente |
| #40 | rascunho | antiga | verificar | Vision residual em workflow | corrigir ou reconstruir | pendente |
| #46 | rascunho | main v2.6 | verificar | documentação e Telegram | reavaliar após gates | pendente |
| #48 | aberta | main v2.6 | verificar | Health Watch documental | manter separada | não é implementação funcional |

### Prioridade 5: encerramento

- remover `.github/workflows/v28-regenerate-artifacts.yml` após a sincronização;
- remover `.github/workflows/v28-diagnostics.yml` após a coleta;
- executar gates finais;
- atualizar issue `#49` e PR `#50`;
- manter PR em rascunho se qualquer gate obrigatório falhar;
- nunca habilitar auto-merge enquanto a configuração permitir métodos alternativos.

## 6. Testes e gates mínimos

```bash
python3 scripts/audit_confirmation_v7.py
python3 scripts/validate_repository.py
python3 scripts/check_generated_artifacts.py
python3 -m pytest -q tests/test_security_gates.py
python3 -m pytest -q tests/test_telegram_activity_reporter.py
python3 scripts/validate_valley_android_release.py
```

Executar também os workflows:

- Continuous Integration;
- Security;
- Docker Compose Health Gate;
- OpenAPI e Database, quando acionados pela PR.

## 7. Critérios de aceite

O ciclo só pode ser concluído quando:

- artefatos gerados estiverem sincronizados;
- validação de repositório e OpenAPI passarem;
- auditoria Python passar sobre as dependências declaradas;
- Trivy Jobs passar ou houver correção comprovada;
- Android passar em contrato, testes, lint e assemble;
- Docker Compose tiver todos os serviços obrigatórios saudáveis;
- PRs substituídas estiverem encerradas;
- cada PR aberta tiver destino documentado;
- nenhuma referência operacional ao Vision permanecer;
- configuração exclusiva de Squash and Merge estiver comprovada ou registrada como bloqueio administrativo;
- workflows temporárias forem removidas;
- PR `#50` contiver evidências completas.

## 8. Resultado parcial do ciclo

- **SHA inicial:** `77fa6fab5f1c881ba6289dc288dc64e20421614a`
- **Branch:** `fix/cicd-governanca-v2-8-2026-07-27`
- **Issue:** `#49`
- **PR:** `#50`
- **PR encerrada:** `#34`, sem merge
- **Correção aplicada:** auditoria Python direcionada a `requirements-dev.txt`
- **Gates verdes:** ainda não declarados
- **Gates em execução ou falha:** CI, Security, Docker Compose e regeneração
- **Risco principal:** grande drift entre templates canônicos e artefatos versionados
- **Bloqueio administrativo:** métodos alternativos de merge continuam habilitados

## 9. Primeira ação da próxima IA

Consultar o head atual da PR `#50` e verificar se as workflows criaram:

1. o commit `fix(ci): sincronizar artefatos gerados`;
2. o diretório `docs/relatorios/execucao-v2.8/`.

A partir dessas evidências, corrigir o primeiro gate ainda vermelho sem iniciar nova funcionalidade.

## 10. Histórico de versões

| Versão | Data e hora | Alteração principal |
|---|---|---|
| 1.0 | 26/07/2026 13:49:32 | Criação da diretriz permanente. |
| 1.1 | 26/07/2026 14:01:53 | Primeiro ciclo v2.6 e issue #43. |
| 1.2 | 26/07/2026 23:06:33 | Consolidação documental v2.7 e início do executor Telegram na PR #46. |
| 1.3 | 27/07/2026 01:55:20 | Execução do plano v2.8, issue #49, PR #50, encerramento da #34, correção do pip-audit e workflows de regeneração e diagnóstico. |
