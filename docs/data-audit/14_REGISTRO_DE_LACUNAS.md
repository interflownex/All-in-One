# Registro de Lacunas

| ID | Prioridade | Módulo | Lacuna | Risco | Status | Aceite |
| --- | --- | --- | --- | --- | --- | --- |
| AUD-P0-000 | P0 | infraestrutura | Persistências não PostgreSQL exigem catálogo e validação operacional | Perda, exposição ou inconsistência de dados fora do PostgreSQL. | parcial | MongoDB, SQLite, Redis, object storage e storage de navegador possuem catálogo, retenção, ownership, restore e testes aprovados. |
| AUD-P0-001 | P0 | compliance | Classificação LGPD exige revisão humana por campo | Tratamento indevido de dados pessoais e sensíveis. | pendente_aprovacao | Todos os campos possuem classificação, retenção, criptografia e mascaramento aprovados pelo proprietário do domínio. |
| AUD-P1-002 | P1 | frontend e APIs | Bindings frontend-backend não estão integralmente comprovados | Perda de dados, validação incompleta e contratos divergentes. | pendente | Cada campo UI aponta para DTO, endpoint, validação e teste aprovados. |
| AUD-P1-003 | P1 | eventos | Eventos não possuem catálogo integral de payload versionado | Inconsistência assíncrona e duplicidade de processamento. | pendente | Cada evento possui produtor, consumidor, schema, dados proibidos, idempotência, correlação, retenção e compatibilidade testados. |
| AUD-P1-004 | P1 | formulários dinâmicos | Construtor de formulários dinâmicos é proposta, não implementação | Implementação ad hoc e exposição de tabelas físicas. | proposta | Metadados, API, homologação, segurança, publicação, cobrança, auditoria e testes estão implementados. |
| AUD-P1-005 | P1 | catálogo e fiscal | Regras fiscais, unidades e conversões carecem de implementação completa | Cálculo financeiro ou fiscal não homologado. | implementacao_parcial | Unidades, conversões, perfis fiscais, vigência e cálculos possuem migrations, backend, frontend, integração e homologação aprovados. |
| AUD-P1-006 | P1 | arquitetura modular | Entidades lógicas não possuem persistência ou superfície UI correspondente | Duplicação, persistência implícita ou funcionalidade inacessível. | pendente_decisao | Cada entidade possui decisão explícita de persistência, ownership e coordenada UI, ou justificativa versionada de ausência. |
| AUD-P1-007 | P1 | auditoria e segurança | Trilhas de auditoria não cobrem todos os atributos mandatórios | Não repúdio insuficiente, investigação incompleta e descumprimento de auditoria/LGPD. | parcial | Os 35 requisitos de auditoria têm implementação ou decisão justificada por operação, com integridade, retenção e testes aprovados. |

EVIDÊNCIAS: `artifacts/relatorio_divergencias.json`.
