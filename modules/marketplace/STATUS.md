# Status: Marketplace

- Estado: `consumer_discovery_beta`
- Runtime: FastAPI com persistencia SQLite contratual, autorizacao, auditoria e outbox
- Contrato: publicado localmente em `OPENAPI.yaml`, `CONTRACT.md` e `README.md`
- Persistencia: schema e tabelas iniciais cobertos por migracoes
- Descoberta: catalogo pesquisavel, categoria, preco, geolocalizacao, raio e ordenacao
- Feed: cards verticais 9:16 com identificacao de conteudo patrocinado
- Promocao: selecao diaria elegivel, dispensavel e com fallback sem bloquear a homepage
- Usuario: favoritos e carrinho isolados por All-in-One ID e auditados
- Testes dedicados: `tests/test_marketplace_discovery.py`
- Proximo incremento: checkout integrado a Stock, Wallet e Orders, seguido de E2E produtivo
