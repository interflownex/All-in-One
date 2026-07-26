# Tarefas da IA Desenvolvedora

**Versão:** 1.1  
**Data da entrega:** 26/07/2026  
**Hora da entrega:** 14:01:53  
**Fuso horário:** `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch de elaboração:** `docs/pendencias-v2-6-primeiro-teste-2026-07-26`  
**Commit de referência:** `c2c8eaccc1581ed674821feaaa3336c03a5b763c`  
**Issue de orquestração:** `#43`  
**Classificação:** `Pendências > Técnico > Equipe técnica`  
**Destino:** Codex e demais IAs desenvolvedoras autorizadas

## 1. Objetivo desta versão

Registrar o primeiro teste completo das diretrizes permanentes e fornecer à próxima IA desenvolvedora uma passagem operacional suficiente para executar o ciclo v2.6 sem depender de explicação adicional.

## 2. Resultado da varredura

### Confirmado

- catálogo e configuração Business sincronizados em 24 módulos;
- `legal`, `property` e `ai_core` presentes em `MODULE_NAMES`;
- auditor v7 versionado;
- referências ativas ao Vision removidas no escopo verificado;
- PR Render `#27` encerrado sem merge;
- política Telegram atualizada;
- watchdog Gemini restaurado;
- diretrizes de Estudar, Pesquisa Avançada, data, hora e `tarefas.md` integradas;
- issue `#28` encerrada;
- issue `#43` aberta para o ciclo v2.6.

### Pendente

- executar checks no commit atual;
- regularizar PRs `#34`, `#36`, `#37`, `#38` e `#40`;
- resolver sobreposição entre `#34` e `#37`;
- auditar commit `44be12a9751d336f0c8094f79c893eb69008eaf4` e o pacote `.gemini/skills`;
- corrigir identidade pública `tmp-valley`;
- homologar API Hub e `/health`;
- criar executor Telegram real;
- validar APK Admin;
- validar PDV Desktop;
- validar onda de inovação;
- concluir issue `#24` no Stitch;
- incorporar ativo oficial Valley Riders;
- impor administrativamente uso exclusivo de Squash and Merge.

## 3. Fontes de verdade

Antes de editar, consultar:

1. `AGENTS.md`;
2. este `tarefas.md`;
3. `docs/Pendências Do desenvolvedor.md`, versão 2.6;
4. `docs/relatorios/pendencias/RELATORIO_VARREDURA_STATUS_v2.6_2026-07-26.md`;
5. `docs/relatorios/pendencias/PLANO_ACAO_CODEX_v2.6_2026-07-26.md`;
6. issue `#43`;
7. PRs `#34`, `#36`, `#37`, `#38` e `#40`;
8. issues `#24`, `#39` e `#41`;
9. `scripts/audit_confirmation_v7.py`;
10. `config/autonomy/telegram_delivery_policy.json`;
11. manifestos de skills em `.gemini/skills` e `.github/skills`.

## 4. Pré-requisitos obrigatórios

1. executar `git status --short --branch`;
2. buscar referências remotas permitidas;
3. executar `python3 scripts/multi_agent_sync_guard.py preflight --integrate`;
4. adquirir lock da atividade;
5. confirmar ausência de merge ou rebase em andamento;
6. criar branch de trabalho se estiver na `main`;
7. preservar mudanças de outros agentes;
8. confirmar que nenhum segredo será versionado.

## 5. Ordem de execução

### Prioridade 1: checks e auditoria

- executar auditor v7;
- executar validação do repositório;
- executar testes relacionados;
- registrar checks ausentes ou falhos.

### Prioridade 2: PRs desatualizados

- comparar os cinco PRs com a `main` atual;
- resolver sobreposição `#34` e `#37`;
- atualizar, dividir ou encerrar PRs substituídos;
- não integrar PR com base antiga ou `mergeable` falso.

### Prioridade 3: pacote de skills

- auditar commit `44be12a`;
- comparar manifestos;
- identificar remoções, restaurações e alterações de conteúdo;
- abrir issue se a atualização não for reproduzível.

### Prioridade 4: ambiente público

- corrigir identificação `tmp-valley`;
- validar Render, URL do API Hub e `/health`;
- registrar CORS, logs e bloqueios externos.

### Prioridade 5: Telegram

- implementar `activity_started`;
- implementar `activity_completed`;
- implementar quatro relatórios diários;
- criar retry, timeout, mocks e logs seguros.

### Prioridade 6: artefatos

- validar APK Admin do PR `#36`;
- validar PDV Desktop do PR `#38`;
- registrar hash, versão, commit e smoke test.

### Prioridade 7: encerramento

- atualizar issue `#43`;
- atualizar pendências e relatórios;
- incrementar a versão deste arquivo;
- abrir ou atualizar PR;
- integrar apenas com checks e Squash and Merge;
- liberar lock.

## 6. Ciclo de tempo

- execução principal: 8 horas;
- tolerância normal: até 4 horas;
- limite de coleta: 12 horas;
- após 12 horas, não iniciar nova frente e registrar tudo que restou.

## 7. Testes mínimos esperados

```bash
python3 scripts/audit_confirmation_v7.py
python3 scripts/validate_repository.py
```

Executar também testes específicos de cada PR e componente alterado. Não usar resultados antigos como prova do commit atual.

## 8. Critérios de aceite

Uma tarefa só pode ser concluída quando houver:

- implementação versionada;
- teste reproduzível;
- evidência do ambiente correto;
- referência ao commit e PR;
- checks executados;
- ausência de regressão relevante;
- confirmação de que nenhum segredo foi exposto;
- atualização da issue `#43`;
- atualização deste `tarefas.md`.

## 9. Riscos e bloqueios

- PRs antigos podem sobrescrever correções mais novas;
- PRs `#34` e `#37` podem duplicar alterações;
- APK e instalador podem existir sem homologação real;
- domínio público possui identidade temporária;
- pacote de skills teve mudança ampla sem PR localizado;
- Telegram possui política, mas não executor completo localizado;
- repositório ainda permite métodos de merge além de squash;
- credenciais externas podem bloquear Render, Google, Stitch e Telegram.

## 10. Entrega obrigatória da próxima IA

A próxima IA deve entregar:

1. resumo simples para o gestor;
2. lista do que foi concluído, parcial, falhou e bloqueou;
3. comandos e testes executados;
4. evidências e artefatos;
5. commits e pull requests;
6. atualização da issue `#43`;
7. nova versão dos relatórios, quando houver mudança;
8. nova versão de `tarefas.md` com data e hora;
9. integração por Squash and Merge quando os critérios forem atendidos.

## 11. Histórico de versões

| Versão | Data e hora | Alteração principal |
|---|---|---|
| 1.0 | 26/07/2026 13:49:32 | Criação da diretriz permanente de Estudar, Pesquisa Avançada, versionamento e entrega do arquivo `tarefas.md`. |
| 1.1 | 26/07/2026 14:01:53 | Primeiro teste completo, consolidação v2.6, issue #43 e tarefas para checks, PRs, skills, ambiente público, Telegram, APK Admin e PDV Desktop. |
