# Tarefas da IA Desenvolvedora

**Versão:** 2.2  
**Data e hora:** 28/07/2026  
**Fuso horário:** `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `codex/marketplace-fase1-descoberta-2026-07-28`  
**Commit-base:** `396d2539480ece1757b29bcd8b4ed18f7e9091a5`  
**Commit de referência da atividade:** `909ce084c38aac80603c78482b873037fdebdcd8`  
**Issue de orquestração:** `#51`  
**Classificação:** `Pendências > Técnico > Equipe técnica`  
**Aplicação:** `modules/marketplace`

## 1. Regra mandatória de prioridade

Antes de qualquer evolução, verificar e tratar nesta ordem:

1. workflows falhos, cancelados ou bloqueados;
2. merges pendentes, parciais ou conflitantes;
3. pull requests abertas;
4. commits e branches ainda não integrados;
5. issues abertas com escopo executável;
6. somente depois, nova evolução de produto.

A fonte persistente desta regra é `config/autonomy/pending_work_priority_policy.json`, complementada pelo `AGENTS.md`.

## 2. Objetivo atual

Concluir e integrar a primeira vertical funcional do Marketplace, com descoberta pública e jornada autenticada de favoritos e carrinho, preservando a sequência da issue #51: Marketplace → Stock → Delivery.

## 3. Estado implementado

- catálogo público com busca textual;
- filtros por categoria, loja, preço, estoque e raio;
- cálculo de distância por latitude e longitude;
- ordenação por relevância, preço, distância e avaliação;
- exposição exclusiva de lojas aprovadas e produtos publicados;
- feed vertical contratual em formato 9:16;
- identificação explícita de conteúdo patrocinado;
- promoção do dia com elegibilidade, prioridade e fallback;
- favoritos isolados por All-in-One ID;
- carrinho isolado por usuário, com quantidade, disponibilidade e total em BRL;
- OpenAPI Marketplace `0.3.0`;
- testes dedicados em `tests/test_marketplace_discovery.py`;
- governança persistente de issues, PRs, commits, merges e workflows.

## 4. Fontes de verdade

1. `AGENTS.md`;
2. `config/autonomy/pending_work_priority_policy.json`;
3. este `tarefas.md`;
4. issue `#51`;
5. issue `#24`;
6. `modules/marketplace/main.py`;
7. `modules/marketplace/OPENAPI.yaml`;
8. `modules/marketplace/README.md`;
9. `modules/marketplace/STATUS.md`;
10. `tests/test_marketplace_discovery.py`;
11. `docs/relatorios/pendencias/RELATORIO_VARREDURA_STATUS_v3.4_2026-07-28.md`;
12. `docs/relatorios/pendencias/PLANO_ACAO_CODEX_v3.4_2026-07-28.md`;
13. pull request da branch desta atividade.

## 5. Pré-requisitos

- não versionar credenciais;
- não alterar diretamente a `main`;
- preservar mudanças de outros agentes;
- revisar merges e PRs antes de nova evolução;
- usar o mesmo SHA para testes, revisão e decisão de merge;
- manter auto-merge desabilitado;
- usar Squash and Merge.

## 6. Sequência imediata obrigatória

### P0 — fechar a rodada atual

1. abrir PR da branch para `main`;
2. verificar diff e mergeabilidade;
3. executar os workflows aplicáveis;
4. abrir logs de qualquer job falho;
5. corrigir falhas reproduzíveis na mesma branch;
6. repetir os gates no novo SHA;
7. verificar threads de revisão e alteração do head;
8. integrar por Squash and Merge;
9. atualizar a issue #51 com evidências;
10. revisar novamente PRs, merges, commits, workflows e issues antes da próxima tarefa.

### P1 — checkout Marketplace

1. integrar reserva transacional com Stock;
2. validar preço e disponibilidade no momento do checkout;
3. usar idempotência para impedir pedidos duplicados;
4. integrar Wallet e Orders;
5. publicar eventos de pedido e reserva;
6. tratar expiração, cancelamento e compensação.

### P1 — issue #24

1. conectar o frontend Valley Consumidor ao endpoint `/valley/promotions/today`;
2. exibir modal dispensável e acessível;
3. não bloquear a homepage em erro ou ausência de promoção;
4. registrar telemetria sem dados pessoais desnecessários;
5. testar offline, expiração e destino indisponível.

### P2 — Stock e Delivery

1. concluir fonte única de saldo e reservas;
2. implementar Delivery a partir de pedidos confirmados;
3. integrar Riders, Wallet e notificações;
4. retomar a homologação produtiva do Valley Rider.

## 7. Testes

```bash
python -m pytest -q tests/test_marketplace_discovery.py
python -m pytest -q tests/test_marketplace_support_metrics.py
python -m pytest -q tests/test_marketplace_commercial_metrics.py
python -m pytest -q --ignore=tests/e2e
python scripts/validate_repository.py
```

Gates remotos esperados:

- Continuous Integration;
- Security;
- Database;
- Docker Compose Health Gate;
- OpenAPI;
- demais gates acionados pelo diff.

## 8. Critérios de aceite

- testes reproduzíveis aprovados no SHA final;
- nenhuma loja não aprovada exposta;
- nenhum produto não publicado exposto;
- filtros e geolocalização validados;
- favoritos e carrinho isolados por usuário;
- conteúdo patrocinado identificado;
- promoção sem bloquear a homepage;
- auditoria e outbox preservados;
- nenhuma credencial no Git;
- PR revisada e mesclável;
- integração somente por Squash and Merge;
- issue #51 atualizada com commit final.

## 9. Riscos e bloqueios

- disponibilidade atual do carrinho ainda é contratual e não reserva Stock;
- a interface visual da promoção ainda depende do Valley Consumidor;
- a jornada de pagamento depende de Wallet e PSP homologado;
- testes remotos devem confirmar lint, segurança e regressão do repositório;
- nenhuma dessas limitações pode ser ocultada ou marcada como homologada.

## 10. Evidências esperadas

- SHA final da branch;
- número da PR;
- lista de arquivos alterados;
- resultados dos workflows no mesmo SHA;
- ausência de threads não resolvidas;
- resultado do Squash and Merge;
- commit final na `main`;
- comentário de encerramento da rodada na issue #51.

## 11. Procedimento de decisão autônoma

- decidir com base no diff, testes, contratos e riscos;
- corrigir automaticamente tudo que seja tecnicamente resolvível;
- não solicitar aprovação para decisões técnicas reversíveis e seguras;
- solicitar intervenção apenas diante de credencial ausente, exigência legal, decisão comercial irreversível, bloqueio externo ou indisponibilidade real de ferramenta;
- não iniciar nova evolução enquanto esta entrega tiver PR, merge ou gate pendente.

## 12. Histórico

| Versão | Data | Alteração |
|---|---|---|
| 1.8 | 28/07/2026 | Rodada 004 do APK Valley registrada. |
| 1.9 | 28/07/2026 | Auditoria do Valley Rider e plano de homologação. |
| 2.0 | 28/07/2026 | PR #62, QA Rider e testes Git determinísticos. |
| 2.1 | 28/07/2026 | Rodada 005 implementada com 24 contratos e feature flags. |
| 2.2 | 28/07/2026 | Marketplace Fase 1 e prioridade mandatória de issues, PRs, commits, merges e workflows. |
