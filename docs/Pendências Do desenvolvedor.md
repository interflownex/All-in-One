# Pendências do Desenvolvedor

**Versão:** 2.6  
**Data da verificação:** 26/07/2026  
**Hora da entrega:** 14:01:53  
**Fuso horário:** `America/Sao_Paulo`  
**Repositório verificado:** `interflownex/All-in-One`  
**Branch de referência:** `main`  
**Commit de referência:** `c2c8eaccc1581ed674821feaaa3336c03a5b763c`  
**Versão anterior:** 2.5  
**Pasta lógica:** `Pendências > Técnico > Equipe técnica`  
**Contextos relacionados:** Técnico, comercial, produto, conceito e governança  
**Públicos impactados:** Pessoa física, pessoa jurídica, equipe técnica e gestão  
**Issue de orquestração:** `#43`  
**Objetivo:** registrar o primeiro teste completo das diretrizes permanentes, consolidar o estado real do repositório e entregar ao Codex um ciclo executável com rastreabilidade.

## 1. Regra permanente de atualização

Toda atualização de pendências deve:

1. verificar `main`, commits, pull requests, issues, workflows, configurações e evidências;
2. comparar o estado atual com a última versão dos relatórios;
3. incrementar a versão deste documento;
4. registrar data, hora, fuso, branch e commit de referência;
5. gerar o Relatório de Varredura e Status;
6. gerar o Plano de Ação Estruturado para o Codex;
7. atualizar o arquivo raiz `tarefas.md`;
8. criar ou atualizar uma issue de orquestração;
9. inserir tudo no GitHub por branch e pull request;
10. integrar por Squash and Merge;
11. atualizar resultados após 8 horas, considerando tolerância de até 4 horas;
12. após 12 horas, registrar concluído, falhas, causas, bloqueios, evidências e pendências restantes.

Os arquivos oficiais desta versão são:

- `docs/relatorios/pendencias/RELATORIO_VARREDURA_STATUS_v2.6_2026-07-26.md`;
- `docs/relatorios/pendencias/PLANO_ACAO_CODEX_v2.6_2026-07-26.md`;
- `tarefas.md`, versão 1.1.

## 2. Regras de governança

- Nenhum item é concluído apenas porque existe código, configuração, commit, documento ou pull request.
- A conclusão exige teste reproduzível e evidência no ambiente correto.
- Segredos, tokens, senhas, chaves de assinatura e credenciais devem permanecer fora do Git.
- Toda alteração deve usar branch, revisão, checks e Squash and Merge.
- Nenhum agente ou workflow deve executar push direto na `main`.
- O módulo Vision permanece desativado e não deve voltar ao catálogo ativo.
- Ativos oficiais de marca não podem ser reconstruídos ou substituídos sem autorização.
- Informações externas, atuais ou instáveis devem ser verificadas com pesquisa avançada e fontes confiáveis.

## 3. Resumo executivo da varredura

### 3.1 Avanços confirmados

1. O ciclo v2.5 foi integrado pelo commit `8af9b729ebaeb5f992a81e35a60ce797b27e60fd`.
2. O catálogo e `MODULE_NAMES` estão sincronizados em 24 módulos ativos.
3. `legal`, `property` e `ai_core` estão presentes em `MODULE_NAMES` e nos presets.
4. O auditor `scripts/audit_confirmation_v7.py` está versionado e reproduzível.
5. As referências ativas ao Vision foram removidas do código operacional verificado pelo auditor v7.
6. O PR `#27` da Render foi encerrado sem merge, evitando regressão do Blueprint antigo.
7. A política Telegram passou a descrever início, encerramento e quatro relatórios diários.
8. O watchdog do Gemini foi restaurado e ganhou tarefa de execução periódica.
9. As regras permanentes de Estudar, Pesquisa Avançada, data, hora e `tarefas.md` foram integradas pelo PR `#42`.
10. A issue antiga `#28` foi encerrada e a issue `#43` foi criada para o ciclo v2.6.

### 3.2 Riscos e divergências atuais

1. O commit atual não possui status checks nem workflow associado.
2. O repositório ainda permite `merge commit`, `rebase merge` e `squash merge` simultaneamente.
3. Os PRs `#34`, `#36`, `#37`, `#38` e `#40` foram abertos sobre o commit antigo `cbbe7bd61bdf13604f5d71167dc5b54f7435cffa` e precisam ser atualizados antes de qualquer integração.
4. Os PRs `#34` e `#37` possuem escopo amplo e parcialmente sobreposto, com risco de duplicidade e regressão.
5. O PR `#36` declara um APK Admin, mas o artefato instalável e os testes ainda precisam ser confirmados.
6. O PR `#38` declara um PDV Desktop offline, mas o instalador, os testes e a segurança operacional ainda precisam ser comprovados.
7. O PR `#40` registra a fundação da onda de inovação com flags desligadas, mas está em rascunho e sem gates finais.
8. O commit `44be12a9751d336f0c8094f79c893eb69008eaf4` alterou amplamente o pacote `.gemini/skills` e não foi localizado um pull request correspondente. O escopo deve ser auditado antes de novas atualizações do pacote.
9. A política Telegram existe, mas não foi localizado executor completo para `activity_started`, `activity_completed` e os quatro relatórios diários.
10. A página `brasildesconto.com.br` respondeu com identificação `tmp-valley`, indicando divergência de nome e ambiente público.
11. A URL de AppDeploy citada no PR `#36` não foi homologada de forma independente nesta varredura.
12. A publicação do API Hub na Render continua sem URL oficial, logs de build e evidência do `/health` vinculados ao commit atual.

## 4. Classificação por contexto e público

| Frente | Contexto | Público principal | Estado |
|---|---|---|---|
| Ambiente público e API Hub | Técnico e comercial | PF, PJ e equipe técnica | Crítico |
| APK Admin e aplicativo Valley | Técnico e produto | PJ e equipe técnica | Alto |
| PDV Desktop e venda offline | Técnico e comercial | PJ e equipe técnica | Alto |
| Promoção do Dia | Comercial, produto e conceito | PF e PJ anunciante | Alto |
| Onda de inovação | Conceito e técnico | PF, PJ e equipe técnica | Alto |
| Governança Git e CI | Técnico e governança | Equipe técnica | Alto |
| Marca Valley Riders | Comercial e identidade | PF, PJ e marketing | Alto |
| Documentação de módulos | Comercial e conceito | PF, PJ e investidores | Secundário |

## 5. Contagem consolidada

| Classificação | Quantidade |
|---|---:|
| Críticas | 5 |
| Altas | 20 |
| Médias | 8 |
| Secundárias | 2 |
| Concluídas com evidência | 5 |
| Resolvidas em princípio, aguardando evidência final | 2 |

## 6. Quadro de acompanhamento

| Nome da atividade | Descrição | Passo sendo executado | Dificuldade [1 a 5] | % concluído | Tempo previsto | Etapas [Total] | Concluídas [X] | Pendentes [Y] |
|---|---|---|---:|---:|---|---:|---:|---:|
| Publicação externa | Homologar domínio, HTTPS e identidade | Corrigir `tmp-valley` e registrar ambiente oficial | 5 | 50% | 2h | 6 | 3 | 3 |
| API Hub público | Publicar backend e conectar front-end | Obter URL, logs e `/health` | 5 | 60% | 2h | 7 | 4 | 3 |
| Auditoria das 325 rotas | Validar jornadas ponta a ponta | Aguardar ambiente público homologado | 5 | 35% | 2h30 | 6 | 2 | 4 |
| Assinatura Android | Proteger keystore de produção | Definir cofre, backup e recuperação | 5 | 45% | 1h30 | 4 | 2 | 2 |
| Login Google | Homologar autenticação real | Executar com conta de teste autorizada | 4 | 55% | 1h30 | 5 | 3 | 2 |
| GitHub Actions | Tornar checks obrigatórios | Executar gates no commit atual | 5 | 25% | 2h | 5 | 1 | 4 |
| Governança de merge | Exigir PR e squash | Alterar configurações administrativas | 4 | 45% | 1h | 5 | 2 | 3 |
| Triage dos PRs antigos | Atualizar ou encerrar PRs desatualizados | Comparar `#34`, `#36`, `#37`, `#38` e `#40` | 5 | 10% | 2h | 8 | 1 | 7 |
| Sobreposição #34 e #37 | Evitar integração duplicada | Produzir matriz de arquivos e decisões | 5 | 5% | 1h30 | 5 | 0 | 5 |
| Auditoria `.gemini/skills` | Confirmar integridade do pacote de skills | Revisar commit `44be12a` e manifestos | 5 | 20% | 1h30 | 6 | 1 | 5 |
| APK Admin PR #36 | Validar APK, URL e segurança | Executar build e smoke test | 4 | 55% | 2h | 6 | 3 | 3 |
| PDV Desktop PR #38 | Validar operação offline e instalador | Executar testes e empacotamento Windows | 5 | 60% | 3h | 8 | 4 | 4 |
| Onda de inovação PR #40 | Validar catálogo e flags | Executar gates e remover Vision residual | 4 | 35% | 2h | 7 | 3 | 4 |
| Telegram executável | Enviar eventos e quatro relatórios | Criar executor, retry, mocks e logs | 4 | 45% | 2h | 6 | 3 | 3 |
| Watchdog Gemini | Monitorar processos e locks | Validar execução contínua e retenção de logs | 3 | 70% | 1h | 5 | 3 | 2 |
| Backlog oficial | Transformar pendências em issues | Expandir a partir de `#24`, `#39`, `#41` e `#43` | 3 | 35% | 1h30 | 8 | 3 | 5 |
| Promoção do Dia | Implementar modal comercial auditável | Executar issue `#24` no Stitch existente | 4 | 5% | 3h | 7 | 0 | 7 |
| Valley Riders | Incorporar ativo oficial | Obter e versionar PNG original aprovado | 3 | 35% | 45min | 4 | 1 | 3 |
| Catálogo de módulos | Manter 24 módulos sincronizados | Executar auditor v7 a cada mudança | 3 | 100% | contínuo | 5 | 5 | 0 |
| Auditoria v7 | Verificar catálogo, contratos e OpenAPI | Integrar aos gates obrigatórios | 4 | 85% | 1h | 6 | 5 | 1 |

## 7. Pendências críticas

### 7.1 Publicar e homologar o ambiente externo definitivo

Corrigir identidade, domínio, HTTPS, DNS, cache, fallback SPA e headers. A página pública não deve permanecer identificada como `tmp-valley`.

**Critério de aceite:** URL oficial, identidade correta, certificado válido, rotas funcionais e evidência versionada.

### 7.2 Conectar o front-end ao API Hub público

Publicar o API Hub, registrar a URL e validar autenticação, CRUD, uploads, pagamentos sandbox, auditoria, eventos e falhas.

### 7.3 Reexecutar a auditoria integral das 325 rotas

Executar no ambiente publicado e registrar erros JavaScript, telas travadas, botões mortos, formulários, persistência e autenticação.

### 7.4 Proteger a assinatura Android de produção

Armazenar keystore em cofre, definir backup, Play App Signing, upload key e recuperação.

### 7.5 Homologar autenticação Google real no APK

Validar token, renovação, logout, cancelamento, falha de rede e integração com backend.

## 8. Pendências de prioridade alta

### 8.1 Concluir sincronização remota do Google Stitch

Usar secret legítimo, preservar manifestos e registrar evidência do projeto correto.

### 8.2 Homologar infraestrutura produtiva

Validar billing, IAM, bancos, mensageria, observabilidade, backups, restauração e rede.

### 8.3 Tornar os workflows obrigatórios

Executar e exigir segurança, testes, banco, Android, web, Docker, OpenAPI, marca e publicação.

### 8.4 Expandir e governar o backlog

Criar issues para pendências críticas e altas ainda sem responsável, dependências e critérios de aceite.

### 8.5 Auditar documentação contra implementação

Confrontar `STATUS.md`, `ROADMAP.md`, `EXECUTION_PLAN.md`, OpenAPI, catálogo, Stitch, migrations e código.

### 8.6 Impor uso exclusivo de Squash and Merge

Desabilitar merge commit e rebase merge, proteger `main`, exigir revisão e checks.

### 8.7 Implementar Telegram executável

Criar execução real para eventos de início e fim e quatro relatórios diários.

### 8.8 Consolidar o núcleo funcional do PDV e validar o PR #38

Validar caixa, venda, estoque, pagamentos, cancelamento, auditoria, instalador e modo offline.

### 8.9 Implementar venda offline segura

Confirmar criptografia, idempotência, sincronização, reconciliação e prevenção de duplicidade.

### 8.10 Integrar o aplicativo Valley ao PDV de forma opcional

Usar autorização explícita, sessão curta e confirmação do cliente.

### 8.11 Implementar fila digital e acompanhamento

Unificar balcão, aplicativo, retirada e delivery com alternativa tradicional.

### 8.12 Implementar combos temporários e presença na loja

Governar filial, estoque, validade, consentimento e frequência.

### 8.13 Governar personalização e dados sensíveis

Impedir publicidade baseada automaticamente em prontuário ou condição médica.

### 8.14 Implementar a Promoção do Dia da issue #24

Usar o projeto Stitch existente, sem duplicar projeto ou tela.

### 8.15 Incorporar o ativo oficial da Valley Riders

Versionar somente o arquivo original aprovado e registrar hash e transparência.

### 8.16 Homologar a Render

Registrar build, start, URL, `/health`, CORS e secrets externos.

### 8.17 Regularizar PRs desatualizados

Atualizar ou encerrar `#34`, `#36`, `#37`, `#38` e `#40` antes de merge.

### 8.18 Resolver sobreposição entre PRs #34 e #37

Produzir comparação por arquivo, escolher fonte de verdade e impedir duplicidade.

### 8.19 Validar o APK Admin do PR #36

Executar testes, build, instalação, URL segura e isolamento da WebView.

### 8.20 Auditar pacote `.gemini/skills` e o commit `44be12a`

Confirmar escopo, manifestos, arquivos removidos ou restaurados, origem e ausência de perda acidental.

## 9. Pendências de prioridade média

### 9.1 Revalidar emulador Android e instalação dos APKs

### 9.2 Centralizar evidências de validação

### 9.3 Separar demonstração, sandbox, homologação e produção

### 9.4 Verificar integridade de contratos, DTOs, eventos e migrations

### 9.5 Revisar performance, acessibilidade e responsividade

### 9.6 Implementar sugestões responsáveis da Helena no PDV

### 9.7 Criar destaques de venda e resumo operacional

### 9.8 Governar retenção e privacidade dos logs do watchdog

Definir tamanho, rotação, informações permitidas e acesso aos relatórios de monitoramento.

## 10. Pendências secundárias

### 10.1 Ampliar documentação comercial para PF e PJ

Descrever módulos, benefícios, comodidade, uso e economia sem divulgar margens internas.

### 10.2 Padronizar pt-BR no front-end

Revisar acentuação, labels, ajuda contextual e mensagens de erro.

## 11. Concluídas com evidência

1. Catálogo Business sincronizado com 24 módulos.
2. Auditor de confirmação v7 versionado e executável.
3. Referências ativas ao Vision removidas no escopo verificado pelo auditor.
4. PR `#27` encerrado sem merge por estar substituído.
5. Diretriz permanente de Estudar, Pesquisa Avançada e `tarefas.md` integrada pelo PR `#42`.

## 12. Resolvidas em princípio, aguardando evidência final

### 12.1 Ativos oficiais do All in One e Valley

A conclusão depende de workflow de integridade executado e superfícies verificadas.

### 12.2 Remoção do Vision

A conclusão administrativa depende da execução da migration no banco real e do fechamento da issue `#41`.

## 13. Plano do próximo ciclo de 8 horas

### Bloco 1: 0h a 1h

- executar os checks aplicáveis ao commit atual;
- registrar logs e falhas;
- confirmar auditor v7 no estado atual.

### Bloco 2: 1h a 2h30

- comparar PRs `#34` e `#37`;
- revisar bases dos PRs `#36`, `#38` e `#40`;
- definir atualizar, dividir ou encerrar.

### Bloco 3: 2h30 a 3h30

- auditar o commit `44be12a`;
- comparar manifestos `.gemini/skills` e `.github/skills`;
- registrar qualquer perda, restauração ou alteração sem rastreabilidade.

### Bloco 4: 3h30 a 4h30

- validar ambiente público e Render;
- corrigir identidade `tmp-valley`;
- registrar URL, build e `/health` ou bloqueio real.

### Bloco 5: 4h30 a 6h

- implementar executor Telegram;
- criar testes, retry, mocks e logs sem segredos;
- validar início, fim e relatório agregado.

### Bloco 6: 6h a 7h30

- validar APK Admin e PDV Desktop;
- registrar builds, artefatos, smoke tests e riscos.

### Bloco 7: 7h30 a 8h

- atualizar issue `#43`;
- atualizar relatórios e `tarefas.md`;
- criar issues para falhas restantes.

## 14. Tolerância operacional

Atrasos de até 4 horas são normais. Usar a tolerância para concluir, nesta ordem:

1. impedir integração de PRs conflitantes;
2. executar checks e corrigir falhas causadas pelo ciclo;
3. homologar ambiente público;
4. concluir executor Telegram;
5. validar artefatos Admin e PDV;
6. atualizar evidências.

Após 12 horas, interromper novas frentes e registrar o estado para retomada.

## 15. Critério de encerramento

Uma pendência somente pode ser concluída quando houver:

- implementação versionada;
- teste reproduzível;
- evidência no ambiente correto;
- commit e pull request identificados;
- checks executados;
- ausência de segredo exposto;
- atualização deste documento, dos relatórios, da issue e do `tarefas.md`.

## 16. Histórico de versões

| Versão | Data e hora | Alteração principal |
|---|---|---|
| 2.4 | 25/07/2026 | Publicação dos relatórios e início da orquestração pelo Codex. |
| 2.5 | 26/07/2026 | Remoção do Vision, sincronização dos 24 módulos e criação do auditor v7. |
| 2.6 | 26/07/2026 14:01:53 | Primeiro teste completo das diretrizes, nova issue #43, triagem dos PRs abertos, auditoria de skills, ambiente público, Telegram, APK Admin e PDV Desktop. |
