# Diagnostico do gate de artefatos gerados

## /opt/hostedtoolcache/Python/3.12.13/x64/bin/python scripts/scaffold_modules.py --check
exit_code: 1
```text
Artefatos customizados ausentes:
- apps/valley_business/STATUS.md
- apps/valley_rider/STATUS.md
```

## /opt/hostedtoolcache/Python/3.12.13/x64/bin/python scripts/generate_domain_event_fixtures.py --check
exit_code: 0
```text
Catalogo de fixtures validado: config/events/domain_event_fixtures.json
```

## /opt/hostedtoolcache/Python/3.12.13/x64/bin/python scripts/validate_openapi.py
exit_code: 0
```text
OpenAPI valido para 24 modulos e todas as operacoes minimas.
```

## /opt/hostedtoolcache/Python/3.12.13/x64/bin/python scripts/validate_repository.py
exit_code: 1
```text
Falhas de validacao encontradas:
- Stitch deve declarar um projeto por modulo.
- Ativo oficial de marca ausente: None
- Branding deve declarar exatamente os apps Valley oficiais.
- Matriz de compliance deve cobrir exatamente os 25 modulos do catalogo.
- Fluxo de direitos do titular deve cobrir exatamente os 25 modulos do catalogo.
- Jobs de retencao devem cobrir exatamente os 25 modulos do catalogo.
```
