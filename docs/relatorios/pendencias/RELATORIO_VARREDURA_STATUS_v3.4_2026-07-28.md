# Relatório de Varredura e Status

**Versão:** 3.4  
**Data e hora:** 28/07/2026 21:01:59  
**Fuso horário:** `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `docs/marketplace-fase-1-baseline-2026-07-28`  
**Commit-base:** `396d2539480ece1757b29bcd8b4ed18f7e9091a5`  
**Issues:** `#51` e `#66`  
**Classificação:** `Pendências > Técnico > Equipe técnica`  
**Públicos impactados:** Pessoa Física, Pessoa Jurídica, equipe técnica e gestão

## 1. Resumo executivo

A Fase 0 foi concluída. A ordem funcional oficial permanece Marketplace → Stock → Delivery.

A `main` avançou depois da regularização e recebeu diversas integrações paralelas. A issue #51 foi atualizada para refletir o estado atual e a issue #66 foi aberta para iniciar formalmente a Fase Marketplace.

O módulo Marketplace já apresenta evidências de fundação técnica:

- documentos `CONTRACT.md`, `OPENAPI.yaml`, `DATABASE.md`, `EVENTS.md`, `SECURITY.md` e `MONETIZATION.md`;
- entidades documentadas como `stores`, `products`, `carts` e `orders`;
- eventos como `marketplace.store.created`, `marketplace.product.created`, `marketplace.order.created` e `marketplace.order.paid`;
- testes de existência dos contratos;
- teste de autorização para criação;
- fluxo genérico de criação e aprovação.

Essas evidências não comprovam, por si só, a implementação completa de catálogo, busca, filtros, mídia, carrinho, favoritos, avaliações, promoções, geolocalização, feed vertical ou jornadas PF/PJ.

## 2. Estado de governança

- issue #49 encerrada;
- issue #51 atualizada para a sequência Marketplace → Stock → Delivery;
- issue #66 criada para o primeiro ciclo Marketplace;
- branch de mapeamento criada a partir da `main` atual;
- Vision permanece excluído;
- auto-merge permanece bloqueado;
- configuração administrativa ainda permite merge commit, rebase merge e squash merge simultaneamente.

## 3. Matriz inicial do Marketplace

| Componente | Documentado | Implementado | Testado | Homologado | Estado atual |
|---|---:|---:|---:|---:|---|
| Contrato do módulo | Sim | Parcial | Sim | Não | Fundação existente |
| OpenAPI | Sim | Parcial | Sim | Não | Exige inventário de rotas reais |
| Banco | Sim | Parcial | Parcial | Não | Entidades planejadas/documentadas |
| Eventos | Sim | Parcial | Parcial | Não | Outbox e consumidores precisam ser confirmados |
| Autorização | Sim | Parcial | Sim | Não | Teste de fronteira existente |
| Lojas | Sim | Indeterminado | Parcial | Não | Mapear CRUD e regras PF/PJ |
| Produtos | Sim | Indeterminado | Parcial | Não | Mapear leitura, mídia, preço e disponibilidade |
| Categorias | Indeterminado | Indeterminado | Não confirmado | Não | Lacuna do primeiro incremento |
| Busca e filtros | Indeterminado | Indeterminado | Não confirmado | Não | Lacuna |
| Geolocalização | Não confirmada | Não confirmada | Não confirmada | Não | Lacuna |
| Carrinho | Sim | Indeterminado | Não confirmado | Não | Não incluir no primeiro incremento |
| Pedidos | Sim | Parcial | Parcial | Não | Depende de Stock e Finance |
| Favoritos | Não confirmado | Não confirmado | Não confirmado | Não | Lacuna |
| Avaliações | Não confirmado | Não confirmado | Não confirmado | Não | Lacuna |
| Promoções | Não confirmado | Não confirmado | Não confirmado | Não | Lacuna |
| Feed vertical | Não confirmado | Não confirmado | Não confirmado | Não | Lacuna de produto |
| Jornada PF | Parcial | Indeterminado | Não confirmado | Não | Mapear |
| Jornada PJ | Parcial | Indeterminado | Não confirmado | Não | Mapear |

## 4. Primeiro incremento selecionado

**Catálogo somente leitura de categorias e produtos**, com:

- paginação;
- filtros básicos;
- ordenação segura;
- feature flag desligada por padrão;
- sem carrinho;
- sem pagamento;
- sem reserva de estoque;
- sem Delivery;
- sem escrita produtiva;
- contrato OpenAPI e testes de contrato.

A implementação só deve começar depois que o inventário confirmar os caminhos existentes e evitar duplicação de código.

## 5. Tabela obrigatória de acompanhamento

| Nome da atividade | Descrição | Passo sendo executado | Dificuldade [1 a 5] | % concluído | Tempo previsto | Etapas [Total] | Concluídas [X] | Pendentes [Y] |
|---|---|---|---:|---:|---|---:|---:|---:|
| Atualizar orquestração | Refletir estado atual na issue #51 | Concluído | 3 | 100% | concluído | 4 | 4 | 0 |
| Criar issue Marketplace | Abrir ciclo formal da Fase 1 | Concluído, issue #66 | 2 | 100% | concluído | 3 | 3 | 0 |
| Criar branch | Isolar mapeamento e documentação | Concluído | 2 | 100% | concluído | 2 | 2 | 0 |
| Mapear contratos | Inventariar documentos e testes existentes | Evidência inicial coletada | 4 | 45% | 1h30 | 8 | 3 | 5 |
| Mapear banco | Localizar migrations, tabelas, índices e stores | Pendente | 5 | 20% | 1h30 | 7 | 1 | 6 |
| Mapear APIs | Localizar rotas reais e OpenAPI | Pendente | 5 | 25% | 1h | 6 | 1 | 5 |
| Mapear produto | Catálogo, filtros, mídia e jornadas | Matriz inicial criada | 4 | 30% | 1h30 | 10 | 3 | 7 |
| Selecionar incremento | Definir escopo pequeno e reversível | Catálogo somente leitura selecionado | 4 | 80% | 30min | 5 | 4 | 1 |
| Implementar incremento | Criar flag, contrato, código e testes | Não iniciado | 5 | 0% | ciclo posterior | 8 | 0 | 8 |
| Stock | Segunda fase | Bloqueado pelo Marketplace | 5 | 0% | posterior | 9 | 0 | 9 |
| Delivery | Terceira fase | Bloqueado por Marketplace e Stock | 5 | 0% | posterior | 9 | 0 | 9 |

## 6. Riscos

1. Duplicar endpoints ou stores existentes por inventário incompleto.
2. Misturar catálogo com carrinho, pagamento ou reserva de estoque no primeiro incremento.
3. Usar disponibilidade simulada como saldo real de Stock.
4. Expor produtos de empresas sem isolamento por entidade.
5. Permitir ordenação ou filtros não parametrizados.
6. Integrar sem feature flag e rollback.
7. Tratar contrato documentado como homologação produtiva.
8. Continuar integrando frentes paralelas e perder novamente a prioridade do Marketplace.

## 7. Decisão

O ciclo Marketplace está iniciado, mas a implementação de código permanece bloqueada até a conclusão do inventário técnico. O primeiro incremento aprovado para detalhamento é catálogo somente leitura, pequeno e reversível, com feature flag desligada.
