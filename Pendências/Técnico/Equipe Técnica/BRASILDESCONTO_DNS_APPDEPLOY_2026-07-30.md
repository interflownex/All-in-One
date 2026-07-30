# Pendência técnica — DNS brasildesconto.com.br

**Público-alvo:** Equipe Técnica  
**Classificação:** Pendências > Técnico  
**Prioridade:** Bloqueio externo imediato

## Situação

O domínio `brasildesconto.com.br` está associado ao aplicativo AppDeploy `9135635066da434181`, porém permanece em `pending_dns`.

## Causa comprovada

A validação do AppDeploy detectou registros AAAA inesperados publicados pela Cloudflare:

- `2606:4700:3031::6815:4b28`
- `2606:4700:3033::ac43:d3cb`

## Ação externa necessária

No painel Cloudflare:

1. abrir **DNS > Registros**;
2. localizar o host raiz `@`;
3. remover qualquer registro `AAAA` do host raiz;
4. manter um registro `A` apontando para `18.232.7.146`;
5. alterar o proxy para **Somente DNS** (nuvem cinza) durante a validação;
6. remover outros registros `A`, `AAAA`, `CNAME`, `ALIAS` ou redirecionamentos conflitantes no host raiz;
7. aguardar a propagação e repetir a verificação no AppDeploy.

## Aceite

A pendência somente pode ser encerrada quando o AppDeploy retornar domínio ativo e o site abrir por HTTPS.
