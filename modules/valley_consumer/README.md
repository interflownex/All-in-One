# APK Valley Consumidor — Rodadas 004 e 005

Aplicação FastAPI que materializa as decisões de inovação do APK Valley Consumidor como verticais executáveis e testáveis.

## Estado

- Rodada 004 preservada com seus contratos e salvaguardas;
- Rodada 005 registrada com 24 ideias aprovadas;
- todas as feature flags da Rodada 005 começam desligadas;
- escritas de teste exigem o cabeçalho `X-Innovation-Sandbox: true` enquanto a flag estiver desligada;
- a rota de flags não permite habilitar produção sem homologação externa;
- Vision permanece excluído.

## Execução local

```bash
uvicorn modules.valley_consumer.main:app --reload
```

## Rotas principais da Rodada 005

- `GET /innovation/round-005`;
- `GET /innovation/round-005/flags`;
- `GET /innovation/round-005/{idea_id}`;
- `POST /innovation/round-005/{idea_id}/execute`;
- `GET /innovation/round-005/{idea_id}/records`.

Cada uma das 24 ideias possui regra de validação específica no endpoint de execução. O contrato cobre identidade, compromissos empresariais, privacidade, recibos, ranking ético, compatibilidade, missões de entrega, apoio a Riders, triagem de serviços, embarque acessível, portfólio profissional, simulação ERP, reservas domésticas, rotas urbanas, reconciliação CRM, saída segura, documentos sanitizados, tempo de aprendizagem, compartilhamento clínico, consentimento, convivência condominial, valor entregue, memória semântica e teste de integrações.

## Testes

```bash
pytest -q tests/test_valley_consumer_innovation_round_004.py
pytest -q tests/test_valley_consumer_innovation_round_005.py
```

## Limite da entrega

A Rodada 005 foi implementada como vertical executável de contratos, estados, validações e testes. Produção ainda depende de persistência definitiva, autenticação, migrações, outbox, PSP, passkeys, operadores de transporte, Health Connect/FHIR, aplicativos móveis, observabilidade e revisões jurídica, financeira, clínica e de proteção de dados.
