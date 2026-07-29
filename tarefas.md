# Tarefas da IA Desenvolvedora

**Versão:** 2.4  
**Data e hora:** 29/07/2026 04:11, `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `fix/android-validator-productiondebug-2026-07-29`  
**Commit-base:** `f1681dd2cbff145a661254cb1ce49f059121d7f2`  
**Issue de orquestração:** `#51`  
**Classificação:** `Pendências > Técnico > Equipe Técnica`

## 1. Regra mandatória de prioridade

Antes de qualquer nova evolução, tratar nesta ordem:

1. workflows falhos ou bloqueados;
2. merges pendentes ou conflitantes;
3. pull requests abertas;
4. commits e branches não integrados;
5. issues executáveis;
6. somente depois, nova evolução autorizada.

A política autoritativa permanece em `config/autonomy/pending_work_priority_policy.json` e `AGENTS.md`.

## 2. Estado confirmado neste ciclo

- PR #74 validada e integrada por Squash and Merge;
- commit de integração da PR #74: `f1681dd2cbff145a661254cb1ce49f059121d7f2`;
- PR #75 encerrada sem merge por conter 304 arquivos e 32.228 exclusões fora do escopo declarado;
- o ajuste legítimo da PR #75 foi isolado em branch limpa;
- o workflow permanente de Security já usa `testProductionDebugUnitTest`, `lintProductionDebug` e `assembleProductionDebug`;
- o adaptador `scripts/validate_valley_android_release_v29.py` preserva as verificações legadas e valida as tarefas explícitas;
- o workflow de release passou a chamar o adaptador v2.9;
- foi criado teste de regressão para impedir retorno ao contrato Android genérico;
- Vision permanece excluído;
- nenhuma credencial ou segredo foi versionado.

## 3. Objetivo imediato

Concluir a correção mínima do gate Android sem incorporar alterações alheias:

1. validar o adaptador v2.9;
2. validar o workflow de release;
3. executar testes de regressão;
4. executar CI, Security e Docker Compose no mesmo head;
5. revisar diff, threads, segredos e mergeabilidade;
6. integrar exclusivamente por Squash and Merge.

## 4. Arquivos autorizados neste incremento

- `.github/workflows/valley-android-release.yml`;
- `tests/test_valley_android_release_adapter.py`;
- `tarefas.md`;
- relatório e plano versionados deste ciclo.

Qualquer arquivo adicional exige justificativa técnica explícita e nova revisão de escopo.

## 5. Testes obrigatórios

```bash
python scripts/validate_valley_android_release_v29.py
python -m pytest -q tests/test_valley_android_release_adapter.py
python -m pytest -q tests/test_valley_android_workflow_contract.py
python scripts/validate_repository.py
```

Gates remotos obrigatórios no mesmo SHA:

- Continuous Integration;
- Security;
- Docker Compose Health Gate;
- demais workflows acionados pelo diff.

## 6. Critérios de aceite

- workflow de release chama `validate_valley_android_release_v29.py`;
- contrato legado continua sendo executado por meio do adaptador;
- tarefas Android genéricas são rejeitadas;
- tarefas `ProductionDebug` são obrigatórias;
- `${{ runner.temp }}` permanece utilizado para arquivos efêmeros de assinatura;
- nenhuma alteração de interface, branding, skills ou produto entra no diff;
- nenhum segredo é versionado;
- gates verdes no mesmo head;
- ausência de threads não resolvidas;
- integração por Squash and Merge com `expected_head_sha`.

## 7. Próxima sequência funcional após o fechamento

### Marketplace

O PR #65 já integrou:

- catálogo público;
- busca, filtros e paginação;
- geolocalização e ordenação por distância;
- feed vertical;
- promoção do dia;
- favoritos;
- carrinho isolado por usuário.

Próximo incremento permitido:

1. mapear contrato de reserva no Stock;
2. desenhar checkout idempotente;
3. validar preço e disponibilidade no momento do checkout;
4. integrar Wallet e Orders sem lançar valores fora do ledger;
5. publicar eventos de reserva, pedido e pagamento;
6. manter feature flag desligada até homologação;
7. não iniciar Delivery antes da conclusão formal de Marketplace e Stock.

### Stock

Permanece como segunda fase e deve fornecer:

- fonte única de saldo;
- reservas com expiração;
- concorrência segura;
- idempotência;
- auditoria;
- prevenção de estoque negativo.

### Delivery

Permanece como terceira fase. O Valley Rider já integrado não equivale à homologação completa do Delivery.

## 8. Proibições

- não executar push direto na `main`;
- não integrar PR com escopo divergente;
- não usar resultados de head anterior;
- não ativar auto-merge enquanto outros métodos de merge estiverem habilitados;
- não versionar segredos;
- não reativar Vision;
- não iniciar Delivery;
- não declarar checkout concluído sem reserva transacional e ledger.

## 9. Histórico

| Versão | Data | Alteração |
|---|---|---|
| 2.0 | 28/07/2026 | PR #62, QA Rider e testes Git determinísticos. |
| 2.1 | 28/07/2026 | Rodada 005 com contratos e feature flags. |
| 2.2 | 28/07/2026 | Marketplace Fase 1 e governança de pendências. |
| 2.3 | 28/07/2026 | A1 Admin Web + Mobile, Android seguro e pacote Figma. |
| 2.4 | 29/07/2026 | PR #74 integrada, PR #75 rejeitada por escopo divergente e correção Android v2.9 isolada. |
