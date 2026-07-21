# Decisões Arquiteturais da Auditoria

1. Migrations versionadas são a fonte do catálogo físico, não prova do banco em execução.
2. Catálogo lógico e bindings exigem validação cruzada; inferência não equivale a evidência.
3. Formulários dinâmicos apontam para comandos/DTOs allowlist, nunca para tabela física arbitrária.
4. Cobertura inferior a 100% impede status concluído.
5. Propostas de schema exigem migration reversível, backfill, rollback e testes antes de aplicação.

EVIDÊNCIAS: `config/data_audit/delivery_contract.json`.
