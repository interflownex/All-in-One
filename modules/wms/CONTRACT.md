        # Contrato: WMS

        ## Descricao

        Armazens, bins, recebimento, separacao, lote, validade e inventario.

        ## Entidades

        - `warehouses`

- `bins`
- `inventory`
- `picking_waves`
- `shipments`

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

## Recebimento, picking e despacho

- `warehouses` exige `name`, inicia em `active` e emite `wms.warehouse.created`.
- `bins` exige `warehouse_id` e `code`, inicia em `active` e emite `wms.bin.created`.
- `inventory` exige `warehouse_id`, `sku`, `quantity` e `received_at`, iniciando em `received` e emitindo `wms.inventory.received`.
- A acao `allocate` move inventario para `allocated` e emite `wms.inventory.allocated`.
- `picking_waves` exige `warehouse_id`, `order_reference`, `sku` e `quantity`, iniciando em `open` e emitindo `wms.picking.created`.
- A acao `pick` emite `wms.picking.completed`; `close` exige papel aprovador, MFA e emite `wms.picking.closed`.
- `shipments` exige `warehouse_id`, `picking_wave_id` e `carrier_reference`; `dispatch` exige papel aprovador, MFA e emite `wms.shipment.dispatched`.

        ## Eventos

        - `wms.warehouse.created`

- `wms.bin.created`
- `wms.inventory.received`
- `wms.inventory.allocated`
- `wms.picking.created`
- `wms.picking.completed`
- `wms.picking.closed`
- `wms.shipment.created`
- `wms.shipment.dispatched`

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

        Modulo SaaS por deposito e volume operacional.

        ## Integracoes e erros

        Eventos sao entregues pelo barramento RabbitMQ. Respostas esperadas:
        `401` ator ausente, `404` recurso inexistente e `422` regra de validacao
        ou politica anti-burla violada.

        ## Auditoria

        `POST /audit` e todas as mutacoes geram evento destinado a `audit.logs`,
        que e append-only no PostgreSQL.
