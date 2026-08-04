# Dependabot e segurança de dependências

**Projeto:** All in One + Valley  
**Classificação:** Pendências / Técnico / Equipe Técnica  
**Público-alvo:** Equipe Técnica  
**Data:** 03/08/2026, America/Sao_Paulo  
**Repositório:** `interflownex/All-in-One`

## Visão geral

A `main` não possuía `.github/dependabot.yml`. Correções npm anteriores já elevaram pisos mínimos de segurança e adicionaram testes de regressão, porém não havia uma política versionada cobrindo atualizações futuras dos vários ecossistemas do monorepo.

Esta rodada cria uma configuração central do Dependabot para:

- GitHub Actions;
- 12 projetos npm;
- Android/Gradle;
- Flutter/Pub.

As atualizações de segurança npm são agrupadas para reduzir ruído, enquanto atualizações comuns de desenvolvimento ficam limitadas a versões minor e patch.

## Evidências observadas

- nenhuma PR aberta do Dependabot foi localizada na consulta disponível;
- `.github/dependabot.yml` não existia na `main`;
- o teste `tests/test_dependency_security_floors.py` já protege pisos mínimos para `postcss`, `brace-expansion`, `react-router`, `vite` e dependências transitivas Android;
- a PR #105 integrou correções npm em múltiplos aplicativos e elevou `brace-expansion` para versão corrigida;
- o conector GitHub disponível nesta execução não expõe o endpoint administrativo que lista cada alerta privado da página Security > Dependabot.

## Alteração implantada em branch isolada

Branch: `codex/dependabot-seguranca-20260803`

Arquivo criado:

- `.github/dependabot.yml`

Cobertura configurada:

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
- `/.github/workflows` por meio do ecossistema `github-actions` na raiz.

## Regras de segurança preservadas

- nenhuma escrita direta na `main`;
- nenhuma atualização de versão major agrupada automaticamente para dependências de desenvolvimento;
- nenhum segredo ou token adicionado;
- nenhum alerta foi descartado ou marcado como risco aceito sem evidência;
- merge somente após todos os gates obrigatórios ficarem verdes no mesmo SHA;
- integração somente por Squash and Merge;
- o painel de Dependabot deve ser revisitado após a integração, porque o GitHub processa a configuração a partir da branch padrão.

## Critérios para eliminar marcadores vermelhos

1. integrar a PR somente com CI e Security verdes;
2. aguardar o Dependabot processar a configuração na `main`;
3. revisar os PRs de segurança gerados, um grupo por ecossistema;
4. executar testes e builds específicos antes de cada merge;
5. não dispensar alertas sem justificativa técnica documentada;
6. confirmar que a página Security > Dependabot apresenta zero alertas abertos;
7. confirmar que a aba Actions não contém workflows obrigatórios vermelhos no SHA integrado.

## Limitação objetiva desta execução

A configuração e a governança foram implantadas, mas não é tecnicamente honesto declarar zero alertas no painel privado sem acesso ao endpoint que enumera os alertas individuais. O fechamento final depende de o GitHub gerar os PRs de correção após a configuração chegar à `main` e de esses PRs passarem pelos testes do repositório.
