# Mapa de Domínios: All-in-One + Valley

Este documento realiza a correspondência entre os módulos oficiais do projeto (identificados nas pastas `modules/` e `contracts/`) e a lista de domínios conceituais descrita na seção 6.2 do "MEMORANDO MESTRE DE VARREDURA".

## Módulos Oficiais (25)

A análise da estrutura de diretórios revelou 25 domínios de negócio principais, cada um com seu próprio módulo e contrato de API. O módulo `shared` foi excluído desta lista por ser uma biblioteca transversal, não um domínio de negócio.

Os módulos oficiais são:

1.  `ai_core`
2.  `api_hub`
3.  `bi`
4.  `bpm`
5.  `business`
6.  `crm`
7.  `delivery`
8.  `document`
9.  `erp`
10. `finance`
11. `health`
12. `hr`
13. `identity`
14. `jobs`
15. `legal`
16. `marketplace`
17. `mobility`
18. `permissions`
19. `property`
20. `riders`
21. `services`
22. `stock`
23. `tms`
24. `vision`
25. `wms`

## Mapeamento de Domínios Conceituais para Módulos Oficiais

A seguir, a lista de domínios conceituais do memorando é agrupada sob os módulos oficiais correspondentes.

### 1. `identity`

- Identidade
- Usuários
- Perfis
- Autenticação
- Consentimentos (parcial)
- Privacidade (parcial)

### 2. `permissions`

- Autorização
- RBAC (Role-Based Access Control)
- ABAC (Attribute-Based Access Control)
- Segurança (parcial)
- Administração interna (parcial)

### 3. `business`

- Empresas
- Configurações (parcial, específico da empresa)

### 4. `marketplace`

- Marketplace
- Catálogo
- Produtos
- Compras
- Vendas
- Pedidos

### 5. `stock`

- Estoque

### 6. `services`

- Serviços

### 7. `delivery`

- Delivery

### 8. `riders`

- Riders

### 9. `mobility`

- Mobility

### 10. `jobs`

- Jobs
- Currículos
- CTPS (Carteira de Trabalho e Previdência Social)

### 11. `finance`

- Pagamentos
- Wallet (Carteira)
- Escrow
- Faturamento
- Fiscal
- Financeiro
- Contabilidade
- Cobrança

### 12. `document`

- Documentos
- Mídia

### 13. `health`

- Health
- Agenda (parcial, específico de saúde)

### 14. `hr` (Recursos Humanos)

- RH

### 15. `crm` (Customer Relationship Management)

- CRM
- Atendimento
- Suporte

### 16. `erp` (Enterprise Resource Planning)

- ERP

### 17. `wms` (Warehouse Management System)

- WMS (relacionado a `stock`)

### 18. `tms` (Transportation Management System)

- TMS (relacionado a `delivery` e `mobility`)

### 19. `bpm` (Business Process Management)

- BPM
- Orquestração Helena (provável)
- Homologação (parcial)

### 20. `ai_core`

- Inteligência artificial
- Analytics (parcial)

### 21. `api_hub`

- API Hub (Gateway de API)

### 22. `bi` (Business Intelligence)

- Relatórios
- Analytics (parcial)

### 23. `legal`

- Legal
- Compliance (parcial)

### 24. `property`

- Property (Imóveis)

### 25. `vision`

- Vision (Processamento de Imagem/Visão Computacional)

## Domínios Transversais e Não Mapeados Diretamente

Os seguintes conceitos do memorando são considerados preocupações transversais (cross-cutting concerns) ou não têm um mapeamento claro para um único módulo de negócio existente.

- **Eventos:** Mecanismo de integração transversal, provavelmente gerenciado por uma biblioteca `shared` e infraestrutura (ex: RabbitMQ), com o `api_hub` talvez atuando como gateway ou orquestrador.
- **Observabilidade:** Transversal. Coleta de logs, métricas e traces de todos os módulos.
- **Auditoria:** Transversal. Todos os módulos devem produzir logs de auditoria, possivelmente consumidos por um serviço central (`bi` ou `legal`/`compliance`).
- **Segurança:** Transversal. Implementado em múltiplos níveis (`identity`, `permissions`, `api_hub`, e em cada módulo individualmente).
- **Privacidade:** Transversal. Relacionado a `identity`, `legal`, e como cada módulo lida com dados de usuário.
- **Notificações:** Transversal. Um serviço central que envia emails, push notifications, etc., para eventos gerados por outros módulos.
- **Configurações:** Transversal. Cada módulo pode ter sua própria configuração, além de configurações globais/de tenant.
- **Assinaturas / Planos:** Poderia ser um módulo próprio (`billing`? `subscriptions`?) ou parte do `finance` ou `business`.
- **Administração interna:** Transversal, relacionado a `permissions` e ferramentas de back-office.
- **Homologação:** Processo transversal, pode ser parte do `bpm` ou uma política de deploy.
- **Compliance:** Transversal, responsabilidade compartilhada entre `legal` e todos os outros módulos.

Este mapeamento inicial servirá como base para a Fase 2 (Planejar) da varredura de dados.
