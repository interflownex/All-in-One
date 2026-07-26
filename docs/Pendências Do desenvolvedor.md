# Pendências do Desenvolvedor

**Versão:** 2.4  
**Data da verificação:** 25/07/2026  
**Repositório verificado:** `interflownex/All-in-One`  
**Branch de referência:** `main`  
**Commit de referência:** `b9e6871467601ed77c0bf373143eae8320f55773`  
**Versão anterior:** 2.3  
**Pasta lógica do projeto:** `Pendências > Técnico > Equipe técnica`  
**Público principal:** Codex, IA desenvolvedora, desenvolvimento, DevOps, segurança e gestão técnica  
**Issue de orquestração:** `#28`  
**Objetivo:** consolidar o estado verificável do projeto, versionar os relatórios dentro do GitHub e entregar ao Codex um plano executável para o próximo ciclo.

## 1. Regra permanente de atualização e orquestração

A partir desta versão, toda atualização de pendências deve obrigatoriamente:

1. verificar o estado atual da branch `main`, commits, pull requests, issues, workflows, configurações e evidências;
2. atualizar este documento com nova versão, data e commit de referência;
3. gerar um **Relatório de Varredura e Status** versionado em `docs/relatorios/pendencias/`;
4. gerar um **Plano de Ação para o Codex** versionado em `docs/relatorios/pendencias/`;
5. criar ou atualizar uma issue de orquestração do Codex vinculada à versão;
6. inserir os relatórios no GitHub por branch e pull request;
7. integrar a atualização por **Squash and Merge**;
8. após o limite operacional de 12 horas, registrar concluído, falhas, bloqueios, evidências e itens restantes.

Os relatórios oficiais desta versão são:

- `docs/relatorios/pendencias/RELATORIO_VARREDURA_STATUS_v2.4_2026-07-25.md`;
- `docs/relatorios/pendencias/PLANO_ACAO_CODEX_v2.4_2026-07-25.md`.

## 2. Regras de governança

- **Crítica:** bloqueia publicação, segurança, autenticação, integridade financeira ou operação real.
- **Alta:** impede homologação completa, rastreabilidade, governança ou integração de uma frente importante.
- **Média:** reduz confiabilidade, qualidade, acessibilidade ou capacidade de auditoria.
- **Secundária:** melhoria planejada que não impede o funcionamento atual.
- Nenhum item é concluído apenas porque existe código, configuração, documento, commit ou PR fechado.
- A conclusão exige implementação versionada, teste reproduzível e evidência no ambiente correto.
- Segredos, tokens, senhas, chaves de assinatura e credenciais devem permanecer fora do Git.
- Toda alteração funcional deve passar por branch, revisão, checks e **Squash and Merge**.
- Nenhum agente ou workflow deve executar push direto na `main`.
- Correções automáticas devem abrir PR, publicar patch revisável ou produzir artefato para revisão.
- Este documento não autoriza divulgação de custos internos, margens ou lucros.

## 3. Resumo da atualização

Desde a versão 2.3, foram identificados sete commits relacionados ao bootstrap de implantação do API Hub na Render. Foram adicionados `.python-version`, `main.py`, `requirements.txt`, dependências no `pyproject.toml` e um `render.yaml` apontando para a branch `main`.

O avanço é relevante porque o repositório agora possui um entrypoint de execução na raiz e uma configuração de serviço web para o API Hub. Entretanto, não foram encontradas evidências de implantação concluída, URL pública oficial, logs de build aprovados, resposta registrada do endpoint `/health`, testes externos ou workflow associado ao commit atual.

O PR `#27`, criado para o Blueprint inicial da Render, continua aberto e foi baseado no commit `24d20ad9cc4575534298375c6d2ccc8fe8e2f2c0`. A branch `main` recebeu alterações posteriores no mesmo conjunto de arquivos. Portanto, o PR precisa ser revisado, atualizado ou encerrado como substituído, evitando integração duplicada ou regressão do Blueprint.

Foi confirmado um conflito de governança: `AGENTS.md` orientava sincronização automática com commit e push ao término de cada atividade, enquanto este documento exige branch, PR, checks e Squash and Merge. Nesta atualização, a orientação do agente passa a proibir push direto na `main` e a usar branch de trabalho.

O repositório ainda permite simultaneamente `merge commit`, `rebase merge` e `squash merge`. Essa configuração administrativa continua pendente, mesmo após o alinhamento documental.

O commit atual não apresenta status checks nem execução de workflow associada. A implantação Render, a integridade visual e os demais gates ainda não possuem comprovação vinculada ao commit de referência.

O backlog oficial avançou de uma para duas issues abertas:

- `#24`: Promoção do Dia na homepage Valley Consumidor;
- `#28`: orquestração do ciclo de pendências v2.4 pelo Codex.

As divergências de módulos, automação Telegram, auditor v7, homologação externa, integração pública do API Hub, APK, Valley Riders e núcleo do PDV permanecem abertas.

## 4. Mudanças confirmadas desde a versão 2.3

### 4.1 Avanços confirmados

1. Adição de `.python-version` com runtime Python 3.12.
2. Criação de `main.py` como entrypoint do API Hub.
3. Criação de `requirements.txt` na raiz, reutilizando as dependências do API Hub.
4. Registro das dependências executáveis no `pyproject.toml`.
5. Criação e ajustes sucessivos do `render.yaml`.
6. Configuração do endpoint `/health` como verificação de saúde da Render.
7. Geração externa dos segredos JWT e webhook prevista no Blueprint.
8. CORS configurado para os domínios conhecidos do projeto.
9. Criação da issue `#28` para orquestração do Codex.
10. Definição da regra permanente de inserir relatórios versionados no GitHub.

### 4.2 Pendências novas ou reclassificadas

1. Executar a implantação real na Render e registrar a URL pública.
2. Validar build, start command, dependências e endpoint `/health` no ambiente remoto.
3. Confirmar que o serviço Render está ligado à branch e ao repositório corretos.
4. Revisar o PR `#27`, que ficou baseado em estado anterior do Blueprint.
5. Impedir que atualizações de deploy sejam feitas por vários commits diretos na `main`.
6. Alinhar `AGENTS.md` e a política de sincronização ao fluxo branch, PR e squash.
7. Executar workflows e registrar checks no commit atual.
8. Atualizar o front-end com a URL pública do API Hub somente após homologação.
9. Criar issues para as demais pendências críticas e altas.

## 5. Contagem consolidada

| Classificação | Quantidade |
|---|---:|
| Críticas | 5 |
| Altas | 18 |
| Médias | 7 |
| Secundárias | 2 |
| Resolvidas em princípio, aguardando evidência final | 1 |

## 6. Quadro de acompanhamento

> Percentuais e tempos são estimativas gerenciais. Não substituem testes nem evidências.

| Nome da atividade | Descrição | Passo atual | Dificuldade [1 a 5] | % concluído | Tempo previsto | Etapas [Total] | Concluídas [X] | Pendentes [Y] |
|---|---|---|---:|---:|---|---:|---:|---:|
| Publicação externa definitiva | Homologar domínio, HTTPS, DNS, cache e headers | Validar bootstrap Render e registrar URL oficial | 5 | 50% | 2h | 6 | 3 | 3 |
| API Hub público | Publicar o API Hub e conectar o front-end | Executar deploy, `/health` e jornadas remotas | 5 | 60% | 2h | 7 | 4 | 3 |
| Bootstrap Render | Validar Blueprint, build, start e secrets | Executar implantação e arquivar logs | 4 | 70% | 1h30 | 6 | 4 | 2 |
| Auditoria das 325 rotas | Validar jornadas ponta a ponta | Aguardar API Hub público homologado | 5 | 35% | 2h30 | 6 | 2 | 4 |
| Assinatura Android | Proteger keystore e Play App Signing | Definir cofre e recuperação | 5 | 45% | 1h30 | 4 | 2 | 2 |
| Login Google no APK | Homologar autenticação e sessão | Executar com conta real | 4 | 55% | 1h30 | 5 | 3 | 2 |
| GitHub Actions | Tornar checks executáveis e obrigatórios | Executar workflows no commit atual | 5 | 25% | 2h | 5 | 1 | 4 |
| Governança de merge | Exigir branch, PR e Squash and Merge | Alinhar agentes e configurações administrativas | 4 | 40% | 1h | 5 | 2 | 3 |
| PR Render #27 | Evitar duplicidade e regressão do Blueprint | Comparar com `main` e decidir atualização ou encerramento | 3 | 20% | 30min | 4 | 1 | 3 |
| Integridade visual | Validar marcas oficiais e bloquear alterações | Executar workflow e arquivar evidência | 4 | 75% | 1h | 5 | 4 | 1 |
| Ativo Valley Riders | Incorporar o PNG oficial aprovado | Obter e versionar o binário original | 3 | 35% | 45min | 4 | 1 | 3 |
| Catálogo de módulos | Sincronizar os 24 módulos | Incluir quatro módulos na configuração Business | 4 | 60% | 1h30 | 5 | 3 | 2 |
| Automação Telegram | Implementar eventos e relatórios periódicos | Criar executor e testes | 4 | 35% | 2h | 6 | 2 | 4 |
| Auditoria v7 | Restaurar o auditor e integrá-lo à CI | Localizar ou recriar script e fixtures | 4 | 30% | 1h30 | 5 | 1 | 4 |
| Backlog oficial | Transformar pendências em issues | Expandir a partir das issues `#24` e `#28` | 3 | 20% | 1h30 | 6 | 2 | 4 |
| Promoção do Dia | Implementar modal comercial auditável | Executar a issue `#24` no Stitch existente | 4 | 5% | 3h | 7 | 0 | 7 |
| Núcleo do PDV | Consolidar venda presencial e caixa | Definir contrato e jornada mínima | 5 | 15% | 4h | 8 | 1 | 7 |
| Venda offline | Sincronizar operações sem duplicidade | Projetar fila local e reconciliação | 5 | 5% | 4h | 7 | 0 | 7 |
| Integração Valley no caixa | Parear aplicativo e PDV com autorização | Definir sessão temporária | 4 | 10% | 3h | 7 | 1 | 6 |
| Fila digital e combos | Integrar pedidos, presença e promoções | Definir regras e consentimentos | 4 | 10% | 3h | 7 | 1 | 6 |
| Personalização responsável | Isolar dados sensíveis e governar consentimento | Aguardar privacidade e jurídico | 5 | 0% | 3h | 8 | 0 | 8 |

## 7. Pendências críticas

### 7.1 Publicar e homologar o ambiente externo definitivo

Concluir domínio público, DNS, HTTPS, cache, fallback SPA, headers de segurança e registro da URL oficial. A existência do Blueprint Render não comprova publicação.

**Critério de aceite:** URL oficial acessível, certificado válido, rotas funcionais, endpoint de saúde aprovado e evidência versionada.

### 7.2 Conectar o front-end ao API Hub público

Executar a implantação do API Hub, registrar a URL e configurar `VITE_API_HUB_URL`. Validar autenticação, CRUD, uploads, pagamentos sandbox, auditoria, eventos e falhas contra o backend remoto.

**Critério de aceite:** jornadas principais sem fallback local, com persistência e evidência no backend correto.

### 7.3 Reexecutar a auditoria integral das 325 rotas

Executar a auditoria no ambiente publicado, verificando erros JavaScript, telas travadas, botões mortos, formulários, persistência e autenticação.

### 7.4 Proteger a assinatura Android de produção

Armazenar keystore e credenciais em cofre, definir backup, Play App Signing, upload key e procedimento de recuperação.

### 7.5 Homologar autenticação Google real no APK

Validar token, sessão, renovação, logout, cancelamento, erro de rede e integração com backend em dispositivo ou emulador homologado.

## 8. Pendências de prioridade alta

### 8.1 Concluir sincronização remota do Google Stitch

Fornecer `STITCH_API_KEY` por secret e validar projetos, manifestos e telas pendentes, incluindo `finance/entity_valley_gold_ledger_entries`.

### 8.2 Homologar infraestrutura produtiva

Validar billing, IAM, cluster, bancos, mensageria, observabilidade, backups, restauração, secrets e políticas de rede.

### 8.3 Validar e tornar obrigatórios os workflows do GitHub Actions

O commit atual não possui checks ou workflow associado. Executar segurança, testes, banco, Android, web, Docker, artefatos, marca e publicação.

**Critério de aceite:** merges bloqueados quando checks obrigatórios falharem.

### 8.4 Expandir e governar o backlog oficial

As issues `#24` e `#28` iniciaram o backlog, mas as demais pendências críticas e altas ainda precisam virar issues com responsável, prioridade, dependências, critérios de aceite e evidências.

### 8.5 Auditar consistência entre documentação e implementação

Confrontar `STATUS.md`, `ROADMAP.md`, `EXECUTION_PLAN.md`, OpenAPI, catálogo, manifests Stitch, migrations e código executável.

### 8.6 Impor uso exclusivo de Squash and Merge

- desabilitar `merge commit`;
- desabilitar `rebase merge`;
- proteger a `main` contra push direto;
- exigir PR, revisão e checks;
- impedir agentes e workflows de executar `git push` direto na `main`;
- fazer correções automáticas abrirem PR ou gerarem patch revisável.

### 8.7 Sincronizar catálogo de módulos e configuração Business

`config/module_catalog.json` possui 24 módulos e `MODULE_NAMES` possui 21. Incluir e testar:

- `vision`;
- `legal`;
- `property`;
- `ai_core`.

### 8.8 Implementar o ciclo de atividade e relatórios pelo Telegram

Criar execução real para `activity_started`, `activity_completed` e quatro relatórios diários, com logs, retry, mocks e secrets externos.

### 8.9 Restaurar a auditoria de confirmação v7

Recriar ou localizar `scripts/audit_confirmation_v7.py`, versionar regras e fixtures, executar na CI e publicar relatório como artefato.

### 8.10 Consolidar o núcleo funcional do PDV

Definir caixa, operador, venda, pagamentos, troco, cancelamento, sangria, suprimento, estoque, fiscal, comprovante e auditoria.

### 8.11 Implementar venda offline segura

Criar armazenamento local criptografado, idempotência, sincronização, reconciliação, limites de risco e prevenção de duplicidade.

### 8.12 Integrar o aplicativo Valley ao PDV sem obrigatoriedade

Suportar QR Code e Bluetooth de baixa energia com autorização explícita, sessão curta e confirmação do cliente.

### 8.13 Implementar fila digital e acompanhamento

Unificar balcão, aplicativo, retirada e delivery; manter alternativa tradicional para clientes sem aplicativo.

### 8.14 Implementar combos temporários e presença na loja

Permitir criação, ativação e encerramento pelo gerente, com filial, estoque, validade, consentimento e limite de frequência.

### 8.15 Governar personalização e dados sensíveis

Impedir uso automático de prontuário ou condição médica para publicidade. Exigir isolamento técnico, consentimento específico, finalidade e alternativa sem perfilamento.

### 8.16 Implementar a Promoção do Dia da issue `#24`

Usar o projeto Stitch existente `VALLEY APK - Template Completo`, sem duplicar projeto ou tela. Criar modal centralizado, campanha paga, controles da empresa, interação do consumidor, auditoria, frequência e experiência não invasiva.

### 8.17 Incorporar o ativo oficial da Valley Riders

Obter o arquivo original aprovado `LOGO OFICIAL VALLEY RIDERS_2.png`, versioná-lo em `assets/brand/valley-riders-logo-official.png`, registrar hash, validar transparência e impedir substitutos.

### 8.18 Validar e regularizar o bootstrap da Render

- executar a importação ou atualização do Blueprint;
- confirmar repositório, branch, região, runtime e comandos;
- validar instalação das dependências;
- confirmar inicialização do Uvicorn;
- registrar URL, logs e resposta do `/health`;
- verificar CORS e secrets externos;
- comparar e regularizar o PR `#27`;
- não declarar publicação concluída antes da homologação remota.

## 9. Pendências de prioridade média

### 9.1 Revalidar emulador Android e instalação do APK

Confirmar boot, instalar APK e repetir smoke tests.

### 9.2 Centralizar evidências de validação

Registrar logs, relatórios, capturas, hashes, URLs, commits, PRs e resultados por versão.

### 9.3 Separar dados demonstrativos e ambientes

Distinguir dados fictícios, sandbox, homologação e produção com flags e avisos claros.

### 9.4 Verificar integridade dos contratos

Validar DTOs, formulários, persistência, OpenAPI, eventos e migrations.

### 9.5 Revisar performance, acessibilidade e responsividade

Executar Lighthouse, Web Vitals, teclado, leitor de tela, contraste, zoom e testes em aparelhos limitados.

### 9.6 Implementar sugestões responsáveis da Helena no PDV

Permitir sugestões explicáveis e dispensáveis, sem executar autonomamente desconto elevado, cancelamento, estorno, sangria, suprimento ou alteração fiscal.

### 9.7 Criar destaques de venda e resumo operacional

Exibir métricas por empresa, filial, caixa, operador e período, sem exposição indevida de dados pessoais.

## 10. Pendências secundárias

### 10.1 Ampliar documentação para pessoa física e jurídica

Descrever módulos, serviços e microsserviços em linguagem comercial, incluindo benefícios, comodidade, usabilidade e economia, sem divulgar custos internos ou margens.

### 10.2 Padronizar nomenclatura e idioma do front-end

Concluir pt-BR, pluralização, acentuação, labels, ajuda contextual e mensagens de erro.

## 11. Item resolvido em princípio, aguardando evidência final

### 11.1 Ativos oficiais do All in One e Valley

Os PNGs oficiais estão versionados e os aliases legados apontam para os ativos canônicos. A conclusão final depende de:

1. execução comprovada do workflow de integridade;
2. testes aprovados no commit atual;
3. verificação das superfícies web, business, desktop e documentação;
4. ausência de reconstruções ou versões alternativas.

## 12. Plano de ação para o próximo ciclo de 8 horas

Atrasos de até 4 horas são tolerância operacional normal. Após 12 horas, os relatórios e a issue `#28` devem ser atualizados com evidências, falhas e pendências restantes.

### Bloco 1, 0h a 1h30

1. Validar o `render.yaml`, `main.py`, `requirements.txt` e `pyproject.toml`.
2. Executar a implantação Render ou coletar o bloqueio real.
3. Registrar logs de build, start e `/health`.

### Bloco 2, 1h30 a 2h30

1. Comparar o PR `#27` com a `main` atual.
2. Atualizar ou encerrar o PR como substituído.
3. Evitar integração duplicada do Blueprint.

### Bloco 3, 2h30 a 3h30

1. Alinhar `AGENTS.md` e políticas de sincronização.
2. Proibir push direto na `main`.
3. Garantir branch, PR, checks e squash para o Codex.

### Bloco 4, 3h30 a 4h30

1. Executar os workflows principais no commit atual.
2. Arquivar checks e logs.
3. Registrar falhas como issues rastreáveis.

### Bloco 5, 4h30 a 6h

1. Restaurar ou recriar o auditor v7.
2. Executar catálogo, diretórios, aplicações, OpenAPI e configuração Business.
3. Salvar relatório versionado.

### Bloco 6, 6h a 7h

1. Incluir `vision`, `legal`, `property` e `ai_core` em `MODULE_NAMES`.
2. Definir presets, dependências e visibilidade.
3. Criar testes unitários.

### Bloco 7, 7h a 8h

1. Atualizar a issue `#28` com evidências.
2. Expandir o backlog das pendências críticas.
3. Manter a issue `#24` preparada para execução no Stitch existente.
4. Atualizar os dois relatórios desta versão.

## 13. Ordem recomendada das próximas atividades

1. Validar e homologar o bootstrap Render.
2. Registrar URL pública, logs e resposta do `/health`.
3. Regularizar o PR `#27`.
4. Alinhar a sincronização dos agentes ao fluxo branch, PR e squash.
5. Executar e comprovar os workflows do commit atual.
6. Expandir o backlog oficial a partir da issue `#28`.
7. Restaurar o auditor v7.
8. Corrigir a divergência dos quatro módulos.
9. Implementar a automação Telegram executável.
10. Impor Squash and Merge e proteção administrativa da `main`.
11. Implementar a issue `#24` sem duplicar projeto Stitch.
12. Incorporar o ativo oficial da Valley Riders.
13. Definir contrato e arquitetura do PDV.
14. Implementar frente de caixa, venda offline e integração opcional Valley.
15. Conectar o front-end ao API Hub homologado.
16. Rodar a auditoria das 325 rotas.
17. Homologar login Google e assinatura Android.

## 14. Critério de encerramento

Uma pendência somente pode ser marcada como concluída quando houver:

- implementação versionada;
- teste automatizado ou procedimento reproduzível;
- evidência do ambiente correto;
- referência ao commit e ao PR;
- checks executados e aprovados;
- URL e logs quando a atividade envolver publicação;
- ausência de bloqueio externo não declarado;
- confirmação de que nenhum segredo foi exposto;
- atualização deste documento, dos dois relatórios e da issue de orquestração.

## 15. Histórico de versões

| Versão | Data | Alteração principal |
|---|---|---|
| 2.0 | 22/07/2026 | Consolidação inicial das pendências do projeto. |
| 2.1 | 23/07/2026 | Governança de merge, divergência de módulos, CI, Telegram e auditor v7. |
| 2.2 | 23/07/2026 | Diretrizes planejadas do PDV, venda offline, Valley, fila digital, combos, Helena e privacidade. |
| 2.3 | 24/07/2026 | Governança das marcas, primeira issue oficial, Valley Riders e atualização do plano de 8 horas. |
| 2.4 | 25/07/2026 | Bootstrap Render, PR #27 desatualizado, conflito de sincronização, issue #28 do Codex e regra permanente de inserir relatórios versionados no GitHub. |
