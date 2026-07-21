# Backlog de Implementação

| Ordem | ID | Responsável sugerido | Entrega | Dependências | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | AUD-P0-000 | plataforma e dados | MongoDB, SQLite, Redis, object storage e storage de navegador possuem catálogo, retenção, ownership, restore e testes aprovados. | credenciais dos ambientes, serviços acessíveis | parcial |
| 2 | AUD-P0-001 | DPO e compliance | Todos os campos possuem classificação, retenção, criptografia e mascaramento aprovados pelo proprietário do domínio. | DPO, proprietários de domínio | pendente_aprovacao |
| 3 | AUD-P1-002 | frontend e backend | Cada campo UI aponta para DTO, endpoint, validação e teste aprovados. | contratos DTO, rotas frontend | pendente |
| 4 | AUD-P1-003 | arquitetura de integração | Cada evento possui produtor, consumidor, schema, dados proibidos, idempotência, correlação, retenção e compatibilidade testados. | produtores, consumidores, mensageria | pendente |
| 5 | AUD-P1-004 | produto, arquitetura e engenharia | Metadados, API, homologação, segurança, publicação, cobrança, auditoria e testes estão implementados. | decisão arquitetural, modelo de cobrança | proposta |
| 6 | AUD-P1-005 | catálogo, estoque, ERP e fiscal | Unidades, conversões, perfis fiscais, vigência e cálculos possuem migrations, backend, frontend, integração e homologação aprovados. | especialista fiscal, ambiente PostgreSQL | implementacao_parcial |
| 7 | AUD-P1-006 | arquitetura e responsáveis de domínio | Cada entidade possui decisão explícita de persistência, ownership e coordenada UI, ou justificativa versionada de ausência. | proprietários dos 25 módulos | pendente_decisao |
| 8 | AUD-P1-007 | segurança, plataforma e compliance | Os 35 requisitos de auditoria têm implementação ou decisão justificada por operação, com integridade, retenção e testes aprovados. | segurança, compliance, proprietários de domínio | parcial |

A ordem prioriza P0, integridade contratual e funcionalidades P1. EVIDÊNCIAS: `14_REGISTRO_DE_LACUNAS.md`.
