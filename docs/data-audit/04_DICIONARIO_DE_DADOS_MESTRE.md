# Dicionário de Dados Mestre

O dicionário físico contém 1189 campos. Tipo, nulabilidade, padrão, PK, unique e FK são extraídos das migrations. Nome lógico, LGPD e mascaramento são triagem e requerem homologação.

Arquivos canônicos: `artifacts/dicionario_de_dados.csv` e `artifacts/dicionario_de_dados.json`.

EVIDÊNCIAS: `database/postgres/migrations/001_identity_and_schemas.sql`, `database/postgres/migrations/002_business_permissions_finance.sql`, `database/postgres/migrations/003_marketplace_delivery_services_mobility.sql`, `database/postgres/migrations/004_enterprise_verticals.sql`, `database/postgres/migrations/005_audit_events_api_security.sql` e demais migrations listadas no JSON.
