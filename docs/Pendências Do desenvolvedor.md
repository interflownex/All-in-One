# Pendências do Desenvolvedor

**Versão:** 2.3  
**Data da verificação:** 24/07/2026  
**Repositório verificado:** `interflownex/All-in-One`  
**Branch de referência:** `main`  
**Commit de referência:** `c63396d8238140870195854070892c4f5d94ce97`  
**Versão anterior:** 2.2  
**Pasta lógica do projeto:** `Pendências > Técnico > Equipe técnica`  
**Público principal:** IA desenvolvedora, desenvolvimento, DevOps, segurança e gestão técnica  
**Objetivo:** consolidar as pendências reais, registrar avanços confirmados, remover informações ultrapassadas e preparar o próximo ciclo de execução.

## 1. Regras de governança

- **Crítica:** bloqueia publicação, segurança, autenticação, integridade financeira ou operação real.
- **Alta:** impede homologação completa, rastreabilidade, governança ou integração de uma frente importante.
- **Média:** reduz confiabilidade, qualidade, acessibilidade ou capacidade de auditoria.
- **Secundária:** melhoria planejada que não impede o funcionamento atual.
- Nenhum item é concluído apenas porque existe código, configuração, documento, commit ou PR fechado.
- A conclusão exige implementação versionada, teste reproduzível e evidência no ambiente correto.
- Segredos, tokens, senhas, chaves de assinatura e credenciais devem permanecer fora do Git.
- Toda alteração funcional deve passar por branch, revisão, checks e **Squash and Merge**.
- Workflows automáticos não devem gravar diretamente na `main`; correções automáticas devem abrir PR ou produzir artefato para revisão.
- Este documento não autoriza divulgação de custos internos, margens ou lucros.

## 2. Resumo da atualização

Desde a versão 2.2, o repositório avançou na governança visual e recebeu o PR `#25`, que registrou os ativos oficiais do All in One, Valley e Valley Riders, fortaleceu as regras multiagente, adicionou testes e criou o workflow de integridade das marcas.

Os ativos oficiais do **All in One** e da **Valley** foram versionados como arquivos canônicos. Os aliases SVG antigos passaram a apontar para os PNGs oficiais, reduzindo o risco de uso de reconstruções visuais não autorizadas.

O arquivo binário oficial da **Valley Riders** ainda não foi incorporado. O manifesto bloqueia substitutos, mas a pendência continua aberta até que o PNG original aprovado seja versionado e validado.

Foi criada a issue `#24`, iniciando o uso de issues como backlog oficial. Entretanto, uma única issue não cobre as pendências críticas e altas já identificadas; o backlog precisa ser ampliado e governado.

A governança de merge continua incompleta. O repositório ainda permite `merge commit`, `rebase merge` e `squash merge`. Além disso, o workflow de integridade de marca possui permissão de escrita e executa `git push origin HEAD:main` quando realiza correções, contrariando a diretriz de PR obrigatório e uso exclusivo de Squash and Merge.

O commit atual não apresenta status checks nem execução de workflow associada. A existência do arquivo `.github/workflows/brand-integrity.yml` não comprova que o gate foi executado com sucesso no commit atual.

As divergências de módulos, a automação Telegram, o auditor v7, a homologação externa, o API Hub público, o APK e o núcleo do PDV permanecem pendentes.

## 3. Mudanças confirmadas desde a versão 2.2

### 3.1 Avanços confirmados

1. PR `#25` integrado para governança das marcas oficiais.
2. Ativo oficial do All in One versionado e referenciado.
3. Ativo oficial da Valley versionado e referenciado.
4. Aliases legados do All in One e Valley convertidos em ponteiros para os PNGs oficiais.
5. Manifesto `config/branding/authorized_assets.json` criado.
6. Workflow `.github/workflows/brand-integrity.yml` criado.
7. Testes e script de verificação de integridade visual ampliados.
8. Primeira issue oficial de backlog criada: `#24`.
9. Diretrizes e pendências planejadas do PDV adicionadas ao documento anterior.

### 3.2 Pendências novas ou reclassificadas

1. Alterar o workflow de marca para não realizar push direto na `main`.
2. Validar a execução real do workflow de integridade visual.
3. Incorporar o PNG original aprovado da Valley Riders.
4. Expandir o backlog para todas as pendências críticas e altas.
5. Implementar a issue `#24`, referente à Promoção do Dia na homepage Valley Consumidor.
6. Corrigir a contagem das pendências altas da versão 2.2.
7. Atualizar a referência do documento, que ainda apontava para um commit anterior ao estado atual.

## 4. Contagem consolidada

| Classificação | Quantidade |
|---|---:|
| Críticas | 5 |
| Altas | 17 |
| Médias | 7 |
| Secundárias | 2 |
| Resolvidas em princípio, aguardando evidência final | 1 |

## 5. Quadro de acompanhamento

> Percentuais e tempos são estimativas gerenciais. Não substituem testes nem evidências.

| Nome da atividade | Descrição | Passo atual | Dificuldade [1 a 5] | % concluído | Tempo previsto | Etapas [Total] | Concluídas [X] | Pendentes [Y] |
|---|---|---|---:|---:|---|---:|---:|---:|
| Publicação externa definitiva | Homologar domínio, HTTPS, DNS, cache e headers | Aguardar credenciais e validação final | 5 | 40% | 2h | 5 | 2 | 3 |
| API Hub público | Conectar o front-end aos microsserviços reais | Configurar URL pública e repetir jornadas | 5 | 50% | 2h | 6 | 3 | 3 |
| Auditoria das 335 rotas | Validar jornadas ponta a ponta | Preparar execução no ambiente publicado | 5 | 35% | 2h30 | 6 | 2 | 4 |
| Assinatura Android | Proteger keystore e Play App Signing | Definir cofre e recuperação | 5 | 45% | 1h30 | 4 | 2 | 2 |
| Login Google no APK | Homologar autenticação e sessão | Executar com conta real | 4 | 55% | 1h30 | 5 | 3 | 2 |
| GitHub Actions | Tornar checks executáveis e obrigatórios | Validar workflows no commit atual | 5 | 25% | 2h | 5 | 1 | 4 |
| Governança de merge | Exigir PR e Squash and Merge | Remover push direto e outros métodos | 4 | 25% | 1h | 5 | 1 | 4 |
| Integridade visual | Validar marcas oficiais e bloquear alterações | Executar workflow e arquivar evidência | 4 | 75% | 1h | 5 | 4 | 1 |
| Ativo Valley Riders | Incorporar o PNG oficial aprovado | Obter e versionar o binário original | 3 | 35% | 45min | 4 | 1 | 3 |
| Catálogo de módulos | Sincronizar os 25 módulos | Incluir quatro módulos na configuração Business | 4 | 60% | 1h30 | 5 | 3 | 2 |
| Automação Telegram | Implementar eventos e relatórios periódicos | Criar executor e testes | 4 | 35% | 2h | 6 | 2 | 4 |
| Auditoria v7 | Restaurar o auditor e integrá-lo à CI | Localizar ou recriar script e fixtures | 4 | 30% | 1h30 | 5 | 1 | 4 |
| Backlog oficial | Transformar pendências em issues | Expandir a partir da issue `#24` | 3 | 10% | 1h30 | 6 | 1 | 5 |
| Promoção do Dia | Implementar modal comercial auditável | Executar a issue `#24` no projeto Stitch existente | 4 | 5% | 3h | 7 | 0 | 7 |
| Núcleo do PDV | Consolidar venda presencial e caixa | Definir contrato e jornada mínima | 5 | 15% | 4h | 8 | 1 | 7 |
| Venda offline | Sincronizar operações sem duplicidade | Projetar fila local e reconciliação | 5 | 5% | 4h | 7 | 0 | 7 |
| Integração Valley no caixa | Parear aplicativo e PDV com autorização | Definir sessão temporária | 4 | 10% | 3h | 7 | 1 | 6 |
| Fila digital e combos | Integrar pedidos, presença e promoções | Definir regras e consentimentos | 4 | 10% | 3h | 7 | 1 | 6 |
| Personalização responsável | Isolar dados sensíveis e governar consentimento | Aguardar privacidade e jurídico | 5 | 0% | 3h | 8 | 0 | 8 |

## 6. Pendências críticas

### 6.1 Publicar e homologar o ambiente externo definitivo

Concluir domínio público, DNS, HTTPS, cache, fallback SPA, headers de segurança e registro da URL oficial. Credenciais devem permanecer em secrets ou cofre externo.

**Critério de aceite:** URL oficial acessível, certificado válido, rotas funcionais e evidência versionada.

### 6.2 Conectar o front-end ao API Hub público

Configurar `VITE_API_HUB_URL` e executar autenticação, CRUD, uploads, pagamentos sandbox, auditoria, eventos e tratamento de falhas contra os serviços reais.

**Critério de aceite:** jornadas principais sem fallback local, com persistência e evidência no backend correto.

### 6.3 Reexecutar a auditoria integral das 335 rotas

Executar a auditoria no ambiente publicado, verificando erros JavaScript, telas travadas, botões mortos, formulários, persistência e autenticação.

### 6.4 Proteger a assinatura Android de produção

Armazenar keystore e credenciais em cofre, definir backup, Play App Signing, upload key e procedimento de recuperação.

### 6.5 Homologar autenticação Google real no APK

Validar token, sessão, renovação, logout, cancelamento, erro de rede e integração com backend em dispositivo ou emulador homologado.

## 7. Pendências de prioridade alta

### 7.1 Concluir sincronização remota do Google Stitch

Fornecer `STITCH_API_KEY` por secret e validar projetos, manifestos e telas pendentes, incluindo `finance/entity_valley_gold_ledger_entries`.

### 7.2 Homologar infraestrutura produtiva

Validar billing, IAM, cluster, bancos, mensageria, observabilidade, backups, restauração, secrets e políticas de rede.

### 7.3 Validar e tornar obrigatórios os workflows do GitHub Actions

O commit atual não possui checks ou workflow associado. Executar segurança, testes, banco, Android, web, Docker, artefatos, marca e publicação.

**Critério de aceite:** merges bloqueados quando checks obrigatórios falharem.

### 7.4 Expandir e governar o backlog oficial

A issue `#24` iniciou o backlog, mas as demais pendências críticas e altas ainda precisam virar issues com responsável, prioridade, dependências, critérios de aceite e evidências.

### 7.5 Auditar consistência entre documentação e implementação

Confrontar `STATUS.md`, `ROADMAP.md`, `EXECUTION_PLAN.md`, OpenAPI, catálogo, manifests Stitch, migrations e código executável.

### 7.6 Impor uso exclusivo de Squash and Merge

- desabilitar `merge commit`;
- desabilitar `rebase merge`;
- proteger a `main` contra push direto;
- exigir PR, revisão e checks;
- impedir workflows de executar `git push` direto;
- fazer correções automáticas abrirem PR ou gerarem patch revisável.

### 7.7 Sincronizar catálogo de módulos e configuração Business

`config/module_catalog.json` possui 25 módulos e `MODULE_NAMES` possui 21. Incluir e testar:

- `vision`;
- `legal`;
- `property`;
- `ai_core`.

### 7.8 Implementar o ciclo de atividade e relatórios pelo Telegram

Criar execução real para `activity_started`, `activity_completed` e quatro relatórios diários, com logs, retry, mocks e secrets externos.

### 7.9 Restaurar a auditoria de confirmação v7

Recriar ou localizar `scripts/audit_confirmation_v7.py`, versionar regras e fixtures, executar na CI e publicar relatório como artefato.

### 7.10 Consolidar o núcleo funcional do PDV

Definir caixa, operador, venda, pagamentos, troco, cancelamento, sangria, suprimento, estoque, fiscal, comprovante e auditoria.

### 7.11 Implementar venda offline segura

Criar armazenamento local criptografado, idempotência, sincronização, reconciliação, limites de risco e prevenção de duplicidade.

### 7.12 Integrar o aplicativo Valley ao PDV sem obrigatoriedade

Suportar QR Code e Bluetooth de baixa energia com autorização explícita, sessão curta e confirmação do cliente.

### 7.13 Implementar fila digital e acompanhamento

Unificar balcão, aplicativo, retirada e delivery; manter alternativa tradicional para clientes sem aplicativo.

### 7.14 Implementar combos temporários e presença na loja

Permitir criação, ativação e encerramento pelo gerente, com filial, estoque, validade, consentimento e limite de frequência.

### 7.15 Governar personalização e dados sensíveis

Impedir uso automático de prontuário ou condição médica para publicidade. Exigir isolamento técnico, consentimento específico, finalidade e alternativa sem perfilamento.

### 7.16 Implementar a Promoção do Dia da issue `#24`

Usar o projeto Stitch existente `VALLEY APK - Template Completo`, sem duplicar projeto ou tela. Criar modal centralizado, campanha paga, controles da empresa, interação do consumidor, auditoria, frequência e experiência não invasiva.

### 7.17 Incorporar o ativo oficial da Valley Riders

Obter o arquivo original aprovado `LOGO OFICIAL VALLEY RIDERS_2.png`, versioná-lo em `assets/brand/valley-riders-logo-official.png`, registrar hash, validar transparência e impedir substitutos.

## 8. Pendências de prioridade média

### 8.1 Revalidar emulador Android e instalação do APK

Confirmar boot, instalar APK e repetir smoke tests.

### 8.2 Centralizar evidências de validação

Registrar logs, relatórios, capturas, hashes, URLs, commits, PRs e resultados por versão.

### 8.3 Separar dados demonstrativos e ambientes

Distinguir dados fictícios, sandbox, homologação e produção com flags e avisos claros.

### 8.4 Verificar integridade dos contratos

Validar DTOs, formulários, persistência, OpenAPI, eventos e migrations.

### 8.5 Revisar performance, acessibilidade e responsividade

Executar Lighthouse, Web Vitals, teclado, leitor de tela, contraste, zoom e testes em aparelhos limitados.

### 8.6 Implementar sugestões responsáveis da Helena no PDV

Permitir sugestões explicáveis e dispensáveis, sem executar autonomamente desconto elevado, cancelamento, estorno, sangria, suprimento ou alteração fiscal.

### 8.7 Criar destaques de venda e resumo operacional

Exibir métricas por empresa, filial, caixa, operador e período, sem exposição indevida de dados pessoais.

## 9. Pendências secundárias

### 9.1 Ampliar documentação para pessoa física e jurídica

Descrever módulos, serviços e microsserviços em linguagem comercial, incluindo benefícios, comodidade, usabilidade e economia, sem divulgar custos internos ou margens.

### 9.2 Padronizar nomenclatura e idioma do front-end

Concluir pt-BR, pluralização, acentuação, labels, ajuda contextual e mensagens de erro.

## 10. Item resolvido em princípio, aguardando evidência final

### 10.1 Ativos oficiais do All in One e Valley

Os PNGs oficiais estão versionados e os aliases legados apontam para os ativos canônicos. A conclusão final depende de:

1. execução comprovada do workflow de integridade;
2. testes aprovados no commit atual;
3. verificação das superfícies web, business, desktop e documentação;
4. ausência de reconstruções ou versões alternativas.

## 11. Plano de ação para o próximo ciclo de 8 horas

Atrasos de até 4 horas são tolerância operacional normal. Após 12 horas, o documento deve ser atualizado com evidências, falhas e pendências restantes.

### Bloco 1, 0h a 1h

1. Alterar o workflow de marca para remover `git push` direto na `main`.
2. Fazer a remediação automática abrir PR ou gerar patch revisável.
3. Revisar permissões de escrita do workflow.

### Bloco 2, 1h a 2h

1. Executar `check_brand_integrity.py`.
2. Executar `tests/test_branding_assets.py`.
3. Disparar o workflow manualmente e arquivar evidências.

### Bloco 3, 2h a 3h

1. Incorporar o PNG oficial da Valley Riders, caso esteja disponível.
2. Validar hash, transparência e referências.
3. Caso o arquivo esteja indisponível, criar issue bloqueada com origem e responsável.

### Bloco 4, 3h a 4h

1. Criar issues para as cinco pendências críticas.
2. Criar issues para governança de merge, CI, módulos, Telegram e auditor v7.
3. Relacionar dependências e critérios de aceite.

### Bloco 5, 4h a 5h30

1. Restaurar ou recriar o auditor v7.
2. Executar catálogo, diretórios, aplicações, OpenAPI e configuração Business.
3. Salvar relatório versionado.

### Bloco 6, 5h30 a 7h

1. Incluir `vision`, `legal`, `property` e `ai_core` em `MODULE_NAMES`.
2. Definir presets, dependências e visibilidade.
3. Criar testes unitários.

### Bloco 7, 7h a 8h

1. Preparar a primeira entrega da issue `#24` no projeto Stitch existente.
2. Atualizar o backlog e este documento.
3. Registrar commits, PRs, checks, evidências e bloqueios externos.

## 12. Ordem recomendada das próximas atividades

1. Corrigir o workflow de marca para não gravar diretamente na `main`.
2. Executar e comprovar os gates de integridade visual.
3. Incorporar o ativo oficial da Valley Riders.
4. Expandir o backlog oficial.
5. Restaurar o auditor v7.
6. Corrigir a divergência dos quatro módulos.
7. Implementar a automação Telegram executável.
8. Impor Squash and Merge e proteção da `main`.
9. Executar os workflows principais.
10. Implementar a issue `#24` sem duplicar projeto Stitch.
11. Definir contrato e arquitetura do PDV.
12. Implementar frente de caixa, venda offline e integração opcional Valley.
13. Publicar e homologar o ambiente externo.
14. Configurar o API Hub público.
15. Rodar a auditoria das 335 rotas.
16. Homologar login Google e assinatura Android.

## 13. Critério de encerramento

Uma pendência somente pode ser marcada como concluída quando houver:

- implementação versionada;
- teste automatizado ou procedimento reproduzível;
- evidência do ambiente correto;
- referência ao commit e ao PR;
- checks executados e aprovados;
- ausência de bloqueio externo não declarado;
- confirmação de que nenhum segredo foi exposto;
- atualização deste documento.

## 14. Histórico de versões

| Versão | Data | Alteração principal |
|---|---|---|
| 2.0 | 22/07/2026 | Consolidação inicial das pendências do projeto. |
| 2.1 | 23/07/2026 | Governança de merge, divergência de módulos, CI, Telegram e auditor v7. |
| 2.2 | 23/07/2026 | Diretrizes planejadas do PDV, venda offline, Valley, fila digital, combos, Helena e privacidade. |
| 2.3 | 24/07/2026 | Governança das marcas, PR #25, primeira issue oficial, reclassificação Valley Riders, conflito do workflow com a proteção da main, correção da contagem e atualização do plano de 8 horas. |
