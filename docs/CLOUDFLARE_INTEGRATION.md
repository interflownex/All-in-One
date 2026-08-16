# Integração Cloudflare Pages

## Escopo

O site público está em `apps/public-web` e usa um projeto Cloudflare Pages
Direct Upload já provisionado.

- branch de produção: `main`;
- validação de pull request: `azure-pipelines.pr.yml`;
- publicação de produção: `azure-pipelines.cloudflare.yml`;
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

## Validação de pull requests

Cadastre `azure-pipelines.pr.yml` como política obrigatória da branch `main`.
No Azure Repos, a validação de PR é acionada pela branch policy, não pelo bloco
`pr:` do YAML. Configure a política como automática e obrigatória. Esse pipeline
compila, testa, audita dependências e procura segredos sem receber credenciais
Cloudflare ou executar deploy.

## Produção pelo Azure Pipelines

Cadastre `azure-pipelines.cloudflare.yml` como pipeline e configure duas
variáveis secretas no Azure DevOps:

- `CLOUDFLARE_API_TOKEN`: token de escopo mínimo para Pages Write;
- `CLOUDFLARE_ACCOUNT_ID`: Account ID da conta Cloudflare.
- `CLOUDFLARE_PAGES_PROJECT`: identificador do projeto Pages.

As variáveis devem ser marcadas como secretas e ficar disponíveis somente ao
pipeline de produção. Nenhuma credencial deve ser entregue à validação de PR ou
gravada em arquivos, logs, commits ou artefatos.

O pipeline privilegiado não é acionado por pull requests. Apenas um commit já
integrado em `main` pode publicar no ambiente produtivo do projeto Pages.
Antes do upload, o pipeline consulta a API e falha se a branch de produção
remota não for `main`.

## Rollback

O Pages mantém deployments anteriores. Em caso de problema, selecione um
deployment saudável no painel Cloudflare e promova-o para produção antes de
investigar a nova build. A aplicação não depende de migrações ou storage.

Identificadores de conta, projeto, domínios e demais detalhes operacionais
permanecem fora do Git público.
