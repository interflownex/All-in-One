# Catálogo de Bancos e Persistências

## PostgreSQL

Fonte física versionada com 31 schemas e 81 tabelas. Proprietários são inferidos pelo schema/módulo e precisam de confirmação. Backup, restore, retenção e estado de produção não são comprovados pelas migrations.

## Persistências adicionais

| Tecnologia | Uso encontrado | Situação |
| --- | --- | --- |
| MongoDB | memória IA, social, métricas e telemetria | parcial |
| Redis | cache e rate limit | parcial |
| SQLite | contrato local/fallback | parcial |
| Object storage | documentos privados e mídia | parcial |
| Browser storage | cache, demonstração e sessão | parcial |

EVIDÊNCIAS: `database/postgres/migrations/`, `database/mongodb/init/001_ai_social_telemetry.js`, `modules/shared/store.py`, `modules/api_hub/main.py`, `modules/shared/private_documents.py`.
