# Pendências do Desenvolvedor

**Versão:** 2.1  
**Data da verificação:** 23/07/2026  
**Repositório verificado:** `interflownex/All-in-One`  
**Branch de referência:** `main`  
**Commit de referência:** `61b18d2da27f536bcbbd7c7ff14a2e14bb2a48a3`  
**Pasta lógica do projeto:** `Pendências > Técnico > Equipe técnica`  
**Público principal:** IA desenvolvedora, desenvolvimento, DevOps, segurança e gestão técnica  
**Objetivo:** consolidar pendências reais, remover duplicidades, registrar novas divergências e dimensionar o próximo ciclo técnico de 8 horas.

## 1. Regra de governança

- **Crítica:** bloqueia publicação, segurança, integridade financeira, autenticação ou operação real.
- **Alta:** impede homologação completa, rastreabilidade ou integração de uma frente importante.
- **Média:** não bloqueia a base local, mas reduz confiabilidade, qualidade ou capacidade de auditoria.
- **Secundária:** melhoria planejada que não impede o funcionamento atual.
- Nenhum item é concluído apenas porque existe código, configuração, documento ou PR fechado.
- A conclusão exige implementação versionada, teste reproduzível e evidência no ambiente correto.
- Segredos, tokens, senhas, chaves de assinatura e credenciais devem permanecer fora do Git.
- Toda alteração funcional deve passar por branch, revisão e **Squash and Merge**.
- Este documento não autoriza commit de credenciais, publicação de custos internos, margens ou lucros.

## 2. Resumo atualizado

O projeto continua ativo e recebeu uma nova política de automação para notificações via Telegram. A configuração declara avisos de início e término de atividades e quatro relatórios diários de pendências. Entretanto, a implementação executável encontrada ainda cobre apenas o envio de ambiente web pronto ou APK pronto. Não foi encontrada integração executável para os novos eventos de atividade nem para a agenda de quatro relatórios por dia.

Também foram confirmadas as seguintes divergências:

1. o repositório permite `merge commit`, `rebase merge` e `squash merge`, portanto o uso exclusivo de **Squash and Merge** ainda não está imposto;
2. o commit atual não possui status checks nem execução de workflow associada;
3. não existem issues abertas como backlog oficial;
4. `config/module_catalog.json` contém 25 módulos, mas `MODULE_NAMES` contém 21;
5. os módulos `vision`, `legal`, `property` e `ai_core` estão ausentes da configuração empresarial;
6. o auditor `scripts/audit_confirmation_v7.py` não foi encontrado na branch `main`, impedindo a reprodução direta do relatório v7 anteriormente apresentado.

### Contagem consolidada

| Classificação | Quantidade |
|---|---:|
| Críticas | 5 |
| Altas | 9 |
| Médias | 5 |
| Secundárias | 2 |
| Resolvidas em princípio, aguardando validação | 2 |

## 3. Quadro de acompanhamento

> Os percentuais e tempos abaixo são estimativas gerenciais para organização do trabalho. Eles não substituem evidência técnica.

| Nome da atividade | Descrição | Passo sendo executado | Dificuldade [1 a 5] | % concluído | Tempo previsto | Etapas [Total] | Concluídas [X] | Pendentes [Y] |
|---|---|---|---:|---:|---|---:|---:|---:|
| Publicação externa definitiva | Homologar domínio, HTTPS, DNS, cache e headers | Aguardar credenciais e validação do ambiente final | 5 | 40% | 2h | 5 | 2 | 3 |
| API Hub público | Conectar front-end aos microsserviços reais | Configurar URL pública e repetir jornadas | 5 | 50% | 2h | 6 | 3 | 3 |
| Auditoria das 335 rotas | Validar jornadas ponta a ponta no ambiente publicado | Preparar execução e evidências | 5 | 35% | 2h30 | 6 | 2 | 4 |
| Assinatura Android | Proteger keystore, upload key e Play App Signing | Definir cofre e procedimento de recuperação | 5 | 45% | 1h30 | 4 | 2 | 2 |
| Login Google no APK | Homologar autenticação real e sessão | Executar teste com conta real | 4 | 55% | 1h30 | 5 | 3 | 2 |
| Stitch remoto | Sincronizar a tela e os manifestos pendentes | Fornecer secret e executar sincronização | 3 | 95% | 1h | 4 | 3 | 1 |
| GitHub Actions | Validar testes, segurança, web, Android, banco e artefatos | Reativar ou disparar os workflows do `main` | 5 | 25% | 2h | 5 | 1 | 4 |
| Governança de merge | Permitir exclusivamente Squash and Merge | Ajustar configurações e proteção da branch | 3 | 25% | 45min | 4 | 1 | 3 |
| Catálogo de módulos | Sincronizar catálogo, diretórios, OpenAPI e Business | Incluir quatro módulos ausentes e revalidar presets | 4 | 60% | 1h30 | 5 | 3 | 2 |
| Automação Telegram | Implementar eventos de atividade e relatórios periódicos | Criar executor, testes e integração com scheduler | 4 | 35% | 2h | 6 | 2 | 4 |
| Auditoria v7 reproduzível | Restaurar o auditor e torná-lo gate de CI | Localizar ou recriar script, fixtures e relatório | 4 | 30% | 1h30 | 5 | 1 | 4 |
| Backlog oficial | Converter pendências em issues ou project board | Definir modelo, responsáveis e critérios | 3 | 0% | 1h | 4 | 0 | 4 |

## 4. Pendências críticas

### 4.1 Publicar e homologar o ambiente externo definitivo

**Categoria:** Crítica  
**Necessidade:** concluir a publicação real no Cloudflare Pages ou no ambiente definitivo aprovado, configurar credenciais operacionais fora do repositório e validar o domínio público final.

**Inclui:**

- disponibilizar `CLOUDFLARE_API_TOKEN` e `CLOUDFLARE_ACCOUNT_ID` por cofre ou secrets;
- realizar, pelo titular, os aceites jurídicos exigidos pelo provedor;
- validar DNS, HTTPS, cache, fallback SPA e headers de segurança;
- registrar a URL pública oficial e substituir referências temporárias.

**Critério de aceite:** URL oficial acessível, certificado válido, rotas SPA funcionais, headers verificados e evidência versionada.

### 4.2 Conectar o front-end ao API Hub público e aos microsserviços reais

**Categoria:** Crítica  
**Necessidade:** configurar `VITE_API_HUB_URL` público e executar as jornadas contra os 25 microsserviços no ambiente externo.

**Inclui:** autenticação, autorização, CRUD, persistência, upload, pagamentos sandbox, auditoria, eventos, outbox e tratamento de falhas.

**Critério de aceite:** as jornadas principais devem funcionar sem fallback local e registrar evidências no backend correto.

### 4.3 Reexecutar a auditoria integral das 335 rotas no ambiente publicado

**Categoria:** Crítica  
**Necessidade:** repetir a auditoria automatizada das 335 rotas React contra o API Hub e a infraestrutura pública.

**Critérios mínimos:** ausência de erros JavaScript, telas travadas, botões mortos, formulários sem persistência, falhas de autenticação ou respostas incoerentes.

### 4.4 Proteger e governar a assinatura Android de produção

**Categoria:** Crítica  
**Necessidade:** armazenar keystore e credenciais em cofre seguro, criar backup controlado e definir formalmente Play App Signing e upload key.

**Critério de aceite:** procedimento de assinatura e recuperação testado sem expor chaves no repositório.

### 4.5 Homologar autenticação Google real no APK

**Categoria:** Crítica  
**Necessidade:** executar login completo com conta de teste real, validar token, sessão, renovação, logout, cancelamento, erro de rede e vínculo com o backend.

**Critério de aceite:** fluxo completo reproduzido em dispositivo ou emulador homologado com evidência de backend.

## 5. Pendências de prioridade alta

### 5.1 Concluir sincronização remota do Google Stitch

**Necessidade:** fornecer `STITCH_API_KEY` por secret e executar a sincronização remota dos projetos e telas.

**Escopo imediato:** validar `finance/entity_valley_gold_ledger_entries` e qualquer tela adicionada após o último manifesto.

### 5.2 Homologar infraestrutura produtiva e serviços externos

**Necessidade:** validar billing, IAM, provedores reais, cluster produtivo, bancos gerenciados, mensageria, observabilidade, secrets, backups, restauração e políticas de rede.

### 5.3 Validar e tornar obrigatórios os workflows do GitHub Actions

**Evidência atual:** o commit de referência não possui status checks nem execução de workflow associada.

**Necessidade:** confirmar os workflows de segurança, testes, banco, Android, web, Docker, artefatos e publicação, além de torná-los obrigatórios antes do merge.

**Critério de aceite:** commit do `main` com checks executados, resultados arquivados e bloqueio de merge em caso de falha.

### 5.4 Criar backlog oficial por issues ou project board

**Evidência atual:** não existem issues abertas no repositório.

**Necessidade:** transformar as pendências deste documento em itens rastreáveis com responsável, prioridade, dependências, prazo, critérios de aceite e evidências.

### 5.5 Auditar consistência entre documentação e implementação

**Necessidade:** confrontar `STATUS.md`, `ROADMAP.md`, `EXECUTION_PLAN.md`, contratos OpenAPI, catálogo de módulos, manifests Stitch, migrations e código executável.

### 5.6 Impor uso exclusivo de Squash and Merge

**Evidência atual:** o repositório permite merge commit, rebase merge e squash merge simultaneamente.

**Necessidade:**

- desabilitar `merge commit`;
- desabilitar `rebase merge`;
- manter apenas `squash merge`;
- proteger a branch `main` contra push direto;
- exigir PR, revisão e checks obrigatórios;
- padronizar título e mensagem do commit final.

**Critério de aceite:** nenhuma alteração chega à `main` por método diferente de Squash and Merge.

### 5.7 Sincronizar o catálogo de módulos com a configuração Business

**Evidência atual:** o catálogo possui 25 módulos e `MODULE_NAMES` possui 21.

**Módulos ausentes:**

- `vision`;
- `legal`;
- `property`;
- `ai_core`.

**Necessidade:** incluir nomes em pt-BR, presets, dependências, regras de visibilidade, recomendações e testes para os quatro módulos.

**Critério de aceite:** igualdade entre catálogo, diretórios, `MODULE_NAMES`, presets, contratos e OpenAPI.

### 5.8 Implementar de fato o ciclo de atividade e relatórios pelo Telegram

**Evidência atual:** a política JSON declara notificações de início e conclusão e quatro relatórios diários, mas o script executável localizado envia apenas ambiente web pronto ou APK pronto.

**Necessidade:**

- criar comandos para `activity_started` e `activity_completed`;
- validar todos os campos obrigatórios definidos na política;
- gerar relatório de pendências quatro vezes por dia no fuso `America/Sao_Paulo`;
- registrar falhas, tentativas e confirmação de entrega;
- adicionar testes sem contato real com o Telegram;
- integrar o executor ao mecanismo de agendamento aprovado.

**Critério de aceite:** execução automatizada comprovada em ambiente de teste, com secrets externos e logs auditáveis.

### 5.9 Restaurar e automatizar a auditoria de confirmação v7

**Evidência atual:** `scripts/audit_confirmation_v7.py` não foi encontrado na branch `main`, e a busca pelo relatório reproduzível não retornou artefato correspondente.

**Necessidade:**

- localizar a versão correta ou recriar o auditor;
- versionar regras, fixtures e formato de saída;
- comparar diretórios, catálogo, `MODULE_NAMES`, aplicações, OpenAPI e manifests;
- executar na CI;
- falhar o workflow quando houver divergência;
- publicar relatório como artefato do workflow.

**Critério de aceite:** qualquer pessoa autorizada consegue reproduzir o mesmo resultado a partir do commit informado.

## 6. Pendências de prioridade média

### 6.1 Revalidar o emulador Android e a instalação do APK

Aguardar boot completo, confirmar `sys.boot_completed`, instalar novamente o APK e repetir smoke tests.

### 6.2 Centralizar evidências de validação

Registrar por versão logs, relatórios, capturas, artefatos, hashes, URLs, commits e resultados dos testes.

### 6.3 Revisar dados demonstrativos e separação de ambiente

Garantir separação explícita entre dados fictícios, sandbox, homologação e produção, incluindo banners e flags de ambiente.

### 6.4 Verificar integridade dos contratos após padronização massiva

Validar compatibilidade entre DTOs, formulários, persistência, OpenAPI, eventos e migrations de todas as entidades alteradas.

### 6.5 Revisar performance, acessibilidade e responsividade em dispositivos reais

Executar Lighthouse, Web Vitals, testes de teclado, leitor de tela, contraste, zoom, telas pequenas e aparelhos Android de desempenho limitado.

## 7. Pendências secundárias

### 7.1 Ampliar documentação funcional para clientes pessoa física e jurídica

Descrever cada módulo, serviço e microsserviço em linguagem comercial, incluindo aplicação, benefícios, comodidade, usabilidade, custo e economia para o cliente, sem expor custos internos, margens ou lucros.

### 7.2 Padronizar nomenclatura e idioma do front-end

Concluir revisão pt-BR, pluralização, acentuação, mensagens de erro, labels, ajuda contextual e manutenção apenas dos termos estrangeiros consolidados no Brasil.

## 8. Itens resolvidos em princípio, aguardando validação

### 8.1 Ativos oficiais da marca Valley

Confirmar que todas as superfícies usam exclusivamente o ativo oficial vigente, sem redesenho, alteração de linhas, formas ou cores.

### 8.2 Ativos oficiais da marca Valley Riders

Confirmar presença do PNG oficial com fundo transparente e ausência de versões provisórias ou modificadas.

## 9. Plano de ação para um ciclo de 8 horas

A execução deve priorizar tarefas que aumentem rastreabilidade e evitem novas divergências. Atrasos de até 4 horas são considerados tolerância operacional normal. Após 12 horas, este documento deve ser atualizado com o que foi concluído e com as pendências restantes.

### Bloco 1, 0h a 1h

1. Restaurar ou recriar o auditor v7.
2. Executar a comparação de catálogo, diretórios, aplicações, OpenAPI e configuração Business.
3. Salvar o resultado como artefato versionado.

### Bloco 2, 1h a 2h30

1. Incluir `vision`, `legal`, `property` e `ai_core` em `MODULE_NAMES`.
2. Definir presets e dependências.
3. Criar testes unitários para recomendações e visibilidade.

### Bloco 3, 2h30 a 4h

1. Implementar comandos de início e término de atividade no Telegram.
2. Implementar geração do relatório de pendências.
3. Criar mocks e testes de falha, timeout e resposta inválida.

### Bloco 4, 4h a 5h

1. Ajustar o repositório para uso exclusivo de Squash and Merge.
2. Configurar proteção da `main`.
3. Definir checks obrigatórios e revisão mínima.

### Bloco 5, 5h a 7h

1. Executar os workflows principais.
2. Corrigir falhas diretamente relacionadas às mudanças do ciclo.
3. Arquivar logs e relatórios.

### Bloco 6, 7h a 8h

1. Atualizar este documento.
2. Criar ou atualizar issues do backlog.
3. Registrar commits, PRs, testes e bloqueios externos.
4. Preparar a retomada para o limite operacional de 12 horas.

## 10. Ordem recomendada das próximas atividades

1. Restaurar o auditor v7 e transformá-lo em gate.
2. Corrigir a divergência dos quatro módulos.
3. Implementar a automação Telegram executável.
4. Impor Squash and Merge e proteção da `main`.
5. Executar e registrar todos os workflows.
6. Publicar o ambiente externo definitivo.
7. Configurar o API Hub público.
8. Rodar a auditoria ponta a ponta das 335 rotas.
9. Homologar login Google e assinatura Android.
10. Converter pendências em backlog rastreável.

## 11. Critério de encerramento

Uma pendência somente pode ser marcada como concluída quando houver:

- implementação versionada;
- teste automatizado ou procedimento reproduzível;
- evidência do ambiente correto;
- referência ao commit e ao PR;
- ausência de bloqueio externo não declarado;
- atualização deste documento com data e evidência;
- confirmação de que nenhum segredo foi exposto.

## 12. Histórico de versões

| Versão | Data | Alteração principal |
|---|---|---|
| 2.0 | 22/07/2026 | Consolidação inicial de pendências críticas, altas, médias e secundárias. |
| 2.1 | 23/07/2026 | Inclusão de governança de merge, divergência de quatro módulos, ausência de CI no commit atual, lacuna da automação Telegram e falta do auditor v7 reproduzível. |
