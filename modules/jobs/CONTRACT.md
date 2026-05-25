        # Contrato: Jobs

        ## Descricao

        Curriculos do usuario final, importacao rastreavel da CTPS Digital PDF, experiencias autodeclaradas, vagas e candidaturas com acesso Business controlado.

        ## Entidades

        - `resumes`
- `employment_records`
- `resume_documents`
- `job_postings`
- `applications`
- `resume_access_logs`

        ## APIs

        - `GET /health`
- `GET /version`
- `GET /status`
- `GET /metrics`
- `GET /catalog`
- `POST /resources/{resource_type}`
- `GET /resources/{resource_type}`
- `GET /resources/{resource_type}/{resource_id}`
- `PATCH /resources/{resource_type}/{resource_id}`
- `DELETE /resources/{resource_type}/{resource_id}`
- `POST /resources/{resource_type}/{resource_id}/actions/{action}`
- `GET /audit/events`
- `GET /events/outbox`
- `POST /create`
- `GET /{id}`
- `PATCH /{id}`
- `DELETE /{id}`
- `GET /list`
- `POST /approve`
- `POST /reject`
- `POST /audit`


## Fluxo Jobs e procedencia

- `POST /resumes/{resume_id}/imports/ctps-digital` recebe PDF da CTPS Digital, registra hash imutavel e classifica itens extraidos como `validated_by_document_import`.
- Experiencias digitadas em `employment_records` sao sempre `self_declared_unverified`, inclusive trabalho informal e descricoes adicionais.
- `GET /vacancies` expõe vagas publicadas para candidatos.
- `GET /recruiting/resumes/{resume_id}` exige empresa ativa no All-in-One Business, papel de recrutador, escopo Jobs e registra cada visualizacao.
- O importador documental nao equivale a verificacao oficial externa; esse estado permanece exibido em `official_verification_status`.


        ## Eventos

        - `jobs.resume.created`
- `jobs.resume.ctps_imported`
- `jobs.employment.self_declared`
- `jobs.job_posting.created`
- `jobs.application.created`
- `jobs.resume.viewed`

        ## Regras

        - `user_id` e obrigatorio em todo recurso operacional e referencia `identity.users`.
        - Exclusao e logica; registros financeiros, de aprovacao e auditoria nao sao apagados.
        - Aprovacao e rejeicao exigem ator autenticado, justificativa e log imutavel.
        - A empresa ou profissional deve estar aprovado antes de uma operacao publica.

        ## Seguranca e permissoes

        Mutacoes dependem de OAuth2/JWT ou API key no gateway e do escopo do
        modulo. O runtime inicial representa o ator por `X-Actor-User-Id` e
        registra auditoria; o gateway deve validar a credencial antes do repasse.

        ## Monetizacao

        Plano Business de recrutamento e publicacao de vagas com acesso auditado a candidatos.

        ## Integracoes e erros

        Eventos sao entregues pelo barramento RabbitMQ. Respostas esperadas:
        `401` ator ausente, `404` recurso inexistente e `422` regra de validacao
        ou politica anti-burla violada.

        ## Auditoria

        `POST /audit` e todas as mutacoes geram evento destinado a `audit.logs`,
        que e append-only no PostgreSQL.
