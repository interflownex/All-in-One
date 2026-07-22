# Catálogo Lógico de Dados (Análise de Backend)

**Referência:** `docs/plano_de_leitura.md`, Ordem 3

Este documento detalha o modelo de dados lógico do ecossistema, inferido a partir da análise do código-fonte dos módulos de backend. Ele descreve as entidades de domínio, os DTOs (Data Transfer Objects), as regras de negócio e as operações (APIs) que atuam sobre eles.

---

## 1. Domínio: Identity

### 1.1 Entidades de Domínio

#### **User** (Entidade Principal)

- **Descrição:** Representa o usuário final do sistema, com sua identidade central e dados de segurança.
- **Campos Lógicos:**
  - `id` (UUID): Identificador único do usuário.
  - `email` (String): E-mail de login, único no sistema.
  - `password_hash` (String): Hash da senha do usuário. **(Campo sensível, nunca exposto)**.
  - `full_name` (String): Nome completo do usuário.
  - `cpf_document` (String): CPF do usuário, usado para unicidade.
  - `birth_date` (Date): Data de nascimento.
  - `phone_e164` (String): Telefone em formato E.164.
  - `status` (String): Status da conta (`pending_validation`, `active`, `blocked`).
  - `roles` (Array[String]): Lista de papéis de permissão associados ao usuário.
  - ... (e outros campos do `identity.users`).

#### **KYCRecord**

- **Descrição:** Armazena o estado de uma submissão de verificação de identidade (Know Your Customer).
- **Campos Lógicos:**
  - `record_id` (UUID): ID do registro de verificação.
  - `user_id` (UUID): ID do usuário associado.
  - `status` (String): Estado da verificação (`PROCESSING`, `APPROVED`, `REJECTED`).
  - `biometry_hash` (String): Hash do dado biométrico.
  - `risk_score` (Float): Pontuação de risco calculada.
  - `decision_reason` (String): Motivo da decisão (e.g., em caso de rejeição).

#### **Session**

- **Descrição:** Representa uma sessão de usuário ativa.
- **Campos Lógicos:**
  - `id` (UUID): ID da sessão.
  - `user_id` (UUID): ID do usuário dono da sessão.
  - `token_hash` (String): Hash do refresh token. **(Sensível)**.
  - `device_fingerprint` (String): Impressão digital do dispositivo cliente.
  - `ip_address` (String): Endereço IP de origem.
  - `expires_at` (DateTime): Data e hora de expiração.
  - `revoked_at` (DateTime): Data e hora de revogação.
  - `mfa_verified_at` (DateTime): Timestamp de quando o segundo fator foi verificado na sessão.

---

### 1.2 DTOs (Data Transfer Objects) e Operações

#### **POST /registrations**

- **Descrição:** Cria um novo usuário no sistema.
- **DTO de Entrada:** `dict` flexível contendo os campos da entidade `User`.
- **DTO de Saída:** Objeto `User` público (sem campos sensíveis como `password_hash`).
- **Regras de Negócio:**
  - A senha é hasheada usando `get_password_hash`.
  - Dispara o evento `identity.user.created`.

#### **POST /auth/login**

- **Descrição:** Autentica um usuário e retorna tokens de acesso.
- **DTO de Entrada:** `LoginRequest` (`email`, `password`).
- **DTO de Saída:** `TokenResponse` (`access_token`, `refresh_token`, `session_id`, etc.).
- **Regras de Negócio:**
  - Requer verificação de integridade via Google Play Integrity (`X-Play-Integrity-Token`).
  - Verifica a senha.
  - Cria uma nova entidade `Session` no banco.
  - Dispara o evento `identity.session.created`.

#### **POST /kyc/submit**

- **Descrição:** Inicia um processo de verificação de identidade.
- **DTO de Entrada:** `KYCSubmission` (`user_id`, `biometry_hash`, `doc_front_base64`, etc.).
- **DTO de Saída:** `dict` com o ID do registro e o status inicial.
- **Regras de Negócio:**
  - Cria uma nova entidade `KYCRecord` (via tabela `kyc_records`).
  - Dispara o evento `identity.kyc.submitted`.

#### **GET /kyc/status/{user_id}**

- **Descrição:** Consulta o status do último processo de KYC de um usuário.
- **DTO de Saída:** `KYCStatus`.

#### **POST /mfa/setup**

- **Descrição:** Inicia a configuração de um novo método de MFA para um usuário.
- **DTO de Entrada:** `MFASetup` (`user_id`, `method`).
- **DTO de Saída:** `dict` contendo o `secret` e `qr_code_url` para configuração no app autenticador.
- **Regras de Negócio:**
  - Apenas o próprio usuário pode configurar seu MFA.
  - Atualmente, apenas o método `totp` é suportado.
  - Cria um registro de verificação (`identity_verifications`) com o segredo criptografado.
  - Dispara o evento `identity.mfa.setup_started`.

#### **POST /mfa/verify**

- **Descrição:** Verifica um código MFA para validar um fator ou uma sessão.
- **DTO de Entrada:** `MFAVerification` (`user_id`, `session_id`, `code`).
- **DTO de Saída:** `dict` com o status e um novo `access_token` com a declaração de MFA verificado.
- **Regras de Negócio:**
  - O código TOTP é validado, prevenindo reuso.
  - A sessão do usuário é atualizada com o status de MFA verificado.
  - Dispara os eventos `identity.mfa.verified` e `identity.session.mfa_verified`.

---

_(Este catálogo será expandido com a análise dos demais módulos.)_

---

## 6. Domínio: Stock

... (e todos os outros 19 domínios) ...
---

## 25. Domínio: API Hub

### 25.1 Entidades de Domínio

#### **APIClient**

- **Descrição:** Cliente de API para acesso programático.
- **Regra Principal:** `RULE_OVERRIDES[("api_hub", "api_clients")]`
  - **Dados Sensíveis:** Sim.
  - **Campos Obrigatórios:** `client_name`, `scopes`.
  - **Máquina de Estados:** Segue o `review_flow`.

#### **APIKey**

- **Descrição:** Chave de API associada a um cliente.
- **Regra Principal:** `RULE_OVERRIDES[("api_hub", "api_keys")]`
  - **Dados Sensíveis:** Sim.
  - **Campos Obrigatórios:** `key_name`, `key_hash`, `key_hint`, `scopes`.
  - **Máquina de Estados:** Segue o `review_flow`.

---

## 4. Domínio: Finance

### 4.1 Entidades de Domínio

#### **Wallet**

- **Descrição:** Carteira digital do usuário, contendo saldos em BRL e NEX.
- **Regra Principal:** `RULE_OVERRIDES[("finance", "wallets")]`
  - **Dados Sensíveis:** Sim.
  - **Campos Obrigatórios:** `wallet_type`.
  - **Status Inicial:** `active`.

#### **LedgerEntry**

- **Descrição:** Registro imutável de uma transação no livro-razão de uma carteira.
- **Regra Principal:** `RULE_OVERRIDES[("finance", "ledger_entries")]`
  - **Dados Sensíveis:** Sim.
  - **Imutável:** Sim.
  - **Campos Obrigatórios:** `wallet_id`, `currency`, `idempotency_key`.
  - **Campos Monetários:** `amount_brl`, `amount_nex`.
  - **Status Inicial:** `posted`.

#### **Escrow**

- **Descrição:** Valor mantido em custódia aguardando a conclusão de uma transação.
- **Regra Principal:** `RULE_OVERRIDES[("finance", "escrows")]`
  - **Dados Sensíveis:** Sim.
  - **Campos Obrigatórios:** `wallet_id`, `beneficiary_user_id`, `amount_brl`.
  - **Campos Monetários:** `amount_brl`.
  - **Status Inicial:** `created`.
  - **Máquina de Estados:**
    - `created` -> `authorized` (requer `APPROVER_ROLES`)
    - `authorized` -> `held` (requer `APPROVER_ROLES`, dispara `payment.escrow.created`)
    - `held` -> `released` (requer `APPROVER_ROLES`, dispara `payment.escrow.released`)
    - `held` -> `disputed` (dispara `payment.escrow.disputed`)
    - `authorized`, `held`, `disputed` -> `refunded` (requer `APPROVER_ROLES`, dispara `payment.refunded`)

---

## 5. Domínio: Marketplace

### 5.1 Entidades de Domínio

#### **Store**

- **Descrição:** Loja de um vendedor no marketplace.
- **Regra Principal:** `RULE_OVERRIDES[("marketplace", "stores")]`
  - **Conteúdo Protegido:** Sim (contra spam e links externos).
  - **Campos Obrigatórios:** `company_id`, `company_status`, `name`.
  - **Status Inicial:** `pending_validation`.
  - **Máquina de Estados:** Segue o `review_flow` (draft -> pending -> approved/rejected).

#### **Product**

- **Descrição:** Produto vendido por uma loja no marketplace.
- **Regra Principal:** `RULE_OVERRIDES[("marketplace", "products")]`
  - **Conteúdo Protegido:** Sim.
  - **Campos Obrigatórios:** `store_id`, `sku`, `name`, `price_brl`, `stock_location_type`.
  - **Campo Único:** `sku`.
  - **Campos Monetários:** `price_brl`.
  - **Máquina de Estados:** Segue o `catalog_offer_flow` (ciclo de vida de publicação, incluindo `published` e `paused`).

#### **Order**

- **Descrição:** Pedido de compra realizado no marketplace.
- **Regra Principal:** `RULE_OVERRIDES[("marketplace", "orders")]`
  - **Conteúdo Protegido:** Sim.
  - **Campos Obrigatórios:** `total_brl`.
  - **Campos Monetários:** `total_brl`.
  - **Status Inicial:** `created`.
  - **Máquina de Estados:**
    - `created` -> `paid` (dispara `marketplace.order.paid`)
    - `paid`, `shipped` -> `delivered` (dispara `marketplace.order.delivered`)
    - `created`, `paid` -> `cancelled` (dispara `marketplace.order.cancelled`)

#### **Review**

- **Descrição:** Avaliação de um pedido.
- **Regra Principal:** `RULE_OVERRIDES[("marketplace", "reviews")]`
  - **Imutável:** Sim.
  - **Conteúdo Protegido:** Sim.
  - **Campos Obrigatórios:** `order_id`, `rating`.
  - **Status Inicial:** `pending_review`.
  - **Máquina de Estados:**
    - `pending_review` -> `published` (requer `APPROVER_ROLES`, dispara `valley.review.published`)
    - `pending_review` -> `rejected` (requer `APPROVER_ROLES`, dispara `valley.review.rejected`)

---

## 3. Domínio: Permissions

### 3.1 Entidades de Domínio

#### **Role**

- **Descrição:** Representa um papel que pode ser atribuído a um usuário, concedendo-lhe um conjunto de permissões. Pode ser um papel de sistema (fixo) ou um papel dinâmico (criado por um administrador de empresa).
- **Campos Lógicos:**
  - `id` (UUID): Identificador único do papel.
  - `name` (String): Nome único do papel (e.g., `administrator`, `auditor`).
  - `company_id` (UUID, Nulável): Escopo da empresa, se for um papel dinâmico.
  - `is_system` (Boolean): `True` se for um dos papéis definidos em `domain_rules.py`.

#### **AccessPolicy**

- **Descrição:** Define regras de acesso condicionais (ABAC - Attribute-Based Access Control) para um módulo.
- **Campos Lógicos:**
  - `module` (String): Módulo ao qual a política se aplica.
  - `expression` (JSONB): A expressão da política (detalhes a serem definidos).
  - `company_id` (UUID, Nulável): Escopo da empresa.

#### **ApprovalLimit**

- **Descrição:** Define limites financeiros para aprovações por usuário ou papel.
- **Campos Lógicos:**
  - `role_id` (UUID) ou `user_id` (UUID): A quem o limite se aplica.
  - `scope` (String): O escopo do limite (e.g., 'erp.payable').
  - `limit_brl` (Decimal): O valor monetário do limite.
  - `requires_dual_approval` (Boolean): Se requer uma segunda aprovação.

### 3.2 Regras de Negócio e Lógica de Domínio (de `domain_rules.py`)

- **Conjuntos de Papéis:** O sistema opera com conjuntos de papéis pré-definidos para ações críticas:
  - **`APPROVER_ROLES`**: `owner`, `legal_representative`, `administrator`, `compliance_officer`, `auditor`. Usados em transições de estado que requerem aprovação (e.g., `approve`, `reject`).
  - **`SENSITIVE_ROLES`**: `owner`, `administrator`, `compliance_officer`, `data_protection_officer`, `auditor`. Usados para controlar o acesso de leitura a dados sensíveis nos módulos `identity`, `finance`, `document` e `hr`.
  - **`MEDICAL_ROLES`**: `medical_admin`, `doctor`, `nurse`, `compliance_officer`. Concedem acesso a dados do módulo `health`.
  - **`RECRUITER_ROLES`**: `owner`, `administrator`, `hr_manager`, `recruiter`, `auditor`. Concedem acesso a dados do módulo `jobs`.

- **Gerenciamento de Estado (State Machine):** A lógica de transição de estado para a maioria das entidades do sistema é centralizada em `domain_rules.py`. A entidade `permissions.roles` possui um ciclo de vida simples (apenas criação com status `active`), mas as regras que ela governa são complexas e aplicadas em todas as outras entidades.

- **Operações:** O módulo `permissions` em si não expõe APIs complexas. Sua lógica é consumida por outros módulos para impor as regras de acesso. As operações principais são a verificação de pertencimento de um usuário a um dos conjuntos de papéis (`can_read_sensitive`) e a verificação de permissão para transições de estado.

---

## 2. Domínio: Business

### 2.1 Entidades de Domínio

#### **Company** (Entidade Principal)

- **Descrição:** Representa a entidade jurídica no ecossistema. O `catalogo_fisico_dados.md` confirma a existência da tabela `business.companies`.
- **Campos Lógicos (Chave):**
  - `id` (UUID): Identificador único da empresa.
  - `cnpj` (String): CNPJ único da empresa.
  - `legal_name` (String): Razão Social.
  - `status` (String): Status da empresa (`pending_validation`, `active`, etc.).

#### **CompanyModuleSetting** (Entidade Lógica)

- **Descrição:** Modela a configuração de um módulo específico (e.g., `finance`, `marketplace`) para uma determinada empresa. Esta entidade é gerenciada pela lógica em `module_settings.py` e, no momento, parece ser mantida em memória, embora destinada à persistência.
- **Campos Lógicos:**
  - `company_id` (UUID): A empresa à qual a configuração se aplica.
  - `module_slug` (String): O identificador do módulo (e.g., 'finance').
  - `state` (String): O estado do módulo para a empresa (`mandatory`, `active`, `recommended`, `hidden`, `disabled`).
  - `visibility` (String): Se o módulo está visível para os usuários da empresa.
  - `source` (String): Se a configuração foi `automatic` (via recomendação) ou `manual`.

#### **BusinessClassificationRecord** (Entidade Lógica)

- **Descrição:** Armazena o resultado da classificação de uma empresa em uma categoria de negócio, o que direciona a recomendação de módulos.
- **Campos Lógicos:**
  - `company_id` (UUID): A empresa classificada.
  - `business_kind` (String): O tipo de negócio (e.g., `physical_store`, `ecommerce`, `restaurant`).
  - `operational_tags` (Array[String]): Tags operacionais inferidas (e.g., `SELLS_ONLINE`, `HIRES_PEOPLE`).

---

### 2.2 DTOs (Data Transfer Objects) e Operações

#### **POST /business-modules/recommendations**

- **Descrição:** Retorna uma lista de módulos recomendados com base em um perfil de negócio.
- **DTO de Entrada:** `BusinessClassificationInput` (`businessKind`, `cnaePrimary`, etc.).
- **DTO de Saída:** `Array[ModuleRecommendation]`.
- **Regras de Negócio:**
  - Utiliza uma matriz de `PRESETS` para determinar os estados (`mandatory`, `active`, `recommended`) para cada `BusinessKind`.
  - Adiciona recomendações dinâmicas com base em tags operacionais (e.g., ativa `delivery` se `performsDelivery` for `true`).

#### **POST /business-modules/companies/{company_id}/apply-recommendations**

- **Descrição:** Aplica um conjunto de recomendações de módulos a uma empresa.
- **DTO de Entrada:** `ApplyRecommendationsPayload` (contém a `BusinessClassificationInput`).
- **DTO de Saída:** `ModuleSettingsResponse` (o estado completo dos módulos da empresa).
- **Regras de Negócio:**
  - Gera e armazena (em memória) a `BusinessClassificationRecord`.
  - Cria as entidades `CompanyModuleSetting` para todos os módulos aplicáveis com o estado `automatic`.
  - Registra um evento de auditoria (`business.module.recommendations_applied`).

#### **GET /business-modules/companies/{company_id}/modules**

- **Descrição:** Obtém as configurações atuais de todos os módulos para uma empresa.
- **DTO de Saída:** `ModuleSettingsResponse`.

#### **PATCH /business-modules/companies/{company_id}/modules/{module_slug}**

- **Descrição:** Permite a um administrador alterar manualmente o estado de um módulo para sua empresa.
- **DTO de Entrada:** `ModulePatch` (`state`, `reason`).
- **DTO de Saída:** `CompanyModuleSetting` (o estado atualizado do módulo).
- **Regras de Negócio:**
  - Impede que módulos obrigatórios (`identity`, `business`, `permissions`) sejam desativados ou ocultados.
  - Registra a alteração como de origem `manual`.
  - Registra um evento de auditoria (`business.module.configuration_updated`).
