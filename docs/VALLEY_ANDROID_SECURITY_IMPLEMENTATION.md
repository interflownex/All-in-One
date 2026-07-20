# Valley Android — execução do plano de segurança

## Estado desta entrega

### Implementado

- [x] Separação de variantes `debug`, `staging` e `production`.
- [x] Release não depurável.
- [x] Minificação e redução de recursos no release.
- [x] Remoção da preservação indiscriminada de símbolos nativos.
- [x] `android:allowBackup="false"`.
- [x] `android:usesCleartextTraffic="false"`.
- [x] Pipeline Android com testes, build release e evidência de dependências.
- [x] Gate que rejeita referência a `debug.keystore` ou assinatura debug.

## Pendências que exigem implementação adicional

- [ ] Substituir o identificador provisório `com.example.valley` pelo namespace definitivo.
- [ ] Integrar Android Keystore para tokens e dados sensíveis.
- [ ] Implementar Play Integrity API no cliente e validação no backend.
- [ ] Adicionar validação de assinatura e anti-repackaging.
- [ ] Revisar anti-root, anti-hooking e anti-Frida com política de risco, evitando bloquear dispositivos legítimos sem evidência.
- [ ] Implementar autenticação real, refresh token rotativo, MFA, sessão e RBAC.
- [ ] Integrar crash reporting, analytics consentido, logs estruturados e tracing.
- [ ] Completar SAST, DAST, SBOM CycloneDX e varredura de dependências.
- [ ] Implementar consentimento granular, retenção, exclusão e portabilidade LGPD.
- [ ] Executar benchmark, regressão e pentest em ambiente homologado.

## Bloqueios externos

- Keystore de produção e senhas não podem ser commitidos.
- Play App Signing e Play Integrity exigem acesso ao Google Play Console.
- Provedores de MFA, observabilidade e analytics exigem definição e credenciais.
- Pentest final exige escopo, ambiente e autorização formal.

## Critério de aprovação

A release de produção só poderá ser promovida quando o workflow Android estiver verde, a assinatura de produção estiver configurada fora do repositório, os controles de autenticação e autorização estiverem integrados e as evidências de regressão e pentest estiverem anexadas à release.
