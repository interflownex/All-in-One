# Correção de alertas de credenciais e aleatoriedade

## Classificação

- Projeto: All in One + Valley
- Pasta lógica: Pendências
- Assunto: Técnico
- Público-alvo: Equipe Técnica e Segurança

## Escopo

Este lote corrige os alertas de logging sensível e aleatoriedade insegura nas respectivas fontes, além de regenerar os assets Android a partir do frontend Valley.

## Segredos de nuvem

O script `scripts/setup_cloud_secrets.py` passa a:

- receber `GCP_PROJECT_ID` exclusivamente por variável de ambiente;
- receber os payloads por `AIO_IDENTITY_DSN`, `AIO_JWT_SECRET` e `AIO_DOCUMENT_ENCRYPTION_KEY`;
- criar o segredo somente quando ainda não existe;
- adicionar versões por stdin;
- suprimir stdout e stderr da CLI `gcloud`;
- registrar apenas identificador e código de retorno, sem payload;
- falhar quando qualquer variável obrigatória estiver ausente.

A remoção da árvore atual não revoga valores presentes no histórico. A rotação operacional está registrada na issue #224.

## Valley

A função `randomId` usa `crypto.getRandomValues` no navegador. O bundle Android não foi editado manualmente: ele foi apagado e regenerado com `npm ci`, lint e build da fonte `apps/valley`.

## Testes de regressão

- bloqueio de URI de banco e marcadores de segredo literal no script;
- exigência das quatro variáveis de ambiente;
- verificação de ausência do payload nos logs;
- exigência de `crypto.getRandomValues` na função `randomId`;
- rejeição de `Math.random().toString(36)` nos assets Android gerados.

## Limites

- nenhuma credencial externa foi criada ou rotacionada por este lote;
- nenhum valor de segredo deve ser anexado a PR, issue, log ou artefato;
- a issue #224 permanece bloqueante até evidência de revogação e rotação.
