# Valley Rider — Mapbox em ambiente de navegação

**Projeto:** All in One + Valley  
**Classificação:** Pendências / Técnico  
**Público-alvo:** Equipe Técnica  
**Impacto:** Valley Rider, Delivery, Mobility, B2B e B2C  
**Data:** 01/08/2026  
**Branch:** `feat/valley-rider-mapbox-production-20260801`

## 1. Decisão visual reescrita

A personalização anterior tratava o mapa como superfície de marca. Em navegação real, a prioridade muda: primeiro segurança, leitura da via, rota, manobra e contexto; depois identidade visual.

### Padrão aprovado: Navegação Valley Rider

- estilos oficiais Mapbox Navigation Day e Navigation Night;
- troca automática por horário e preferência do dispositivo;
- rota ativa em ciano `#20C8F3`;
- contorno escuro `#06111F` para manter contraste sobre qualquer via;
- posição do Rider em ciano;
- coleta em âmbar `#F2A93B`;
- destino em verde `#22B86B`;
- ocorrências críticas em vermelho `#E45B6A`;
- câmera inclinada a 52 graus quando há posição e destino;
- orientação da câmera pelo rumo até o próximo alvo;
- painel de marca pequeno, neutro e fora da área principal de orientação;
- logomarca oficial sem recoloração, recorte, filtro ou distorção;
- fallback textual `VALLEY RIDER` enquanto o PNG canônico não estiver fisicamente ingerido no Git;
- mensagens específicas para token ausente, inválido, revogado, sem escopo ou bloqueado por origem.

### O que foi rejeitado para navegação ativa

- fundo cósmico decorativo;
- vias recoloridas de forma ampla;
- excesso de pontos de interesse;
- brilho forte na rota;
- animações contínuas;
- logomarca grande sobre o mapa;
- elementos 3D que prejudiquem a leitura durante deslocamento;
- troca de estilo no meio de uma manobra.

Esses recursos podem permanecer em telas de apresentação, acompanhamento estático ou marketing, mas não na navegação operacional.

## 2. Marca oficial Valley Rider

Fonte de verdade:

```text
Arquivo: VALLEY_RIDER_LOGOMARCA_PRINCIPAL_OFICIAL_20260729.png
Drive ID: 1o17hEuccrJDZLUL2EbL06Pgq9MIyq6mQ
Dimensões: 1024x1024
Formato: PNG RGBA
SHA-256: f5fba898ee9c660a35e359b8968b1b7d7256d7ded7434e34d1abd601e609db73
```

O texto visual permanece `VALLEY RIDER`. O nome técnico legado `Valley Riders` pode continuar em rotas, chaves e contratos até uma migração nominal separada.

Ingestão sem alteração de bytes:

```bash
python3 scripts/branding/ingest_valley_rider_logo.py \
  --source /caminho/VALLEY_RIDER_LOGOMARCA_PRINCIPAL_OFICIAL_20260729.png
```

O script copia o mesmo binário para:

```text
assets/brand/valley-riders-logo-official.png
apps/valley_rider/public/brand/valley-riders-logo-official.png
```

## 3. Arquitetura implantada

```text
apps/valley_rider/src/mapboxConfig.ts
  ├─ valida token público pk.
  ├─ fixa versão do GL JS
  ├─ escolhe navegação day/night
  └─ centraliza cores operacionais

apps/valley_rider/src/MapboxRouteMap.tsx
  ├─ carrega Mapbox GL JS
  ├─ usa estilo de navegação oficial
  ├─ desenha rota com casing
  ├─ posiciona Rider/coleta/destino
  ├─ orienta câmera e bearing
  ├─ mantém atribuição Mapbox
  └─ exibe identidade Valley Rider sem cobrir a orientação

scripts/mapbox/provision_valley_rider_tokens.mjs
  ├─ cria tokens web e mobile
  ├─ separa staging e production
  ├─ restringe token web por URL
  ├─ mantém token mobile sem URL restriction
  ├─ grava arquivos com permissão 0600
  ├─ não imprime tokens
  └─ revoga o lote se houver falha

scripts/mapbox/validate_valley_rider_mapbox.mjs
  ├─ valida Style API
  ├─ valida Directions API
  ├─ valida Geocoding API
  └─ mascara o token no relatório
```

## 4. Modelo obrigatório de credenciais

### Token administrativo de provisionamento

Criar no console Mapbox um token secreto temporário para provisionamento com:

```text
tokens:write
styles:read
fonts:read
```

Regras:

- nome sugerido: `Valley Provisioner One-Time`;
- copiar uma única vez para cofre local ou Secret Manager;
- nunca inserir em Vite, frontend, APK, issue, Markdown, commit ou chat;
- revogar após a criação dos tokens definitivos, salvo se existir processo formal de rotação automatizada.

### Tokens definitivos

Criar quatro tokens separados:

```text
Valley Rider Web staging
Valley Rider Web production
Valley Rider Mobile staging
Valley Rider Mobile production
```

Escopos públicos:

```text
styles:read
fonts:read
```

Regras:

- token web: `pk.` com URL restrictions;
- token mobile: `pk.` sem URL restrictions, pois Mapbox não oferece essa proteção para SDKs nativos;
- staging e production nunca compartilham token;
- localhost só pode aparecer no token de development;
- cada token deve ser acompanhado separadamente nas estatísticas Mapbox.

## 5. Provisionamento autônomo preparado

Variáveis necessárias, informadas somente no terminal seguro:

```bash
export MAPBOX_USERNAME='USUARIO_MAPBOX'
export MAPBOX_ADMIN_TOKEN='sk_TOKEN_DE_PROVISIONAMENTO'
export MAPBOX_ENVIRONMENTS='staging,production'
export MAPBOX_WEB_ALLOWED_URLS_STAGING='https://staging.exemplo.com'
export MAPBOX_WEB_ALLOWED_URLS_PRODUCTION='https://rider.exemplo.com'
export MAPBOX_CREATE_MOBILE_TOKENS='true'

node scripts/mapbox/provision_valley_rider_tokens.mjs
```

Saída protegida:

```text
tmp/mapbox-secrets/.env.mapbox.staging.local
tmp/mapbox-secrets/.env.mapbox.production.local
tmp/mapbox-secrets/mapbox-token-manifest.json
```

O diretório `tmp/` já é ignorado pelo Git.

## 6. Ativação do aplicativo

```bash
cd apps/valley_rider
cp ../../tmp/mapbox-secrets/.env.mapbox.staging.local .env.local
npm ci
npm run lint
npm run build
```

Validação real:

```bash
set -a
. ./.env.local
set +a
export MAPBOX_TEST_REFERER='https://staging.exemplo.com'
node ../../scripts/mapbox/validate_valley_rider_mapbox.mjs
```

## 7. Configuração no deploy

Configurar no ambiente de hospedagem, sem arquivo versionado:

```text
VITE_MAPBOX_ACCESS_TOKEN
VITE_MAPBOX_GL_JS_VERSION=3.25.0
VITE_MAPBOX_STYLE_DAY=mapbox://styles/mapbox/navigation-day-v1
VITE_MAPBOX_STYLE_NIGHT=mapbox://styles/mapbox/navigation-night-v1
VITE_MAPBOX_NAVIGATION_MODE=auto
```

O token público ficará visível no bundle web por natureza. A segurança depende de:

- token público sem escopos secretos;
- restrição de URL;
- ambientes separados;
- rotação;
- monitoramento de consumo;
- nenhuma operação administrativa no cliente.

## 8. Limite desta execução

O console Mapbox aberto no navegador do usuário não é acessível pelo conector desta conversa. Portanto:

- o código, provisionador, validação, governança e branch foram implantados;
- nenhum token falso foi inventado;
- nenhum segredo foi solicitado no chat;
- a criação efetiva dos tokens só ocorre quando o token administrativo `sk.` é fornecido diretamente ao terminal seguro ou Secret Manager;
- produção não deve ser declarada pronta antes da validação real retornar sucesso.

## 9. Critérios de aprovação

- [ ] logomarca canônica ingerida com SHA-256 correto;
- [ ] token web staging criado e restrito;
- [ ] token web production criado e restrito;
- [ ] tokens mobile separados;
- [ ] token administrativo de provisionamento revogado ou guardado sob política formal;
- [ ] Style, Directions e Geocoding aprovados;
- [ ] lint aprovado;
- [ ] build aprovado;
- [ ] QA Android/WebView aprovado;
- [ ] GPS em campo aprovado;
- [ ] erros 401 e 403 testados;
- [ ] atribuição Mapbox visível;
- [ ] consumo acompanhado por token;
- [ ] rollback documentado.

## 10. Fontes oficiais

- https://docs.mapbox.com/accounts/guides/tokens/
- https://docs.mapbox.com/api/accounts/tokens/
- https://docs.mapbox.com/help/dive-deeper/access-tokens/
- https://docs.mapbox.com/mapbox-gl-js/guides/styles/
