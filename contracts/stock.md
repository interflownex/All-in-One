        # Contrato: STOCK

        ## Descricao

        Catálogo curado de fornecedores homologados, sem estoque físico próprio, com pedido sob demanda, regras de preço, tracking e descontos por Pepitas. Entra na primeira etapa com AliExpress e CJ Dropshipping como fontes iniciais, sob operação controlada e expansão condicionada à qualidade.

        ## Entidades

        - `suppliers`
- `catalog_products`
- `price_rules`
- `supplier_orders`
- `discount_quotes`

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

        - `stock.product.imported`
- `stock.supplier_order.created`
- `stock.supplier_order.acknowledged`
- `stock.supplier_order.shipped`
- `stock.supplier_order.delivered`
- `stock.supplier_order.cancelled`
- `valley.stock.discount.quoted`

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

        Comissão ou margem negociada, destaque, taxa de operação e planos para lojistas; a expansão depende de prazo, devoluções, suporte e margem auditada.

        ## Integracoes e erros

        Eventos sao entregues pelo barramento RabbitMQ. Respostas esperadas:
        `401` ator ausente, `404` recurso inexistente e `422` regra de validacao
        ou politica anti-burla violada.

        ## Auditoria

        `POST /audit` e todas as mutacoes geram evento destinado a `audit.logs`,
        que e append-only no PostgreSQL.
