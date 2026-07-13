# Cloud Build / GitOps deploy

Arquivos nesta pasta:

- `cloudbuild-deploy.yaml` — pipeline para executar no Cloud Build que injeta secrets do Secret Manager e aplica `infra/kubernetes` via kustomize.

Como usar

1. Ajuste `cloudbuild/cloudbuild-deploy.yaml` substituindo `_CLUSTER_NAME` e `_CLUSTER_ZONE` (ou passe via substituições no trigger).
2. Crie um trigger no Cloud Build apontando para este arquivo e ativado em push para o branch desejado.
3. Garanta que a conta de serviço do Cloud Build tenha permissão `roles/container.clusterViewer` e `roles/container.developer` ou equivalente para executar `get-credentials` e `kubectl`.
4. Armazene secrets no Secret Manager (ex: `DATABASE_PASSWORD`, `JWT_SECRET`) e garanta que o Cloud Build service account tenha acesso `roles/secretmanager.secretAccessor`.
