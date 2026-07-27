# Índice e Governança da Documentação

**Versão:** 1.0  
**Data e hora:** 26/07/2026 às 23:06:33  
**Repositório:** `interflownex/All-in-One`  
**Issue:** `#45`

## 1. Objetivo

Classificar a documentação do projeto para impedir que registros históricos,
artefatos gerados ou documentos desatualizados sejam usados como estado atual.

## 2. Hierarquia documental

| Nível | Tipo | Regra |
|---|---|---|
| 1 | Catálogo e políticas | Fonte de verdade estrutural |
| 2 | Pendências, status atual e tarefas | Estado operacional vigente |
| 3 | Roadmap e planos | Direção e sequência de execução |
| 4 | Operação, segurança e compliance | Procedimentos especializados |
| 5 | Relatórios versionados | Evidência de uma varredura específica |
| 6 | Inventários e documentação gerada | Derivados do código e banco |
| 7 | Histórico | Preservado para auditoria, não autoritativo |

## 3. Documentos autoritativos

| Documento | Versão atual | Estado | Finalidade |
|---|---:|---|---|
| `README.md` | 2.7 | Atualizado | Visão geral e fontes de verdade |
| `AGENTS.md` | 2.7 operacional | Atualizado | Regras para IAs e agentes |
| `docs/Pendências Do desenvolvedor.md` | 2.7 | Atualizado | Pendências consolidadas |
| `docs/STATUS_ATUAL.md` | 1.0 | Novo | Fotografia operacional vigente |
| `docs/ROADMAP.md` | 1.1 | Atualizado | Direção de produto e tecnologia |
| `tarefas.md` | 1.2 | Atualizado | Passagem para a próxima IA |
| `config/module_catalog.json` | 0.2.0 | Fonte estrutural | 24 módulos e 9 aplicações |
| `config/branding/authorized_assets.json` | vigente | Fonte de marca | Ativos oficiais autorizados |
| `config/autonomy/*.json` | por política | Fonte operacional | Autonomia e integrações |

## 4. Documentos operacionais especializados

Estes documentos permanecem válidos em seu domínio, mas devem ser confrontados
com o status atual antes de qualquer execução:

- `docs/OPERATIONS.md`;
- `docs/COMPLIANCE.md`;
- `docs/STITCH_FRONTEND.md`;
- `docs/JOBS_CTSP_DIGITAL.md`;
- documentação de cada módulo em `modules/*/`;
- contratos em `contracts/`;
- migrations e rollbacks em `database/`;
- workflows em `.github/workflows/`.

## 5. Documentos históricos

- `STATUS.md`: diário operacional acumulado. Pode conter fatos válidos de datas
  anteriores, contagens antigas e branches já encerradas.
- `docs/EXECUTION_PLAN.md`: plano extenso de 19/07/2026. Preserva decisões e
  evidências, mas possui referências a `worktree-sync`, 25 módulos e estados
  anteriores.
- versões anteriores em `docs/relatorios/pendencias/`.
- relatórios de remoção do Vision e auditorias de versões anteriores.

A existência desses registros não reativa Vision nem altera a baseline de 24
módulos.

## 6. Documentação gerada e inventários

`docs/data-audit/` contém inventários, dicionários, matrizes e tabelas geradas.
Eles devem ser regenerados por script quando o schema mudar. Arquivos
`vision.*.md` nesse diretório representam histórico de banco e não módulo ativo.

Regras:

1. não editar manualmente artefato gerado sem corrigir o gerador;
2. registrar commit, data e comando de geração;
3. preservar histórico necessário para auditoria;
4. marcar dados obsoletos no resumo executivo;
5. impedir que PR antigo regenere documentação com catálogo desatualizado.

## 7. Divergências corrigidas nesta versão

- README: 25 para 24 módulos ativos.
- Roadmap: 25 domínios para 24 módulos ativos.
- Fontes de verdade explicitadas.
- `STATUS.md` classificado como histórico.
- `docs/EXECUTION_PLAN.md` classificado como plano histórico detalhado.
- referências Vision em inventários classificadas como históricas.
- implementação Telegram vinculada à documentação e à issue `#45`.

## 8. Divergências ainda pendentes

1. Atualizar `docs/OPERATIONS.md` de 25 para 24 stores após executar os testes.
2. Produzir nova edição detalhada do Execution Plan após regularizar os PRs.
3. Regenerar os inventários de dados no commit escolhido entre `#34` e `#37`.
4. Revisar status locais dos apps após validar APK Admin e PDV Desktop.
5. Revisar documentação Stitch após sincronização remota autenticada.

## 9. Processo de atualização

Toda mudança relevante deve:

1. atualizar código e testes;
2. atualizar o documento especializado afetado;
3. atualizar `docs/STATUS_ATUAL.md`;
4. atualizar pendências e `tarefas.md`;
5. registrar versão, data, hora, branch e commit;
6. abrir Pull Request;
7. integrar por Squash and Merge após checks.

## 10. Histórico

| Versão | Data e hora | Alteração |
|---|---|---|
| 1.0 | 26/07/2026 23:06:33 | Criação do índice, classificação de documentos e baseline de 24 módulos. |