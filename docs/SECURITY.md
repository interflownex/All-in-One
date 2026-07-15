# Seguranca E Compliance

## Controles implementados no baseline

- Identidade unica por CPF/documento, e-mail, telefone e hash facial.
- MFA requerido no modelo de identidade e aprovacao manual para KYC/KYB/Rider.
- FK de proprietario para wallet, LED/NFC, ledger, rider e escrow.
- Logs e ledger append-only via trigger SQL.
- Runtime de modulos exige ator para mutacoes, valida assinatura do gateway em
  producao e audita create/update/delete/transicoes.
- Bloqueio inicial de telefone, e-mail, rede social, Pix e URL em conteudo de
  Marketplace, Delivery, Services e Mobility.
- MongoDB com retencao TTL para memoria e telemetria.
- Curriculos ficam privados por padrao; consulta de terceiros no Jobs exige
  empresa Business `active`, papel de recrutador e escopo `jobs:resumes:read`.
- O PDF CTPS importado e evidenciado por hash; registros extraidos sao
  separados visualmente de declaracoes manuais e cada leitura empresarial e
  registrada de forma imutavel.
- Arquivos CTPS sao cifrados em storage privado com AES-256-GCM, recuperaveis
  somente pelo titular; producao exige chave carregada por vault/KMS.

## Controles de producao obrigatorios

- TLS fim a fim, criptografia em repouso/KMS, secret vault e rotacao.
- OAuth2/OIDC, JWT assinado, revogacao de sessoes, API keys hash-only e rate
  limit no gateway.
- Provider homologado de biometria/liveness, antifraude/IP intelligence e OCR.
- DPIA/LGPD, politica de retencao, direitos do titular e anonimization jobs.
- Moderacao com OCR/IA, fila humana, apelacao e auditoria.
- Pentest, SAST/SCA, DAST, testes de permissao e plano de incidente.

## Revisao De Permissoes Sensiveis

A revisao RBAC/ABAC para dados sensiveis fica versionada em
`config/security/sensitive_permissions_review.json`. Ela cobre Identity,
Finance, Jobs, Document, Health e HR com papeis autorizados, papeis negados,
recursos sensiveis, evidencias exigidas, testes negativos e regra de runtime
correspondente (`SENSITIVE_ROLES`, `RECRUITER_ROLES` ou `MEDICAL_ROLES`).

Leitura de dado sensivel deve ser deny-by-default, auditada, sem payload bruto
em logs e com evidencias por hash/ID auditavel. Mutacoes sensiveis continuam
exigindo MFA quando a transicao de dominio assim declarar.

Nenhuma chave real, prontuario, documento, biometria bruta ou dado de cartao
deve ser persistido no repositorio.
