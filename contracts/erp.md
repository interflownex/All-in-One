        # Contrato: ERP

        ## Descricao

        Financeiro empresarial, compras, vendas, fiscal, controladoria e aprovacao.

        ## Entidades

        - `accounts`
- `payables`
- `receivables`
- `cost_centers`
- `fiscal_documents`

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


## Contas, pagamentos e conciliacao

- `accounts` exige `account_code` e `name`, iniciando em `active` e emitindo `erp.account.created`.
- `cost_centers` exige `cost_center_code` e `name`, iniciando em `active` e emitindo `erp.cost_center.created`.
- `payables` exige `supplier_name`, `due_at`, `amount_brl` e `cost_center_id`, iniciando em `open` e emitindo `erp.payable.created`.
- A acao `approve_payment` exige papel aprovador, MFA e emite `erp.payment.approved`; `settle` move para `paid` com `erp.payable.paid`.
- `receivables` exige `customer_name`, `due_at`, `amount_brl` e `account_id`, iniciando em `issued` e emitindo `erp.receivable.created`.
- A acao `receive` emite `erp.receivable.received`; `reconcile` exige papel aprovador, MFA e emite `erp.receivable.reconciled`.


        ## Eventos

        - `erp.account.created`
- `erp.cost_center.created`
- `erp.payable.created`
- `erp.payment.approved`
- `erp.payable.paid`
- `erp.receivable.created`
- `erp.receivable.received`
- `erp.receivable.reconciled`
- `erp.invoice.created`
- `erp.invoice.submitted`
- `erp.invoice.completed`
- `erp.invoice.cancelled`

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

        Modulo SaaS Business contratado por entidade.

        ## Integracoes e erros

        Eventos sao entregues pelo barramento RabbitMQ. Respostas esperadas:
        `401` ator ausente, `404` recurso inexistente e `422` regra de validacao
        ou politica anti-burla violada.

        ## Auditoria

        `POST /audit` e todas as mutacoes geram evento destinado a `audit.logs`,
        que e append-only no PostgreSQL.
