# `identity_core.audit_logs`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| log_id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:72 |
| actor_user_id | UUID | False | False |  | pseudônimo vinculável | database/postgres/migrations/009_identity_core_refinement.sql:73 |
| action_type | VARCHAR(100) | False | False |  | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:74 |
| target_table | VARCHAR(100) | False | False |  | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:75 |
| target_record_id | UUID | False | False |  | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:76 |
| old_payload | JSONB | True | False |  | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:77 |
| new_payload | JSONB | True | False |  | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:78 |
| ip_address | INET | True | False |  | dado pessoal | database/postgres/migrations/009_identity_core_refinement.sql:79 |
| created_at | TIMESTAMP WITH TIME ZONE | True | False |  | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:80 |
