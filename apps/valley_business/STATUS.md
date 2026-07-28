# Status: Valley Business

**Estado:** `frontend_vite_active`  
**Aplicação:** `apps/valley_business`  
**Público principal:** Pessoa Jurídica  
**Atualização:** 27/07/2026

## Implementado

- shell React/Vite versionado;
- scripts de desenvolvimento, build, lint e preview;
- dependência do All-in-One ID e do API Hub preservada;
- diretório operacional real separado do contrato documental `apps/valley-business`.

## Validação obrigatória

```bash
cd apps/valley_business
npm ci
npm run lint
npm run build
```

## Pendências

- homologar jornadas empresariais contra o API Hub público;
- validar autenticação, permissões, estoque, pedidos e relatórios;
- executar testes de interface e acessibilidade;
- registrar evidências antes de considerar a aplicação pronta para produção.
