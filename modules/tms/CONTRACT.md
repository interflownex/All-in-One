        # Contrato: TMS

        ## Descricao

        Transportadoras, frota, rotas, fretes, documentos e torre de controle.

        ## Entidades

        - `carriers`

- `freights`
- `routes`
- `proofs_of_delivery`
- `freight_audits`

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

## Frete, POD e auditoria

- `carriers` exige `name` e `coverage`, iniciando em `pending_review` e emitindo `tms.carrier.created`.
- `routes` exige `origin`, `destination`, `distance_km` e `eta_minutes`, iniciando em `planned` e emitindo `tms.route.created`.
- `freights` exige `carrier_id`, `route_id`, `freight_brl` e `scheduled_at`, iniciando em `quoted` e emitindo `tms.freight.created`.
- A acao `approve` exige papel aprovador, MFA e emite `tms.freight.approved`; `dispatch` emite `tms.freight.dispatched`.
- A acao `complete` exige papel aprovador, MFA e emite `tms.freight.completed`.
- `proofs_of_delivery` exige `freight_id`, `file_sha256`, `storage_key` e `delivered_at`, e e append-only com evento `tms.delivery.proved`.
- `freight_audits` exige `freight_id`, `audit_result` e `audited_at`; `close` exige papel aprovador, MFA e emite `tms.freight.audit_closed`.

        ## Eventos

        - `tms.carrier.created`

- `tms.carrier.submitted`
- `tms.carrier.approved`
- `tms.carrier.rejected`
- `tms.route.created`
- `tms.route.activated`
- `tms.freight.created`
- `tms.freight.approved`
- `tms.freight.dispatched`
- `tms.freight.completed`
- `tms.delivery.proved`
- `tms.freight.audit_created`
- `tms.freight.audit_closed`

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

        Modulo SaaS e taxas por operacao logistica.

        ## Integracoes e erros

        Eventos sao entregues pelo barramento RabbitMQ. Respostas esperadas:
        `401` ator ausente, `404` recurso inexistente e `422` regra de validacao
        ou politica anti-burla violada.

        ## Auditoria

        `POST /audit` e todas as mutacoes geram evento destinado a `audit.logs`,
        que e append-only no PostgreSQL.
