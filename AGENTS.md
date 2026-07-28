# Preferencia obrigatoria de idioma

- Todas as respostas, alertas, erros, orientacoes, perguntas e opcoes devem ser escritos em portugues do Brasil.
- Essa regra vale para este workspace (`all-in-one`) e deve prevalecer sobre respostas em ingles quando nao houver conflito tecnico ou legal.
- Codigos, nomes de arquivos, comandos, identificadores, logs e mensagens externas devem permanecer no idioma/formato original quando isso preservar precisao tecnica.

# Modo Estudar, Pesquisa Avancada e entrega `tarefas.md`

- Toda atividade do projeto deve aplicar permanentemente uma abordagem de estudo: verificar o conhecimento existente, explicar decisoes importantes, conectar evidencias, conferir entendimento e registrar criterios reproduziveis.
- Toda informacao externa, atual, instavel, especializada ou com risco relevante de desatualizacao deve ser verificada por pesquisa avancada antes de orientar implementacao ou declarar conclusao.
- Quando a interface nao expuser um seletor persistente para os plugins Estudar ou Pesquisa Avancada, o agente deve aplicar o comportamento equivalente: aprendizagem guiada, verificacao cruzada, consulta a fontes atuais e registro das fontes de verdade.
- Toda entrega deve informar obrigatoriamente versao, data e hora no fuso `America/Sao_Paulo`, repositorio, branch e commit de referencia.
- Ao final de toda entrega tecnica, criar ou atualizar obrigatoriamente o arquivo raiz `tarefas.md`.
- O arquivo `tarefas.md` deve conter todas as diretrizes necessarias para a IA desenvolvedora executar a proxima etapa sem depender de explicacao adicional.
- O `tarefas.md` deve incluir, no minimo: objetivo, contexto, escopo, fontes de verdade, pre-requisitos, sequencia de execucao, prioridades, testes, criterios de aceite, riscos, bloqueios, evidencias esperadas, pendencias restantes e procedimento de entrega.
- Cada atualizacao do `tarefas.md` deve incrementar sua versao e preservar um historico resumido no proprio arquivo.
- O `tarefas.md` deve ser versionado na mesma branch e pull request da atividade correspondente.
- Nenhuma tarefa pode ser marcada como concluida apenas pela existencia de codigo ou documento. Sao obrigatorios teste reproduzivel, evidencia no ambiente correto e referencia ao commit e pull request.

# Sincronizacao Git obrigatoria e segura

- Ao concluir cada atividade que altere arquivos neste workspace, o Codex deve versionar o trabalho no Git.
- Antes de editar, executar `git status --short --branch`, integrar as referencias remotas permitidas e preservar mudancas existentes.
- Se a branch atual for `main`, criar uma branch de trabalho antes de alterar arquivos.
- O padrao de nome recomendado e `codex/<atividade>-<data>`.
- O comando de sincronizacao automatica somente pode ser usado em branch de trabalho:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/git_auto_sync.ps1 -Activity "<descricao da atividade>"
```

- A politica persistente fica em `config/autonomy/git_auto_sync_policy.json`.
- O push deve usar a branch de trabalho no remoto autorizado. E proibido executar push direto na `main`.
- Ao finalizar, abrir ou atualizar pull request para `main`, registrar testes e evidencias e usar **Squash and Merge**.
- Quando a abertura do pull request nao estiver disponivel, manter a branch publicada e registrar claramente o bloqueio; nunca substituir isso por push direto na `main`.
- Nao criar commit vazio quando nao houver mudancas.
- O Codex deve gerar e aplicar a mensagem de commit com base na atividade e no diff real, sem transferir essa responsabilidade ao usuario nem solicitar edicao manual de `COMMIT_EDITMSG`.
- A mensagem deve ser concisa, rastreavel e escrita em portugues do Brasil.
- Se houver merge ou rebase em andamento, parar e reportar o bloqueio em portugues do Brasil.

# Orquestracao obrigatoria de pendencias

- A fonte principal das pendencias e `docs/Pendencias Do desenvolvedor.md`, considerando o nome real versionado `docs/Pendências Do desenvolvedor.md`.
- Toda atualizacao de pendencias deve incrementar a versao e registrar data, branch e commit de referencia.
- A cada atualizacao, gerar obrigatoriamente dois arquivos em `docs/relatorios/pendencias/`:
  1. `RELATORIO_VARREDURA_STATUS_v<versao>_<AAAA-MM-DD>.md`;
  2. `PLANO_ACAO_CODEX_v<versao>_<AAAA-MM-DD>.md`.
- O relatorio de status deve conter a tabela: Nome da atividade | Descricao | Passo sendo executado | Dificuldade [1 a 5] | % concluido | Tempo previsto | Etapas [Total] | Concluidas [X] | Pendentes [Y].
- O plano do Codex deve ser dimensionado para 8 horas de execucao, com tolerancia operacional de ate 4 horas.
- Apos 12 horas, atualizar os documentos com tarefas concluidas, falhas, causas, bloqueios, evidencias e proximos passos.
- Criar ou atualizar uma issue de orquestracao vinculada a cada versao dos relatorios.
- O Codex deve iniciar pelo plano mais recente, verificar dependencias e nao declarar conclusao sem teste reproduzivel e evidencia no ambiente correto.
- Os relatorios devem ser inseridos no GitHub pela mesma branch e pull request da atualizacao das pendencias.

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

# Governanca inviolavel de marca

- A fonte de verdade dos ativos autorizados e `config/branding/authorized_assets.json`, complementada por `config/branding/brand_identity.json` e `assets/brand/README.md`.
- As marcas oficiais abrangidas sao All in One, Valley e Valley Riders.
- Sem autorizacao explicita do proprietario da marca, somente duas operacoes sao permitidas: remover exclusivamente o fundo externo sem tocar na arte e redimensionar proporcionalmente.
- E proibido redesenhar, recolorir, recortar, girar, distorcer, trocar tipografia, alterar linhas, curvas, formas ou composicao, aplicar filtros, mascaras ou opacidade decorativa, ou criar simbolo substituto.
- Todo ativo digital deve manter fundo externo totalmente transparente.
- Quando o binario original de uma marca nao estiver disponivel, o agente deve bloquear qualquer substituto ou aproximacao e registrar a pendencia. Nunca deve fabricar uma versao.
- Ao identificar uma violacao clara e objetiva dessa politica, o proprio agente deve restaurar o ativo canonico, executar `python3 scripts/check_brand_integrity.py --fix` e `python3 scripts/check_brand_integrity.py`, validar o repositorio e sincronizar a correcao em branch de trabalho com pull request. Nao e necessario solicitar nova autorizacao para restaurar conformidade.
- A autorizacao de remediacao imediata nao permite alterar a arte oficial nem tomar decisoes criativas sobre a marca.
