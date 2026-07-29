# Plano de Ação Estruturado para a IA Desenvolvedora

**Versão:** 3.4  
**Data e hora:** 28/07/2026 21:01:59  
**Fuso horário:** `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `docs/marketplace-fase-1-baseline-2026-07-28`  
**Commit-base:** `396d2539480ece1757b29bcd8b4ed18f7e9091a5`  
**Issues:** `#51` e `#66`  
**Ciclo principal:** 8 horas  
**Tolerância operacional:** até 4 horas  
**Limite de coleta:** 12 horas

## 1. Missão

Concluir o inventário técnico do Marketplace e preparar o primeiro incremento seguro: catálogo somente leitura de categorias e produtos, sem iniciar Stock ou Delivery.

## 2. Regras mandatórias

1. Não executar push direto na `main`.
2. Não iniciar Stock.
3. Não iniciar Delivery.
4. Não reativar Vision.
5. Não versionar credenciais ou segredos.
6. Não duplicar contratos, rotas, migrations ou stores existentes.
7. Não usar disponibilidade simulada como saldo oficial de Stock.
8. Não incluir carrinho, pagamento ou reserva de estoque no primeiro incremento.
9. Toda feature flag começa desligada.
10. Integração somente por Squash and Merge.
11. Auto-merge permanece bloqueado enquanto merge commit e rebase merge estiverem habilitados.

## 3. Bloco 1 — 0h a 1h30: inventário do código

Localizar e registrar:

- entrypoint do módulo Marketplace;
- routers e dependências;
- serviços e stores;
- modelos e schemas;
- rotas de criação, leitura, aprovação e listagem;
- tratamento de paginação e filtros;
- arquivos de teste;
- dependências compartilhadas.

Entrega: tabela com caminho, responsabilidade, estado e risco.

## 4. Bloco 2 — 1h30 a 3h: inventário de contratos e banco

### Contratos

- revisar `CONTRACT.md`;
- revisar `OPENAPI.yaml`;
- revisar `EVENTS.md`;
- revisar `SECURITY.md`;
- revisar `MONETIZATION.md`;
- comparar contrato documentado com rotas reais.

### Banco

- localizar migrations do schema `marketplace`;
- confirmar tabelas `stores`, `products`, `carts` e `orders`;
- localizar categorias e mídia, se existirem;
- localizar índices de busca, tenant e status;
- verificar soft delete e auditoria;
- verificar idempotência e outbox;
- verificar isolamento PF/PJ e por empresa.

Entrega: matriz `documentado | implementado | testado | homologado | bloqueado`.

## 5. Bloco 3 — 3h a 4h: inventário das integrações

Confirmar contratos reais com:

- Identity;
- Business;
- Finance / Wallet;
- Orders;
- Stock;
- Notifications;
- Audit;
- API Hub.

Delivery deve aparecer somente como dependência futura. Nenhuma implementação da Fase 3 será aberta.

## 6. Bloco 4 — 4h a 5h: desenho do primeiro incremento

### Escopo permitido

- listagem de categorias;
- listagem de produtos;
- paginação por cursor ou página, conforme padrão existente;
- filtros básicos e parametrizados;
- ordenação por allowlist;
- somente leitura;
- feature flag desligada;
- resposta sem informações sensíveis da empresa;
- isolamento por visibilidade e entidade.

### Escopo proibido

- carrinho;
- checkout;
- pagamento;
- reserva de estoque;
- baixa de estoque;
- entrega;
- cálculo de frete;
- ativação produtiva da flag.

## 7. Bloco 5 — 5h a 7h: implementação condicional

Executar somente se o inventário provar que não existe incremento equivalente.

1. Criar ou reutilizar feature flag.
2. Atualizar contrato OpenAPI.
3. Criar schemas de leitura.
4. Criar consultas parametrizadas.
5. Implementar paginação e filtros.
6. Aplicar autorização e isolamento.
7. Criar testes unitários e de contrato.
8. Criar telemetria mínima.
9. Definir rollback.

Se já existir implementação equivalente, não duplicar. Corrigir lacunas e testes.

## 8. Bloco 6 — 7h a 8h: validação e passagem

Executar:

- testes específicos do Marketplace;
- validação OpenAPI;
- validação do repositório;
- Security quando houver mudança Python;
- Database quando houver migration ou store;
- CI completo no SHA do Pull Request.

Atualizar:

- issue #66;
- issue #51;
- relatório v3.4;
- este plano;
- arquivo `tarefas.md` do ciclo.

## 9. Tolerância de até 4 horas

Usar apenas para:

1. concluir inventário iniciado;
2. corrigir testes do incremento;
3. estabilizar OpenAPI;
4. corrigir autorização, paginação ou filtros;
5. concluir documentação e evidências.

Não ampliar o escopo durante a tolerância.

## 10. Critérios de aceite

- inventário completo e citável;
- ausência de duplicação;
- feature flag desligada;
- leitura somente;
- autorização e isolamento definidos;
- filtros parametrizados;
- ordenação por allowlist;
- paginação testada;
- OpenAPI atualizado;
- testes reproduzíveis;
- rollback documentado;
- gates verdes no mesmo SHA;
- revisão concluída;
- Squash and Merge.

## 11. Regra após 12 horas

Não iniciar nova atividade. Registrar:

- concluído;
- parcial;
- falhou;
- causa;
- ação executada;
- evidência;
- bloqueio externo;
- primeira tarefa do próximo ciclo.
