# Resumo Executivo da Auditoria de Dados

**Status:** em execução; conclusão de 100% não declarada.

A varredura física reproduzível encontrou 28 migrations PostgreSQL, 32 schemas, 164 tabelas, 2276 campos, 566 referências, 118 índices e 112 endpoints candidatos. Também foram catalogados estaticamente 4 coleções MongoDB, 4 tabelas SQLite, 1 padrão Redis, 4 stores de objetos e 12 chaves/famílias de browser storage. A validação operacional desses mecanismos permanece pendente.

## Limitações

- O banco em execução não foi consultado; o catálogo representa o estado versionado.
- Classificação LGPD automática é triagem, não decisão jurídica.
- Bindings, permissões, cálculos, regras fiscais e ações UI exigem validação funcional por domínio.

EVIDÊNCIAS: `docs/data-audit/artifacts/checklist_cobertura.json` e `docs/data-audit/artifacts/relatorio_divergencias.json`.
