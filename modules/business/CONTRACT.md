        # Contrato: Business

        ## Descricao

        Matriz, filiais, documentos empresariais, aprovacao manual, memberships e ofertas comerciais publicaveis no catalogo Valley.

        ## Entidades

        - `companies`

- `branches`
- `company_documents`
- `user_company_memberships`
- `catalog_offers`

        ## APIs

        - `GET /health`

- `GET /version`
- `GET /status`
- `GET /metrics`
- `GET /catalog`
- `POST /resources/{resource_type}`
- `GET /resources/{resource_type}`
- `GET /resources/{resource_type}/{resource_id}`
- `PATCH /resources/{resource_type}/{resource_id}`
- `DELETE /resources/{resource_type}/{resource_id}`
- `POST /resources/{resource_type}/{resource_id}/actions/{action}`
- `GET /audit/events`
- `GET /events/outbox`
- `POST /create`
- `GET /{id}`
- `PATCH /{id}`
- `DELETE /{id}`
- `GET /list`
- `POST /approve`
- `POST /reject`
- `POST /audit`

## Publicacao Marketplace e Valley

- `catalog_offers` exige `offer_type`, `consumer_category`, `company_type`, `company_category`, `business_activity_id`, `source_module` e `source_resource_type`.
- O Valley so exibe ofertas com `publish_to_valley=true`, publicacao aprovada ou publicada e `visible_to_consumer` ativo.
- Ofertas locais exigem regiao, coordenadas publicas de base e `service_radius_km`; enderecos sensiveis nunca entram no payload publico.
- A transicao de publicacao emite `valley.catalog.offer.synced` com allowlist publica.

## Convites e memberships

- `user_company_memberships` exige `company_id` e `role`.
- A criacao representa convite operacional com status inicial `invited` e emite `business.user.invited`.
- A acao `activate` exige papel aprovador, MFA e emite `business.role.assigned`.
- A acao `revoke` exige papel aprovador, MFA e emite `business.user.revoked`.

        ## Eventos

        - `business.company.created`

- `business.company.submitted`
- `business.company.approved`
- `business.company.rejected`
- `business.branche.created`
- `business.branche.submitted`
- `business.branche.cancelled`
- `business.branche.completed`
- `business.company_document.created`
- `business.company_document.submitted`
- `business.company_document.cancelled`
- `business.company_document.completed`
- `business.user.invited`
- `business.role.assigned`
- `business.user.revoked`
- `business.catalog_offer.created`
- `business.catalog_offer.submitted`
- `business.catalog_offer.cancelled`
- `business.catalog_offer.completed`
- `valley.catalog.offer.synced`
- `business.catalog_offer.paused`

        ## Regras

        - `user_id` e obrigatorio em todo recurso operacional e referencia `identity.users`.
        - Exclusao e logica; registros financeiros, de aprovacao e auditoria nao sao apagados.
        - Aprovacao e rejeicao exigem ator autenticado, justificativa e log imutavel.
        - A empresa ou profissional deve estar aprovado antes de uma operacao publica.

        ## Seguranca e permissoes

        Mutacoes dependem de OAuth2/JWT ou API key no gateway e do escopo do
        modulo. O runtime inicial representa o ator por `X-Actor-User-Id` e
        registra auditoria; o gateway deve validar a credencial antes do repasse.

        ## Monetizacao

        Planos SaaS por empresa, usuario, modulo, API e SLA.

        ## Integracoes e erros

        Eventos sao entregues pelo barramento RabbitMQ. Respostas esperadas:
        `401` ator ausente, `404` recurso inexistente e `422` regra de validacao
        ou politica anti-burla violada.

        ## Auditoria

        `POST /audit` e todas as mutacoes geram evento destinado a `audit.logs`,
        que e append-only no PostgreSQL.
