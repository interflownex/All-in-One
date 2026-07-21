# Catálogo Físico de Dados - PostgreSQL

Este documento representa o catálogo de dados físico, derivado diretamente da análise dos arquivos de migração SQL em `database/postgres/migrations/`.

## Análise do Arquivo: `001_identity_and_schemas.sql`

### Schemas Criados

O arquivo inicializa os seguintes schemas, que correspondem aos módulos de negócio do sistema:
- `identity`, `business`, `permissions`, `marketplace`, `stock`, `delivery`, `services`, `mobility`, `erp`, `wms`, `tms`, `crm`, `bpm`, `document`, `finance`, `billing`, `fiscal`, `hr`, `health`, `vision`, `legal`, `property`, `audit`, `compliance`, `notifications`, `api_hub`, `insurance`, `bi`, `ai_core`.

### Tabela: `identity.users`

| Coluna | Tipo | Constraints | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY`, `DEFAULT gen_random_uuid()` | Identificador único do usuário. |
| `all_in_one_id` | `UUID` | `NOT NULL`, `UNIQUE`, `DEFAULT gen_random_uuid()`| ID universal do usuário no ecossistema. |
| `full_name` | `VARCHAR(200)`| `NOT NULL` | Nome completo do usuário. |
| `cpf_document` | `VARCHAR(32)` | `NOT NULL`, `UNIQUE`, `CHECK (cpf_document ~ '...')` | CPF ou outro documento, com formato validado. |
| `birth_date` | `DATE` | `NOT NULL` | Data de nascimento. |
| `email` | `CITEXT` | `NOT NULL`, `UNIQUE` | E-mail (case-insensitive). |
| `phone_e164` | `VARCHAR(20)`| `NOT NULL`, `UNIQUE`, `CHECK (phone_e164 ~ '...')` | Telefone em formato E.164. |
| `password_hash` | `TEXT` | `NOT NULL` | Hash da senha. |
| `face_hash` | `TEXT` | `NOT NULL`, `UNIQUE` | Hash da biometria facial. |
| `liveness_score`| `NUMERIC(5, 4)`| `NOT NULL`, `CHECK (BETWEEN 0 AND 1)` | Pontuação da prova de vida. |
| `document_status`| `VARCHAR(40)` | `NOT NULL`, `DEFAULT 'pending_validation'` | Status da validação dos documentos. |
| `kyc_status` | `VARCHAR(40)` | `NOT NULL`, `DEFAULT 'pending_validation'` | Status do processo de KYC. |
| `mfa_required` | `BOOLEAN` | `NOT NULL`, `DEFAULT TRUE` | Flag que exige autenticação multifator. |
| `terms_accepted_at`| `TIMESTAMPTZ`| `NOT NULL` | Timestamp do aceite dos termos. |
| `lgpd_consent_at`| `TIMESTAMPTZ`| `NOT NULL` | Timestamp do consentimento LGPD. |
| `default_wallet_id`| `UUID` | (FK em migration futura) | ID da carteira padrão. |
| `primary_led_card_id`| `UUID` | (FK em migration futura) | ID do cartão LED primário. |
| `status` | `VARCHAR(40)` | `NOT NULL`, `DEFAULT 'pending_validation'` | Status geral do registro do usuário. |
| `metadata` | `JSONB` | `NOT NULL`, `DEFAULT '{}'`, `CHECK (jsonb_typeof = 'object')` | Metadados flexíveis. |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL`, `DEFAULT NOW()` | Timestamp de criação. |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL`, `DEFAULT NOW()` | Timestamp da última atualização. |
| `deleted_at` | `TIMESTAMPTZ` | - | Timestamp de exclusão lógica. |
| `created_by` | `UUID` | - | Usuário que criou o registro. |
| `updated_by` | `UUID` | - | Usuário que atualizou o registro. |

### Tabela: `identity.documents`

| Coluna | Tipo | Constraints | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY`, `DEFAULT gen_random_uuid()` | ID do documento. |
| `user_id` | `UUID` | `NOT NULL`, `REFERENCES identity.users(id)` | FK para o usuário proprietário. |
| `document_type` | `VARCHAR(60)`| `NOT NULL` | Tipo do documento (ex: RG, CNH). |
| `document_number_hash`| `TEXT` | `NOT NULL` | Hash do número do documento. |
| `storage_key` | `TEXT` | `NOT NULL` | Chave de acesso no storage privado. |
| `expires_at` | `DATE` | - | Data de expiração do documento. |
| `verification_status`| `VARCHAR(40)`| `NOT NULL`, `DEFAULT 'pending_review'` | Status da verificação do documento. |
| `status` | `VARCHAR(40)` | `NOT NULL`, `DEFAULT 'active'` | Status do registro do documento. |
| `metadata` | `JSONB` | `NOT NULL`, `DEFAULT '{}'` | Metadados. |
| `created_at` | `TIMESTAMPTZ` | `NOT NULL`, `DEFAULT NOW()` | Timestamp de criação. |
| `updated_at` | `TIMESTAMPTZ` | `NOT NULL`, `DEFAULT NOW()` | Timestamp da última atualização. |
| `deleted_at` | `TIMESTAMPTZ` | - | Timestamp de exclusão lógica. |
| `created_by` | `UUID` | `REFERENCES identity.users(id)` | Usuário que criou. |
| `updated_by` | `UUID` | `REFERENCES identity.users(id)` | Usuário que atualizou. |
| *Constraint* | `UNIQUE` | `(user_id, document_type, document_number_hash)` | Garante unicidade do documento por tipo para um usuário. |

### Tabela: `identity.biometrics`

| Coluna | Tipo | Constraints | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY`, `DEFAULT gen_random_uuid()` | ID do registro biométrico. |
| `user_id` | `UUID` | `NOT NULL`, `UNIQUE`, `REFERENCES identity.users(id)` | FK para o usuário. |
| `face_hash` | `TEXT` | `NOT NULL`, `UNIQUE` | Hash da biometria facial. |
| `provider_reference`| `TEXT` | - | ID de referência no provedor de biometria. |
| `last_liveness_score`| `NUMERIC(5, 4)`| `CHECK (BETWEEN 0 AND 1)` | Última pontuação da prova de vida. |
| `consent_recorded_at`| `TIMESTAMPTZ`| `NOT NULL` | Timestamp do consentimento para uso da biometria. |
| `status` | `VARCHAR(40)` | `NOT NULL`, `DEFAULT 'pending_validation'` | Status da validação biométrica. |
| `metadata` | `JSONB` | `NOT NULL`, `DEFAULT '{}'` | Metadados. |
| ... | ... | ... | (Campos de auditoria omitidos por brevidade) |

---
*Este é um documento inicial. As demais tabelas deste arquivo e dos arquivos de migração subsequentes serão adicionadas progressivamente.*

---

## Análise do Arquivo: `002_business_permissions_finance.sql`

### Tabela: `business.companies`

| Coluna | Tipo | Constraints | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY`, `DEFAULT gen_random_uuid()` | ID da empresa. |
| `user_id` | `UUID` | `NOT NULL`, `REFERENCES identity.users(id)` | FK para o usuário proprietário/criador. |
| `parent_company_id`| `UUID` | `REFERENCES business.companies(id)` | FK para a empresa controladora (matriz). |
| `cnpj` | `VARCHAR(18)` | `NOT NULL`, `UNIQUE` | CNPJ da empresa. |
| `root_cnpj` | `VARCHAR(18)` | `NOT NULL` | CNPJ raiz (8 primeiros dígitos). |
| `legal_name` | `VARCHAR(240)`| `NOT NULL` | Razão Social. |
| `trade_name` | `VARCHAR(240)`| - | Nome Fantasia. |
| `status` | `VARCHAR(40)` | `NOT NULL`, `DEFAULT 'pending_validation'`, `CHECK (...)` | Status do cadastro da empresa (draft, approved, etc.). |
| `...` | `...` | `...` | (Campos de auditoria e outros omitidos por brevidade) |

### Tabela: `business.user_company_memberships`

| Coluna | Tipo | Constraints | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY`, `DEFAULT gen_random_uuid()` | ID da associação. |
| `user_id` | `UUID` | `NOT NULL`, `REFERENCES identity.users(id)` | FK para o usuário membro. |
| `company_id`| `UUID` | `NOT NULL`, `REFERENCES business.companies(id)`| FK para a empresa. |
| `status` | `VARCHAR(40)` | `NOT NULL`, `DEFAULT 'pending_invitation'` | Status do membro (convidado, ativo, etc.). |
| *Constraint* | `UNIQUE` | `(user_id, company_id)` | Garante que um usuário só pode ser membro de uma empresa uma vez. |
| `...` | `...` | `...` | (Campos de auditoria e outros omitidos por brevidade) |

### Tabela: `permissions.roles`

| Coluna | Tipo | Constraints | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY`, `DEFAULT gen_random_uuid()` | ID do papel. |
| `company_id`| `UUID` | `REFERENCES business.companies(id)` | Escopo da empresa (se não for um papel de sistema). |
| `name` | `VARCHAR(80)` | `NOT NULL` | Nome do papel (ex: administrator, viewer). |
| `is_system` | `BOOLEAN` | `NOT NULL`, `DEFAULT FALSE` | Flag que indica se é um papel protegido pelo sistema. |
| `status` | `VARCHAR(40)` | `NOT NULL`, `DEFAULT 'active'` | Status do papel. |
| `...` | `...` | `...` | (Campos de auditoria omitidos por brevidade) |

### Tabela: `permissions.user_roles`

| Coluna | Tipo | Constraints | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY`, `DEFAULT gen_random_uuid()` | ID da atribuição. |
| `user_id` | `UUID` | `NOT NULL`, `REFERENCES identity.users(id)` | FK para o usuário. |
| `role_id` | `UUID` | `NOT NULL`, `REFERENCES permissions.roles(id)` | FK para o papel atribuído. |
| `company_id`| `UUID` | `REFERENCES business.companies(id)` | Escopo da atribuição. |
| `status` | `VARCHAR(40)` | `NOT NULL`, `DEFAULT 'active'` | Status da atribuição. |
| `...` | `...` | `...` | (Campos de auditoria omitidos por brevidade) |

### Tabela: `finance.wallets`

| Coluna | Tipo | Constraints | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY`, `DEFAULT gen_random_uuid()` | ID da carteira. |
| `user_id` | `UUID` | `NOT NULL`, `REFERENCES identity.users(id)` | FK para o usuário dono da carteira. |
| `wallet_type` | `VARCHAR(30)` | `NOT NULL`, `DEFAULT 'personal'` | Tipo da carteira (pessoal, empresarial). |
| `brl_available`| `NUMERIC(18,4)`| `NOT NULL`, `DEFAULT 0`, `CHECK (>= 0)` | Saldo disponível em BRL. |
| `brl_held` | `NUMERIC(18,4)`| `NOT NULL`, `DEFAULT 0`, `CHECK (>= 0)` | Saldo em BRL retido (em escrow). |
| `status` | `VARCHAR(40)` | `NOT NULL`, `DEFAULT 'active'` | Status da carteira. |
| *Constraint* | `UNIQUE` | `(id, user_id)` | Chave para referência segura em FKs. |
| `...` | `...` | `...` | (Campos de auditoria e outros omitidos por brevidade) |

### Tabela: `finance.ledger_entries`

| Coluna | Tipo | Constraints | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY`, `DEFAULT gen_random_uuid()` | ID do lançamento contábil. |
| `wallet_id` | `UUID` | `NOT NULL` | FK para a carteira. |
| `currency` | `VARCHAR(10)` | `NOT NULL`, `CHECK (IN ('BRL', 'NEX'))` | Moeda da transação. |
| `amount_brl`| `NUMERIC(18,4)`| `...` | Valor em BRL. |
| `entry_type`| `VARCHAR(40)` | `NOT NULL` | Tipo do lançamento (crédito, débito, etc.). |
| `idempotency_key`| `TEXT` | `NOT NULL`, `UNIQUE` | Chave para previnir duplicidade. |
| `status` | `VARCHAR(40)` | `NOT NULL`, `DEFAULT 'posted'` | Status do lançamento. |
| *Constraint* | `FOREIGN KEY` | `(wallet_id, user_id) REFERENCES finance.wallets(id, user_id)`| Garante consistência do dono da carteira. |
| `...` | `...` | `...` | (Campos de auditoria omitidos por brevidade) |

---

## Análise do Arquivo: `003_marketplace_delivery_services_mobility.sql`

### Tabela: `delivery.rider_profiles`

| Coluna | Tipo | Constraints | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY`, `DEFAULT gen_random_uuid()` | ID do perfil do entregador. |
| `user_id` | `UUID` | `NOT NULL`, `UNIQUE`, `REFERENCES identity.users(id)` | FK para o usuário. |
| `wallet_id`| `UUID` | `NOT NULL`, `FK REFERENCES finance.wallets(id, user_id)`| FK para a carteira do entregador. |
| `cnh_number_hash`| `TEXT` | - | Hash do número da CNH. |
| `status` | `VARCHAR(40)` | `NOT NULL`, `DEFAULT 'pending_documents'` | Status do cadastro do entregador. |
| `...` | `...` | `...` | (Campos de auditoria omitidos por brevidade) |

### Tabela: `marketplace.stores`

| Coluna | Tipo | Constraints | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY`, `DEFAULT gen_random_uuid()` | ID da loja. |
| `company_id`| `UUID` | `NOT NULL`, `REFERENCES business.companies(id)` | FK para a empresa dona da loja. |
| `name` | `VARCHAR(200)`| `NOT NULL` | Nome da loja. |
| `status` | `VARCHAR(40)` | `NOT NULL`, `DEFAULT 'pending_validation'` | Status da loja. |
| `...` | `...` | `...` | (Campos de auditoria omitidos por brevidade) |

### Tabela: `marketplace.products`

| Coluna | Tipo | Constraints | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY`, `DEFAULT gen_random_uuid()` | ID do produto. |
| `store_id` | `UUID` | `NOT NULL`, `REFERENCES marketplace.stores(id)` | FK para a loja. |
| `sku` | `VARCHAR(100)`| `NOT NULL` | Stock Keeping Unit. |
| `name` | `VARCHAR(240)`| `NOT NULL` | Nome do produto. |
| `price_brl`| `NUMERIC(18,4)`| `NOT NULL`, `CHECK (>= 0)` | Preço em BRL. |
| `stock_quantity`| `NUMERIC(18,4)`| `NOT NULL`, `DEFAULT 0` | Quantidade em estoque. |
| `status` | `VARCHAR(40)` | `NOT NULL`, `DEFAULT 'draft'` | Status do produto (rascunho, publicado, etc.). |
| *Constraint* | `UNIQUE` | `(store_id, sku)` | Garante unicidade do SKU por loja. |
| `...` | `...` | `...` | (Campos de auditoria omitidos por brevidade) |

### Tabela: `marketplace.orders`

| Coluna | Tipo | Constraints | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY`, `DEFAULT gen_random_uuid()` | ID do pedido. |
| `user_id` | `UUID` | `NOT NULL`, `REFERENCES identity.users(id)` | FK para o usuário cliente. |
| `store_id` | `UUID` | `NOT NULL`, `REFERENCES marketplace.stores(id)` | FK para a loja. |
| `escrow_id` | `UUID` | `REFERENCES finance.escrows(id)` | FK para a transação de escrow. |
| `total_brl`| `NUMERIC(18,4)`| `NOT NULL`, `CHECK (>= 0)` | Valor total do pedido em BRL. |
| `status` | `VARCHAR(40)` | `NOT NULL`, `DEFAULT 'created'` | Status do pedido (criado, pago, entregue, etc.). |
| `...` | `...` | `...` | (Campos de auditoria omitidos por brevidade) |

### Tabela: `services.providers`

| Coluna | Tipo | Constraints | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY`, `DEFAULT gen_random_uuid()` | ID do prestador de serviço. |
| `user_id` | `UUID` | `NOT NULL`, `UNIQUE`, `REFERENCES identity.users(id)` | FK para o usuário. |
| `category` | `VARCHAR(100)`| `NOT NULL` | Categoria do serviço prestado. |
| `status` | `VARCHAR(40)` | `NOT NULL`, `DEFAULT 'pending_review'` | Status do cadastro do prestador. |
| `...` | `...` | `...` | (Campos de auditoria omitidos por brevidade) |

### Tabela: `mobility.rides`

| Coluna | Tipo | Constraints | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PRIMARY KEY`, `DEFAULT gen_random_uuid()` | ID da corrida. |
| `user_id` | `UUID` | `NOT NULL`, `REFERENCES identity.users(id)` | FK para o usuário passageiro. |
| `driver_user_id`| `UUID` | `REFERENCES identity.users(id)` | FK para o usuário motorista. |
| `escrow_id` | `UUID` | `REFERENCES finance.escrows(id)` | FK para a transação de escrow. |
| `origin` | `JSONB` | `NOT NULL` | Dados de geolocalização da origem. |
| `destination`| `JSONB` | `NOT NULL` | Dados de geolocalização do destino. |
| `fare_brl` | `NUMERIC(18,4)`| `CHECK (>= 0)` | Valor da corrida em BRL. |
| `status` | `VARCHAR(40)` | `NOT NULL`, `DEFAULT 'requested'` | Status da corrida (solicitada, aceita, etc.). |
| `...` | `...` | `...` | (Campos de auditoria omitidos por brevidade) |

---

## Análise do Arquivo: `004_enterprise_verticals.sql`

### Tabela: `erp.fiscal_documents`
| Coluna | Tipo | Constraints | Descrição |
|:---|:---|:---|:---|
| `id` | `UUID` | `PRIMARY KEY`, `DEFAULT gen_random_uuid()` | ID do documento fiscal. |
| `company_id`| `UUID` | `NOT NULL`, `REFERENCES business.companies(id)` | FK para a empresa. |
| `document_type`| `VARCHAR(20)` | `NOT NULL` | Tipo (NFe, CTe, etc.). |
| `amount_brl`| `NUMERIC(18,4)`| `NOT NULL`, `DEFAULT 0` | Valor do documento. |
| `...` | `...` | `...` | (Campos omitidos por brevidade) |

### Tabela: `wms.warehouses`
| Coluna | Tipo | Constraints | Descrição |
|:---|:---|:---|:---|
| `id` | `UUID` | `PRIMARY KEY`, `DEFAULT gen_random_uuid()` | ID do armazém. |
| `company_id`| `UUID` | `NOT NULL`, `REFERENCES business.companies(id)` | FK para a empresa. |
| `name` | `VARCHAR(160)`| `NOT NULL` | Nome do armazém. |
| `...` | `...` | `...` | (Campos omitidos por brevidade) |

### Tabela: `hr.employees`
| Coluna | Tipo | Constraints | Descrição |
|:---|:---|:---|:---|
| `id` | `UUID` | `PRIMARY KEY`, `DEFAULT gen_random_uuid()` | ID do funcionário. |
| `user_id` | `UUID` | `NOT NULL`, `REFERENCES identity.users(id)` | FK para o usuário. |
| `company_id`| `UUID` | `NOT NULL`, `REFERENCES business.companies(id)` | FK para a empresa. |
| `employment_type`| `VARCHAR(40)` | `NOT NULL` | Tipo de contrato (CLT, PJ). |
| `...` | `...` | `...` | (Campos omitidos por brevidade) |

### Tabela: `health.patients`
| Coluna | Tipo | Constraints | Descrição |
|:---|:---|:---|:---|
| `id` | `UUID` | `PRIMARY KEY`, `DEFAULT gen_random_uuid()` | ID do paciente. |
| `user_id` | `UUID` | `NOT NULL`, `UNIQUE`, `REFERENCES identity.users(id)`| FK para o usuário. |
| `health_identifier`| `VARCHAR(80)`| `UNIQUE` | Identificador de saúde único. |
| `...` | `...` | `...` | (Campos omitidos por brevidade) |

### Tabela: `notifications.messages`
| Coluna | Tipo | Constraints | Descrição |
|:---|:---|:---|:---|
| `id` | `UUID` | `PRIMARY KEY`, `DEFAULT gen_random_uuid()` | ID da mensagem. |
| `user_id` | `UUID` | `NOT NULL`, `REFERENCES identity.users(id)` | FK para o usuário destinatário. |
| `channel` | `VARCHAR(30)` | `NOT NULL` | Canal de envio (email, push, sms). |
| `template_key`| `VARCHAR(100)`| `NOT NULL` | Chave do template usado. |
| `status` | `VARCHAR(40)` | `NOT NULL`, `DEFAULT 'queued'` | Status do envio. |
| `...` | `...` | `...` | (Campos omitidos por brevidade) |
