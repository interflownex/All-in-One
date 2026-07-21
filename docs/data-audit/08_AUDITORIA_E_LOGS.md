# Auditoria, Logs e Rastreabilidade

O schema `audit` e eventos versionados são a base encontrada. A validação deve separar auditoria de alteração, leitura sensível, segurança, negócio, métrica e trace, sem gravar segredos. A cobertura permanece parcial até provar retenção, imutabilidade e correlação em todos os módulos.

EVIDÊNCIAS: `database/postgres/migrations/005_audit_events_api_security.sql`, `modules/shared/`.
