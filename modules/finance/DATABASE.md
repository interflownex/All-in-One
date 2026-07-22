        # Database: Finance Pay Billing Fiscal

        Schema relacional principal: `finance`.

        ## Entidades planejadas

        - `finance.wallets`

- `finance.ledger_entries`
- `finance.escrows`
- `finance.splits`
- `finance.invoices`
- `finance.valley_gold_ledger_entries`

        Todo registro operacional inclui UUID, `user_id`, status, timestamps,
        atores de criacao/atualizacao e `metadata JSONB`. A implementacao inicial
        esta nas migracoes em `database/postgres/migrations/`; novas tabelas
        preservam a FK para `identity.users(id)`.
        `finance.valley_gold_ledger_entries` e append-only e lastreia compras e
        usos de Gold Valley sem automatizar a concessao de Pepitas.
