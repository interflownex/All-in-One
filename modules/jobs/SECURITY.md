# Security: Jobs

- OAuth2/JWT ou API key com escopo de modulo no API Hub.
- MFA para aprovacoes, pagamentos e leitura de dados sensiveis.
- RBAC/ABAC, device fingerprint, rate limit e auditoria imutavel.
- Segredos apenas via vault ou variaveis de ambiente.
- Retencao, consentimento e anonimizacao em conformidade com LGPD.
- PDFs CTPS sao cifrados em storage privado; somente o titular recupera o arquivo e cada leitura gera auditoria.
