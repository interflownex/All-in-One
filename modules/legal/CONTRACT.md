        # Contrato: Legal

        ## Descricao

        Processos, contratos, prazos, audiencias, provisionamento e alertas.

        ## Entidades

        - `cases`

- `deadlines`
- `hearings`
- `legal_contracts`

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

## Caso, prazo e alerta juridico

- `cases` exige `case_number`, `case_type` e `opened_at`, preserva `risk_brl` como valor monetario auditavel e emite `legal.case.created`.
- `deadlines` exige `case_id`, `deadline_type` e `due_at`, iniciando em `pending` e emitindo `legal.deadline.created`.
- A acao `alert` move prazos para `alerted`, exige papel aprovador, MFA e emite `legal.deadline.alerted`.
- A acao `complete` move prazos pendentes ou alertados para `completed` e emite `legal.deadline.completed`.
- `hearings` exige `case_id` e `scheduled_at`, iniciando em `scheduled` e emitindo `legal.hearing.scheduled`.

        ## Eventos

        - `legal.case.created`

- `legal.deadline.created`
- `legal.deadline.alerted`
- `legal.deadline.completed`
- `legal.hearing.scheduled`

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

        Modulo SaaS para juridico interno e escritorios.

        ## Integracoes e erros

        Eventos sao entregues pelo barramento RabbitMQ. Respostas esperadas:
        `401` ator ausente, `404` recurso inexistente e `422` regra de validacao
        ou politica anti-burla violada.

        ## Auditoria

        `POST /audit` e todas as mutacoes geram evento destinado a `audit.logs`,
        que e append-only no PostgreSQL.
