# Preferência obrigatória de idioma

- Todas as respostas, alertas, erros, orientações, perguntas e opções devem ser escritos em português do Brasil.
- Códigos, nomes de arquivos, comandos, identificadores, logs e mensagens externas permanecem no idioma ou formato original quando isso preservar precisão técnica.

# Modo Estudar, Pesquisa Avançada e entrega `tarefas.md`

- Toda atividade deve aplicar abordagem de estudo: verificar conhecimento existente, consultar fontes de verdade, explicar decisões, dividir problemas em etapas verificáveis e registrar evidências.
- Toda informação externa, atual, instável ou especializada deve ser verificada em fontes atuais e confiáveis antes de orientar implementação ou declarar conclusão.
- Quando a interface não oferecer seletor persistente para Estudar ou Pesquisa Avançada, aplicar o comportamento equivalente.
- Toda entrega deve informar versão, data, hora, fuso `America/Sao_Paulo`, repositório, branch e commit de referência.
- Ao final de toda entrega técnica, criar ou atualizar o arquivo raiz `tarefas.md`.
- `tarefas.md` deve conter objetivo, contexto, fontes de verdade, pré-requisitos, sequência, prioridades, testes, critérios de aceite, riscos, bloqueios, evidências, pendências e procedimento de entrega.
- Cada atualização de `tarefas.md` incrementa a versão e preserva histórico resumido.
- Nenhuma tarefa é concluída apenas pela existência de código ou documento. São obrigatórios teste reproduzível, evidência no ambiente correto e referência ao commit e Pull Request.

# Revisão consolidada de documentação

- Toda revisão geral deve confrontar documentação, código, catálogo, contratos, migrations, workflows, issues e Pull Requests.
- A revisão deve atualizar no mesmo ciclo os documentos autoritativos: `README.md`, `docs/ROADMAP.md`, `docs/Pendências Do desenvolvedor.md`, `docs/STATUS_ATUAL.md`, `docs/DOCUMENTATION_INDEX.md`, relatórios versionados e `tarefas.md`.
- `STATUS.md` e documentos extensos antigos são registros históricos. Não devem ser apagados nem tratados como estado atual sem confirmação.
- Documentos gerados, inventários de dados e tabelas históricas devem ser classificados no índice documental. Referências históricas ao Vision não reativam o módulo.
- Após gerar o relatório e o plano do ciclo, iniciar pelo menos uma implementação técnica priorizada quando ela puder ser executada com segurança e sem credenciais ausentes.
- A implementação iniciada deve ficar na mesma branch do ciclo ou em branch explicitamente vinculada, com issue, testes e critérios de aceite.

# Sincronização Git obrigatória e segura

- Ao concluir atividade que altere arquivos, versionar o trabalho no Git.
- Antes de editar, executar `git status --short --branch`, integrar referências remotas permitidas e preservar mudanças existentes.
- Se a branch atual for `main`, criar branch de trabalho. Padrão recomendado: `codex/<atividade>-<data>`.
- Executar o preflight multiagente e adquirir lock antes de alterações locais.
- O push deve usar branch de trabalho. É proibido push direto na `main`.
- Ao finalizar, abrir ou atualizar Pull Request, registrar testes e evidências e usar Squash and Merge.
- Quando a abertura do Pull Request não estiver disponível, manter a branch publicada e registrar o bloqueio.
- Não criar commit vazio.
- A mensagem de commit deve ser concisa, rastreável e escrita em português do Brasil.
- Em merge ou rebase ativo, parar e registrar o bloqueio.
- Nunca executar `git reset --hard`, limpeza destrutiva ou descarte de trabalho alheio sem ordem explícita.

# Orquestração obrigatória de pendências

- A fonte principal é `docs/Pendências Do desenvolvedor.md`.
- Toda atualização incrementa versão e registra data, hora, branch e commit.
- Gerar obrigatoriamente em `docs/relatorios/pendencias/`:
  1. `RELATORIO_VARREDURA_STATUS_v<versao>_<AAAA-MM-DD>.md`;
  2. `PLANO_ACAO_CODEX_v<versao>_<AAAA-MM-DD>.md`.
- O relatório deve conter a tabela: Nome da atividade | Descrição | Passo sendo executado | Dificuldade [1 a 5] | % concluído | Tempo previsto | Etapas [Total] | Concluídas [X] | Pendentes [Y].
- O plano deve ser dimensionado para 8 horas, com tolerância de até 4 horas.
- Após 12 horas, atualizar concluído, falhas, causas, bloqueios, evidências e próximos passos.
- Criar ou atualizar issue de orquestração vinculada a cada versão.
- O Codex inicia pelo plano mais recente e não declara conclusão sem teste e evidência.

# Alinhamento multiagente

- Codex CLI, Antigravity, Gemini Code Assist e Gemini CLI seguem `config/autonomy/multi_agent_sync_policy.json`.
- Git é a fonte de verdade compartilhada. Nenhum agente sobrescreve trabalho de outro sem integrar primeiro.
- Executar `python3 scripts/multi_agent_sync_guard.py preflight --integrate` e adquirir lock com `python3 scripts/multi_agent_sync_guard.py acquire --agent <agent_id> --activity "<descricao>"`.
- Liberar o lock ao concluir.
- Buscar `origin/main` e `fork/main` quando acessíveis.
- Preservar `config/stitch/screen_manifest.json` e `config/stitch/sync_state.json`.
- Segredos permanecem em variáveis de ambiente, GitHub Actions Secrets ou cofres externos.

# Integrações Google ativas

- Google SDK, Google AI Studio, Google Cloud, AlloyDB, Google Code CLI, Gemini CLI, Gemini Code Assist e Google Stitch permanecem ativos por ordem do usuário.
- A política obrigatória fica em `config/autonomy/google_integrations_policy.json`.
- Operações podem executar quando credenciais legítimas estiverem disponíveis fora do Git.
- Não contornar billing, IAM, compliance ou enforcement do provedor.

# Governança inviolável de marca

- A fonte de verdade é `config/branding/authorized_assets.json`, complementada por `config/branding/brand_identity.json` e `assets/brand/README.md`.
- As marcas oficiais são All in One, Valley e Valley Riders.
- Sem autorização, somente remover o fundo externo sem tocar na arte e redimensionar proporcionalmente.
- É proibido redesenhar, recolorir, recortar, girar, distorcer, trocar tipografia, alterar linhas, curvas, formas ou composição, aplicar filtros ou criar substitutos.
- Todo ativo digital deve manter fundo externo transparente.
- Quando o binário original não estiver disponível, bloquear substitutos e registrar pendência.
- Violações objetivas devem ser restauradas ao ativo canônico e validadas em branch com Pull Request.