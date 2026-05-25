        # Contrato: One Services

        ## Descricao

        Prestadores, visitas pagas, orcamentos, contratos, evidencias e anti-burla.

        ## Entidades

        - `providers`
- `visits`
- `quotes`
- `service_contracts`
- `evidence`

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


        ## Eventos

        - `services.visit.created`
- `services.visit.completed`
- `services.quote.created`
- `services.contract.created`
- `services.contract.completed`

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

        Visita de 15 a 25 por cento, servico de 8 a 20 por cento e premium.

        ## Integracoes e erros

        Eventos sao entregues pelo barramento RabbitMQ. Respostas esperadas:
        `401` ator ausente, `404` recurso inexistente e `422` regra de validacao
        ou politica anti-burla violada.

        ## Auditoria

        `POST /audit` e todas as mutacoes geram evento destinado a `audit.logs`,
        que e append-only no PostgreSQL.
