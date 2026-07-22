        # Contrato: Vision

        ## Descricao

        Dispositivos de camera, streams, gravacoes, deteccao e ocorrencias.

        ## Entidades

        - `devices`

- `streams`
- `recordings`
- `motion_alerts`

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

## Stream, gravacao e alerta operacional

- `streams` exige `device_id`, `stream_url_hash`, `protocol` e `started_at`, iniciando em `active` e emitindo `vision.stream.started`.
- `recordings` exige `stream_id`, `storage_key`, `file_sha256` e `started_at`, e e append-only com evento `vision.recording.stored`.
- `motion_alerts` exige `device_id`, `stream_id`, `detected_at` e `confidence_score`, iniciando em `detected` e emitindo `vision.motion.detected`.
- A acao `triage` exige papel aprovador, MFA e cria incidente com `vision.incident.created`.
- A acao `resolve` exige papel aprovador, MFA e emite `vision.incident.resolved`.

        ## Eventos

        - `vision.device.registered`

- `vision.device.submitted`
- `vision.device.cancelled`
- `vision.device.completed`
- `vision.stream.started`
- `vision.stream.paused`
- `vision.stream.resumed`
- `vision.recording.stored`
- `vision.motion.detected`
- `vision.incident.created`
- `vision.incident.resolved`

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

        Plano por camera, retencao e analise IA.

        ## Integracoes e erros

        Eventos sao entregues pelo barramento RabbitMQ. Respostas esperadas:
        `401` ator ausente, `404` recurso inexistente e `422` regra de validacao
        ou politica anti-burla violada.

        ## Auditoria

        `POST /audit` e todas as mutacoes geram evento destinado a `audit.logs`,
        que e append-only no PostgreSQL.
