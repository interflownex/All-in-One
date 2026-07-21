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
*(Este catálogo será expandido com a análise dos demais módulos.)*
