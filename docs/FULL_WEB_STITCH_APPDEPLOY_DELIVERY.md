# Entrega web All-in-One no padrão Stitch

## Ambiente

- Aplicação pública: https://9135635066da434181.v2.appdeploy.ai/
- Domínio solicitado: https://brasildesconto.com.br/
- Estado do domínio: aguardando apontamento DNS no Cloudflare.

## Implementado

- logomarca oficial utilizada como recurso preservado, sem redesenho;
- navegação lateral e móvel no padrão visual do projeto;
- painel geral com indicadores reais do backend;
- cadastro empresarial com recomendação de módulos;
- ativação e desativação persistente de módulos;
- catálogo operacional para clientes, produtos, serviços, pedidos, estoque, financeiro, marketplace, delivery, logística, ERP, RH, Jobs, documentos, BI, usuários e integrações;
- criação, listagem, busca e exclusão de registros persistentes;
- relatórios com filtros e exportação CSV;
- configurações e atalhos funcionais;
- textos em português do Brasil;
- estados vazios, validação, sucesso e erro.

## Backend

Rotas adicionadas no ambiente publicado:

- `GET /api/state`
- `POST /api/company`
- `PUT /api/modules/:slug`
- `GET /api/records/:entity`
- `POST /api/records/:entity`
- `DELETE /api/records/:entity/:id`

## Validação

- build aprovado;
- frontend sem erros;
- backend sem erros;
- rede sem erros;
- testes E2E: 3/3 aprovados;
- QA desktop e móvel aprovado.

## DNS necessário

No Cloudflare, o domínio raiz deve apontar por CNAME flattening/ALIAS para `proxy-v2.appdeploy.ai` ou, como alternativa, por registro A para `18.232.7.146`. Depois da propagação, é necessária a verificação do domínio no AppDeploy.
