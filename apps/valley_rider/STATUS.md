# Status: Valley Rider

**Estado:** `frontend_vite_active`  
**Aplicação:** `apps/valley_rider`  
**Público principal:** Riders e equipe operacional  
**Atualização:** 27/07/2026

## Implementado

- shell React/Vite versionado;
- scripts de desenvolvimento, build, lint e preview;
- dependência do All-in-One ID, Riders, Delivery e Mobility preservada;
- diretório operacional real separado do contrato documental `apps/valley-rider`.

## Validação obrigatória

```bash
cd apps/valley_rider
npm ci
npm run lint
npm run build
```

## Pendências

- homologar cadastro, disponibilidade, corridas, entregas, ganhos e ocorrências;
- validar permissões, localização, contingência e operação em rede instável;
- executar testes de interface, acessibilidade e segurança;
- incorporar a logomarca oficial Valley Riders somente após ingestão do arquivo original aprovado.
