# Arquitetura

## Principios

1. O All-in-One ID nasce em `identity.users` e acompanha toda operacao.
2. Dinheiro, identidade, contratos e auditoria permanecem no PostgreSQL.
3. Memoria IA consentida, feed e telemetria volumosa permanecem no MongoDB.
4. Cada modulo publica contrato HTTP e eventos; nenhum acesso cruza bancos sem
   API ou evento versionado.
5. Empresas e riders nao ficam publicos antes de aprovacao manual.
6. Curriculos sao privados por padrao; leitura por recrutador exige Business
   ativa, escopo Jobs e evento de acesso auditavel.

## Visao de componentes

```mermaid
flowchart LR
  U["Apps: User, Business, Riders, Services, Health, Mobility"] --> G["API Hub / OAuth2 / Rate Limit"]
  G --> I["Identity + Permissions"]
  G --> D["Dominio: Marketplace, Delivery, Services, Mobility, Jobs"]
  G --> E["Enterprise: ERP, WMS, TMS, CRM, BPM"]
  G --> V["Verticals: Health, Vision, Legal, Property"]
  D --> F["Finance / Escrow / Billing"]
  D --> J["Jobs: Curriculo, CTPS PDF, Vagas"]
  J --> P
  J --> Q
  E --> F
  V --> F
  I --> P[("PostgreSQL")]
  F --> P
  D --> P
  E --> P
  V --> P
  D --> Q["RabbitMQ Domain Events"]
  Q --> A["Audit + Compliance + BI + AI Core"]
  A --> P
  A --> M[("MongoDB")]
```

## Request e auditoria

```mermaid
sequenceDiagram
  participant App
  participant Hub as API Hub
  participant Mod as Microservico
  participant DB as PostgreSQL
  participant Bus as RabbitMQ
  App->>Hub: JWT/MFA + request
  Hub->>Hub: scope, ABAC, rate limit
  Hub->>Mod: X-Actor-User-Id + correlation
  Mod->>DB: transacao com user_id
  Mod->>DB: audit.logs append-only
  Mod->>Bus: evento versionado
  Mod-->>App: resposta
```
