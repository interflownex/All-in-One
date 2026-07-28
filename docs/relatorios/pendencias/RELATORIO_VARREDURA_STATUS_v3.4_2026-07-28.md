# Relatório de Varredura e Status

**Versão:** 3.4  
**Data:** 28/07/2026  
**Fuso:** `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `codex/marketplace-fase1-descoberta-2026-07-28`  
**Commit-base:** `396d2539480ece1757b29bcd8b4ed18f7e9091a5`  
**Issue de orquestração:** `#51`  
**Classificação:** `Pendências > Técnico > Equipe técnica`

## Resumo executivo

A linha de regularização de PRs foi concluída e a execução funcional avançou para a Fase 1 da issue #51. O Marketplace já possuía runtime genérico para lojas, produtos, carrinhos, pedidos, avaliações e disputas, mas não oferecia uma jornada pública completa de descoberta e compra.

Esta rodada implementa a primeira vertical de consumo do Marketplace: catálogo pesquisável, geolocalização, feed vertical, promoção do dia, favoritos e carrinho. Também registra a política persistente que prioriza workflows, merges, PRs, commits e issues antes de novas evoluções.

| Nome da atividade | Descrição | Passo sendo executado | Dificuldade [1 a 5] | % concluído | Tempo previsto | Etapas [Total] | Concluídas [X] | Pendentes [Y] |
|---|---|---|---:|---:|---|---:|---:|---:|
| Auditoria Git | Verificar PRs, commits, merges, workflows e issues | concluída para esta rodada | 4 | 100% | concluído | 6 | 6 | 0 |
| Governança persistente | Priorizar issues, PRs, commits, merges e workflows | implementada | 3 | 100% | concluído | 4 | 4 | 0 |
| Catálogo público | Busca, categoria, preços, estoque, raio e ordenação | implementado | 4 | 90% | gates pendentes | 10 | 9 | 1 |
| Feed vertical | Cards 9:16 e identificação de patrocinado | implementado | 3 | 90% | gates pendentes | 6 | 5 | 1 |
| Promoção do dia | Elegibilidade, prioridade, fallback e fechamento | backend implementado | 4 | 70% | frontend pendente | 10 | 7 | 3 |
| Favoritos | Isolamento por All-in-One ID e auditoria | implementado | 3 | 90% | gates pendentes | 6 | 5 | 1 |
| Carrinho | Quantidade, disponibilidade e total em BRL | implementado | 4 | 85% | Stock pendente | 8 | 7 | 1 |
| Testes | Catálogo, feed, promoção, favoritos, carrinho e validações | adicionados | 4 | 75% | CI remoto pendente | 8 | 6 | 2 |
| Integração | PR, revisão, gates e Squash and Merge | aguardando PR | 3 | 40% | nesta rodada | 5 | 2 | 3 |

## Pendências identificadas

### P0 — antes da integração

1. abrir PR para `main`;
2. executar todos os workflows aplicáveis no mesmo SHA;
3. corrigir qualquer falha reproduzível;
4. revisar diff, threads e segredos;
5. integrar somente por Squash and Merge.

### P1 — continuação da Fase 1 Marketplace

1. checkout com reserva real no Stock;
2. integração com Wallet e Orders;
3. estoque concorrente e idempotente;
4. interface do modal da issue #24 no Valley Consumidor;
5. telemetria de visualização, fechamento e conversão da promoção;
6. testes ponta a ponta com frontend.

### P2 — fases seguintes

1. Stock como fonte única de saldo e reservas;
2. Delivery integrado a pedidos, Stock, Wallet e Riders;
3. retomada da homologação produtiva do Valley Rider.

## Evidências desta rodada

- branch criada a partir da `main` consolidada;
- código do Marketplace atualizado sem alteração direta na `main`;
- contrato OpenAPI elevado para versão `0.3.0`;
- testes dedicados adicionados em `tests/test_marketplace_discovery.py`;
- política criada em `config/autonomy/pending_work_priority_policy.json`;
- `AGENTS.md` atualizado com prioridade obrigatória de merges e demais pendências;
- nenhum segredo ou credencial adicionado.

## Riscos residuais

- o carrinho ainda usa disponibilidade contratual do produto, não reserva transacional no Stock;
- a promoção do dia possui contrato backend, mas a interface visual da issue #24 ainda deve ser integrada ao APK;
- o feed ainda depende do frontend para renderização 9:16 e telemetria completa;
- a homologação depende dos gates remotos no SHA final.
