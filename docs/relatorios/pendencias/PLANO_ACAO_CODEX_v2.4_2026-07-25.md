# Plano de Ação Estruturado para o Codex

**Versão:** 2.4  
**Data:** 25/07/2026  
**Repositório:** `interflownex/All-in-One`  
**Issue de orquestração:** `#28`  
**Ciclo principal:** 8 horas  
**Tolerância operacional:** até 4 horas adicionais  
**Limite para nova coleta:** 12 horas

## Missão

Assumir a postura de desenvolvedora sênior, executar o ciclo técnico de maior valor e devolver evidências reproduzíveis. O Codex deve trabalhar a partir de:

- `docs/Pendências Do desenvolvedor.md`;
- `docs/relatorios/pendencias/RELATORIO_VARREDURA_STATUS_v2.4_2026-07-25.md`;
- issue `#28`.

## Regras obrigatórias

1. executar `git status --short --branch` antes de qualquer alteração;
2. executar o preflight multiagente e adquirir lock;
3. criar ou usar branch de trabalho, nunca alterar a `main` diretamente;
4. não descartar alterações de outro agente;
5. não inserir credenciais no Git;
6. executar testes relacionados às alterações;
7. publicar branch e abrir ou atualizar pull request;
8. usar Squash and Merge após revisão e checks;
9. atualizar a issue `#28` com progresso, falhas e evidências;
10. não declarar conclusão apenas porque existe código ou configuração.

## Resultado esperado do ciclo

Ao final das 8 horas, entregar o máximo possível desta sequência:

1. implantação Render validada ou bloqueio real documentado;
2. PR `#27` atualizado ou encerrado como substituído;
3. governança dos agentes alinhada a branch, PR e squash;
4. workflows executados e resultados registrados;
5. auditor v7 restaurado ou primeira versão reproduzível criada;
6. divergência dos quatro módulos corrigida e testada;
7. backlog ampliado com issues rastreáveis;
8. relatórios e issue `#28` atualizados.

## Plano de 8 horas

### Bloco 1: 0h a 1h30 — Validar a Render

**Atividades**

- revisar `.python-version`, `main.py`, `requirements.txt`, `pyproject.toml` e `render.yaml`;
- confirmar que o entrypoint importa corretamente o API Hub;
- validar instalação das dependências;
- executar importação ou atualização do Blueprint no ambiente autorizado;
- registrar logs de build e inicialização;
- validar o endpoint `/health`;
- registrar URL pública quando disponível.

**Critério de aceite**

URL e `/health` funcionais, ou bloqueio externo documentado com causa e próximo passo.

### Bloco 2: 1h30 a 2h — Regularizar o PR #27

**Atividades**

- comparar a branch do PR com a `main` atual;
- identificar arquivos e commits já substituídos;
- atualizar a branch quando ainda houver valor;
- encerrar como substituído quando o conteúdo já estiver integralmente na `main`;
- impedir regressão do Blueprint.

**Critério de aceite**

Nenhum PR aberto deve propor uma versão antiga dos arquivos Render sem justificativa explícita.

### Bloco 3: 2h a 3h — Governança Git e agentes

**Atividades**

- validar as novas orientações de `AGENTS.md`;
- revisar `config/autonomy/git_auto_sync_policy.json`;
- revisar scripts de sincronização automática;
- impedir push direto na `main`;
- garantir uso de branch de trabalho;
- preparar ajuste administrativo para permitir somente squash.

**Critério de aceite**

Fluxo reproduzível por branch, PR, checks e squash, sem instruções conflitantes.

### Bloco 4: 3h a 4h — Executar os gates

**Atividades**

- executar testes do API Hub;
- executar validações de integridade visual;
- executar os workflows aplicáveis;
- registrar logs e resultados;
- abrir issues para falhas não resolvidas no ciclo.

**Critério de aceite**

Resultados associados ao commit ou ao PR, com falhas claramente rastreadas.

### Bloco 5: 4h a 5h30 — Restaurar auditoria v7

**Atividades**

- localizar ou recriar `scripts/audit_confirmation_v7.py`;
- comparar diretórios, catálogo, aplicações, OpenAPI, manifests e configuração Business;
- criar saída Markdown reproduzível;
- adicionar teste ou gate de CI;
- salvar artefato da execução.

**Critério de aceite**

Outra pessoa autorizada consegue repetir a varredura no mesmo commit e obter resultado equivalente.

### Bloco 6: 5h30 a 7h — Corrigir os quatro módulos

**Atividades**

- incluir `vision`, `legal`, `property` e `ai_core` em `MODULE_NAMES`;
- definir nomes em pt-BR;
- revisar presets, visibilidade, dependências e recomendações;
- criar testes unitários;
- executar a auditoria atualizada.

**Critério de aceite**

Catálogo e configuração Business apresentam o mesmo conjunto de módulos, com testes aprovados.

### Bloco 7: 7h a 8h — Rastreabilidade e retomada

**Atividades**

- atualizar a issue `#28`;
- criar issues para pendências críticas ainda sem rastreamento;
- registrar commits, PRs, testes, URLs, logs e bloqueios;
- atualizar os dois relatórios v2.4;
- manter a issue `#24` preparada para o fluxo Jules + Stitch sem duplicar projeto ou tela.

**Critério de aceite**

O gestor consegue identificar imediatamente o que foi concluído, o que falhou e qual é a próxima ação.

## Tolerância de 4 horas

Caso o ciclo principal ultrapasse 8 horas, usar a tolerância nesta ordem:

1. concluir a homologação Render e registrar evidências;
2. resolver falhas de CI diretamente causadas pelas alterações do ciclo;
3. concluir o auditor v7;
4. finalizar a correção dos quatro módulos;
5. ampliar o backlog;
6. preparar a retomada da issue `#24`.

Não iniciar grandes frentes novas durante a tolerância quando houver tarefas do ciclo principal incompletas.

## Atualização obrigatória após 12 horas

Atualizar os relatórios e a issue `#28` com:

- atividade;
- descrição técnica;
- status final;
- percentual concluído;
- falha detectada;
- causa da falha;
- ação realizada;
- possibilidade de resolução;
- evidências;
- pendências restantes;
- próximos passos.

## Formato dos commits e pull request

- commits pequenos e rastreáveis na branch de trabalho;
- título do PR em português do Brasil;
- descrição com objetivo, alterações, testes, evidências, riscos e pendências;
- integração final por Squash and Merge;
- nenhum dado sensível no código, logs ou documentos.

## Condições de parada

Parar e registrar bloqueio quando houver:

- credencial legítima ausente;
- aceite jurídico ou billing obrigatório;
- conflito ou lock de outro agente;
- risco de sobrescrever trabalho alheio;
- necessidade de alterar ativo oficial sem autorização;
- falha que exija decisão do proprietário do projeto.
