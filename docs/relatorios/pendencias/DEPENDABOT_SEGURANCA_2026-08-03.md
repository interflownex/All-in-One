# Dependabot e segurança de dependências

**Projeto:** All in One + Valley  
**Classificação:** `Pendências > Técnico`  
**Público-alvo:** Equipe Técnica  
**Data:** 03/08/2026, `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`

## Visão geral

A `main` não possuía política versionada do Dependabot. Esta entrega cria uma configuração central para monitorar os ecossistemas usados pelo monorepo e gerar correções futuras sem dispensar gates ou alertas.

## Cobertura configurada

- GitHub Actions na raiz;
- Python/Pip na raiz e em `services/aio-mcp-gateway`;
- 12 projetos npm;
- Android/Gradle;
- Flutter/Pub.

As atualizações de segurança Python e npm são agrupadas por ecossistema. Atualizações comuns de desenvolvimento npm ficam limitadas a `minor` e `patch`.

## Evidências desta execução

Durante a regularização foram detectadas e corrigidas vulnerabilidades reais:

- `cryptography==48.0.1` foi elevado para `50.0.0`;
- `mcp==1.27.0` foi elevado para `1.28.1`;
- `pip-audit`, Bandit, scans JavaScript, containers e Android/CodeQL passaram após as correções;
- nenhum segredo ou token foi adicionado.

## Arquivo versionado

- `.github/dependabot.yml`

Diretórios cobertos:

- `/` e `/services/aio-mcp-gateway` para Pip;
- `/apps/all-in-one`;
- `/apps/all-in-one-admin`;
- `/apps/all-in-one-business`;
- `/apps/all-in-one-health`;
- `/apps/all-in-one-mobility`;
- `/apps/all-in-one-riders`;
- `/apps/all-in-one-services`;
- `/apps/all-in-one-user`;
- `/apps/valley`;
- `/apps/valley_business`;
- `/apps/valley_rider`;
- `/desktop/valley-erp`;
- `/apps/valley-android`;
- `/apps/valley-flutter`;
- GitHub Actions na raiz.

## Regras preservadas

- nenhuma escrita direta na `main`;
- nenhum segredo no Git;
- nenhuma dispensa automática de alerta;
- nenhuma atualização major agrupada automaticamente para dependências npm de desenvolvimento;
- cada PR do Dependabot deve passar pelos gates aplicáveis no mesmo SHA;
- integração somente por Squash and Merge;
- alertas só podem ser encerrados com atualização, mitigação comprovada ou justificativa técnica documentada.

## Critério operacional

1. integrar esta política somente com CI, Docker e Security verdes;
2. permitir que o GitHub processe a configuração na branch padrão;
3. revisar cada PR de segurança gerada;
4. executar testes específicos do ecossistema antes do merge;
5. confirmar que não permanecem workflows obrigatórios vermelhos.

## Limitação objetiva

O conector disponível não enumera os alertas privados individuais da página Security. Portanto, a integração desta política não autoriza declarar o painel administrativo como zerado. O estado deve ser confirmado no GitHub após o processamento do Dependabot e a integração das correções geradas.