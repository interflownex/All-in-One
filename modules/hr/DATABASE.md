        # Database: HR HCM ATS LMS

        Schema relacional principal: `hr`.

        ## Entidades planejadas

        - `hr.employees`
- `hr.payroll_runs`
- `hr.candidates`
- `hr.courses`
- `hr.occupational_records`

        Todo registro operacional inclui UUID, `user_id`, status, timestamps,
        atores de criacao/atualizacao e `metadata JSONB`. A implementacao inicial
        esta nas migracoes em `database/postgres/migrations/`; novas tabelas
        preservam a FK para `identity.users(id)`.
