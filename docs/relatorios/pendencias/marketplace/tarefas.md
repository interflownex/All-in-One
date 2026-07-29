# Tarefas da IA Desenvolvedora — Marketplace

**Versão:** 1.0  
**Data e hora:** 28/07/2026 21:01:59  
**Fuso horário:** `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `docs/marketplace-fase-1-baseline-2026-07-28`  
**Commit-base:** `396d2539480ece1757b29bcd8b4ed18f7e9091a5`  
**Issues:** `#51` e `#66`  
**Classificação:** `Pendências > Técnico > Equipe técnica`

## 1. Objetivo imediato

Concluir o inventário do Marketplace e confirmar se o primeiro incremento de catálogo somente leitura já existe total ou parcialmente.

## 2. Fontes de verdade

1. `AGENTS.md`;
2. `tarefas.md` da raiz;
3. issue `#51`;
4. issue `#66`;
5. `modules/marketplace/CONTRACT.md`;
6. `modules/marketplace/OPENAPI.yaml`;
7. `modules/marketplace/DATABASE.md`;
8. `modules/marketplace/EVENTS.md`;
9. `modules/marketplace/SECURITY.md`;
10. `modules/marketplace/MONETIZATION.md`;
11. migrations do schema Marketplace;
12. testes do módulo Marketplace;
13. contratos do API Hub.

## 3. Estado já confirmado

- a Fase 0 foi concluída;
- a issue #49 está encerrada;
- a issue #51 foi atualizada;
- a issue #66 foi criada;
- a ordem oficial é Marketplace → Stock → Delivery;
- o módulo possui documentação de contrato, banco, eventos, segurança e monetização;
- há testes de contrato, autorização e fluxo genérico de criação/aprovação;
- entidades documentadas incluem lojas, produtos, carrinhos e pedidos;
- a implementação funcional completa do catálogo ainda não foi comprovada;
- Vision permanece excluído;
- métodos de merge proibidos continuam habilitados administrativamente.

## 4. Primeira ação obrigatória

1. Confirmar o head atual da `main`.
2. Confirmar que a branch está baseada nesse head.
3. Executar inventário por caminho de arquivo.
4. Comparar OpenAPI documentado com rotas registradas.
5. Comparar banco documentado com migrations e stores.
6. Não alterar código até concluir a comparação.

## 5. Primeiro incremento candidato

**Catálogo somente leitura de categorias e produtos.**

### Requisitos

- feature flag desligada;
- paginação;
- filtros básicos;
- ordenação por allowlist;
- consultas parametrizadas;
- isolamento por empresa e visibilidade;
- nenhuma escrita produtiva;
- nenhum carrinho;
- nenhum pagamento;
- nenhuma reserva de Stock;
- nenhum Delivery.

## 6. Testes mínimos

- contrato dos documentos obrigatórios;
- autorização de leitura;
- isolamento entre empresas;
- paginação;
- filtros;
- ordenação permitida e rejeição de valores inválidos;
- produto inativo ou privado não exposto;
- OpenAPI consistente;
- validação do repositório.

## 7. Condições de parada

Parar e registrar bloqueio quando houver:

- implementação equivalente já existente;
- conflito com trabalho paralelo;
- necessidade de migration sem rollback;
- dependência obrigatória de Stock ainda não definida;
- credencial externa ausente;
- risco de exposição de dados empresariais;
- tentativa de iniciar Delivery;
- configuração de merge incompatível com a política.

## 8. Entrega obrigatória da próxima IA

1. matriz completa de arquivos e responsabilidades;
2. rotas reais do Marketplace;
3. tabelas, índices e stores reais;
4. testes existentes e lacunas;
5. decisão sobre o primeiro incremento;
6. código e testes, somente quando não houver duplicação;
7. evidências dos gates;
8. atualização da issue #66;
9. atualização deste arquivo;
10. Pull Request em rascunho, sem auto-merge.

## 9. Proibições

- push direto na `main`;
- reativação do Vision;
- versionamento de secrets;
- uso de saldo simulado como Stock oficial;
- inclusão de checkout no primeiro incremento;
- início da Fase Delivery;
- integração sem gates verdes;
- merge diferente de Squash and Merge.
