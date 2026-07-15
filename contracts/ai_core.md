        # Contrato: AI Core

        ## Descricao

        Memoria autorizada, classificacao anti-burla, modelos e governanca.

        ## Entidades

        - `ai_memories`
- `moderation_decisions`
- `model_runs`

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


## Provider, custo e governanca de modelo

- `ai_memories` exige `memory_key` e `summary`, inicia em `draft` e emite `ai.memory.created`.
- A acao `index` move memorias para `indexed` com `ai.memory.indexed`; `update` emite `ai.memory.updated`.
- `model_runs` exige `provider_adapter`, `provider_name`, `model_name`, `prompt_tokens`, `completion_tokens`, `estimated_cost_brl` e `requested_at`.
- A criacao de execucao emite `ai.model_run.requested`; `complete` emite `ai.model_run.completed` e `fail` emite `ai.model_run.failed`.
- A acao `approve_cost` exige papel aprovador, MFA e emite `ai.model_run.cost_approved`.
- `estimated_cost_brl` e validado como valor monetario nao negativo; providers reais seguem pendentes de homologacao.


        ## Eventos

        - `ai.memory.created`
- `ai.memory.indexed`
- `ai.memory.updated`
- `ai.moderation.created`
- `ai.moderation.completed`
- `ai.model_run.requested`
- `ai.model_run.completed`
- `ai.model_run.failed`
- `ai.model_run.cost_approved`

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

        Consumo de IA e automacoes premium.

        ## Integracoes e erros

        Eventos sao entregues pelo barramento RabbitMQ. Respostas esperadas:
        `401` ator ausente, `404` recurso inexistente e `422` regra de validacao
        ou politica anti-burla violada.

        ## Auditoria

        `POST /audit` e todas as mutacoes geram evento destinado a `audit.logs`,
        que e append-only no PostgreSQL.
