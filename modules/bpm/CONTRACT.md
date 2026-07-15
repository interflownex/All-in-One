        # Contrato: BPM

        ## Descricao

        Processos, workflows, tarefas, SLA, escalonamento e automacao.

        ## Entidades

        - `processes`
- `workflow_instances`
- `tasks`
- `sla_policies`

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


## Timers, SLA e escalonamento

- `sla_policies` exige `policy_key`, `response_minutes` e `escalation_role`, com status inicial `active`.
- `workflow_instances` exige `process_key`, `sla_policy_id` e `started_at`, iniciando em `running` e emitindo `bpm.process.started`.
- `tasks` exige `workflow_instance_id`, `assignee_user_id`, `due_at` e `sla_policy_id`, iniciando em `open`.
- A acao `escalate` move tarefas para `escalated`, exige papel aprovador, MFA e emite `bpm.task.escalated`.
- A acao `complete` move tarefas abertas, em progresso ou escaladas para `completed` e emite `bpm.task.completed`.


        ## Eventos

        - `bpm.process.started`
- `bpm.task.created`
- `bpm.task.escalated`
- `bpm.task.completed`
- `bpm.sla_policy.published`

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

        Modulo SaaS por execucao e automacao.

        ## Integracoes e erros

        Eventos sao entregues pelo barramento RabbitMQ. Respostas esperadas:
        `401` ator ausente, `404` recurso inexistente e `422` regra de validacao
        ou politica anti-burla violada.

        ## Auditoria

        `POST /audit` e todas as mutacoes geram evento destinado a `audit.logs`,
        que e append-only no PostgreSQL.
