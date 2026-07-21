# `health.appointments`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:183 |
| user_id | UUID | False | False | identity.users.id | pessoal | database/postgres/migrations/004_enterprise_verticals.sql:184 |
| patient_id | UUID | False | False | health.patients.id | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:185 |
| professional_user_id | UUID | False | False | identity.users.id | pessoal | database/postgres/migrations/004_enterprise_verticals.sql:186 |
| scheduled_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:187 |
| telemedicine | BOOLEAN | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:188 |
| clinical_data_encrypted | TEXT | True | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:189 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:190 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:191 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:192 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:193 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:194 |
| created_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:195 |
| updated_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:196 |
| idempotency_key | VARCHAR(120) | True | False |  | não classificado automaticamente | database/postgres/migrations/012_platform_idempotency.sql:59 |
| offer_id | UUID | True | False | business.catalog_offers.id | não classificado automaticamente | database/postgres/migrations/020_valley_services_health_sprint3.sql:17 |
| company_id | UUID | True | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/020_valley_services_health_sprint3.sql:18 |
