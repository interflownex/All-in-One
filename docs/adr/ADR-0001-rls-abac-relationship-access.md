# ADR-0001: RLS, ABAC e acesso baseado em relacionamento

- Status: Proposto
- Data: 2026-08-05
- Issue: #204
- Escopo: Fundação de Governança F0.3

## Contexto

O ecossistema All in One + Valley combina dados de múltiplos tenants, usuários, empresas e serviços. RBAC isolado não representa finalidade de tratamento, relacionamento com o recurso nem acesso temporário de suporte. A ausência de contexto deve negar acesso, e não ampliar permissões.

## Decisão

1. PostgreSQL aplicará Row Level Security nas tabelas tenant-aware e usará `FORCE ROW LEVEL SECURITY` quando a tabela estiver sob controle da aplicação.
2. A conexão deverá fornecer contexto transacional por configurações locais: `app.tenant_id`, `app.subject_id`, `app.subject_type`, `app.processing_purpose` e `app.request_id`.
3. Políticas devem combinar:
   - isolamento obrigatório por tenant;
   - atributos do sujeito e da finalidade;
   - relacionamento comprovável com o recurso;
   - menor privilégio.
4. Contexto ausente, inválido ou incompleto resulta em negação.
5. Roles de aplicação não podem ser proprietárias das tabelas protegidas nem possuir `BYPASSRLS`.
6. Suporte e break-glass exigem ticket ou incidente, prazo de expiração e evento de auditoria. Não haverá role global permanente de bypass.
7. Serviços internos devem declarar finalidade e identidade próprias. Credenciais humanas não serão reutilizadas por serviços.
8. A implementação física ocorrerá em migrations pequenas, reversíveis e acompanhadas de testes negativos entre tenants.

## Contrato executável

O arquivo `config/compliance/access_control.v1.json` é a fonte versionada desta decisão. Mudanças incompatíveis exigem nova versão, revisão de Segurança/DPO e evidência nos gates.

## Consequências

- Queries sem contexto válido deixarão de funcionar, o que é intencional.
- Pools de conexão deverão usar contexto local por transação e limpar o estado antes da reutilização.
- Jobs assíncronos precisarão carregar tenant, sujeito técnico, finalidade e request ID de forma explícita.
- A observabilidade deverá registrar decisões e referências de auditoria, sem copiar PII para logs.

## Próximos passos

- criar migration RLS inicial em lote separado;
- implementar funções SQL fail-closed para leitura do contexto;
- adicionar testes de tenant cruzado, contexto ausente e suporte expirado;
- mapear owners e consumidores antes de ativar políticas em produção;
- manter a issue #204 aberta até os demais gates F0.3 e validações externas.

## Fora de escopo

Este ADR não ativa políticas em produção, não concede acesso privilegiado e não representa validação jurídica final.
