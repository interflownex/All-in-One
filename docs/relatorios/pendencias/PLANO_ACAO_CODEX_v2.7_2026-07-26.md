# Plano de Ação Estruturado para o Codex

**Versão:** 2.7  
**Data e hora:** 26/07/2026 às 23:06:33  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `docs/pendencias-documentacao-v2-7-telegram-2026-07-26`  
**Commit-base:** `77fa6fab5f1c881ba6289dc288dc64e20421614a`  
**Issue:** `#45`  
**Ciclo principal:** 8 horas  
**Tolerância:** até 4 horas  
**Nova coleta:** após 12 horas

## 1. Missão

Validar a consolidação documental v2.7, concluir o executor Telegram iniciado
nesta branch e reduzir o risco dos PRs paralelos antes de iniciar novas frentes.

## 2. Pré-requisitos

1. executar `git status --short --branch`;
2. atualizar referências remotas permitidas;
3. executar preflight multiagente;
4. adquirir lock da atividade;
5. confirmar ausência de merge ou rebase;
6. criar branch própria quando necessário;
7. preservar trabalho de outros agentes;
8. manter secrets fora do Git.

## 3. Fontes de verdade

- `AGENTS.md`;
- `docs/Pendências Do desenvolvedor.md` versão 2.7;
- `docs/STATUS_ATUAL.md`;
- `docs/DOCUMENTATION_INDEX.md`;
- `tarefas.md` versão 1.2;
- issue `#45`;
- PRs `#34`, `#36`, `#37`, `#38` e `#40`;
- política e executor Telegram.

## 4. Plano de 8 horas

### 0h a 1h: validar a consolidação

```bash
python3 scripts/audit_confirmation_v7.py
python3 scripts/validate_repository.py
python3 -m pytest -q tests/test_telegram_activity_reporter.py
```

- registrar versões, saídas e falhas;
- confirmar 24 módulos;
- confirmar ausência de Vision ativo;
- confirmar que documentação e código não divergem nos itens críticos.

### 1h a 2h30: concluir executor Telegram

- validar todos os subcomandos em `--dry-run`;
- validar campos obrigatórios da política;
- validar relatório com índices 1 a 4;
- testar retry e timeout com mocks;
- validar truncamento de mensagem;
- garantir que tokens não apareçam em exceções ou logs;
- documentar comandos de uso;
- não ativar cron antes dos testes passarem.

### 2h30 a 4h: regularizar PRs

- comparar `#34` e `#37` por arquivo;
- escolher uma única fonte de verdade;
- encerrar ou reduzir o PR duplicado;
- atualizar a base de `#36`, `#38` e `#40`;
- executar checks específicos de cada branch;
- impedir merge quando `mergeable=false`.

### 4h a 5h30: ambiente público e API Hub

- identificar o artefato que produz identidade temporária;
- validar domínio e HTTPS;
- obter URL oficial do API Hub;
- testar `/health`;
- validar CORS;
- registrar logs e commit do deploy;
- não contornar billing, IAM ou aceite jurídico.

### 5h30 a 7h: validar artefatos

#### APK Admin

- executar testes Gradle;
- gerar APK debug;
- instalar em emulador ou dispositivo;
- validar URL segura, conteúdo misto, navegação e arquivos locais;
- registrar hash do APK.

#### PDV Desktop

- executar testes de armazenamento, caixa e idempotência;
- gerar artefato Windows em ambiente autorizado;
- validar operação sem internet;
- validar backup, restauração e sincronização sem duplicidade;
- registrar hash do instalador.

### 7h a 8h: rastreabilidade

- atualizar issue `#45`;
- criar issues para falhas abertas;
- atualizar pendências, status, relatório, plano e `tarefas.md`;
- registrar commits, PRs, checks, artefatos e bloqueios;
- liberar lock.

## 5. Tolerância de 4 horas

Usar apenas para concluir, nesta ordem:

1. estabilizar testes da branch;
2. resolver conflito entre PRs;
3. concluir executor Telegram;
4. homologar `/health`;
5. terminar smoke tests de APK e PDV;
6. atualizar evidências.

Não iniciar nova frente grande durante a tolerância.

## 6. Critérios de aceite

- documentação autoritativa alinhada a 24 módulos;
- testes da implementação executados no commit atual;
- modo `--dry-run` Telegram aprovado;
- credenciais ausentes do Git e dos logs;
- decisão registrada para cada PR aberto;
- nenhum merge sem checks;
- issue `#45` atualizada;
- `tarefas.md` incrementado no fechamento;
- integração por Squash and Merge quando os gates permitirem.

## 7. Condições de parada

Parar diante de credencial ausente, lock de outro agente, conflito destrutivo,
necessidade de alterar marca sem autorização, ação administrativa do titular,
billing/IAM ou ausência de ambiente seguro para testar artefato.

## 8. Relatório após 12 horas

Registrar para cada atividade:

- status;
- percentual;
- falha;
- causa;
- ação realizada;
- evidência;
- bloqueio;
- possibilidade de resolução;
- pendências;
- próximo passo;
- commit e Pull Request.
