# Catálogo de Bancos e Persistências

## PostgreSQL

Fonte física versionada com 32 schemas e 164 tabelas. Proprietários são inferidos pelo schema/módulo e precisam de confirmação. Backup, restore, retenção e estado de produção não são comprovados pelas migrations.

## Persistências adicionais

| Tecnologia | Uso encontrado | Situação |
| --- | --- | --- |
| MongoDB | 4 coleções / 29 campos | inventário estático; runtime pendente |
| Redis | 1 padrão de chave com TTL | inventário estático; runtime pendente |
| SQLite | 4 tabelas / 39 campos | inventário estático; runtime pendente |
| Object storage | 4 stores/referências | inventário estático; buckets e restore pendentes |
| Browser storage | 12 chaves/famílias | inventário estático; comportamento E2E pendente |

EVIDÊNCIAS: `database/postgres/migrations/`, `database/mongodb/init/001_ai_social_telemetry.js`, `modules/shared/store.py`, `modules/api_hub/main.py`, `modules/shared/private_documents.py`.
