# APK Valley Consumidor — Rodada 004

Aplicação FastAPI que materializa as decisões aprovadas da Rodada 004 de inovação do APK Valley Consumidor.

## Estado

- 23 ideias aprovadas para evolução;
- ideia 5 classificada como `P0`;
- ideia 6 direcionada ao `Marketplace`, sem implementação no `STOCK`;
- ideia 14 bloqueada e rejeitada nesta rodada;
- salvaguardas específicas implementadas para Services, Mobility, Jobs, lista de compras, Health, autonomia da Helena e eventos offline.

## Execução local

```bash
uvicorn modules.valley_consumer.main:app --reload
```

## Testes

```bash
pytest -q tests/test_valley_consumer_innovation_round_004.py
```

## Limite desta entrega

Esta entrega cria uma vertical executável, contratos de API, estados e regras de negócio testáveis. Persistência definitiva, autenticação, integrações reais com PSP, operadores de transporte, prontuário, notificações e aplicativos móveis dependem das etapas de produção descritas em `tarefas.md`.
