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

## Controles de producao obrigatorios

- TLS fim a fim, criptografia em repouso/KMS, secret vault e rotacao.
- OAuth2/OIDC, JWT assinado, revogacao de sessoes, API keys hash-only e rate
  limit no gateway.
- Provider homologado de biometria/liveness, antifraude/IP intelligence e OCR.
- DPIA/LGPD, politica de retencao, direitos do titular e anonimization jobs.
- Moderacao com OCR/IA, fila humana, apelacao e auditoria.
- Pentest, SAST/SCA, DAST, testes de permissao e plano de incidente.

Nenhuma chave real, prontuario, documento, biometria bruta ou dado de cartao
deve ser persistido no repositorio.
