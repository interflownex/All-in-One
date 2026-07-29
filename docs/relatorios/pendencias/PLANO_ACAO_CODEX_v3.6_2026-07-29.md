# Plano de Ação Codex

**Versão:** 3.6  
**Data e hora:** 29/07/2026 04:11, `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `fix/android-validator-productiondebug-2026-07-29`  
**Issue de orquestração:** `#51`  
**Ciclo principal:** 8 horas  
**Tolerância:** até 4 horas

## 1. Objetivo

Concluir a correção mínima do contrato Android e liberar a retomada segura da Fase Marketplace, sem incorporar o escopo divergente da PR #75.

## 2. Bloco 1 — correção Android

1. Confirmar o head da branch.
2. Confirmar que o diff contém apenas arquivos autorizados.
3. Executar `validate_valley_android_release_v29.py`.
4. Executar o novo teste de regressão.
5. Executar os testes de contrato Android existentes.
6. Validar sintaxe do workflow.
7. Abrir PR em rascunho.
8. Considerar válidos somente os workflows do head atual.

## 3. Bloco 2 — revisão de segurança

Confirmar:

- nenhuma credencial no diff;
- `${{ runner.temp }}` preservado;
- nenhuma chave de assinatura materializada no workspace;
- tarefas `ProductionDebug` obrigatórias;
- tarefas genéricas rejeitadas;
- CodeQL, SBOM, atestação e assinatura não enfraquecidos;
- nenhuma alteração em branding, interfaces ou skills.

## 4. Bloco 3 — integração

Somente com gates verdes:

1. verificar mergeabilidade;
2. verificar reviews e threads;
3. confirmar o head novamente;
4. marcar a PR como pronta;
5. integrar por Squash and Merge com `expected_head_sha`;
6. registrar o commit final na issue #51;
7. revisar novamente PRs e workflows abertos.

## 5. Bloco 4 — retomada do Marketplace

Após a correção Android:

1. confirmar o estado integrado pelo PR #65;
2. mapear contratos de Stock, Wallet e Orders;
3. definir checkout idempotente;
4. validar preço e disponibilidade no momento da confirmação;
5. criar reserva de estoque com expiração;
6. impedir estoque negativo e dupla cobrança;
7. publicar eventos de reserva, pedido, pagamento e liberação;
8. manter feature flag desligada até homologação.

## 6. Escopo proibido no próximo incremento

- iniciar Delivery;
- criar saldo paralelo fora do Stock;
- lançar valores fora do ledger;
- simular pagamento como liquidado;
- ativar produção sem credenciais e homologação;
- misturar novas interfaces ou branding ao checkout.

## 7. Testes obrigatórios

```bash
python scripts/validate_valley_android_release_v29.py
python -m pytest -q tests/test_valley_android_release_adapter.py
python -m pytest -q tests/test_valley_android_workflow_contract.py
python scripts/validate_repository.py
```

No checkout futuro:

- idempotência;
- concorrência;
- preço divergente;
- item indisponível;
- reserva expirada;
- rollback de pagamento;
- isolamento PF/PJ e por empresa;
- eventos e auditoria;
- testes de contrato e integração.

## 8. Critérios de aceite

- PR Android com diff mínimo;
- gates verdes no mesmo SHA;
- nenhuma thread pendente;
- Squash and Merge;
- issue #51 atualizada;
- Marketplace retomado somente depois do fechamento;
- Stock permanece segunda fase;
- Delivery permanece terceira fase;
- Vision permanece excluído.

## 9. Regra de parada

Após 12 horas, não iniciar nova frente. Registrar estado, evidências, bloqueios e a primeira tarefa do próximo ciclo.
