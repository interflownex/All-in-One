# Auditoria, Logs e Rastreabilidade

O inventário encontrou 7 tabelas candidatas de auditoria/log/evento. O contrato possui 35 requisitos de alteração e leitura; 35 possuem ao menos um alias físico em alguma tabela candidata.

Os 35 requisitos possuem representação física no contrato unificado da migration 029. O writer único atende a base e os sete stores PostgreSQL especializados; o runtime captura contexto HTTP governado e audita leituras sensíveis. PostgreSQL vivo e homologação positiva e negativa por operação permanecem pendentes.

Logs técnicos, segurança, auditoria, negócio, métricas, traces e eventos de integração devem permanecer separados e correlacionados. Segredos e valores sensíveis não podem ser gravados em texto aberto.

EVIDÊNCIAS: `config/data_audit/audit_traceability_policy.json`, `artifacts/cobertura_auditoria.json`, `database/postgres/migrations/005_audit_events_api_security.sql`, `database/postgres/migrations/029_unified_immutable_audit.sql`, `modules/shared/audit_contract.py`, `modules/shared/`.
