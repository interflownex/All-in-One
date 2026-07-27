# Tarefas da IA Desenvolvedora

**Versão:** 1.4  
**Data da entrega:** 27/07/2026  
**Hora da entrega:** 02:17:29  
**Fuso horário:** `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch de execução:** `fix/cicd-governanca-v2-8-2026-07-27`  
**Commit-base:** `77fa6fab5f1c881ba6289dc288dc64e20421614a`  
**Issue de orquestração:** `#49`  
**Pull request:** `#50`  
**Destino:** Codex e demais IAs desenvolvedoras autorizadas

## 1. Objetivo desta versão

Registrar o estado real após a execução do plano v2.8, preservar as evidências produzidas e definir uma retomada inequívoca para os gates ainda vermelhos.

## 2. Entregas concluídas

### Governança

- branch limpa criada diretamente da `main`;
- issue `#49` criada e atribuída ao mantenedor;
- PR `#50` aberta e mantida em rascunho;
- PR `#34` encerrada sem merge por substituição pela `#37`;
- PRs `#36` e `#38` convertidas para rascunho;
- matriz de decisão das PRs `#36`, `#37`, `#38`, `#40`, `#46`, `#48` e `#50` registrada na issue `#49`;
- nenhum push direto na `main`;
- nenhum merge ou auto-merge executado;
- configuração exclusiva de Squash and Merge registrada como bloqueio administrativo, pois os três métodos de merge continuam habilitados.

### Artefatos e contratos

- artefatos canônicos regenerados a partir de `scripts/scaffold_modules.py`;
- contratos, OpenAPI, testes e entrypoints derivados sincronizados;
- arquivos alterados pela regeneração limitados ao escopo autorizado;
- nenhuma exclusão em massa aceita;
- `pypdf` atualizado de `6.13.3` para `6.14.2` na fonte canônica e no módulo Jobs;
- workflow temporária de regeneração arquivada e sem permissão de escrita.

### Segurança

- `pip-audit` alterado para auditar `requirements-dev.txt`, não o ambiente completo do runner;
- auditoria Python de dependências passou após atualização do `pypdf`;
- imagens API Hub, Identity e Jobs passaram no Trivy;
- todos os projetos JavaScript passaram no `npm audit` configurado;
- contrato Android passou;
- causa do primeiro bloqueio Android identificada como permissão de execução do `gradlew`;
- gate Android atualizado com `chmod +x apps/valley-android/gradlew`;
- relatório Bandit versionado em `docs/relatorios/execucao-v2.8/bandit-summary.md`.

### Banco de dados e Vision

- etapa operacional `Exercise Vision PostgreSQL store` removida do workflow de banco;
- migração com falha identificada: `029_unified_immutable_audit.sql`;
- palavra reservada `authorization` citada corretamente na migração;
- writer PostgreSQL de auditoria atualizado para usar `"authorization"` no `INSERT`;
- DSN Riders conferido e corrigido após a edição do workflow;
- remediação SQL temporária arquivada e sem permissão de escrita.

### Evidências e gates verdes já observados

- OpenAPI: aprovado;
- Valley DAST: aprovado;
- contrato Android: aprovado;
- `pip-audit`: aprovado;
- Trivy API Hub, Identity e Jobs: aprovado;
- auditorias JavaScript: aprovadas;
- relatórios versionados em `docs/relatorios/execucao-v2.8/`.

## 3. Pendências atuais

### Críticas

1. **Continuous Integration**
   - ainda para em `Check generated artifacts`;
   - OpenAPI já passa separadamente;
   - isolar se a falha restante está em `scaffold_modules.py --check`, fixtures ou `validate_repository.py`;
   - os testes unitários continuam bloqueados enquanto esse gate falhar.

2. **Bandit**
   - relatório registra 114 achados totais, incluindo itens médios reais;
   - principais grupos: SQL dinâmico, abertura de URL sem restrição de esquema e parsing XML inseguro;
   - não aplicar supressão genérica;
   - corrigir ou justificar individualmente por arquivo e teste Bandit.

3. **Docker Compose Health Gate**
   - ainda falha em `Validate compose services and HTTP healthchecks`;
   - identificar serviço, etapa e endpoint exatos;
   - não aumentar timeout ou retries sem evidência de lentidão legítima.

### Altas

1. Reexecutar o gate Android após o `chmod +x` e verificar testes, lint, assemble e CodeQL.
2. Reexecutar migrações após a correção da coluna `authorization` e registrar o próximo arquivo com falha, se houver.
3. Executar `tests/test_security_gates.py` após a remediação dos achados Bandit médios.
4. Remover fisicamente as workflows v2.8 arquivadas quando a integração permitir exclusão segura; atualmente estão neutralizadas, manuais e somente leitura.
5. Atualizar `docs/Pendências Do desenvolvedor.md` após o resultado dos gates finais.
6. Impor administrativamente uso exclusivo de Squash and Merge nas configurações do repositório.

## 4. Fontes de verdade

Consultar nesta ordem:

1. `AGENTS.md`;
2. este `tarefas.md`;
3. issue `#49`;
4. PR `#50`;
5. `docs/relatorios/execucao-v2.8/`;
6. `docs/Pendências Do desenvolvedor.md`;
7. logs do head atual da PR `#50`;
8. matriz de decisão registrada na issue `#49`.

## 5. Evidências diagnósticas

- `docs/relatorios/execucao-v2.8/android-validation.txt`;
- `docs/relatorios/execucao-v2.8/android-gradle-summary.md`;
- `docs/relatorios/execucao-v2.8/bandit-summary.md`;
- `docs/relatorios/execucao-v2.8/database-migration-summary.md`;
- `docs/relatorios/execucao-v2.8/python-audit.json`;
- `docs/relatorios/execucao-v2.8/jobs-trivy.json`.

## 6. Regras mandatórias

1. Não realizar push direto na `main`.
2. Não realizar merge com gate obrigatório vermelho.
3. Integração final somente por Squash and Merge.
4. Não usar `merge commit` ou `rebase merge`.
5. Não inserir secrets, tokens, senhas, chaves ou certificados.
6. Não reativar o módulo Vision.
7. Não alterar logomarcas oficiais.
8. Não excluir arquivos em massa sem inventário e justificativa.
9. Não declarar Health Watch + SafeZone funcional com base apenas em documentação.
10. Não converter falha de scanner em sucesso por supressão genérica.
11. Não habilitar auto-merge enquanto métodos alternativos de merge permanecerem disponíveis.

## 7. Ordem de retomada

### Passo 1: consultar os gates do head atual

Ler os resultados de:

- Continuous Integration;
- Security;
- Database;
- Docker Compose Health Gate;
- OpenAPI;
- Valley DAST.

### Passo 2: isolar o verificador composto

Executar separadamente:

```bash
python scripts/scaffold_modules.py --check
python scripts/generate_domain_event_fixtures.py --check
python scripts/validate_openapi.py
python scripts/validate_repository.py
```

Corrigir o primeiro comando que retornar código diferente de zero.

### Passo 3: validar banco e Android

```bash
python scripts/validate_valley_android_release.py
chmod +x apps/valley-android/gradlew
apps/valley-android/gradlew -p apps/valley-android testDebugUnitTest lintDebug assembleDebug --no-daemon
```

Aplicar as migrações em ordem e registrar o primeiro arquivo que falhar.

### Passo 4: tratar Bandit

Priorizar achados `MEDIUM` e `HIGH` do relatório. Para cada item:

- confirmar se a entrada é controlada;
- substituir construção insegura quando possível;
- adicionar validação de esquema em URLs;
- substituir parsing XML por alternativa segura;
- usar comentário `# nosec` somente com justificativa específica e teste correspondente.

### Passo 5: encerramento

- atualizar issue `#49` e PR `#50`;
- atualizar `docs/Pendências Do desenvolvedor.md`;
- manter a PR em rascunho se qualquer gate obrigatório falhar;
- não executar merge neste ciclo sem todos os critérios de aceite.

## 8. Critérios de aceite

O ciclo somente pode ser concluído quando:

- `check_generated_artifacts.py` passar;
- testes unitários forem executados e aprovados;
- Bandit e `tests/test_security_gates.py` passarem;
- Android passar em contrato, testes, lint, assemble e CodeQL;
- migrações e stores PostgreSQL passarem;
- Docker Compose tiver todos os serviços obrigatórios saudáveis;
- OpenAPI e Valley DAST permanecerem verdes;
- nenhuma referência operacional ao Vision permanecer;
- workflows temporárias estiverem removidas ou neutralizadas sem escrita automática;
- configuração exclusiva de Squash and Merge estiver comprovada ou formalmente registrada como bloqueio administrativo.

## 9. Resultado do ciclo v2.8

- **SHA inicial:** `77fa6fab5f1c881ba6289dc288dc64e20421614a`
- **Branch:** `fix/cicd-governanca-v2-8-2026-07-27`
- **Issue:** `#49`
- **PR:** `#50`
- **PR encerrada:** `#34`, sem merge
- **PRs protegidas como rascunho:** `#36` e `#38`
- **Gates verdes observados:** OpenAPI, Valley DAST, auditoria de dependências Python, Trivy e JavaScript
- **Gates ainda não concluídos:** CI composto, Bandit, Android completo, Database completo e Docker Compose
- **Bloqueio administrativo:** métodos alternativos de merge continuam habilitados
- **Estado de integração:** não autorizado para merge

## 10. Primeira ação da próxima IA

Consultar o head atual da PR `#50` e executar individualmente os quatro comandos do Passo 2. A primeira correção deve ser aplicada ao primeiro comando que falhar, sem iniciar nova funcionalidade.

## 11. Histórico de versões

| Versão | Data e hora | Alteração principal |
|---|---|---|
| 1.0 | 26/07/2026 13:49:32 | Criação da diretriz permanente. |
| 1.1 | 26/07/2026 14:01:53 | Primeiro ciclo v2.6 e issue #43. |
| 1.2 | 26/07/2026 23:06:33 | Consolidação documental v2.7 e início do executor Telegram na PR #46. |
| 1.3 | 27/07/2026 01:55:20 | Início da execução v2.8, issue #49, PR #50 e diagnósticos iniciais. |
| 1.4 | 27/07/2026 02:17:29 | Artefatos sincronizados, pypdf corrigido, gates parciais verdes, Vision removido do workflow, Android e migração remediados, PRs protegidas e passagem consolidada. |
