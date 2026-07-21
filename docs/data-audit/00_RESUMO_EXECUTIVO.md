# Resumo Executivo da Auditoria de Dados

**Status:** em execução; conclusão de 100% não declarada.

A varredura física reproduzível encontrou 24 migrations PostgreSQL, 31 schemas, 81 tabelas, 1189 campos, 297 referências, 48 índices e 99 endpoints candidatos. Também foram identificados MongoDB, Redis, SQLite, armazenamento privado e storage de navegador; esses mecanismos permanecem parcialmente catalogados.

## Limitações

- O banco em execução não foi consultado; o catálogo representa o estado versionado.
- Classificação LGPD automática é triagem, não decisão jurídica.
- Bindings, permissões, cálculos, regras fiscais e ações UI exigem validação funcional por domínio.

EVIDÊNCIAS: `docs/data-audit/artifacts/checklist_cobertura.json` e `docs/data-audit/artifacts/relatorio_divergencias.json`.
