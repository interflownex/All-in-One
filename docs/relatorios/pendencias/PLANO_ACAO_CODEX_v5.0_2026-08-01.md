# Plano de Ação Codex v5.0

**Data e hora:** 01/08/2026 03:52, `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `codex/corrigir-inconsistencias-mandatorias-20260801`  
**Base:** `63ceb867c6342a3706e82a650e6072522facfbd7`  
**Classificação:** `Pendências > Técnico > Equipe Técnica`  
**Público-alvo:** Equipe Técnica

## Objetivo

Eliminar inconsistências de governança, documentação e rastreabilidade detectáveis no repositório remoto; impedir regressão de escopo; reconciliar issues com entregas reais; preservar bloqueios externos; e preparar a próxima evolução sem risco de merge destrutivo.

## Princípios mandatórios

1. nenhuma escrita direta em `main`;
2. nenhum merge antes de todos os gates verdes no mesmo SHA;
3. somente Squash and Merge;
4. nenhuma credencial no Git;
5. nenhuma exclusão em massa sem inventário;
6. nenhuma branch antiga mesclada diretamente;
7. nenhuma migration 031 ou 032 reutilizada;
8. checkout produtivo desligado até conclusão da issue #95;
9. Delivery e Rider bloqueados até pagamento confirmado e reconciliado;
10. Vision inativo;
11. bloqueios externos nunca convertidos em sucesso forçado.

## Janela técnica de execução

O plano é dimensionado para uma jornada técnica de até 8 horas, com tolerância operacional de 4 horas para workflows, filas externas e testes de integração. Isso não autoriza espera passiva nem declaração antecipada de conclusão.

## Fase 1 — Correção de governança

### Ações

- criar política de escopo oficial;
- declarar Valley como produto interno do monorepo;
- bloquear fontes de repositório abandonadas;
- criar validador executável;
- criar testes pytest;
- atualizar `tarefas.md`;
- atualizar `docs/Pendências Do desenvolvedor.md`;
- gerar relatório e plano v5.0.

### Critérios de aceite

- política JSON válida;
- validador retorna código zero;
- testes de contrato aprovados;
- documentos não contêm marcadores obsoletos;
- nenhum arquivo funcional de produto alterado.

## Fase 2 — Reconciliação das issues

### Issue #51

Atualizar para registrar:

- Fase 0 concluída;
- governança de merge corrigida;
- Marketplace de descoberta integrado;
- Stock transacional integrado;
- checkout idempotente integrado;
- issue #95 como gate financeiro;
- Delivery e Rider ainda bloqueados;
- issue #107 como bloqueio externo de infraestrutura.

### Issue #55

Atualizar para registrar:

- branch inicial substituída;
- PR #57 como entrega integrada;
- estado real da vertical FastAPI;
- pendências de persistência, integrações e homologação.

### Demais issues

Manter abertas quando dependem de implementação ou evidência real. Não encerrar por mera existência de documentação.

## Fase 3 — Validação da branch

Executar no checkout reproduzível:

```bash
python3 scripts/validate_repository_scope.py
python3 -m pytest -q tests/test_repository_scope_policy.py
python3 -m json.tool config/autonomy/repository_scope_policy.json >/dev/null
python3 -m compileall -q scripts/validate_repository_scope.py tests/test_repository_scope_policy.py
git diff --check
git diff --stat origin/main...HEAD
```

Também executar os gates acionados pelo diff:

- Continuous Integration;
- Security;
- documentação e contratos;
- validação do repositório quando aplicável.

## Fase 4 — Pull Request

- abrir PR para `main`;
- manter head congelado durante validação;
- registrar arquivos alterados e riscos;
- confirmar ausência de segredos;
- conferir threads e reviews;
- integrar somente por Squash and Merge com `expected_head_sha`.

## Fase 5 — Auditoria local não destrutiva

No host WSL:

```bash
cd /home/eretazan/all-in-one

git status --short --branch
git status --porcelain=v2 --branch
git diff --stat
git diff --name-status
git diff --cached --stat
git diff --cached --name-status
git diff --cached --diff-filter=D --name-only
git diff --check
git diff --cached --check
git fetch --prune origin
git rev-list --left-right --count HEAD...origin/main
git log --oneline origin/main..HEAD
git log --oneline HEAD..origin/main
```

Se houver alterações:

```bash
timestamp="$(date +%Y%m%d-%H%M%S)"
git branch "backup/pre-audit-$timestamp" HEAD
git diff > "/tmp/all-in-one-worktree-$timestamp.patch"
git diff --cached > "/tmp/all-in-one-index-$timestamp.patch"
```

Classificar cada item como:

- staged válido;
- staged misturado;
- exclusão justificada;
- exclusão suspeita;
- alteração de outro agente;
- arquivo gerado;
- segredo potencial;
- commit local não publicado;
- mudança substituída pela `main`.

## Fase 6 — Próxima evolução funcional

Executar a issue #95 em branch nova baseada na `main` já corrigida.

### Ordem interna

1. contrato PSP;
2. interface de adaptador;
3. sandbox;
4. webhooks autenticados;
5. autorização/captura/cancelamento/estorno;
6. chargeback;
7. liquidação;
8. reconciliação;
9. observabilidade;
10. testes e rollback.

## Fase 7 — Bloqueios externos

### Issue #107

- habilitar faturamento legitimamente;
- confirmar IAM;
- repetir workflow;
- comprovar rollout;
- não alterar gate para mascarar falha.

### Issue #89

- obter fonte produtiva AppDeploy por canal autorizado;
- versionar ou documentar adaptador;
- diferenciar template e runtime;
- validar web, backend e Android.

### Issue #69

- versionar fonte funcional e gerador antes de iniciar persistência.

## Gestão das branches divergentes

Para cada uma das 28 branches:

1. comparar com `main`;
2. identificar commits exclusivos;
3. mapear arquivos já substituídos;
4. verificar migrations, lockfiles, segredos e branding;
5. criar tag de arquivo quando integralmente absorvida;
6. reconstruir código útil em branch nova;
7. nunca fazer merge direto de branch obsoleta.

## Evidências esperadas

- política e gate versionados;
- testes aprovados;
- issues reconciliadas;
- PR aberta;
- checks verdes no mesmo SHA;
- relatório de worktree local quando o host estiver acessível;
- issue #95 iniciada somente após integração desta governança.

## Resultado esperado

Uma `main` com documentação coerente, fonte de verdade única, regras automatizadas contra regressão e fila de evolução ordenada por risco real.
