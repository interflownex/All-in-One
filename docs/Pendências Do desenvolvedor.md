# Pendências do Desenvolvedor

**Versão:** 2.2  
**Data da verificação:** 23/07/2026  
**Repositório verificado:** `interflownex/All-in-One`  
**Branch de referência:** `main`  
**Commit de referência:** `3842a64e4f5439a8c8021e60ee71369485c11073`  
**Pasta lógica do projeto:** `Pendências > Técnico > Equipe técnica`  
**Público principal:** IA desenvolvedora, desenvolvimento, DevOps, segurança e gestão técnica  
**Objetivo:** consolidar pendências reais, remover duplicidades, registrar novas divergências e dimensionar os próximos ciclos técnicos.

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

A análise do PDV confirmou que o repositório já possui partes fundamentais distribuídas entre Marketplace, Finance, ERP, WMS, Business e Valley Business, incluindo lojas, produtos, carrinhos, pedidos, pagamentos, Pix, conciliação, estoque, fiscal, permissões e auditoria. Entretanto, ainda não existe um módulo de frente de caixa completo e explicitamente consolidado, com abertura e fechamento de caixa, turno de operador, venda presencial, troco, cancelamento controlado, operação offline, pareamento com o aplicativo Valley e integração operacional com equipamentos.

Também foram confirmadas as seguintes divergências:

1. o repositório permite `merge commit`, `rebase merge` e `squash merge`, portanto o uso exclusivo de **Squash and Merge** ainda não está imposto;
2. o commit atual não possui status checks nem execução de workflow associada;
3. não existem issues abertas como backlog oficial;
4. `config/module_catalog.json` contém 25 módulos, mas `MODULE_NAMES` contém 21;
5. os módulos `vision`, `legal`, `property` e `ai_core` estão ausentes da configuração empresarial;
6. o auditor `scripts/audit_confirmation_v7.py` não foi encontrado na branch `main`, impedindo a reprodução direta do relatório v7 anteriormente apresentado;
7. as diretrizes funcionais do PDV ainda não possuem contrato de domínio, modelo de dados, telas Stitch, jornadas E2E nem critérios de homologação próprios.

### Contagem consolidada

| Classificação | Quantidade |
|---|---:|
| Críticas | 5 |
| Altas | 14 |
| Médias | 7 |
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
| Núcleo do PDV | Consolidar venda presencial, caixa, operador, pedidos, estoque e financeiro | Definir contrato, entidades e jornada mínima | 5 | 15% | 4h | 8 | 1 | 7 |
| Venda offline | Permitir operação sem internet e sincronização posterior segura | Projetar fila local, idempotência e resolução de conflitos | 5 | 5% | 4h | 7 | 0 | 7 |
| Integração Valley no caixa | Parear aplicativo e PDV por QR Code ou Bluetooth autorizado | Definir sessão temporária e confirmação do cliente | 4 | 10% | 3h | 7 | 1 | 6 |
| Promoções e fila digital | Gerenciar combos temporários, presença em loja e acompanhamento de pedidos | Definir regras, consentimentos e notificações | 4 | 10% | 3h | 7 | 1 | 6 |
| Personalização responsável | Evitar ofertas inadequadas e governar preferências sensíveis | Submeter desenho à privacidade e ao jurídico | 5 | 0% | 3h | 8 | 0 | 8 |

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

### 5.10 Consolidar o núcleo funcional do PDV

**Contexto:** o PDV não será apenas uma tela de checkout. Ele deve funcionar como a frente de operação presencial integrada ao ecossistema All-in-One e Valley.

**Necessidade:** definir contrato de domínio, APIs, migrations, eventos, permissões e telas para:

- abertura, pausa, retomada e fechamento de caixa;
- turno e identificação do operador;
- venda com ou sem cliente identificado;
- busca, leitura e inclusão de produtos;
- alteração de quantidade e desconto conforme alçada;
- dinheiro, Pix, cartão, carteira Valley e pagamento combinado;
- cálculo de troco;
- cancelamento, estorno, devolução, sangria e suprimento;
- baixa de estoque, pedido, financeiro, conciliação e documento fiscal;
- comprovante digital ou impresso;
- funcionamento adaptável a varejo, alimentação, serviços e redes de lojas.

**Critério de aceite:** jornada presencial completa, auditável e integrada, sem depender exclusivamente do aplicativo Valley.

### 5.11 Implementar venda offline com sincronização segura

**Diretriz aprovada:** o caixa deve continuar vendendo quando houver queda de internet.

**Necessidade:** projetar armazenamento local criptografado, fila de operações, identificadores idempotentes, sincronização posterior, resolução de conflitos, limite de risco e bloqueio de operações que exijam autorização online.

**Regras mínimas:**

- nunca duplicar pedido, pagamento ou baixa de estoque durante a reconexão;
- informar claramente ao operador o estado offline;
- separar pagamentos realmente autorizados de pagamentos pendentes;
- manter trilha de auditoria local e remota;
- permitir políticas distintas por empresa, filial e meio de pagamento.

**Critério de aceite:** venda offline reproduzida, reconectada e conciliada sem duplicidade ou perda de registros.

### 5.12 Integrar o aplicativo Valley ao PDV sem torná-lo obrigatório

**Diretriz aprovada:** clientes com o aplicativo Valley poderão interagir com o PDV, mas clientes sem aplicativo continuarão sendo atendidos por todos os meios tradicionais.

**Necessidade:** suportar duas formas complementares de vínculo:

1. leitura de QR Code apresentado pelo PDV ou pelo aplicativo;
2. descoberta por Bluetooth de baixa energia, sempre seguida de autorização e confirmação explícita.

**Regras de segurança e experiência:**

- não selecionar cliente apenas pela intensidade do sinal Bluetooth;
- não abrir pedido apenas porque um aparelho foi detectado;
- criar sessão temporária, curta e vinculada à venda atual;
- solicitar confirmação no aplicativo do cliente;
- permitir confirmação verbal pelo operador somente como etapa adicional, nunca como autenticação única;
- evitar exposição de uma lista ampla de nomes de clientes presentes na loja;
- exibir somente os dados mínimos necessários após autorização;
- encerrar o vínculo quando a venda terminar, expirar ou for cancelada.

**Critério de aceite:** três ou mais clientes próximos podem estar com o aplicativo aberto sem que pedidos, identidades ou pagamentos sejam associados à pessoa errada.

### 5.13 Implementar fila digital e acompanhamento de pedidos

**Diretriz aprovada:** o operador poderá perguntar se o cliente possui o aplicativo Valley. Caso possua, o cliente poderá ler um QR Code e acompanhar seu pedido pelo celular.

**Necessidade:**

- gerar senha ou identificador de pedido;
- mostrar estados como recebido, em preparação, pronto, saiu para entrega, retirado, concluído e cancelado;
- enviar atualização no aplicativo quando houver consentimento;
- manter painel ou chamada tradicional para clientes sem aplicativo;
- integrar pedidos do balcão, aplicativo, retirada e delivery na mesma fila operacional;
- impedir que informações pessoais sejam exibidas publicamente no painel.

**Critério de aceite:** clientes com e sem aplicativo acompanham o pedido sem depender de fluxos separados ou exclusivos.

### 5.14 Implementar combos temporários e ofertas por presença na loja

**Diretriz aprovada:** o gerente poderá criar, ativar, pausar e encerrar combos a qualquer momento, sem depender de campanhas fixas.

**Necessidade:**

- definir produto, quantidade, preço, período opcional, filial e limite de estoque;
- ativar ou finalizar imediatamente;
- registrar usuário responsável e histórico de alterações;
- impedir venda após expiração, encerramento ou falta de estoque;
- permitir oferta no PDV, no aplicativo e na fila digital;
- detectar presença por geofencing, QR Code, Bluetooth ou combinação de sinais de baixo consumo;
- considerar tempo mínimo configurável de permanência, inicialmente idealizado em três minutos;
- respeitar permissão de localização, notificações e personalização;
- limitar frequência para evitar insistência e consumo desnecessário de bateria.

**Critério de aceite:** promoção correta é entregue apenas para a filial, período, público autorizado e estoque definidos, com opção fácil de ignorar ou desativar.

### 5.15 Governar personalização de ofertas e dados sensíveis

**Bloqueio obrigatório:** informações de saúde, prontuário ou qualquer dado que revele condição médica não podem ser reutilizados automaticamente para publicidade ou recomendação comercial.

**Necessidade:** antes de qualquer implementação:

- realizar análise jurídica, de privacidade e segurança;
- produzir relatório de impacto quando aplicável;
- separar tecnicamente o domínio clínico do domínio comercial;
- proibir acesso direto do PDV a prontuários ou diagnósticos;
- priorizar preferências comerciais voluntariamente declaradas, como sem açúcar, sem lactose, vegetariano ou alergênicos;
- obter consentimento específico, destacado, informado e revogável para qualquer uso de dado sensível;
- permitir que o usuário não responda e continue utilizando a plataforma normalmente;
- registrar finalidade, origem, validade e revogação do consentimento;
- criar alternativa sem perfilamento;
- impedir inferências discriminatórias ou exposição da condição do cliente ao operador.

**Critério de aceite:** aprovação formal de privacidade e jurídico, consentimentos auditáveis, isolamento de dados e testes que comprovem que o PDV não acessa informações clínicas indevidas.

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

### 6.6 Implementar sugestões da Helena em tempo real para o operador

**Diretriz aprovada:** a Helena poderá apoiar o operador durante a venda, sem executar operações financeiras sensíveis sozinha.

**Sugestões previstas:**

- combos ativos e produtos comprados em conjunto;
- substitutos disponíveis quando faltar estoque;
- alerta de produto próximo da validade;
- confirmação de desconto fora do padrão;
- oportunidade de fidelidade, Pepitas ou benefício disponível;
- alerta de possível erro de quantidade, preço ou duplicidade;
- orientação contextual sobre a próxima etapa da venda.

**Restrições:** sugestões devem ser explicáveis, não invasivas, dispensáveis e submetidas às permissões da empresa. Desconto elevado, cancelamento, estorno, sangria, suprimento e alteração fiscal continuam exigindo ação humana autorizada.

### 6.7 Criar destaques de venda e resumo operacional

**Diretriz aprovada:** o gerente e o operador autorizado poderão visualizar os destaques do período.

**Inclui:** produtos mais vendidos, horários de maior movimento, ticket médio, meios de pagamento, combos com melhor resultado, cancelamentos, devoluções, rupturas de estoque e diferenças de caixa.

**Critério de aceite:** métricas reproduzíveis, filtráveis por empresa, filial, caixa, operador e período, sem exposição indevida de dados pessoais.

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

## 10. Trilha planejada para construção do PDV

### Fase 1 — contrato e arquitetura

1. decidir se o PDV será módulo próprio ou aplicação orquestradora dos módulos existentes;
2. definir entidades, eventos, estados, permissões, APIs e migrations;
3. mapear reutilização de Marketplace, Finance, ERP, WMS, Business, Identity e BI;
4. criar contrato funcional e critérios de aceite.

### Fase 2 — frente de caixa mínima

1. criar abertura de caixa e turno do operador;
2. implementar busca, leitura, carrinho, quantidade, desconto e total;
3. implementar dinheiro, Pix, cartão e troco;
4. concluir venda, comprovante, baixa de estoque e lançamento financeiro;
5. criar fechamento e relatório de caixa.

### Fase 3 — segurança e operação offline

1. criar fila local criptografada;
2. definir idempotência e reconciliação;
3. limitar operações de risco offline;
4. testar queda de rede durante cada etapa da venda;
5. sincronizar sem duplicidade.

### Fase 4 — integração com o aplicativo Valley

1. implementar QR Code de vínculo e acompanhamento;
2. prototipar Bluetooth de baixa energia com autorização explícita;
3. criar sessão temporária por venda;
4. testar múltiplos clientes próximos;
5. manter atendimento integral sem aplicativo.

### Fase 5 — fila digital, combos e presença

1. integrar pedidos do balcão, aplicativo, retirada e delivery;
2. criar painel e notificações de acompanhamento;
3. permitir combos temporários controlados pelo gerente;
4. implementar presença de baixo consumo e limites de frequência;
5. registrar consentimento e preferências.

### Fase 6 — inteligência e indicadores

1. conectar Helena ao contexto do caixa com ações apenas sugestivas;
2. criar destaques de venda e alertas operacionais;
3. validar explicabilidade, permissões e auditoria;
4. medir impacto sem expor dados pessoais.

### Fase 7 — privacidade e homologação

1. concluir avaliação jurídica e de proteção de dados;
2. testar isolamento entre saúde e comércio;
3. homologar dispositivos, impressoras, leitores e integrações fiscais escolhidas;
4. executar testes E2E, segurança, acessibilidade e carga;
5. publicar somente após evidências reproduzíveis.

## 11. Ordem recomendada das próximas atividades

1. Restaurar o auditor v7 e transformá-lo em gate.
2. Corrigir a divergência dos quatro módulos.
3. Implementar a automação Telegram executável.
4. Impor Squash and Merge e proteção da `main`.
5. Executar e registrar todos os workflows.
6. Definir o contrato de domínio e a arquitetura do PDV.
7. Criar a frente de caixa mínima integrada a Marketplace, Finance, ERP e WMS.
8. Implementar venda offline e reconciliação.
9. Implementar integração opcional com o aplicativo Valley.
10. Implementar fila digital, combos temporários e presença de baixo consumo.
11. Submeter a personalização de ofertas à validação jurídica e de privacidade.
12. Implementar Helena e destaques de venda.
13. Publicar o ambiente externo definitivo.
14. Configurar o API Hub público.
15. Rodar a auditoria ponta a ponta das 335 rotas.
16. Homologar login Google e assinatura Android.
17. Converter pendências em backlog rastreável.

## 12. Critério de encerramento

Uma pendência somente pode ser marcada como concluída quando houver:

- implementação versionada;
- teste automatizado ou procedimento reproduzível;
- evidência do ambiente correto;
- referência ao commit e ao PR;
- ausência de bloqueio externo não declarado;
- atualização deste documento com data e evidência;
- confirmação de que nenhum segredo foi exposto.

## 13. Histórico de versões

| Versão | Data | Alteração principal |
|---|---|---|
| 2.0 | 22/07/2026 | Consolidação inicial de pendências críticas, altas, médias e secundárias. |
| 2.1 | 23/07/2026 | Inclusão de governança de merge, divergência de quatro módulos, ausência de CI no commit atual, lacuna da automação Telegram e falta do auditor v7 reproduzível. |
| 2.2 | 23/07/2026 | Registro das diretrizes planejadas do PDV: núcleo de caixa, venda offline, integração opcional com Valley, Bluetooth e QR Code autorizados, fila digital, combos temporários, presença em loja, Helena, destaques de venda e governança de dados sensíveis. |
