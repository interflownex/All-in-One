# Prioridades: Health Watch + SafeZone

**Escopo:** Android + Wear OS  
**Regra:** custo zero durante desenvolvimento  
**Estado:** aprovado para execução incremental

## Escala

- **P0 — Crítico:** bloqueia segurança, privacidade, funcionamento mínimo ou validação do produto.
- **P1 — Alto:** necessário para o primeiro piloto funcional e valor principal ao usuário.
- **P2 — Médio:** amplia utilidade após estabilidade do núcleo.
- **P3 — Futuro:** depende de orçamento, parceria, homologação ou validação posterior.

## P0 — Fundação obrigatória

1. ADR da arquitetura Android/Wear OS e SafeZone.
2. Modelo de consentimento, vínculo de cuidado e revogação.
3. Proteção contra rastreamento oculto ou abusivo.
4. Vínculo seguro entre All-in-One ID, celular e smartwatch.
5. Catálogo de capacidades por dispositivo.
6. Estrutura de dados para dispositivos, observações, cercas e incidentes.
7. Contratos OpenAPI versionados.
8. Eventos de domínio com outbox e auditoria.
9. Aplicativo Android companheiro mínimo.
10. Aplicativo Wear OS mínimo.
11. Cerca circular por data, horário, recorrência e permanência.
12. Confirmação de saída com tolerância de precisão para reduzir falsos positivos.
13. Alertas de saída, bateria baixa e dispositivo offline.
14. Respostas simples no relógio.
15. Operação offline e sincronização idempotente.
16. Criptografia e política de retenção.
17. Proibição de dados sensíveis em logs comuns.
18. Testes de revogação, troca de dispositivo, perda de conexão e duplicidade.

### Critério de conclusão P0

O sistema deve vincular um usuário a um dispositivo, criar uma cerca válida, detectar uma saída confirmada, alertar a pessoa e o responsável, registrar o incidente, operar temporariamente offline e impedir acesso sem autorização válida.

## P1 — MVP demonstrável

1. Frequência cardíaca e atividade conforme capacidade real.
2. Sessões de treino.
3. Botão `Senti Agora`.
4. Histórico básico de saúde.
5. Plano de cuidado e lembretes.
6. Tela de incidentes SafeZone.
7. Responsável principal e responsável secundário.
8. Escalonamento configurável.
9. Localização temporária durante incidente.
10. Painel com precisão, horário, bateria e conectividade.
11. Pacote pré-consulta.
12. Testes em Galaxy Watch, Xiaomi Watch com Wear OS e outro fabricante.

### Critério de conclusão P1

O produto deve demonstrar acompanhamento de saúde, treino, sintoma, cerca virtual e resolução de incidente em dispositivos físicos sem depender de serviço pago.

## P2 — Expansão funcional

1. Corredor de rota.
2. Detecção de desvio persistente.
3. Regra de não chegada.
4. Círculo de cuidado com múltiplos responsáveis.
5. Modo Consulta Viva.
6. Painel profissional Health Live.
7. Resumo para prontuário mediante consentimento.
8. Pós-alta conectado.
9. Relatórios para clínicas.
10. Integrações com Services, Mobility e Documents.

## P3 — Dependências futuras

1. Apple Watch e watchOS.
2. Relógios com sistemas fechados.
3. Sensores avançados proprietários.
4. Samsung Health Sensor SDK quando exigir parceria ou homologação.
5. ECG, pressão arterial e funções médicas reguladas.
6. Publicação comercial nas lojas.
7. Operação em nuvem paga.
8. Estudos clínicos e enquadramento SaMD.

## Ordem mandatória

```text
P0.1 Privacidade e vínculo
P0.2 Modelo de dados e contratos
P0.3 Android companheiro
P0.4 Wear OS
P0.5 SafeZone circular
P0.6 Alertas e incidentes
P0.7 Offline, segurança e testes
P1 Saúde e exercícios
P1 Experiência familiar
P2 Rotas e telemedicina
P3 Ecossistemas e funções reguladas
```

## Bloqueios

Não avançar para P1 sem:

- consentimento e revogação testados;
- proteção antiabuso definida;
- vínculo de dispositivo validado;
- logs sem dados sensíveis;
- incidente SafeZone auditável;
- testes de falsos positivos e precisão.

Não avançar para P2 sem:

- piloto P1 estável;
- política de retenção aprovada;
- DPIA/LGPD;
- testes físicos documentados;
- revisão de segurança.
