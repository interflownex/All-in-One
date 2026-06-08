# Integracao

Cada modulo publica `OPENAPI.yaml`. No baseline, o gateway autentica JWT/API
key e repassa `X-Actor-User-Id` somente apos validar escopos.

## Matriz versionada

A matriz operacional de provedores fica em
`config/integrations/provider_matrix.json`. Ela define, por capacidade:

- modulos consumidores;
- adapter sandbox local;
- candidatos primarios e fallback;
- nomes de variaveis de ambiente;
- eventos envolvidos;
- dados sensiveis tratados;
- entrada de custo zero ou menor custo;
- gate minimo de producao.

Essa matriz e validada por `tests/test_integration_provider_matrix.py` para
garantir que os modulos criticos tenham estrategia de integracao, que somente
nomes de segredos sejam versionados e que exista adapter sandbox antes de
qualquer dependencia externa obrigatoria.

## Adapters sandbox

A camada executavel de sandbox fica em `modules/shared/integration_sandbox.py`.
Ela implementa adapters deterministicos para:

- `identity_kyc_kyb`: simulador KYC/KYB com hashes de documento e eventos de
  aprovacao;
- `finance_pix_psp`: simulador de Pix, autorizacao, escrow e release;
- `fiscal_nfse_nfe`: emissao fiscal sandbox com codigo de autorizacao
  deterministico;
- `jobs_ctps_official`: preservacao de hash de PDF CTPS sem alegar verificacao
  oficial externa;
- `maps_routing_tracking`: calculo local de distancia e ETA;
- `health_telemedicine_prescription`: consentimento clinico local com validade;
- `api_hub_oauth_webhooks`: assinatura HMAC e verificacao de API key por hash;
- `stock_supplier_catalog`: fixture de catalogo de fornecedor e disponibilidade.

Os contratos sao validados por `tests/test_integration_sandbox_adapters.py`.
Nenhum adapter sandbox deve realizar chamada externa nem exigir segredo real.

## Endpoints sandbox locais

Os adapters tambem ficam expostos por rotas administrativas dos modulos, sempre
exigindo `X-Actor-Roles` com papel aceito por compliance/operacao:

- Identity/Riders/Services: `POST /integrations/sandbox/kyc/person`;
- Business: `POST /integrations/sandbox/kyb/business`;
- Finance: `POST /integrations/sandbox/psp/pix/authorize`,
  `POST /integrations/sandbox/psp/escrows` e
  `POST /integrations/sandbox/psp/escrows/release`;
- ERP: `POST /integrations/sandbox/fiscal/invoices`;
- Jobs: `POST /integrations/sandbox/ctps/classify`;
- Delivery/Mobility/TMS: `POST /integrations/sandbox/maps/route`;
- Health: `POST /integrations/sandbox/health/consents`;
- API Hub: `POST /integrations/sandbox/api-hub/webhooks/sign` e
  `POST /integrations/sandbox/api-hub/api-key/verify`;
- Stock: `POST /integrations/sandbox/suppliers/products`.

As rotas sao validadas por `tests/test_integration_sandbox_routes.py`.

## Convencoes

- UUID em identificadores e `user_id` sempre associado ao All-in-One ID.
- Eventos no exchange `all-in-one.domain`; consumidores idempotentes.
- Valores BRL com quatro casas; NEX com oito casas.
- Webhooks devem ser assinados e aceitar retry com idempotency key.
- Integracoes nunca recebem biometria bruta nem prontuario sem base legal.
- Valores reais de `*_SECRET`, `*_TOKEN`, `*_API_KEY`, certificados e credenciais
  ficam fora do Git.
- Todo provedor externo precisa de adapter local deterministico para testes.

## Ordem de homologacao

1. `api_hub_oauth_webhooks`: sustenta seguranca, escopos, replay protection e
   webhooks assinados para os demais provedores.
2. `identity_kyc_kyb`: desbloqueia usuarios, empresas, riders, prestadores e
   operacoes reguladas.
3. `finance_pix_psp`: habilita escrow, split, refund, checkout e conciliacao.
4. `maps_routing_tracking`: habilita ETA, tracking e custos de Delivery,
   Mobility e TMS.
5. `jobs_ctps_official`: evolui a importacao de PDF com hash para verificacao
   externa quando houver integrador autorizado.
6. `fiscal_nfse_nfe`: fecha cobranca e fiscal para Finance/ERP.
7. `health_telemedicine_prescription`: so avanca com consentimento, retencao e
   governanca clinica definidos.
8. `stock_supplier_catalog`: entra por CSV/manual e evolui para API conforme
   fornecedor homologado.

## Politica de menor custo

- Comecar com simuladores locais e fixtures auditadas.
- Usar sandbox gratuita quando o provedor oferecer.
- Evitar chamadas pagas em testes automatizados.
- Cachear respostas nao sensiveis e limitar geocoding/rotas por jornada.
- Promover para producao apenas quando houver receita, exigencia legal ou
  dependencia operacional real.

## Acesso Unificado (All-in-One UI)

O ecossistema All-in-One expõe uma interface unificada que consolida todos os 25 módulos. O roteamento é gerenciado pelo Ingress Global na GCP.

### Rotas de Interface
- **Base:** `/all-in-one/`
- **Módulos:** `/{modulo}/overview` (ex: `/identity/overview`)

### Integração com Apigee Gateway
Todas as chamadas de API do frontend devem passar pelo Apigee para garantir governança, quota e segurança:
- **Identity:** `https://api.all-in-one.com/identity/*`
- **API Hub:** `https://api.all-in-one.com/gateway/*`
- **Logística:** `https://api.all-in-one.com/{delivery|wms|tms}/*`

