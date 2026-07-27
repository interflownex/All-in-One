# Política mandatória e persistente de integração

## Escopo

Esta política se aplica a todas as pull requests do ecossistema All-in-One + Valley.

## Regras obrigatórias

1. Nenhuma pull request pode ser integrada com check obrigatório vermelho, cancelado, ausente ou inconclusivo.
2. A estratégia final de integração é exclusivamente **Squash and Merge**.
3. Merge Commit e Rebase Merge não devem ser usados para integrar mudanças do projeto.
4. Auto-merge somente pode ser habilitado quando todos os checks obrigatórios estiverem verdes, a PR estiver mesclável e não houver revisão pendente ou conflito.
5. Nenhuma automação pode publicar diretamente em produção a partir de uma pull request.
6. Pull requests duplicadas, divergentes ou substituídas devem ser encerradas sem merge e apontar para a linha de trabalho vigente.
7. O módulo Vision permanece excluído até reativação expressa do responsável pelo projeto.
8. A Issue #24 permanece fora de qualquer alegação de conclusão sem evidência específica no projeto Stitch indicado.
9. Evidências de CI, banco, segurança, contratos, imagens e aplicações devem ser reproduzíveis e vinculadas ao head exato da PR.
10. Correções de segurança não podem ser resolvidas pela desativação genérica de gates ou pela supressão permanente de vulnerabilidades reais.

## Gate mínimo para autorização de merge

- Continuous Integration: sucesso;
- Security: sucesso;
- Database: sucesso;
- Docker Compose Health Gate: sucesso;
- OpenAPI: sucesso;
- Valley DAST: sucesso;
- Android e demais plataformas afetadas: sucesso;
- branch atualizada e mesclável;
- ausência de segredos ou credenciais versionados;
- revisão das pendências separadas do escopo.

## Regra para agentes e IAs

Qualquer IA ou automação que atue no repositório deve:

- corrigir a causa técnica, não mascarar o gate;
- manter a PR em rascunho enquanto houver bloqueadores;
- nunca autorizar merge apenas com diagnóstico ou recomendação;
- registrar o estado real, sem declarar concluído o que não foi comprovado;
- habilitar auto-merge somente após o gate mínimo integralmente aprovado.

## Linha vigente de estabilização

A PR #50 é a linha vigente para estabilização transversal de CI/CD e governança. Pull requests anteriores com escopo técnico sobreposto devem ser tratadas como substituídas, após verificação de conteúdo útil ainda não reaplicado.
