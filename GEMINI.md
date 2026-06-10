# Regras do Agente de Desenvolvimento (Perfil Gemini)

## Preferencia obrigatoria de idioma

- Todas as respostas, alertas, erros, orientacoes, perguntas e opcoes devem ser escritos em portugues do Brasil.
- Essa regra vale para este workspace (`all-in-one`) e deve prevalecer sobre respostas em ingles quando nao houver conflito tecnico ou legal.
- Codigos, nomes de arquivos, comandos, identificadores, logs e mensagens externas devem permanecer no idioma/formato original quando isso preservar precisao tecnica.

## Sincronizacao Git obrigatoria

- Ao concluir cada atividade que altere arquivos neste workspace, executar sincronizacao Git automatica com `git add`, `git commit` e `git push`.
- O comando padrao e:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/git_auto_sync.ps1 -Activity "<descricao da atividade>"
```

- A politica persistente fica em `config/autonomy/git_auto_sync_policy.json`.
- Neste checkout, o push automatico deve usar o remoto `fork` quando `origin` nao aceitar escrita.
- Nao criar commit vazio quando nao houver mudancas.
- Se houver merge ou rebase em andamento, parar e reportar o bloqueio em portugues do Brasil.

## Alinhamento multiagente obrigatorio

- Codex CLI, Antigravity, Gemini Code Assist e Gemini CLI (Termux/Ubuntu) devem seguir a politica versionada em `config/autonomy/multi_agent_sync_policy.json`.
- Git e a fonte de verdade compartilhada do projeto; nenhum agente deve sobrescrever commits remotos ou mudancas locais de outro agente sem integrar primeiro.
- Antes de alterar arquivos, verificar o estado local com `git status --short --branch` e preservar mudancas existentes.
- Antes de editar, executar `python3 scripts/multi_agent_sync_guard.py preflight --integrate` e adquirir o lock com `python3 scripts/multi_agent_sync_guard.py acquire --agent <agent_id> --activity "<descricao>"`.
- Ao concluir a sincronizacao, liberar o lock com `python3 scripts/multi_agent_sync_guard.py release --agent <agent_id>`.
- Antes de sincronizar, buscar `origin/main` e `fork/main` quando os remotos estiverem acessiveis.
- Nunca executar comandos destrutivos como `git reset --hard`, `git clean` destrutivo ou checkout que descarte trabalho alheio sem ordem explicita do usuario.
- `config/stitch/screen_manifest.json` e `config/stitch/sync_state.json` sao o estado autoritativo para sincronia Stitch e devem ser preservados entre agentes.
- Segredos como `STITCH_API_KEY` devem permanecer apenas em variaveis de ambiente, GitHub Actions Secrets ou cofres externos; nunca versionar segredos.

## Padroes de Engenharia e Qualidade

- **Ferramentas de Linting/Formatação:** O projeto utiliza estritamente `Ruff` (Python), `Mypy` (Tipagem), `Prettier` (Web/Config) e `ESLint` (JS/TS).
- **Proibição de Ferramentas Não Homologadas:** É terminantemente proibido o uso ou configuração de ferramentas como `delegua.estilizador` ou qualquer outro "estilizador" não oficial. Qualquer configuração residual dessas ferramentas deve ser removida imediatamente.
- **Automação:** O ambiente VS Code deve estar configurado para "Format on Save" e "Fix on Save" usando as ferramentas homologadas citadas acima.
- **Tipagem Estrita:** Código Python deve buscar 100% de conformidade com `mypy --strict`.
- **Consistência:** Seguir as regras do `.editorconfig` e `.prettierrc` em todos os commits.

## Padroes de Engenharia de Elite e Google Cloud

- **Segredos Nativos:** O sistema utiliza `get_config()` para buscar segredos. A prioridade é: Variável de Ambiente > Google Secret Manager (`gcloud secrets`).
- **Builds em Nuvem:** Manifestos `cloudbuild.yaml` e `cloudbuild-android.yaml` estão disponíveis para integração contínua (CI/CD) via Google Cloud Build.
- **Observabilidade GCP:** Métricas de log (`all_in_one_errors`) e logs higienizados com `Correlation ID` são mandatórios para todos os módulos.
- **Contração de Código:** O runtime centraliza a lógica de observabilidade, segurança e persistência, reduzindo o boilerplate nos microserviços.
- **Higienizacao e Controle de Armazenamento GCP**

- O espaco do Google Cloud tem teto fixo de 5GB.
- Ao iniciar os trabalhos no sistema (ativacao), o agente deve executar o script mandatorio de higienizacao: `python3 scripts/gcp_storage_hygiene.py`.
- O script avalia a capacidade e ao cruzar 85% descarta recursos secundarios automaticamente.
- A rotina ja esta engatilhada no multi-agente sync guard para rodar a cada termino de atividade.

## Integracoes Google ativas

- Google SDK, Google AI Studio, Google Cloud, AlloyDB, Google Code CLI, Gemini CLI, Gemini Code Assist e Google Stitch estao ativos por ordem explicita do usuario.
- A politica obrigatoria fica em `config/autonomy/google_integrations_policy.json`.
- Discover, sync e operacoes Google podem executar quando credenciais legitimas estiverem disponiveis fora do Git.
- Docker, VS Code, Antigravity, workflows e scripts devem manter as flags Google, AlloyDB, Gemini e Stitch ativas.
- Nao contornar billing, IAM, compliance, enforcement ou suspensao administrativa do provedor.

## Sincronizacao Marketplace Valley

- Para atividades que alterem produtos, servicos ou catalogos, aplicar as regras do documento `docs/ORIENTACAO_CODEX_SYNC_MARKETPLACE_VALLEY.md`.
