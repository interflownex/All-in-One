# DIRETRIZ MANDATÓRIA E PERSISTENTE — RECOMENDAÇÕES DE USABILIDADE, COMERCIALIZAÇÃO E EVOLUÇÃO DO ALL-IN-ONE & VALLEY

**Projeto:** All-in-One & Valley  
**Finalidade:** transformar as recomendações estratégicas, comerciais e de usabilidade em regras de implementação obrigatórias, persistentes e rastreáveis no projeto.  
**Arquivo sugerido no repositório:** `docs/DIRETRIZ_MANDATORIA_USABILIDADE_COMERCIAL_VALLEY.md`  
**Dialeto padrão:** português do Brasil  
**Status:** diretriz mandatória para Codex, Antigravity, Gemini Code Assist, equipe técnica, produto, UX/UI, comercial e implantação.

---

## 1. Regra máxima

A partir desta diretriz, todo desenvolvimento do **All-in-One & Valley** deve obedecer a uma regra central:

> **O All-in-One organiza a operação empresarial. O Valley traduz essa operação em uma experiência simples, clara e comercial para o usuário final.**

O usuário final não deve enxergar a complexidade técnica dos módulos.  
O usuário pessoa jurídica não deve precisar entender arquitetura para vender.  
O investidor deve conseguir enxergar uma máquina comercial clara, mensurável e escalável.

Esta diretriz deve ser tratada como **documentação viva**, atualizada sempre que houver alteração em:

- módulo;
- API;
- tela;
- catálogo;
- fluxo de compra;
- fluxo de serviço;
- pagamento;
- publicação de oferta;
- onboarding;
- integração;
- regra comercial;
- política de confiança;
- jornada do usuário;
- métrica comercial.

---

## 2. Objetivo da implementação

Implantar de forma persistente uma camada de produto e experiência que conecte:

```text
Business / All-in-One → Catálogo Marketplace → Valley Consumer → Compra/Contratação → Pagamento → Execução/Entrega → Avaliação → BI/CRM
```

A implementação deve garantir que uma empresa, profissional ou parceiro consiga configurar produtos e serviços no **All-in-One Business**, publicar esses itens no **Marketplace** e disponibilizá-los ao usuário final no **Valley**, sempre com linguagem simples, navegação clara e rastreabilidade ponta a ponta.

---

## 3. Princípios obrigatórios

### 3.1 Usabilidade orientada por intenção

A interface do Valley deve ser orientada por intenção, não por nome técnico de módulo.

Evitar navegação centrada em nomes como:

- `Marketplace`;
- `Finance`;
- `Services`;
- `Health`;
- `Jobs`;
- `Legal`;
- `Property`;
- `Document`;
- `BPM`.

Preferir ações humanas:

- Comprar;
- Contratar serviço;
- Agendar consulta;
- Procurar emprego;
- Pagar;
- Receber;
- Acompanhar pedido;
- Guardar documentos;
- Solicitar suporte;
- Avaliar;
- Ver benefícios.

### 3.2 Complexidade invisível

A arquitetura pode possuir 25 ou mais módulos, mas o usuário deve perceber apenas jornadas simples.

Exemplo:

```text
Usuário quer contratar eletricista.
Sistema pode usar: Services + Identity + Finance + Document + Notifications + CRM.
Usuário deve ver apenas: buscar → escolher → agendar → pagar → acompanhar → avaliar.
```

### 3.3 Toda oferta deve responder perguntas simples

Cada item exibido no Valley deve responder claramente:

1. O que é?
2. Quanto custa?
3. Quem oferece?
4. O fornecedor é verificado?
5. Quando recebo ou uso?
6. Onde está disponível?
7. Como pago?
8. O que acontece depois da compra?
9. Existe garantia, reembolso ou suporte?
10. Como acompanho o andamento?

### 3.4 Publicação de oferta deve ser guiada

No All-in-One Business, o usuário PF ou PJ deve publicar ofertas por wizard simples:

1. O que você vende?
2. É produto ou serviço?
3. Qual categoria?
4. Qual ramo de atividade?
5. Qual preço?
6. Onde atende?
7. Tem estoque, agenda ou disponibilidade?
8. Quais imagens e descrições?
9. Quais regras de entrega/execução?
10. Deseja publicar no Valley?
11. Revisar e publicar.

---

## 4. Visão obrigatória por persona

## 4.1 Pessoa física como usuário final

### Expectativa

A pessoa física deve perceber o Valley como um aplicativo para resolver a vida cotidiana em um só lugar.

Ela deve conseguir:

- comprar produtos;
- contratar serviços;
- agendar consultas;
- procurar empregos;
- fazer pagamentos;
- acompanhar entregas;
- guardar documentos;
- usar benefícios;
- receber notificações;
- falar com suporte;
- avaliar fornecedores.

### Regras mandatórias para PF

- O cadastro deve ser progressivo: pedir poucos dados no início e solicitar validações adicionais apenas quando necessário.
- A busca deve ser universal.
- O catálogo deve ser regionalizado quando aplicável.
- Ofertas devem mostrar selo de confiança quando o fornecedor estiver validado.
- Pagamento deve ser simples e seguro.
- Toda compra ou contratação deve gerar histórico.
- Toda jornada deve ter status visível.
- Deve haver suporte claro.
- A linguagem deve ser popular, direta e em português do Brasil.

### Exemplo de jornada PF obrigatória

```text
Buscar eletricista → filtrar por região/avaliação/preço → escolher horário → pagar com segurança → acompanhar execução → receber comprovante → avaliar.
```

---

## 4.2 Pessoa jurídica como usuária

### Expectativa

A pessoa jurídica deve perceber o All-in-One como uma plataforma para vender mais, operar melhor e reduzir sistemas separados.

Ela deve conseguir:

- cadastrar empresa;
- validar CNPJ/KYB;
- cadastrar produtos;
- cadastrar serviços;
- publicar ofertas no Valley;
- gerenciar pedidos;
- gerenciar agenda;
- acompanhar pagamentos;
- ver clientes;
- acessar CRM;
- consultar relatórios;
- controlar usuários e permissões;
- integrar estoque, entrega, documentos e financeiro.

### Regras mandatórias para PJ

- O painel Business deve ter onboarding guiado.
- Publicar uma oferta deve exigir o menor número possível de passos.
- O sistema deve informar se a oferta está em rascunho, revisão, publicada, pausada ou rejeitada.
- A PJ deve ver claramente taxas, repasses, pedidos e pendências.
- O painel deve mostrar métricas simples: visualizações, cliques, vendas, conversão, avaliações e faturamento.
- Toda oferta deve ter categoria empresarial, ramo de atividade e tipo de empresa.
- O sistema deve permitir múltiplos usuários e permissões por empresa.
- Franquias e redes devem conseguir padronizar catálogo por unidade.

### Exemplo de jornada PJ obrigatória

```text
Cadastrar empresa → validar documentos → criar produto ou serviço → definir preço/estoque/agenda → publicar no Valley → receber pedido → executar/entregar → receber pagamento → acompanhar relatório.
```

---

## 4.3 Investidor

### Expectativa

O investidor deve conseguir enxergar uma máquina comercial clara, não apenas uma coleção de módulos.

A tese deve ser demonstrada por:

- jornada ponta a ponta funcionando;
- oferta publicada por PJ;
- usuário PF comprando/contratando;
- pagamento realizado;
- pedido/serviço executado;
- repasse registrado;
- avaliação gerada;
- dados indo para BI/CRM;
- métricas reais de aquisição, ativação e retenção.

### Regras mandatórias para visão de investimento

O projeto deve manter uma matriz de métricas com:

- número de empresas cadastradas;
- número de empresas verificadas;
- número de ofertas publicadas;
- número de ofertas ativas;
- número de usuários finais cadastrados;
- número de compras/contratações;
- taxa de conversão;
- ticket médio;
- GMV;
- receita líquida;
- taxa de falha de pagamento;
- taxa de cancelamento;
- tempo médio de publicação de oferta;
- tempo médio de onboarding PJ;
- retenção PF;
- retenção PJ;
- NPS ou avaliação média.

---

## 5. Prioridade mandatória de execução

A implementação deve seguir esta sequência de prioridade.

---

## 5.1 Sprint 1 — Catálogo vendável

### Objetivo

Permitir que uma empresa ou profissional publique uma oferta no Business e que ela apareça no Valley.

### Entregas obrigatórias

- Criar/validar entidade unificada de oferta.
- Criar status de oferta:
  - `draft`;
  - `pending_review`;
  - `published`;
  - `paused`;
  - `rejected`;
  - `archived`.
- Criar vínculo entre oferta e:
  - empresa;
  - usuário responsável;
  - módulo de origem;
  - categoria;
  - ramo de atividade;
  - tipo de empresa;
  - localização;
  - disponibilidade;
  - preço;
  - mídia;
  - política de entrega/execução.
- Criar endpoint de publicação.
- Criar endpoint de listagem pública para Valley.
- Criar endpoint de busca/filtro.
- Criar histórico de alteração da oferta.

### Critério de aceite

Uma empresa deve conseguir criar uma oferta e o usuário final deve vê-la no catálogo Valley.

---

## 5.2 Sprint 2 — Compra e contratação

### Objetivo

Permitir que o usuário final compre produto ou contrate serviço.

### Entregas obrigatórias

- Criar pedido.
- Associar pedido à oferta.
- Associar pedido ao usuário final.
- Criar status:
  - `created`;
  - `awaiting_payment`;
  - `paid`;
  - `accepted`;
  - `in_progress`;
  - `delivered`;
  - `completed`;
  - `cancelled`;
  - `refunded`;
  - `disputed`.
- Implementar pagamento sandbox.
- Gerar histórico do consumidor.
- Notificar empresa.
- Notificar consumidor.
- Registrar evento outbox.

### Critério de aceite

Usuário final deve comprar/contratar pelo Valley e a empresa deve visualizar o pedido no Business.

---

## 5.3 Sprint 3 — Serviços, agenda e execução

### Objetivo

Viabilizar contratação de serviços com agenda, aceite, execução e avaliação.

### Entregas obrigatórias

- Criar disponibilidade/agenda para prestador.
- Permitir reserva de horário.
- Permitir confirmação do prestador.
- Permitir envio de orçamento quando serviço for sob consulta.
- Permitir aceite do usuário.
- Permitir pagamento seguro/escrow sandbox.
- Permitir evidência de execução.
- Permitir avaliação.
- Permitir abertura de suporte ou disputa por pedido com rastreio e retorno.

### Incremento implementado em 6 de junho de 2026

- O histórico do consumidor oferece avaliação para pedidos entregues ou
  concluídos.
- O API Hub valida titularidade e estado do pedido antes da publicação.
- A avaliação registra nota de 1 a 5, comentário opcional, moderação básica
  anti-burla, idempotência, auditoria e evento outbox
  `valley.review.created`.
- A persistência PostgreSQL garante uma avaliação por consumidor e pedido.
- O suporte/disputa registra `marketplace.dispute.created` ou
  `support.ticket.created`, com visibilidade comercial em CRM/BI.

### Critério de aceite

Usuário deve contratar um serviço com horário definido, pagar, acompanhar e avaliar.

---

## 5.4 Sprint 4 — Confiança, suporte e pós-venda

### Objetivo

Reduzir risco percebido e aumentar confiança.

### Entregas obrigatórias

- Selo de empresa verificada.
- Selo de profissional verificado.
- Política de cancelamento por oferta.
- Política de reembolso por oferta.
- Suporte por pedido.
- Abertura de disputa.
- Registro de mensagens e anexos.
- Avaliações com nota e comentário.
- Moderação básica.
- Notificações de mudança de status.

### Critério de aceite

Usuário deve saber o que fazer quando algo falhar.

---

## 5.5 Sprint 5 — Comercialização e planos

### Objetivo

Transformar o produto em máquina comercial.

### Entregas obrigatórias

- Criar planos:
  - gratuito;
  - básico;
  - profissional;
  - empresa;
  - franquia;
  - enterprise.
- Criar limites por plano:
  - quantidade de ofertas;
  - usuários;
  - módulos;
  - transações;
  - mídia;
  - relatórios;
  - automações.
- Criar dashboard PJ.
- Criar métricas comerciais.
- Criar onboarding guiado.
- Criar materiais de venda.
- Criar tela de upgrade.

### Critério de aceite

Uma PJ deve entender rapidamente por que pagar e qual plano escolher.

---

## 6. Modelo obrigatório de oferta de catálogo

Toda oferta publicada no Valley deve seguir este modelo lógico.

```yaml
catalog_offer:
  id: uuid
  source_module: string
  source_entity_id: uuid
  business_id: uuid
  owner_user_id: uuid
  offer_type: product | service | appointment | job | course | legal | health | property | delivery | finance | document | government
  title: string
  short_description: string
  full_description: text
  category_id: uuid
  business_category: string
  business_type: string
  activity_branch: string
  price_type: fixed | variable | quote | free | subscription
  price_amount: decimal
  currency: BRL
  location_type: local | regional | national | online | hybrid
  availability_type: stock | schedule | quote | immediate | manual
  status: draft | pending_review | published | paused | rejected | archived
  trust_badges: array
  media: array
  payment_methods: array
  fulfillment_policy: object
  cancellation_policy: object
  refund_policy: object
  metadata: json
  created_at: timestamp
  updated_at: timestamp
  published_at: timestamp
```

---

## 7. Módulos que devem abastecer o catálogo

Os módulos abaixo devem ser tratados como fontes de oferta para o Valley quando aplicável.

| Módulo      | Tipo de oferta gerada         | Exemplo para usuário final                             |
| ----------- | ----------------------------- | ------------------------------------------------------ |
| Marketplace | Produto físico/digital        | Comprar cadeira, alimento, eletrônico                  |
| Stock       | Produto com estoque           | Produto disponível para entrega                        |
| Services    | Serviço profissional          | Eletricista, consultor, diarista                       |
| Health      | Consulta/exame                | Agendar dermatologista                                 |
| Legal       | Serviço jurídico              | Revisão de contrato                                    |
| Education   | Curso/trilha                  | Curso com certificado                                  |
| Jobs        | Vaga/oportunidade             | Candidatar-se a vaga                                   |
| Property    | Imóvel/serviço imobiliário    | Alugar imóvel, vistoria                                |
| Delivery    | Entrega/coleta                | Solicitar entrega expressa                             |
| Mobility    | Corrida/transporte            | Agendar deslocamento                                   |
| Finance     | Produto financeiro            | Pagamento, boleto, carteira, crédito quando homologado |
| Document    | Documento/assinatura          | Assinar contrato, guardar laudo                        |
| Gov Digital | Serviço público               | Solicitar certidão                                     |
| HR          | Treinamento/benefício         | Curso interno, benefício corporativo                   |
| CRM         | Campanha/oferta personalizada | Promoção recomendada                                   |
| BI          | Recomendação/insight          | Ofertas mais relevantes                                |
| AI Core     | Assistente/recomendação       | Ajuda para escolher serviço                            |
| Vision      | Evidência/monitoramento       | Prova visual de entrega                                |
| WMS/TMS/YMS | Suporte logístico             | Prazo real de entrega                                  |

---

## 8. Regras obrigatórias de UX/UI

## 8.1 Catálogo Valley

O catálogo deve conter:

- busca universal;
- filtros simples;
- categorias visuais;
- cards objetivos;
- preço visível;
- selo de confiança;
- avaliação;
- distância ou disponibilidade;
- botão de ação claro;
- status de entrega/execução;
- linguagem em português do Brasil.

## 8.2 Card de oferta

Todo card deve exibir:

- imagem;
- título;
- descrição curta;
- preço ou “sob orçamento”;
- fornecedor;
- selo verificado quando aplicável;
- avaliação;
- disponibilidade;
- botão principal:
  - Comprar;
  - Contratar;
  - Agendar;
  - Solicitar orçamento;
  - Candidatar-se;
  - Ver detalhes.

## 8.3 Página de detalhe

A página de detalhe deve mostrar:

- descrição completa;
- imagens;
- quem oferece;
- documentos/selo de confiança;
- preço;
- formas de pagamento;
- prazo;
- região atendida;
- política de cancelamento;
- política de reembolso;
- avaliações;
- perguntas frequentes;
- botão de ação principal.

---

## 9. Regras obrigatórias para Business

## 9.1 Painel Business

O painel deve permitir:

- criar oferta;
- editar oferta;
- pausar oferta;
- republicar oferta;
- ver pedidos;
- ver agenda;
- ver pagamentos;
- ver avaliações;
- responder suporte;
- acompanhar métricas;
- controlar usuários.

## 9.2 Wizard de criação de oferta

Implementar wizard obrigatório com estas etapas:

1. Tipo de oferta.
2. Categoria.
3. Título e descrição.
4. Imagens.
5. Preço.
6. Estoque, agenda ou disponibilidade.
7. Região atendida.
8. Pagamento.
9. Políticas.
10. Revisão.
11. Publicação.

## 9.3 Validação antes da publicação

Nenhuma oferta deve ser publicada se faltar:

- título;
- categoria;
- fornecedor;
- tipo de oferta;
- preço ou regra de orçamento;
- status de disponibilidade;
- política de execução;
- localização/região quando aplicável.

---

## 10. Regras obrigatórias de confiança

A confiança deve ser visível.

Implementar:

- selo de identidade confirmada;
- selo de empresa verificada;
- selo de profissional validado;
- selo de pagamento seguro;
- selo de entrega rastreável;
- histórico de avaliações;
- política de disputa;
- suporte visível;
- registro de eventos.

---

## 11. Eventos obrigatórios

Implementar eventos de domínio para rastreabilidade:

```text
business.offer.created
business.offer.updated
business.offer.submitted_for_review
marketplace.offer.published
marketplace.offer.paused
marketplace.offer.rejected
valley.offer.viewed
valley.offer.clicked
valley.order.created
valley.order.payment_authorized
valley.order.payment_failed
valley.order.accepted
valley.order.in_progress
valley.order.completed
valley.order.cancelled
valley.order.refunded
valley.review.created
support.ticket.created
```

Todos os eventos devem passar por outbox quando houver mudança persistida em banco.

---

## 12. Métricas obrigatórias

O projeto deve medir:

### PF

- buscas realizadas;
- ofertas visualizadas;
- cliques;
- compras;
- contratações;
- cancelamentos;
- avaliações;
- retenção;
- ticket médio;
- frequência de uso.

### PJ

- ofertas criadas;
- ofertas publicadas;
- ofertas rejeitadas;
- pedidos recebidos;
- pedidos concluídos;
- faturamento;
- avaliações;
- tempo médio de publicação;
- conversão por oferta;
- módulos ativos.

### Investidor

- GMV;
- receita líquida;
- CAC;
- LTV;
- churn PF;
- churn PJ;
- take rate;
- conversão PF;
- ativação PJ;
- número de fornecedores ativos;
- número de ofertas ativas;
- margem por vertical.

---

## 13. Regra de foco para MVP comercial

É proibido tentar provar todos os módulos ao mesmo tempo no primeiro ciclo comercial.

O MVP comercial deve focar em:

1. Identity;
2. Business;
3. Marketplace;
4. Services;
5. Finance sandbox;
6. Valley Consumer;
7. CRM básico;
8. Document básico;
9. Notifications.

Os demais módulos entram como expansão, beta controlado ou upsell.

---

## 14. Demonstração obrigatória

O projeto deve manter uma demo funcional com esta cadeia:

```text
PJ cadastra empresa
→ PJ cria oferta
→ PJ publica no Valley
→ PF encontra oferta
→ PF compra ou contrata
→ pagamento sandbox é registrado
→ pedido/serviço muda status
→ PF acompanha
→ PF avalia
→ PJ vê resultado
→ BI/CRM registra evento
```

Esta demo é a prova central para:

- equipe interna;
- parceiros;
- investidores;
- clientes-piloto;
- materiais comerciais.

---

## 15. Pendências mandatórias a resolver

## 15.1 Produto e interface

- Finalizar telas Valley Consumer.
- Finalizar painel Business.
- Finalizar wizard de publicação.
- Criar tela de detalhe de oferta.
- Criar tela de pedido.
- Criar tela de histórico.
- Criar tela de suporte.
- Criar dashboard PJ.

## 15.2 Backend e APIs

- Consolidar entidade unificada de oferta.
- Implementar APIs de publicação.
- Implementar APIs de busca.
- Implementar APIs de pedido.
- Implementar APIs de pagamento sandbox.
- Implementar APIs de avaliação.
- Implementar eventos outbox.

## 15.3 Comercial

- Definir planos.
- Definir limites.
- Definir take rate.
- Definir comissões.
- Definir política freemium.
- Definir vertical inicial.
- Criar material comercial.
- Criar roteiro de demonstração.

## 15.4 Operação

- Criar suporte inicial.
- Criar monitoramento.
- Criar logs de auditoria.
- Criar política de disputa.
- Criar política de reembolso.
- Criar documentação de onboarding.

---

## 16. Critérios de aceite global

A implementação será aceita quando:

- [ ] Uma PJ conseguir cadastrar uma oferta pelo Business.
- [ ] A oferta aparecer no Valley.
- [ ] O usuário PF conseguir encontrar a oferta.
- [ ] O usuário PF conseguir comprar ou contratar.
- [ ] O pagamento sandbox for registrado.
- [ ] A PJ receber o pedido.
- [ ] O pedido tiver status rastreável.
- [ ] O usuário PF conseguir acompanhar.
- [ ] O usuário PF conseguir avaliar.
- [ ] O CRM/BI registrar os eventos.
- [ ] O fluxo funcionar em demo ponta a ponta.
- [ ] A interface estiver em português do Brasil.
- [ ] A navegação for orientada por intenção.
- [ ] O catálogo estiver legível para usuário comum.
- [ ] As regras comerciais estiverem documentadas.
- [ ] O fluxo estiver coberto por testes E2E.

---

## 17. Instrução direta para Codex / Antigravity / Gemini Code Assist

Executar a implementação como regra mandatória.

Priorizar o ciclo:

```text
Oferta → Catálogo → Compra/Contratação → Pagamento → Execução → Avaliação → Métricas
```

Não dispersar esforço em módulos avançados antes da prova comercial base.

Sempre que criar nova funcionalidade, atualizar:

- `docs/DIRETRIZ_MANDATORIA_USABILIDADE_COMERCIAL_VALLEY.md`;
- `docs/ROADMAP.md`;
- `STATUS.md`;
- documentação do módulo afetado;
- OpenAPI do módulo afetado;
- testes E2E;
- matriz de rastreabilidade.

---

## 18. Frase norteadora do projeto

> **O All-in-One é a infraestrutura. O Valley é a experiência. O Business é a origem das ofertas. O Marketplace é a ponte. O usuário final quer resolver a vida em poucos toques.**

---

## 19. Determinação final

Esta diretriz deve ser considerada **mandatória, persistente e evolutiva**.

Nenhuma nova tela, módulo, endpoint, oferta ou integração deve ser considerada completa se não responder a pelo menos uma destas perguntas:

1. Isso facilita a vida do usuário final?
2. Isso ajuda a empresa a vender ou operar melhor?
3. Isso aumenta confiança?
4. Isso gera métrica comercial?
5. Isso aproxima o projeto de uma jornada ponta a ponta funcional?

Se a resposta for negativa para todas, a implementação deve ser reavaliada.
