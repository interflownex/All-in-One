# Valley Universal MCP 1.0.0

Servidor MCP público e somente leitura do Valley Universal, construído com Skybridge.

## Finalidade

Permitir que assistentes compatíveis:

- expliquem os contextos do Valley;
- consultem o estado público da entrega;
- retornem a URL oficial do aplicativo;
- orientem a pessoa a escolher um contexto depois da autenticação.

O MCP não concede permissões, não altera cadastros, não movimenta valores e não executa ações administrativas.

## Ferramentas

- `valley_list_contexts`;
- `valley_get_release_status`;
- `valley_open_app`.

## Execução local

```bash
cd apps/valley-universal-mcp
npm install
npm run typecheck
npm run dev
```

O endpoint MCP é disponibilizado pelo Skybridge em `/mcp`, na porta configurada pelo ambiente ou na porta padrão do framework.

## Segurança

A versão 1.0 é deliberadamente somente leitura. Ferramentas autenticadas deverão ser integradas futuramente ao API Hub com OAuth, autorização por contexto, confirmação explícita e auditoria.

Consulte `SPEC.md` antes de alterar ferramentas, contratos ou limites de segurança.
