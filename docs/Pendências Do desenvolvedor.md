# Pendências do Desenvolvedor

**Versão:** 2.7  
**Data da verificação:** 26/07/2026  
**Hora da entrega:** 23:06:33  
**Fuso horário:** `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch de elaboração:** `docs/pendencias-documentacao-v2-7-telegram-2026-07-26`  
**Commit-base:** `77fa6fab5f1c881ba6289dc288dc64e20421614a`  
**Versão anterior:** 2.6  
**Issue de orquestração:** `#45`  
**Classificação:** `Pendências > Técnico > Equipe técnica`  
**Contextos:** técnico, comercial, produto, conceito e governança  
**Públicos:** Pessoa Física, Pessoa Jurídica, equipe técnica, gestão e investidores

## 1. Objetivo

Consolidar em uma única versão o estado das pendências e da documentação,
corrigir divergências autoritativas e iniciar uma implementação técnica após a
geração do novo relatório e do plano de tarefas.

## 2. Regra de leitura

Em caso de divergência, prevalecem nesta ordem:

1. `config/module_catalog.json`;
2. `AGENTS.md`;
3. este documento;
4. `docs/STATUS_ATUAL.md`;
5. relatório e plano v2.7;
6. `tarefas.md` versão 1.2;
7. código, contratos, migrations e testes do commit analisado.

`STATUS.md`, versões anteriores dos relatórios e inventários gerados são
históricos. Eles preservam evidências, mas não substituem o estado atual.

## 3. Avanços confirmados

1. Catálogo oficial consolidado em 24 módulos ativos.
2. `MODULE_NAMES` contém `legal`, `property` e `ai_core`.
3. Vision foi removido do catálogo operacional.
4. Auditor v7 está versionado em `scripts/audit_confirmation_v7.py`.
5. PR Render `#27` foi encerrado sem merge.
6. Regras permanentes de Estudar, Pesquisa Avançada e `tarefas.md` estão em `AGENTS.md`.
7. Issue `#45` foi aberta para o ciclo v2.7.
8. README e Roadmap foram corrigidos nesta branch para a baseline de 24 módulos.
9. A implementação do executor Telegram foi iniciada nesta versão.

## 4. Divergências documentais encontradas

1. `README.md` ainda declarava 25 microserviços, em conflito com o catálogo de 24 módulos.
2. `docs/ROADMAP.md` ainda registrava 25 domínios e stores.
3. `docs/EXECUTION_PLAN.md` possui referências históricas a `worktree-sync`, 25 módulos e estados de 19/07/2026.
4. `STATUS.md` é um diário extenso com estados de várias datas e não deve ser usado sozinho como fotografia atual.
5. `docs/OPERATIONS.md` ainda menciona suíte viva de 25 stores.
6. Inventários em `docs/data-audit/` preservam tabelas Vision históricas. Devem ser marcados como histórico, não apagados automaticamente.
7. PRs antigos alteram centenas de documentos gerados e podem reintroduzir divergências caso sejam integrados sem atualização da base.

## 5. Estado dos Pull Requests abertos

| PR | Escopo | Estado de risco | Decisão necessária |
|---|---|---|---|
| `#34` | Contratos, banco, segurança, CI e documentação gerada | Muito amplo e baseado em estado antigo | Comparar com `#37`; não integrar diretamente |
| `#36` | APK Admin | Artefato e URL precisam de homologação | Atualizar base, executar build e smoke test |
| `#37` | Estabilização derivada do `#34` | Forte sobreposição com `#34` | Escolher fonte de verdade e encerrar duplicado |
| `#38` | PDV Desktop offline | Precisa validar instalador, idempotência e segurança | Atualizar base e executar testes Windows |
| `#40` | Onda de inovação dos 24 módulos | Rascunho, flags desligadas, gates pendentes | Atualizar base e validar fundação |

Os PRs `#34` e `#37` compartilham a maior parte dos arquivos de contratos,
configuração, auditoria de dados, módulos e testes. Integrá-los separadamente
criaria risco alto de duplicidade e regressão.

## 6. Contagem consolidada

| Classificação | Quantidade |
|---|---:|
| Críticas | 5 |
| Altas | 18 |
| Médias | 8 |
| Secundárias | 2 |
| Concluídas com evidência registrada | 5 |
| Em implementação nesta versão | 1 |

## 7. Quadro obrigatório de acompanhamento

| Nome da atividade | Descrição | Passo sendo executado | Dificuldade [1 a 5] | % concluído | Tempo previsto | Etapas [Total] | Concluídas [X] | Pendentes [Y] |
|---|---|---|---:|---:|---|---:|---:|---:|
| Consolidação documental | Alinhar documentação autoritativa | Atualizar índice, README, Roadmap, status e tarefas | 4 | 80% | 2h | 10 | 8 | 2 |
| Publicação externa | Homologar domínio, HTTPS e identidade | Corrigir identidade temporária e registrar URL oficial | 5 | 50% | 2h | 6 | 3 | 3 |
| API Hub público | Publicar backend e conectar front-end | Obter URL, logs, CORS e `/health` | 5 | 60% | 2h | 7 | 4 | 3 |
| Auditoria de rotas | Validar 325 rotas contra backend vivo | Aguardar ambiente homologado | 5 | 35% | 2h30 | 6 | 2 | 4 |
| GitHub Actions | Tornar checks obrigatórios | Executar gates no commit atual | 5 | 25% | 2h | 5 | 1 | 4 |
| Governança de merge | Manter apenas PR e Squash and Merge | Alterar configurações administrativas | 4 | 45% | 1h | 5 | 2 | 3 |
| Triage de PRs | Regularizar `#34`, `#36`, `#37`, `#38`, `#40` | Comparar bases e sobreposição | 5 | 15% | 2h | 8 | 1 | 7 |
| APK Admin | Validar entrega do PR `#36` | Executar build e instalação | 4 | 55% | 2h | 6 | 3 | 3 |
| PDV Desktop | Validar PR `#38` | Executar testes e empacotamento Windows | 5 | 60% | 3h | 8 | 4 | 4 |
| Onda de inovação | Validar PR `#40` | Executar gates com flags desligadas | 4 | 35% | 2h | 7 | 3 | 4 |
| Telegram executável | Enviar eventos e relatórios | Implementar CLI, retry, dry-run e testes | 4 | 60% | 2h | 7 | 4 | 3 |
| Stitch | Sincronizar projeto oficial | Aguardar secret legítimo e validar manifestos | 4 | 35% | 2h | 6 | 2 | 4 |
| Promoção do Dia | Implementar issue `#24` | Manter execução no projeto Stitch existente | 4 | 5% | 3h | 7 | 0 | 7 |
| Valley Riders | Incorporar ativo oficial | Aguardar PNG original aprovado | 3 | 35% | 45min | 4 | 1 | 3 |
| Auditoria de skills | Validar `.gemini/skills` | Revisar commit `44be12a` e manifestos | 5 | 20% | 1h30 | 6 | 1 | 5 |
| Assinatura Android | Proteger identidade de produção | Definir cofre, backup e recuperação | 5 | 45% | 1h30 | 4 | 2 | 2 |
| Login Google | Homologar autenticação real | Executar com conta de teste autorizada | 4 | 55% | 1h30 | 5 | 3 | 2 |
| Backlog oficial | Transformar pendências em issues | Expandir a partir de `#24`, `#39`, `#41` e `#45` | 3 | 40% | 1h30 | 8 | 3 | 5 |

## 8. Pendências críticas

### 8.1 Ambiente público definitivo

Corrigir identidade, DNS, HTTPS, cache, fallback SPA, headers e evidência do
artefato publicado.

### 8.2 API Hub público

Publicar, registrar URL, validar `/health`, CORS, autenticação, CRUD, uploads,
pagamentos sandbox, auditoria e eventos.

### 8.3 Auditoria integral das rotas

Reexecutar as 325 rotas contra o backend público, registrando erros JavaScript,
formulários, persistência, autenticação e botões sem ação.

### 8.4 Assinatura Android de produção

Armazenar keystore e credenciais em cofre, definir backup, upload key, Play App
Signing e procedimento de recuperação.

### 8.5 Google Sign-In real

Validar token, renovação, logout, cancelamento, erro de rede e integração com o
backend em dispositivo homologado.

## 9. Pendências altas

1. Tornar workflows obrigatórios e bloquear merge quando falharem.
2. Desabilitar merge commit e rebase merge, preservando apenas squash.
3. Regularizar os cinco PRs abertos contra a `main` atual.
4. Resolver a duplicidade entre `#34` e `#37`.
5. Validar o APK Admin do PR `#36`.
6. Validar o PDV Desktop do PR `#38`.
7. Validar a fundação da onda de inovação do PR `#40`.
8. Concluir a sincronização remota do Stitch.
9. Homologar infraestrutura, IAM, billing, bancos, mensageria e observabilidade.
10. Concluir executor e agenda Telegram com secrets externos.
11. Auditar o pacote `.gemini/skills` e seus manifestos.
12. Implementar a Promoção do Dia da issue `#24`.
13. Incorporar o ativo oficial original da Valley Riders.
14. Homologar outbox e dashboards no ambiente real.
15. Integrar PSP, fiscal brasileiro e conciliação em sandbox.
16. Expandir backlog com responsável, dependências e critérios de aceite.
17. Manter auditoria contínua entre documentação e implementação.
18. Executar pentest, carga, backup/restore e resposta a incidente antes de produção.

## 10. Pendências médias

1. Atualizar gradualmente documentos extensos que ainda carregam estados históricos.
2. Revalidar emuladores e instalação dos APKs.
3. Separar claramente demonstração, sandbox, homologação e produção.
4. Executar performance, acessibilidade, responsividade e Web Vitals.
5. Comprovar backup e restore por ambiente.
6. Definir retenção e acesso aos logs do watchdog.
7. Concluir padronização de idioma pt-BR no front-end.
8. Ampliar documentação comercial PF, PJ e investidores sem custos internos.

## 11. Pendências secundárias

1. Criar materiais comerciais simplificados por módulo e público.
2. Consolidar glossário de nomes, siglas e equivalências em português do Brasil.

## 12. Itens concluídos com evidência registrada

1. Catálogo oficial com 24 módulos.
2. Sincronização de `MODULE_NAMES` e presets.
3. Auditor de confirmação v7 versionado.
4. Remoção operacional do Vision no escopo auditado.
5. Encerramento do PR Render antigo `#27` sem merge.

## 13. Implementação iniciada

A primeira implementação após este relatório é o executor Telegram. O escopo
inicial inclui:

- eventos de atividade iniciada e concluída;
- relatório de pendências com índice de 1 a 4;
- validação contra a política versionada;
- modo `--dry-run` sem credenciais;
- retry e timeout de rede;
- testes unitários sem comunicação externa;
- proibição de imprimir token ou chat ID.

A agenda automática permanece pendente até os testes e secrets serem validados.

## 14. Próximo ciclo de 8 horas

1. Executar auditor v7, validação do repositório e testes Telegram.
2. Atualizar ou encerrar PRs duplicados e desatualizados.
3. Executar checks e abrir issues para falhas.
4. Homologar ambiente público e API Hub.
5. Validar APK Admin e PDV Desktop.
6. Finalizar executor Telegram e preparar agenda segura.
7. Atualizar issue `#45`, relatórios e `tarefas.md`.

Atrasos de até 4 horas são tolerância operacional. Após 12 horas, registrar o
estado restante sem iniciar nova frente.

## 15. Histórico

| Versão | Data e hora | Alteração principal |
|---|---|---|
| 2.6 | 26/07/2026 14:01:53 | Primeiro teste das diretrizes e criação da issue `#43`. |
| 2.7 | 26/07/2026 23:06:33 | Revisão consolidada de pendências e documentação, issue `#45` e início do executor Telegram. |