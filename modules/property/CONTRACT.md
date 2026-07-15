        # Contrato: Property

        ## Descricao

        Imoveis, unidades, locacoes, condominio, manutencao e votacao.

        ## Entidades

        - `properties`
- `units`
- `leases`
- `assemblies`
- `maintenance_orders`

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


## Locacao e manutencao

- `leases` exige `property_id`, `tenant_user_id`, `starts_at` e `rent_amount_brl`, iniciando em `draft` e emitindo `property.lease.created`.
- A acao `activate` move locacoes para `active`, exige papel aprovador, MFA e emite `property.lease.activated`.
- A acao `terminate` encerra locacoes ativas com papel aprovador, MFA e emite `property.lease.terminated`.
- `maintenance_orders` exige `property_id`, `issue_type` e `requested_at`, iniciando em `requested` e emitindo `property.maintenance.requested`.
- A acao `schedule` agenda manutencao e emite `property.maintenance.scheduled`; `complete` exige papel aprovador, MFA e emite `property.maintenance.completed`.


        ## Eventos

        - `property.lease.created`
- `property.lease.activated`
- `property.lease.terminated`
- `property.maintenance.requested`
- `property.maintenance.scheduled`
- `property.maintenance.completed`

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

        Plano por unidade administrada e servicos.

        ## Integracoes e erros

        Eventos sao entregues pelo barramento RabbitMQ. Respostas esperadas:
        `401` ator ausente, `404` recurso inexistente e `422` regra de validacao
        ou politica anti-burla violada.

        ## Auditoria

        `POST /audit` e todas as mutacoes geram evento destinado a `audit.logs`,
        que e append-only no PostgreSQL.
