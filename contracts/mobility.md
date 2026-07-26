        # Contrato: Mobility

        ## Descricao

        Corridas, transporte publico, rotas, tickets, QR Code, NFC e ETA.

        ## Entidades

        - `rides`
- `routes`
- `stops`
- `tickets`
- `fare_rules`

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


## ETA, NFC e tarifas

- `routes` exige origem, destino, distancia, ETA e hash de rota para registrar `mobility.route.eta_quoted`.
- `tickets` exige QR e NFC tokenizados; uso de ticket emite `mobility.ticket.used`.
- `fare_rules` registra tarifas auditaveis append-only por tipo de veiculo e emite `mobility.fare_rule.published`.
- ETA dinamico, NFC real e tarifas produtivas dependem de provider homologado; o runtime local guarda somente metadados e hashes operacionais.


        ## Eventos

        - `mobility.ride.requested`
- `mobility.ride.accepted`
- `mobility.ride.completed`
- `mobility.route.eta_quoted`
- `mobility.ticket.purchased`
- `mobility.ticket.used`
- `mobility.fare_rule.published`

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

        Comissao de 15 a 25 por cento, cancelamento, tickets e passes.

        ## Integracoes e erros

        Eventos sao entregues pelo barramento RabbitMQ. Respostas esperadas:
        `401` ator ausente, `404` recurso inexistente e `422` regra de validacao
        ou politica anti-burla violada.

        ## Auditoria

        `POST /audit` e todas as mutacoes geram evento destinado a `audit.logs`,
        que e append-only no PostgreSQL.
