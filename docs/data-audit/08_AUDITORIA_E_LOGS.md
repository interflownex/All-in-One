# Auditoria, Logs e Rastreabilidade

O inventário encontrou 7 tabelas candidatas de auditoria/log/evento. O contrato possui 35 requisitos de alteração e leitura; 35 possuem ao menos um alias físico em alguma tabela candidata.

Os 35 requisitos possuem representação física no contrato unificado da migration 029. Essa cobertura estrutural não prova adoção por cada operação ou dado sensível; stores especializados, contexto HTTP e enforcement por módulo permanecem lacunas até testes de integração.

Logs técnicos, segurança, auditoria, negócio, métricas, traces e eventos de integração devem permanecer separados e correlacionados. Segredos e valores sensíveis não podem ser gravados em texto aberto.

EVIDÊNCIAS: `config/data_audit/audit_traceability_policy.json`, `artifacts/cobertura_auditoria.json`, `database/postgres/migrations/005_audit_events_api_security.sql`, `database/postgres/migrations/029_unified_immutable_audit.sql`, `modules/shared/audit_contract.py`, `modules/shared/`.
