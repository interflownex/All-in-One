        # Database: Jobs

        Schema relacional principal: `jobs`.

        ## Entidades planejadas

        - `jobs.resumes`
- `jobs.employment_records`
- `jobs.resume_documents`
- `jobs.job_postings`
- `jobs.applications`
- `jobs.resume_access_logs`

        Todo registro operacional inclui UUID, `user_id`, status, timestamps,
        atores de criacao/atualizacao e `metadata JSONB`. A implementacao inicial
        esta nas migracoes em `database/postgres/migrations/`; novas tabelas
        preservam a FK para `identity.users(id)`.
