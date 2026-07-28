# APK Valley Consumidor — Rodada 004 de Inovação

**Versão:** 4.1.0  
**Data e hora:** 28/07/2026 às 00:29:53  
**Fuso horário:** `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `codex/apk-valley-rodada-004-2026-07-28`  
**Commit-base:** `77fa6fab5f1c881ba6289dc288dc64e20421614a`  
**Classificação:** `Inovação > APK Valley Consumidor > Rodada 004`

## 1. Decisões consolidadas

A decisão do aprovador foi aplicada às 24 ideias da rodada:

- 23 ideias foram aprovadas para implantação progressiva;
- a ideia 5, **Conserte, Alugue ou Compre**, foi marcada como `P0`;
- a ideia 6, **Bolsa Segura de Sobras Produtivas**, foi redirecionada para o `Marketplace`, sem implantação no módulo `STOCK`;
- a ideia 14, **Cadeia de Custódia Sensorial**, foi rejeitada e bloqueada nesta rodada;
- as demais ideias foram classificadas como aprovadas em prioridade `P1`.

## 2. Implementação executável criada

Foi criada a aplicação FastAPI `modules/valley_consumer`, responsável por expor os contratos e regras da Rodada 004.

### Rotas gerais

- `GET /health`;
- `GET /innovation/round-004`;
- `GET /innovation/round-004/{idea_id}`;
- `POST /innovation/round-004/{idea_id}/records`.

A criação genérica de registros atende às ideias aprovadas e recusa a ideia 14 com erro de conflito.

## 3. Regras especiais implementadas

### Ideia 5 — Marketplace P0

Foi criado o contrato de comparação entre:

- reparo;
- aluguel;
- empréstimo autorizado;
- produto recondicionado;
- compra nova.

A classificação deve evoluir para considerar custo total, disponibilidade, garantia e período declarado de uso.

### Ideia 6 — Sobras produtivas no Marketplace

O cadastro foi implementado em rota própria do Marketplace. Materiais declarados como perigosos ou regulados são recusados. Itens aceitos entram em revisão de segurança antes da publicação.

### Ideia 9 — Contrato por resultado medido

Foram implantados:

- valor protegido em escrow lógico;
- prazo máximo de validação configurável;
- evidências do profissional e do cliente;
- liberação imediata quando o cliente aceita;
- retenção para revisão quando o cliente apresenta evidência de falha;
- liberação automática ao profissional após o prazo quando não existe comprovação suficiente do cliente.

A regra protege simultaneamente o direito do cliente ao serviço contratado e o direito do profissional ao pagamento pelo trabalho entregue.

### Ideia 10 — Mobilidade com abrangência comprovada

Foi criado um registro de prontidão por operador, estado, cidade e modalidade. Cada integração é classificada como:

- `full`;
- `partial`;
- `not_eligible`.

A API impede alegação de cobertura nacional enquanto não houver comprovação de API em produção, bilhetagem e forma de pagamento digital compatível.

A pesquisa inicial confirmou disponibilidade fragmentada:

- a SPTrans mantém API oficial com posição de veículos e previsão de chegada;
- a ARTESP disponibiliza GTFS das regiões metropolitanas fiscalizadas no Estado de São Paulo;
- Belo Horizonte disponibiliza GTFS e GTFS Realtime;
- Fortaleza disponibiliza arquivos GTFS oficiais;
- Metrô e CPTM de São Paulo aceitam bilhete unitário por QR Code, e determinadas catracas aceitam cartão por aproximação.

Essas evidências permitem pilotos regionais, mas não comprovam cobertura integral dos 26 estados e do Distrito Federal.

Fontes oficiais iniciais:

- https://www.sptrans.com.br/desenvolvedores/api-do-olho-vivo-guia-de-referencia/documentacao-api/
- https://dadosabertos.artesp.sp.gov.br/pt_BR/dataset/gtfs
- https://ckan.pbh.gov.br/dataset/gtfs
- https://ckan.pbh.gov.br/dataset/gtfs-rt
- https://dados.fortaleza.ce.gov.br/dataset/especificacao-geral-feed-transito-gtfs-010-2025
- https://www.metro.sp.gov.br/pt_BR/sua-viagem/bilhetes-cartoes/

### Ideia 11 — Programa piloto voluntário

A adesão empresarial foi implementada como `opt-in`. Empresas que não aceitarem voluntariamente não podem ser inseridas no piloto.

### Ideia 13 — Despensa e lista contínua de compras

Foram implantadas operações para:

- criar a lista;
- adicionar itens progressivamente;
- registrar quantidade, preço estimado e data desejada;
- sugerir revisão quando houver saldo disponível e itens pendentes;
- verificar se o valor estimado cabe no saldo informado;
- marcar automaticamente itens como comprados após a confirmação da transação.

### Ideia 19 — Agenda de medicação

A agenda somente pode ser criada a partir de prescrição verificada. O sistema gera os horários conforme intervalo e duração prescritos e permite ao usuário confirmar se tomou ou não cada dose.

O aplicativo não altera dose, intervalo ou duração e não substitui o profissional de saúde.

### Ideia 23 — Autonomia da Helena

Foi criado contrato para orçamento por usuário, módulo, ação, nível de autonomia, limite financeiro e validade.

### Ideia 24 — Continuidade offline

Foi criada fila lógica de eventos offline com:

- dispositivo;
- módulo;
- tipo de evento;
- chave de idempotência;
- assinatura;
- validade;
- deduplicação;
- estado de reconciliação.

## 4. Testes executados

Teste local reproduzível:

```bash
pytest -q tests/test_valley_consumer_innovation_round_004.py
```

Resultado obtido antes da publicação da branch:

```text
8 passed
```

Os testes cobrem:

1. 24 decisões e prioridade P0;
2. bloqueio da ideia 14;
3. liberação do pagamento após o prazo sem prova do cliente;
4. cobertura parcial de mobilidade;
5. adesão voluntária das empresas ao piloto Jobs;
6. sugestão e baixa automática da lista de compras;
7. criação da agenda a partir de prescrição verificada;
8. idempotência da fila offline.

## 5. Limites técnicos desta entrega

Esta entrega materializa uma **vertical executável**, com contratos de API, estados, validações e testes. Ela não deve ser confundida com implantação integral em produção dos 23 produtos.

Ainda dependem de implementação e homologação:

- persistência definitiva em PostgreSQL;
- autenticação e autorização por identidade real;
- migrações;
- eventos de outbox e workers;
- integração com PSP e escrow financeiro homologado;
- integração com operadores de transporte e bilhetagem;
- notificações móveis;
- prontuário e prescrição interoperável;
- interfaces Android/iOS;
- observabilidade, proteção antifraude e testes de carga;
- revisão jurídica, financeira, clínica e de proteção de dados.

## 6. Critério de comunicação comercial

Nenhuma funcionalidade deve ser anunciada como nacional, integral ou pronta para produção apenas por existir neste código. A comunicação pública exige:

- integração real;
- ambiente homologado;
- evidência reproduzível;
- abrangência geográfica documentada;
- segurança e conformidade verificadas.
