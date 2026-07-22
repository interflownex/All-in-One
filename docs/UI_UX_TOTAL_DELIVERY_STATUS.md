# Status da Entrega Total UI/UX - All-in-One A1

**Data:** 2026-07-20  
**Branch:** `feat/data-ui-module-rules`

## Objetivo

Executar as diretrizes mandatórias de integridade da logomarca oficial, dashboards, relatórios, tabelas, formulários, português do Brasil, módulos automáticos por tipo de empresa e configuração manual de módulos.

## Status atual

| Atividade                       | Estado                       | Observação                                                                                         |
| ------------------------------- | ---------------------------- | -------------------------------------------------------------------------------------------------- |
| Blindagem da logomarca          | Concluída na primeira frente | `BrandLogo` criado e mesclado no PR #15.                                                           |
| Verificação automática da marca | Concluída na primeira frente | `scripts/check_brand_integrity.py` criado e mesclado no PR #15.                                    |
| Contrato de UI de dados         | Concluída na primeira frente | `config/apps/data_ui_contract.json` define visão geral, relatórios, listas, formulários e estados. |
| Recomendações de módulos        | Em execução                  | `moduleRecommendationRules.ts` cria base front-end para seleção automática por tipo de empresa.    |
| Blueprints de dados             | Em execução                  | `dataUiBlueprints.ts` mapeia telas por módulo, entidade, superfície e ação primária.               |
| Cockpit externo                 | Publicado                    | AppDeploy publicado para acompanhamento público da entrega.                                        |

## Próximas ações mandatórias

1. Substituir usos diretos de `<img src="/assets/brand/all-in-one-logo-light-official.png" />` pelo componente `BrandLogo` onde ainda existirem.
2. Extrair `modulesData` de `Navigation.tsx` para registro modular adaptativo.
3. Aplicar títulos pt-BR para todos os módulos e telas.
4. Implementar `Configurações > Empresa > Módulos e recursos`.
5. Conectar `recommendBusinessModules` ao cadastro de empresa.
6. Aplicar os blueprints em cada visão geral, relatório, listagem e formulário.
7. Garantir estados obrigatórios: carregamento, vazio, erro, sem permissão, sucesso, somente leitura e dados desatualizados.
8. Criar testes unitários para recomendações de módulos.
9. Criar testes de componente para marca, navegação e formulários.
10. Executar validação do repositório e Playwright.

## Critérios de aceite

- Logomarca oficial exibida de forma fiel em todas as telas.
- Nenhuma alteração visual da marca além de redimensionamento proporcional.
- Cadastro empresarial seleciona módulos automaticamente.
- Usuário administrador consegue ativar, ocultar ou desativar módulos manualmente.
- Navegação mostra somente módulos permitidos e úteis ao contexto.
- Todos os formulários possuem campos necessários, validação e tratamento de erro.
- Todos os dashboards possuem KPIs, alertas, ações recomendadas e origem dos dados.
- Todo texto de interface está em português do Brasil, salvo termos amplamente adotados ou nomes próprios.
- Permissões e estado de módulo são validados no servidor.
- Testes e evidências visuais anexados antes de concluir a entrega.
