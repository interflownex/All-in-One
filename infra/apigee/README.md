# Apigee - instruções e artefatos

Este diretório contém instruções para configurar de forma persistente e mandatória chaves e variáveis no Apigee (KeyValue Maps - KVM) e como referenciá-las nas proxies.

Passos recomendados:

1. Criar KVMs para segredos (via Apigee UI ou `apigeecli`):
   - `JWT_SECRET`
   - `DATABASE_PASSWORD`
   - `SENTRY_DSN`

2. Criar Environment properties (se necessário) ou usar KVMs por proxy.

3. Automação (exemplo `apigeectl` ou `apigeecli`):
   - `apigeecli kvm add -o ORG -e ENV -k JWT_SECRET -v "<value>"`

4. Referenciar nos fluxos da proxy com `KeyValueMapOperations` ou `AssignMessage`.

Exemplo mínimo de comando com `apigeecli`:

```bash
apigeecli kvm add -o $APIGEE_ORG -e $APIGEE_ENV -k JWT_SECRET -v "$JWT_SECRET"
apigeecli kvm add -o $APIGEE_ORG -e $APIGEE_ENV -k DATABASE_PASSWORD -v "$DATABASE_PASSWORD"
```

Nota: Não coloque segredos em repositório; use CI/CD protegido e Secret Manager para injetar valores.
