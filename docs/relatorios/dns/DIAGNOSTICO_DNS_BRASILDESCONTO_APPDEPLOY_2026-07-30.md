# Diagnóstico DNS — brasildesconto.com.br

- **Data:** 2026-07-30
- **Classificação:** Pendências > Técnico
- **Público-alvo:** Equipe Técnica
- **Aplicativo AppDeploy:** `9135635066da434181`
- **Domínio:** `brasildesconto.com.br`
- **Estado:** bloqueado por configuração DNS externa

## Visão geral

O domínio está cadastrado corretamente no AppDeploy, porém a validação falha porque a resolução pública retorna registros IPv6 (AAAA) da Cloudflare. Para domínio raiz no AppDeploy, a configuração aceita o proxy IPv4 informado e rejeita registros AAAA inesperados.

## Evidência atual

- AppDeploy: `pending_dns`
- Destino recomendado: `proxy-v2.appdeploy.ai`
- IPv4 de fallback: `18.232.7.146`
- AAAA inesperados detectados:
  - `2606:4700:3031::6815:4b28`
  - `2606:4700:3033::ac43:d3cb`

## Correção obrigatória no provedor DNS

1. Na zona DNS de `brasildesconto.com.br`, manter o domínio raiz apontando para `18.232.7.146` por registro `A`, ou usar `ALIAS/ANAME/flattening` para `proxy-v2.appdeploy.ai`.
2. Remover registros `AAAA` explícitos do domínio raiz.
3. Se o registro estiver com proxy Cloudflare ativado, alterar temporariamente para **Somente DNS** (nuvem cinza), pois o proxy pode publicar IPv6 automaticamente mesmo sem registro AAAA manual.
4. Remover registros conflitantes no host raiz, preservando apenas o destino do AppDeploy.
5. Após propagação, executar novamente a verificação do domínio no AppDeploy.

## Critério de aceite

- A consulta pública do domínio raiz não retorna AAAA.
- O domínio resolve para `18.232.7.146` ou para o proxy do AppDeploy por flattening.
- A verificação AppDeploy retorna `verified`/`active`.
- HTTPS abre o aplicativo AIO Admin sem redirecionamento indevido.

## Limitação operacional

A alteração exige acesso autenticado à conta do provedor DNS/Cloudflare. Nenhuma credencial Cloudflare está disponível no repositório ou no cofre do aplicativo, e nenhuma credencial deve ser versionada.
