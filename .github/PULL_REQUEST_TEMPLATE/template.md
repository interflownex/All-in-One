<!--
AUTOMATION CONTRACT — AUTONOMOUS PULL REQUEST DESCRIPTION

This file is the canonical Pull Request description template for the All in One + Valley project.

Instructions for AI agents, IDE extensions and repository automations:
1. Inspect the complete diff between the PR head and base branches before filling this template.
2. Read changed files, commits, tests, workflows and linked issues. Do not infer implementation details that are not supported by repository evidence.
3. Replace every placeholder enclosed by {{...}} with factual content.
4. Remove instructional HTML comments before publishing the final PR description.
5. Preserve all headings. Use "Não se aplica" only when the item truly does not apply.
6. Never claim tests, builds, scans, migrations, deployments or validations passed without command output or CI evidence.
7. Never hide failures. List unresolved items under "Pendências e limitações".
8. Never include secrets, tokens, credentials, personal data or confidential environment values.
9. Keep the description updated whenever the PR scope changes.
10. If a reliable value cannot be determined, write "Não confirmado" and explain why.

Suggested evidence sources:
- git diff --stat <base>...<head>
- git diff <base>...<head>
- git log --oneline <base>..<head>
- changed-file list
- test, build, lint, migration and security scan outputs
- linked issue acceptance criteria
-->

# {{Título objetivo do Pull Request}}

## Visão geral

<!-- Explain in plain language what this PR changes and why it is necessary. -->

{{Resumo claro do objetivo, do problema resolvido e do resultado esperado.}}

## Contexto e motivação

<!-- Describe the verified background. Reference issues, incidents, requirements or decisions when available. -->

- **Problema identificado:** {{descrição factual do problema}}
- **Causa ou necessidade:** {{causa confirmada ou necessidade de negócio/técnica}}
- **Resultado pretendido:** {{resultado verificável}}
- **Issue, tarefa ou decisão relacionada:** {{#número, URL ou "Não se aplica"}}

## Escopo da alteração

<!-- Summarize the actual changed areas based on the diff. -->

### Incluído

- {{alteração principal 1}}
- {{alteração principal 2}}
- {{alteração principal 3}}

### Fora do escopo

- {{item explicitamente não tratado}}
- {{limite conhecido desta entrega}}

## Alterações realizadas

<!-- Group changes by component. Add or remove subsections to match the real diff. -->

### Aplicação e regras de negócio

- {{mudança realizada ou "Não se aplica"}}

### API, serviços e integrações

- {{mudança realizada ou "Não se aplica"}}

### Banco de dados e migrações

- {{mudança realizada ou "Não se aplica"}}

### Aplicativos e interface

- {{mudança realizada ou "Não se aplica"}}

### Infraestrutura, CI/CD e configuração

- {{mudança realizada ou "Não se aplica"}}

### Segurança, privacidade e conformidade

- {{controle adicionado, corrigido ou validado}}
- {{impacto LGPD, autenticação, autorização, segredos ou "Não se aplica"}}

### Documentação

- {{documentação criada ou atualizada}}

## Arquivos e componentes afetados

<!-- List meaningful paths or groups. Avoid dumping hundreds of filenames without structure. -->

| Componente ou caminho | Tipo de mudança | Finalidade |
|---|---|---|
| `{{caminho}}` | {{criado/alterado/removido}} | {{motivo}} |
| `{{caminho}}` | {{criado/alterado/removido}} | {{motivo}} |

## Comportamento anterior e novo comportamento

| Aspecto | Antes | Depois |
|---|---|---|
| {{aspecto}} | {{comportamento anterior}} | {{novo comportamento}} |

## Decisões técnicas

<!-- Explain important design choices and rejected alternatives when evidenced. -->

- **Decisão:** {{decisão tomada}}
  - **Justificativa:** {{razão técnica ou de negócio}}
  - **Alternativas consideradas:** {{alternativas ou "Não registradas"}}
  - **Impacto:** {{impacto esperado}}

## Compatibilidade e impacto

- **Breaking change:** {{Sim/Não/Não confirmado}}
- **Compatibilidade retroativa:** {{descrição}}
- **Impacto em APIs:** {{descrição ou "Não se aplica"}}
- **Impacto em banco de dados:** {{descrição ou "Não se aplica"}}
- **Impacto em aplicativos móveis/web:** {{descrição ou "Não se aplica"}}
- **Impacto operacional:** {{descrição ou "Não se aplica"}}
- **Impacto de custo ou infraestrutura:** {{descrição ou "Não se aplica"}}

## Configuração e implantação

<!-- Record only verified steps. Never paste secret values. -->

- **Novas variáveis de ambiente:** {{nomes sem valores ou "Nenhuma"}}
- **Novos secrets:** {{nomes sem valores ou "Nenhum"}}
- **Migrações necessárias:** {{comando/ordem ou "Nenhuma"}}
- **Feature flags:** {{nomes e estado esperado ou "Nenhuma"}}
- **Ordem de implantação:** {{passos ou "Fluxo padrão"}}
- **Plano de rollback:** {{procedimento verificável}}

## Validação executada

<!-- Mark a checkbox only when there is evidence. Include the exact command or CI check. -->

| Validação | Status | Evidência |
|---|---|---|
| Testes unitários | {{Passou/Falhou/Não executado/Não se aplica}} | `{{comando ou check}}` |
| Testes de integração | {{status}} | `{{comando ou check}}` |
| Testes end-to-end | {{status}} | `{{comando ou check}}` |
| Lint e formatação | {{status}} | `{{comando ou check}}` |
| Build | {{status}} | `{{comando ou check}}` |
| Migrações | {{status}} | `{{comando ou check}}` |
| CodeQL/SAST | {{status}} | `{{workflow ou evidência}}` |
| Dependências | {{status}} | `{{workflow ou evidência}}` |
| Teste manual | {{status}} | {{cenário e resultado}} |

## Evidências

<!-- Add links to CI runs, screenshots, logs sanitized of secrets, artifacts or reproducible outputs. -->

- {{evidência 1}}
- {{evidência 2}}

## Riscos e mitigação

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| {{risco identificado}} | {{Baixa/Média/Alta}} | {{Baixo/Médio/Alto}} | {{mitigação}} |

## Pendências e limitações

<!-- Do not delete this section. Explicitly state when there are none. -->

- {{pendência, limitação ou "Nenhuma pendência conhecida dentro do escopo deste PR."}}

## Checklist do autor ou automação

- [ ] O diff completo foi revisado.
- [ ] A descrição representa somente alterações realmente presentes no PR.
- [ ] O escopo e os itens fora do escopo estão explícitos.
- [ ] Os testes informados possuem evidência.
- [ ] Falhas e validações não executadas estão declaradas.
- [ ] Não há segredos, tokens, credenciais ou dados pessoais na descrição ou no diff.
- [ ] Compatibilidade, migração e rollback foram avaliados.
- [ ] Segurança, privacidade e LGPD foram avaliadas quando aplicáveis.
- [ ] Documentação e contratos afetados foram atualizados.
- [ ] Não existem marcadores genéricos ou placeholders restantes.

## Critérios de aceite

- [ ] {{critério verificável 1}}
- [ ] {{critério verificável 2}}
- [ ] {{critério verificável 3}}

## Resultado final

<!-- Conclude with the exact delivery state. -->

{{Descrição objetiva do estado entregue, do que foi comprovado e do que ainda não foi confirmado.}}

---

**Classificação:** Pendências / Técnico / Equipe Técnica  
**Público-alvo:** Equipe Técnica  
**Projeto:** All in One + Valley
