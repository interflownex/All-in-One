# Preferencia obrigatoria de idioma

- Todas as respostas, alertas, erros, orientacoes, perguntas e opcoes devem ser escritos em portugues do Brasil.
- Essa regra vale para este workspace (`all-in-one`) e deve prevalecer sobre respostas em ingles quando nao houver conflito tecnico ou legal.
- Codigos, nomes de arquivos, comandos, identificadores, logs e mensagens externas devem permanecer no idioma/formato original quando isso preservar precisao tecnica.

# Sincronizacao Git obrigatoria

- Ao concluir cada atividade que altere arquivos neste workspace, executar sincronizacao Git automatica com `git add`, `git commit` e `git push`.
- O comando padrao e:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/git_auto_sync.ps1 -Activity "<descricao da atividade>"
```

- A politica persistente fica em `config/autonomy/git_auto_sync_policy.json`.
- Neste checkout, o push automatico deve usar o remoto `fork` quando `origin` nao aceitar escrita.
- Nao criar commit vazio quando nao houver mudancas.
- O Codex deve gerar e aplicar a mensagem de commit com base na atividade e no
  diff real, sem transferir essa responsabilidade ao usuario nem solicitar que
  ele edite `COMMIT_EDITMSG` manualmente.
- A mensagem deve ser concisa, rastreavel e escrita em portugues do Brasil;
  preservar o prefixo `chore(auto-sync):` no fluxo automatico.
- Se houver merge ou rebase em andamento, parar e reportar o bloqueio em portugues do Brasil.

# Alinhamento multiagente obrigatorio

- Codex CLI, Antigravity, Gemini Code Assist e Gemini CLI (Termux/Ubuntu) devem seguir a politica versionada em `config/autonomy/multi_agent_sync_policy.json`.
- Git e a fonte de verdade compartilhada do projeto; nenhum agente deve sobrescrever commits remotos ou mudancas locais de outro agente sem integrar primeiro.
- Antes de alterar arquivos, verificar o estado local com `git status --short --branch` e preservar mudancas existentes.
- Antes de editar, executar `python3 scripts/multi_agent_sync_guard.py preflight --integrate` e adquirir o lock com `python3 scripts/multi_agent_sync_guard.py acquire --agent <agent_id> --activity "<descricao>"`.
- Ao concluir a sincronizacao, liberar o lock com `python3 scripts/multi_agent_sync_guard.py release --agent <agent_id>`.
- Antes de sincronizar, buscar `origin/main` e `fork/main` quando os remotos estiverem acessiveis.
- Nunca executar comandos destrutivos como `git reset --hard`, `git clean` destrutivo ou checkout que descarte trabalho alheio sem ordem explicita do usuario.
- `config/stitch/screen_manifest.json` e `config/stitch/sync_state.json` sao o estado autoritativo para sincronia Stitch e devem ser preservados entre agentes.
- Segredos como `STITCH_API_KEY` devem permanecer apenas em variaveis de ambiente, GitHub Actions Secrets ou cofres externos; nunca versionar segredos.

# Integracoes Google ativas

- Google SDK, Google AI Studio, Google Cloud, AlloyDB, Google Code CLI, Gemini CLI, Gemini Code Assist e Google Stitch estao ativos por ordem explicita do usuario.
- A politica obrigatoria fica em `config/autonomy/google_integrations_policy.json`.
- Discover, sync e operacoes Google podem executar quando credenciais legitimas estiverem disponiveis fora do Git.
- Docker, VS Code, Antigravity, workflows e scripts devem manter as flags Google, AlloyDB, Gemini e Stitch ativas.
- Nao contornar billing, IAM, compliance, enforcement ou suspensao administrativa do provedor.
