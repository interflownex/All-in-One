# Cloud Code - configuração mandatória e persistente

Este documento descreve passos e artefatos para configurar a extensão Cloud Code (VS Code) de forma coerente e reprodutível para o projeto `all-in-one`.

Pré-requisitos

- VS Code com a extensão `Cloud Code` instalada (googlecloudtools.cloudcode)
- `gcloud` CLI instalado e autenticado
- Permissões de projeto e IAM para habilitar APIs

Passos automáticos (script)

1. Execute o script que habilita APIs e instala componentes:

```bash
bash scripts/enable_cloud_build_and_cloudcode.sh
```

2. Autentique-se:

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project all-in-one-498012
GCLOUD_TIMEOUT_SECONDS=20 python3 scripts/google_cloud_control.py auth --project all-in-one-498012
```

O Data Agent Kit e bibliotecas Google que usam ADC exigem os dois logins:
`gcloud auth login` para o CLI e `gcloud auth application-default login` para
Application Default Credentials. Se o WSL resolver `gcloud` para o SDK Windows
em `/mnt/c` e ele nao responder, use um SDK Linux responsivo ou defina
`GCLOUD_BIN`.

Configurações recomendadas do VS Code (workspace)

- Abra `Preferences: Open Settings (JSON)` para o workspace e adicione/valide:

- `cloudcode.gcloudSdkPath`: caminho para o `gcloud` (ex: `/usr/bin/gcloud` ou `${env:HOME}/google-cloud-sdk/bin/gcloud`)
- `cloudcode.project`: `all-in-one-498012`
- `cloudcode.cloudBuild.enable`: `true` (usar Cloud Build para builds remotos)
- `cloudcode.skaffold.path`: `skaffold` (se usar Skaffold)

Nota sobre Cloud Build

- Recomendado usar Cloud Build para builds reprodutíveis no CI/CD.
- Garanta que o serviço `cloudbuild` esteja habilitado (o script acima faz isso).

Apigee e Secret Manager

- Use Secret Manager para segredos e `apigeecli`/`apigeectl` para criar KVMs conforme `infra/apigee`.

GitOps e CI

- Adicione o diretório `infra/kubernetes` ao seu pipeline de deploy.
- Em CI, recupere segredos do Secret Manager e crie `Secret` no cluster (não commit no repo).

Se quiser, posso gerar as configurações automatizadas de GitHub Actions ou Cloud Build para aplicar os manifests.
