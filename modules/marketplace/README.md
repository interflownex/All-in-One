# Marketplace

Lojas locais aprovadas, catalogo pesquisavel, descoberta geolocalizada, feed vertical, promocao do dia, favoritos, carrinho, checkout, pedidos e concessao manual de Pepitas.

## Responsabilidade

Este microservico e isolado por dominio, mas toda criacao mantem `user_id`
associado ao All-in-One ID. Operacoes mutaveis sao auditadas e exigem o
cabecalho `X-Actor-User-Id`, salvo o autorregistro inicial em Identity.

A descoberta publica exibe somente lojas aprovadas e produtos publicados ou
ativos. Produtos em rascunho, lojas nao homologadas e itens sem preco valido nao
sao expostos nas rotas de consumo.

## Entidades

`stores`, `products`, `carts`, `orders`, `reviews`, `disputes`, `pepita_grants`.

Os favoritos e o carrinho usam workspaces isolados por usuario dentro de
`carts`, diferenciados por `cart_type`, preservando auditoria e compatibilidade
com os stores SQLite e PostgreSQL existentes.

## Jornadas Valley

- `GET /valley/catalog`: busca, categoria, loja, preco, estoque, distancia e ordenacao;
- `GET /valley/feed`: cards verticais de produtos, com identificacao de patrocinio;
- `GET /valley/promotions/today`: promocao elegivel, dispensavel e sem bloquear a homepage;
- `GET|PUT|DELETE /valley/favorites`: favoritos isolados pelo All-in-One ID;
- `GET /valley/cart`: resumo do carrinho com disponibilidade e total em BRL;
- `PUT|DELETE /valley/cart/items/{product_id}`: inclusao, quantidade e remocao;
- `POST /valley/orders/{order_id}/support`: suporte ou disputa vinculada ao pedido;
- `GET /valley/insights/commercial`: indicadores comerciais e de atendimento.

## Execucao

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Validacao

```bash
pytest -q tests/test_marketplace_discovery.py
pytest -q tests/test_marketplace_support_metrics.py
pytest -q tests/test_marketplace_commercial_metrics.py
```

O contrato HTTP esta em `OPENAPI.yaml`; os controles especificos estao
descritos em `CONTRACT.md` e `SECURITY.md`.
