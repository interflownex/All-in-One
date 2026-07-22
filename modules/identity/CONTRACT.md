        # Contrato: Identity

        ## Descricao

        All-in-One ID, KYC, KYB, biometria, MFA, sessoes e consentimentos.

        ## Entidades

        - `users`

- `documents`
- `biometrics`
- `sessions`
- `identity_verifications`
- `consent_records`

        ## APIs

        - `GET /health`

- `GET /version`
- `GET /status`
- `GET /metrics`
- `GET /catalog`
- `POST /resources/{resource_type}`
- `GET /resources/{resource_type}`
- `GET /resources/{resource_type}/{resource_id}`
- `PATCH /resources/{resource_type}/{resource_id}`
- `DELETE /resources/{resource_type}/{resource_id}`
- `POST /resources/{resource_type}/{resource_id}/actions/{action}`
- `GET /audit/events`
- `GET /events/outbox`
- `POST /create`
- `GET /{id}`
- `PATCH /{id}`
- `DELETE /{id}`
- `GET /list`
- `POST /approve`
- `POST /reject`
- `POST /audit`

- `POST /registrations` cria o All-in-One ID inicial sem ator preexistente e preserva controles de duplicidade.
- `POST /auth/login` emite access token de curta duracao e refresh token opaco associado ao dispositivo.
- `POST /auth/refresh` rotaciona obrigatoriamente a sessao e rejeita replay, expiracao ou troca de dispositivo.
- `POST /auth/logout` revoga a sessao no servidor; apenas o hash SHA-256 do refresh token e persistido.
- `POST /mfa/setup` cria fator TOTP do proprio titular com segredo aleatorio cifrado em AES-GCM e validade de dez minutos.
- `POST /mfa/verify` rejeita replay e emite novo access token com a claim `mfa_verified=true` vinculada a sessao ativa.
- Cadastro, login, refresh e logout exigem `X-Play-Integrity-Token` em producao. O token e decodificado pelo Google com ADC e vinculado ao corpo exato por `requestHash`; pacote, certificado Play App Signing, frescor, licenca, integridade do app/dispositivo e risco de captura/controle sao validados antes da operacao.

        ## Eventos

        - `identity.user.created`

- `identity.user.verified`
- `identity.user.duplicate_detected`
- `identity.document.created`
- `identity.document.approved`
- `identity.document.rejected`
- `identity.biometric.captured`
- `identity.session.created`
- `identity.session.revoked`
- `identity.session.mfa_verified`
- `identity.kyc.submitted`
- `identity.kyc.approved`
- `identity.kyc.rejected`
- `identity.mfa.setup_started`
- `identity.mfa.verified`
- `identity.mfa.setup_expired`
- `identity.consent.recorded`

        ## Regras

        - `user_id` e obrigatorio em todo recurso operacional e referencia `identity.users`.
        - Exclusao e logica; registros financeiros, de aprovacao e auditoria nao sao apagados.
        - Aprovacao e rejeicao exigem ator autenticado, justificativa e log imutavel.
        - A empresa ou profissional deve estar aprovado antes de uma operacao publica.

        ## Seguranca e permissoes

        Mutacoes dependem de OAuth2/JWT ou API key no gateway e do escopo do
        modulo. O runtime inicial representa o ator por `X-Actor-User-Id` e
        registra auditoria; o gateway deve validar a credencial antes do repasse.

        ## Monetizacao

        Sem cobranca direta; habilita todas as receitas com identidade confiavel.

        ## Integracoes e erros

        Eventos sao entregues pelo barramento RabbitMQ. Respostas esperadas:
        `401` ator ausente, `403` veredito Play Integrity rejeitado, `404` recurso inexistente, `503` validador externo indisponivel e `422` regra de validacao
        ou politica anti-burla violada.

        ## Auditoria

        `POST /audit` e todas as mutacoes geram evento destinado a `audit.logs`,
        que e append-only no PostgreSQL.
