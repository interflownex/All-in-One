# Integração Cloudflare Pages

## Escopo

O site público está em `apps/public-web` e usa o projeto Direct Upload
`all-in-one-web` da conta `474fc26bf9c6bcf5e1a84b7f63a516d8`.

- domínio Pages: `all-in-one-web-7fa.pages.dev`;
- domínio customizado: `brasildesconto.com.br`;
- branch de produção: `main`;
- pipeline: `azure-pipelines.cloudflare.yml`;
- configuração versionada: `config/cloudflare/pages-public.json`.

O pipeline não cria nem altera DNS, domínio customizado ou tunnel. Ele apenas
envia o diretório estático compilado para o projeto Pages existente.

## Desenvolvimento local

```bash
cd apps/public-web
npm ci
npm run build
npm test
npm run dev
```

## Preview manual

```bash
cd apps/public-web
npm run deploy:preview
```

O script usa a branch `cloudflare-integration`, portanto não substitui o
deployment de produção.

## Produção pelo Azure Pipelines

Cadastre `azure-pipelines.cloudflare.yml` como pipeline e configure duas
variáveis secretas no Azure DevOps:

- `CLOUDFLARE_API_TOKEN`: token de escopo mínimo para Pages Write;
- `CLOUDFLARE_ACCOUNT_ID`: Account ID da conta Cloudflare.

As variáveis devem ser marcadas como secretas. Nenhuma credencial deve ser
gravada em arquivos, logs, commits ou artefatos.

Branches e pull requests geram URLs de preview. Apenas `main` corresponde ao
ambiente produtivo do projeto Pages.

## Rollback

O Pages mantém deployments anteriores. Em caso de problema, selecione um
deployment saudável no painel Cloudflare e promova-o para produção antes de
investigar a nova build. A aplicação não depende de migrações ou storage.

## Tunnel

O tunnel histórico `all-in-one-stream` não faz parte deste deploy. Sua gestão
exige credencial própria fora do Git e deve permanecer separada da publicação
estática. SSH e bancos de dados não são expostos por esta integração.
