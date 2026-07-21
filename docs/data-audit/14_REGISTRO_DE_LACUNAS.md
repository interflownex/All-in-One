# Registro de Lacunas

| ID | Prioridade | Lacuna | Evidência | Aceite |
| --- | --- | --- | --- | --- |
| AUD-P0-000 | P0 | Persistências não PostgreSQL exigem catálogo de campo e validação em runtime | infra/docker/docker-compose.yml:69 | MongoDB, SQLite, Redis, object storage e storage de navegador possuem catálogo, retenção, ownership e testes aprovados. |
| AUD-P0-001 | P0 | Classificação LGPD exige revisão humana por campo | docs/data-audit/artifacts/dicionario_de_dados.csv | Todos os campos possuem classificação aprovada pelo proprietário do domínio. |
| AUD-P1-002 | P1 | Bindings frontend-backend não estão integralmente comprovados | docs/data-audit/artifacts/matriz_formulario_campo.csv | Cada campo UI aponta para DTO, endpoint, regra e teste. |
| AUD-P1-003 | P1 | Eventos não possuem catálogo de payload versionado | docs/data-audit/artifacts/matriz_evento_campo.csv | Cada evento possui produtor, consumidor, schema, idempotência e compatibilidade. |
| AUD-P1-004 | P1 | Construtor de formulários dinâmicos é proposta, não implementação | docs/MEMORANDO_MESTRE_GEMINI_VARREDURA_DADOS_FORMULARIOS_ALL_IN_ONE.md:1583 | Metadados, API, homologação, segurança e testes implementados. |
| AUD-P1-005 | P1 | Regras fiscais e conversões carecem de modelo completo | database/postgres/migrations/ | Perfis fiscais e conversões versionadas possuem migrations, backend e testes. |

EVIDÊNCIAS: `artifacts/relatorio_divergencias.json`.
