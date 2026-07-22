        # Contrato: BI

        ## Descricao

        Indicadores auditaveis, dashboards e exportacoes por entidade.

        ## Entidades

        - `datasets`

- `dashboards`
- `indicators`
- `exports`

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

## Dataset, dashboard e exportacao

- `datasets` exige `name`, `source_module`, `source_resource_type` e `refresh_mode`, iniciando em `draft` e emitindo `bi.dataset.created`.
- A acao `refresh` registra refresh auditavel com `bi.dataset.refreshed`; `publish` exige papel aprovador, MFA e emite `bi.dataset.published`.
- `dashboards` exige `dataset_id`, `name`, `definition` e `allowed_roles`, inicia em `draft` e emite `bi.dashboard.created`.
- A acao `publish` publica dashboard com papel aprovador, MFA e evento `bi.dashboard.published`; `archive` encerra a exposicao com MFA.
- `exports` exige `dashboard_id`, `export_format` e `requested_at`, inicia em `requested`, emite `bi.export.requested` e conclui com `bi.export.completed`.

        ## Eventos

        - `bi.dataset.created`

- `bi.dataset.refreshed`
- `bi.dataset.published`
- `bi.dashboard.created`
- `bi.dashboard.published`
- `bi.dashboard.archived`
- `bi.indicator.created`
- `bi.indicator.submitted`
- `bi.indicator.cancelled`
- `bi.indicator.completed`
- `bi.export.requested`
- `bi.export.completed`

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

        Relatorios premium e armazenamento analitico.

        ## Integracoes e erros

        Eventos sao entregues pelo barramento RabbitMQ. Respostas esperadas:
        `401` ator ausente, `404` recurso inexistente e `422` regra de validacao
        ou politica anti-burla violada.

        ## Auditoria

        `POST /audit` e todas as mutacoes geram evento destinado a `audit.logs`,
        que e append-only no PostgreSQL.
