# Dicionário de Dados Mestre

O dicionário físico contém 1898 campos. O catálogo lógico contém 120 entidades, das quais 13 não possuem tabela física homônima e 0 não possuem superfície UI homônima. Tipo, nulabilidade, padrão, PK, unique e FK são extraídos das migrations; regras lógicas vêm de `MODULE_ENTITIES` e `RULE_OVERRIDES`. Nome lógico, LGPD e mascaramento são triagem e requerem homologação.

Arquivos canônicos: `artifacts/dicionario_de_dados.csv`, `artifacts/dicionario_de_dados.json`, `artifacts/catalogo_logico.csv` e `artifacts/catalogo_logico.json`.

EVIDÊNCIAS: `database/postgres/migrations/001_identity_and_schemas.sql`, `database/postgres/migrations/002_business_permissions_finance.sql`, `database/postgres/migrations/003_marketplace_delivery_services_mobility.sql`, `database/postgres/migrations/004_enterprise_verticals.sql`, `database/postgres/migrations/005_audit_events_api_security.sql`, `modules/shared/domain_rules.py` e demais migrations listadas no JSON.
