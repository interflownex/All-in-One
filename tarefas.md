# Tarefas da IA Desenvolvedora

**Versao:** 1.0  
**Data da entrega:** 26/07/2026  
**Hora da entrega:** 13:49:32  
**Fuso horario:** `America/Sao_Paulo`  
**Repositorio:** `interflownex/All-in-One`  
**Branch de elaboracao:** `docs/diretriz-tarefas-estudo-pesquisa-2026-07-26`  
**Commit de referencia da varredura:** `44be12a9751d336f0c8094f79c893eb69008eaf4`  
**Classificacao:** `Pendencias > Tecnico > Equipe tecnica`  
**Destino:** Codex e demais IAs desenvolvedoras autorizadas

## 1. Objetivo

Estabelecer a diretriz permanente de entrega tecnica do projeto All-in-One + Valley, garantindo que toda atividade seja estudada, pesquisada, versionada, registrada com data e hora e encerrada com um arquivo `tarefas.md` completo para a proxima IA desenvolvedora.

## 2. Regra permanente de modo Estudar

A IA desenvolvedora deve trabalhar com abordagem de estudo em toda atividade:

1. verificar o conhecimento e o estado ja existentes;
2. consultar as fontes de verdade antes de editar;
3. explicar e documentar decisoes tecnicas relevantes;
4. dividir problemas complexos em etapas verificaveis;
5. validar o entendimento por testes e evidencias;
6. registrar o que foi aprendido, alterado e deixado pendente.

Quando a interface nao oferecer um controle persistente para o plugin Estudar, aplicar obrigatoriamente o comportamento equivalente descrito acima.

## 3. Regra permanente de Pesquisa Avancada

Antes de orientar ou implementar qualquer item baseado em informacao externa, atual, instavel, especializada ou possivelmente desatualizada, a IA deve:

1. realizar pesquisa avancada em fontes atuais e confiaveis;
2. priorizar documentacao oficial e fontes primarias;
3. comparar datas de publicacao e vigencia;
4. registrar as fontes utilizadas no relatorio ou pull request;
5. separar fatos confirmados de inferencias;
6. nao declarar certeza quando a evidencia for incompleta.

Quando a interface nao oferecer um controle persistente para o plugin Pesquisa Avancada, aplicar o comportamento equivalente por consulta web, documentacao oficial e verificacao cruzada.

## 4. Fontes de verdade do projeto

Antes de qualquer alteracao, consultar no minimo:

- `AGENTS.md`;
- `tarefas.md`;
- `docs/Pendências Do desenvolvedor.md`;
- relatorio mais recente em `docs/relatorios/pendencias/`;
- plano mais recente do Codex em `docs/relatorios/pendencias/`;
- issues e pull requests abertos;
- `config/module_catalog.json`;
- contratos OpenAPI e migrations relacionados;
- arquivos de estado Stitch quando a atividade envolver interfaces;
- politicas em `config/autonomy/`;
- manifesto de marca em `config/branding/authorized_assets.json`.

## 5. Pre-requisitos obrigatorios

Antes de editar:

1. executar `git status --short --branch`;
2. atualizar referencias remotas permitidas;
3. executar o preflight multiagente;
4. adquirir o lock da atividade;
5. confirmar que nao existe merge ou rebase em andamento;
6. confirmar que nenhum segredo sera versionado;
7. criar ou usar branch de trabalho;
8. verificar se a tarefa ja foi implementada por outro agente.

## 6. Fluxo de execucao

1. estudar o problema e o contexto existente;
2. pesquisar informacoes externas quando necessario;
3. mapear implementado, parcial, ausente e bloqueado;
4. definir escopo, riscos e criterios de aceite;
5. executar alteracoes pequenas e rastreaveis;
6. criar ou atualizar testes;
7. executar validacoes locais e workflows aplicaveis;
8. registrar evidencias;
9. atualizar documentacao e pendencias;
10. atualizar este arquivo `tarefas.md`;
11. publicar branch;
12. abrir ou atualizar pull request;
13. integrar somente apos revisao e checks, usando Squash and Merge;
14. liberar o lock multiagente.

## 7. Conteudo obrigatorio de toda entrega

Toda entrega deve informar:

- versao;
- data;
- hora;
- fuso horario;
- repositorio;
- branch;
- commit de referencia;
- objetivo;
- escopo executado;
- arquivos alterados;
- testes realizados;
- resultados;
- falhas e causas;
- riscos;
- bloqueios externos;
- evidencias;
- pendencias restantes;
- proximos passos;
- pull request e commit final, quando existirem.

## 8. Regras do arquivo `tarefas.md`

1. o nome deve permanecer exatamente `tarefas.md`;
2. o arquivo deve existir na raiz do repositorio;
3. deve ser atualizado ao final de toda entrega tecnica;
4. cada atualizacao deve incrementar a versao;
5. deve informar data e hora no fuso `America/Sao_Paulo`;
6. deve conter instrucoes suficientes para a proxima IA continuar sem nova explicacao;
7. deve ser versionado na mesma branch e pull request da atividade;
8. deve preservar um historico resumido de versoes;
9. nao pode conter credenciais, tokens, chaves ou dados pessoais desnecessarios;
10. nao substitui os relatorios de pendencias, mas funciona como documento de passagem operacional.

## 9. Testes e evidencias

Nenhuma atividade deve ser marcada como concluida sem:

- teste automatizado ou procedimento reproduzivel;
- saida ou log verificavel;
- evidencia do ambiente correto;
- referencia ao commit e pull request;
- confirmacao de que nao houve regressao relevante;
- confirmacao de que nenhum segredo foi exposto.

## 10. Governanca Git

- nunca executar push direto na `main`;
- usar branch de trabalho;
- abrir pull request;
- registrar testes e evidencias;
- usar Squash and Merge;
- nao descartar trabalho de outros agentes;
- nao executar `git reset --hard` ou limpeza destrutiva sem ordem explicita;
- interromper e registrar bloqueio em caso de conflito, lock ou rebase ativo.

## 11. Estado verificado nesta entrega

- a branch padrao e `main`;
- o repositorio permite atualmente merge commit, rebase merge e squash merge;
- o uso administrativo exclusivo de Squash and Merge continua pendente;
- o documento `AGENTS.md` foi atualizado nesta atividade para registrar as novas regras;
- este e o primeiro arquivo raiz `tarefas.md` identificado no repositorio.

## 12. Criterio de aceite desta diretriz

A diretriz sera considerada implantada quando:

1. `AGENTS.md` contiver as regras de Estudar, Pesquisa Avancada, data, hora e `tarefas.md`;
2. o arquivo raiz `tarefas.md` estiver versionado;
3. a alteracao estiver em pull request;
4. a integracao ocorrer por Squash and Merge;
5. a branch `main` contiver os dois arquivos atualizados.

## 13. Pendencias administrativas relacionadas

1. desabilitar `merge commit` no repositorio;
2. desabilitar `rebase merge`;
3. manter apenas `squash merge`;
4. proteger a branch `main`;
5. exigir checks obrigatorios e revisao antes do merge.

## 14. Historico de versoes

| Versao | Data e hora | Alteracao principal |
|---|---|---|
| 1.0 | 26/07/2026 13:49:32 | Criacao da diretriz permanente de modo Estudar, Pesquisa Avancada, versionamento, data, hora e entrega obrigatoria do arquivo `tarefas.md`. |
