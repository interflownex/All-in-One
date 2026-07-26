# Plano de Ação Estruturado para o Codex

**Versão:** 2.5  
**Data:** 26/07/2026  
**Repositório:** `interflownex/All-in-One`  
**Issue de orquestração:** `#28`  
**Ciclo principal:** 8 horas  
**Tolerância operacional:** até 4 horas adicionais  
**Limite para nova coleta:** 12 horas

## Missão

Assumir a postura de desenvolvedora sênior, executar o ciclo técnico de maior valor e devolver evidências reproduzíveis. O Codex deve trabalhar a partir de:

- `docs/Pendências Do desenvolvedor.md` (v2.5);
- `docs/relatorios/pendencias/RELATORIO_VARREDURA_STATUS_v2.5_2026-07-26.md`;
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

1. referências residuais ao Vision limpas nos ~40 arquivos identificados;
2. `MODULE_NAMES` atualizado com `legal`, `property` e `ai_core`;
3. implantação Render validada ou bloqueio real documentado;
4. PR `#27` atualizado ou encerrado como substituído;
5. workflows executados e resultados registrados;
6. auditor v7 restaurado ou primeira versão reproduzível criada;
7. backlog ampliado com issues rastreáveis;
8. relatórios e issue `#28` atualizados.

## Plano de 8 horas

### Bloco 1: 0h a 1h — Limpar referências residuais ao Vision

**Atividades**

- abrir o relatório `docs/relatorios/remocao-vision/RELATORIO_REMOCAO_VISION_STOCK_2026-07-25.md`;
- percorrer a lista de ~40 arquivos com referências residuais;
- priorizar os arquivos com impacto em execução: `modules/api_hub/main.py`, `modules/identity/main.py`, `modules/shared/valley_catalog.py`;
- remover importações, rotas e referências ao Vision sem alterar comportamento dos demais módulos;
- verificar `apps/valley/src/lib/valleyPlatform.ts` e arquivos de front-end;
- confirmar que testes adaptados do Vision não causam erro de importação.

**Critério de aceite**

Varredura por `grep -r "vision" --include="*.py" --include="*.ts" --include="*.tsx" modules/ apps/ tests/ scripts/` retorna apenas histórico legado, sem referências ativas.

### Bloco 2: 1h a 2h — Atualizar MODULE_NAMES

**Atividades**

- abrir `modules/business/module_settings.py`;
- adicionar `legal`, `property` e `ai_core` ao dicionário `MODULE_NAMES`;
- definir nomes em pt-BR coerentes com o catálogo;
- revisar presets (`physical_store`, `ecommerce`, `restaurant`, etc.) para classificar os novos módulos como `hidden` ou `recommended` conforme pertinência;
- criar testes unitários cobrindo os três módulos;
- executar pytest nos testes de módulo.

**Critério de aceite**

`MODULE_NAMES` possui 24 entradas; testes passam; nenhum preset deixa módulo sem classificação.

### Bloco 3: 2h a 3h30 — Validar a Render

**Atividades**

- revisar `render.yaml`, `main.py`, `requirements.txt` e `pyproject.toml`;
- confirmar que o entrypoint importa corretamente o API Hub;
- confirmar que `modules/api_hub/main.py` não tem referências ao Vision;
- executar implantação no ambiente autorizado ou coletar bloqueio real;
- registrar logs de build e inicialização;
- validar o endpoint `/health`;
- registrar URL pública quando disponível.

**Critério de aceite**

URL pública acessível com HTTP 200 em `/health` e log de inicialização arquivado, ou bloqueio técnico documentado com causa precisa.

### Bloco 4: 3h30 a 4h30 — Regularizar o PR `#27`

**Atividades**

- comparar o estado do PR `#27` com o commit `cbbe7bd61bdf13604f5d71167dc5b54f7435cffa`;
- verificar se há conflitos ou arquivos desatualizados;
- decidir: atualizar o PR para refletir o estado atual, ou encerrá-lo como substituído;
- documentar a decisão com justificativa e link ao commit de referência;
- evitar integração duplicada do Blueprint.

**Critério de aceite**

PR `#27` atualizado ou fechado com comentário explicativo; sem risco de regressão.

### Bloco 5: 4h30 a 5h30 — Executar workflows

**Atividades**

- identificar os workflows relevantes em `.github/workflows/`;
- verificar quais podem ser executados no commit atual sem credencial ausente;
- executar os workflows disponíveis e arquivar resultados;
- registrar falhas como issues rastreáveis;
- verificar se `.github/workflows/apply-remove-vision-update-stock.yml` deve ser executado ou arquivado.

**Critério de aceite**

Ao menos um workflow executado com resultado registrado; falhas documentadas como issues.

### Bloco 6: 5h30 a 7h — Restaurar o auditor v7

**Atividades**

- localizar ou recriar `scripts/audit_confirmation_v7.py`;
- definir escopo: catálogo de módulos, OpenAPI, contratos, configuração Business;
- executar no commit atual e salvar relatório em `docs/relatorios/`;
- integrar à CI se possível;
- publicar resultado como artefato ou arquivo versionado.

**Critério de aceite**

Outra pessoa autorizada consegue repetir a varredura no mesmo commit e obter resultado equivalente.

### Bloco 7: 7h a 8h — Rastreabilidade e retomada

**Atividades**

- atualizar a issue `#28` com progresso, falhas, bloqueios e evidências;
- criar issues para pendências críticas ainda sem rastreamento;
- registrar commits, PRs, testes, URLs, logs e bloqueios;
- atualizar os dois relatórios v2.5;
- manter a issue `#24` preparada para o fluxo Stitch sem duplicar projeto ou tela.

**Critério de aceite**

O gestor consegue identificar imediatamente o que foi concluído, o que falhou e qual é a próxima ação.

## Tolerância de 4 horas

Caso o ciclo principal ultrapasse 8 horas, usar a tolerância nesta ordem:

1. concluir a limpeza das referências residuais ao Vision;
2. concluir a homologação Render e registrar evidências;
3. resolver falhas de CI diretamente causadas pelas alterações do ciclo;
4. concluir o auditor v7;
5. finalizar a correção dos três módulos;
6. ampliar o backlog;
7. preparar a retomada da issue `#24`.

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
