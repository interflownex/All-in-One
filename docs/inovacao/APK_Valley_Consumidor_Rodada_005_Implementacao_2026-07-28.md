# APK Valley Consumidor — Implementação da Rodada 005

**Versão:** 5.1.0  
**Data:** 28/07/2026  
**Fuso:** `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `codex/apk-valley-rodada-005-2026-07-28`  
**Commit-base:** `36ca098461d51db4c6165172fbda6244f3d3c194`  
**Issue:** `#63`  
**Classificação:** `Inovação > APK Valley Consumidor > Rodada 005`

## 1. Entrega executável

A Rodada 005 foi materializada em `modules/valley_consumer/innovation_round_005.py` e registrada no aplicativo principal sem remover a Rodada 004.

Foram incluídos:

- catálogo dos códigos `VLY-20260728-01` a `VLY-20260728-24`;
- prioridade P0, P1 ou P2 por ideia;
- uma feature flag por ideia, desligada por padrão;
- bloqueio de escrita fora do sandbox enquanto a flag estiver desligada;
- endpoint genérico de execução com regra específica para cada uma das 24 propostas;
- armazenamento lógico em memória para prova de contrato;
- consulta dos registros gerados;
- proteção contra habilitação de produção pela rota de contrato.

## 2. Rotas

- `GET /innovation/round-005`;
- `GET /innovation/round-005/flags`;
- `PUT /innovation/round-005/flags/{idea_id}`;
- `GET /innovation/round-005/{idea_id}`;
- `POST /innovation/round-005/{idea_id}/execute`;
- `GET /innovation/round-005/{idea_id}/records`.

Enquanto uma flag estiver desligada, a execução de teste exige:

```http
X-Innovation-Sandbox: true
```

## 3. Cobertura das 24 ideias

A validação específica contempla:

1. quórum de recuperação sem exposição do conteúdo da conta;
2. compromissos empresariais com evidência e validade;
3. privacidade temporária em viagem;
4. conciliação do recibo financeiro;
5. ranking ético controlado pelo usuário;
6. compatibilidade reversa;
7. missão de entrega com múltiplas etapas;
8. pontos de apoio a Riders;
9. limite de três opiniões na triagem de serviços;
10. orientação de embarque acessível;
11. portfólio profissional privado por padrão;
12. simulação ERP sem promessa de previsão;
13. reserva doméstica sem compra automática;
14. rota urbana multiobjetivo;
15. reconciliação CRM sem admissão jurídica automática;
16. saída segura com recibo;
17. cópia sanitizada sem alterar o original;
18. reserva positiva de tempo de aprendizagem;
19. janela clínica temporária sem interpretação automática;
20. consentimento modular por finalidade;
21. eventos condominiais moderados;
22. valor entregue com metodologia visível;
23. memória semântica com expiração;
24. simulação de contrato de dados exclusivamente sintética e sem chamada externa.

## 4. Testes

Teste local reproduzível:

```bash
pytest -q tests/test_valley_consumer_innovation_round_005.py
```

Resultado local obtido antes da publicação:

```text
12 passed
```

A suíte verifica o catálogo completo, todas as 24 regras em sandbox, bloqueio por feature flag, quórum, conciliação financeira, limite de opiniões, preservação documental, consentimento obrigatório, memória vencida, dados sintéticos, bloqueio de produção e preservação da Rodada 004.

## 5. Limites

Esta entrega representa uma vertical executável e não uma homologação produtiva integral dos 24 produtos. Permanecem necessários:

- PostgreSQL e migrações;
- autenticação e autorização reais;
- outbox e workers;
- PSP e conciliação homologados;
- passkeys e antifraude;
- provedores e dados de transporte;
- Health Connect e FHIR;
- notificações e interfaces móveis;
- observabilidade, testes de carga e segurança;
- revisões jurídica, financeira, clínica e de proteção de dados.

Nenhuma funcionalidade deve ser divulgada como pronta, nacional ou produtiva apenas pela existência destes contratos.
