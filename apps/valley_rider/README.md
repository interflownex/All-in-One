# Valley Rider

Aplicação React/Vite mobile-first do entregador e motorista Valley, implementada a partir do contrato oficial do projeto Stitch **VALLEY RIDERS APK - Template Completo**.

## Público-alvo

- Riders, entregadores e motoristas cadastrados;
- equipe operacional e de compliance;
- equipe técnica responsável pelos módulos Identity, Riders, Delivery, Mobility e Finance.

## Jornadas funcionais

- criação de conta e autenticação pelo All-in-One ID;
- cadastro do perfil Rider e criação da carteira financeira;
- envio protegido de CNH, selfie e validação KYC;
- cadastro, vistoria e manutenção do veículo;
- disponibilidade online/offline com bloqueio até homologação;
- GPS contínuo e compartilhamento preciso ou aproximado;
- Mapbox com localização, coleta, destino, rota, distância dinâmica e ETA;
- entregas e corridas com aceite, coleta, conclusão e prova de entrega;
- ganhos no ledger, extrato, repasses auditáveis e cancelamento de repasse pendente;
- seguro/proteção da entrega, suporte, contestação, emergência e compartilhamento de localização;
- histórico, avaliações, notificações e configurações do dispositivo.

## Variáveis

Copie `.env.example` para `.env.local` e defina, sem versionar segredos:

- `VITE_API_HUB_URL`;
- `VITE_MAPBOX_ACCESS_TOKEN`;
- `VITE_PLAY_INTEGRITY_TOKEN`, quando fornecido pelo shell Android.

## Validação obrigatória

```bash
cd apps/valley_rider
npm ci
npm run lint
npm run build
```

O token Mapbox deve ser público e restrito. Chaves secretas não podem ser inseridas no bundle Vite.

O pipeline `.github/workflows/valley-rider-mapbox.yml` exige credenciais
separadas para staging e produção, valida Style, Directions e Geocoding ao vivo
e publica o diretório `dist` como artefato. Os secrets obrigatórios são:

- `VITE_MAPBOX_ACCESS_TOKEN_STAGING`;
- `VITE_MAPBOX_ACCESS_TOKEN_PRODUCTION`;
- `MAPBOX_MOBILE_ACCESS_TOKEN_STAGING`;
- `MAPBOX_MOBILE_ACCESS_TOKEN_PRODUCTION`.

O token mobile é verificado pelo pipeline, mas não é inserido no bundle web.
