# Backlog de Implementação

| Ordem | ID | Entrega | Dependência | Status |
| --- | --- | --- | --- | --- |
| 1 | AUD-P0-000 | MongoDB, SQLite, Redis, object storage e storage de navegador possuem catálogo, retenção, ownership e testes aprovados. | infra/docker/docker-compose.yml:69 | pendente |
| 2 | AUD-P0-001 | Todos os campos possuem classificação aprovada pelo proprietário do domínio. | docs/data-audit/artifacts/dicionario_de_dados.csv | pendente |
| 3 | AUD-P1-002 | Cada campo UI aponta para DTO, endpoint, regra e teste. | docs/data-audit/artifacts/matriz_formulario_campo.csv | pendente |
| 4 | AUD-P1-003 | Cada evento possui produtor, consumidor, schema, idempotência e compatibilidade. | docs/data-audit/artifacts/matriz_evento_campo.csv | pendente |
| 5 | AUD-P1-004 | Metadados, API, homologação, segurança e testes implementados. | docs/MEMORANDO_MESTRE_GEMINI_VARREDURA_DADOS_FORMULARIOS_ALL_IN_ONE.md:1583 | pendente |
| 6 | AUD-P1-005 | Perfis fiscais e conversões versionadas possuem migrations, backend e testes. | database/postgres/migrations/ | pendente |
| 7 | AUD-P1-006 | Cada entidade tem decisão explícita de persistência e coordenada UI, ou justificativa de ausência. | docs/data-audit/artifacts/catalogo_logico.csv | pendente |

A ordem prioriza P0, integridade contratual e funcionalidades P1. EVIDÊNCIAS: `14_REGISTRO_DE_LACUNAS.md`.
