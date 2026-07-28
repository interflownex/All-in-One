# Tarefas da IA Desenvolvedora

**Versão:** 1.2  
**Data da entrega:** 28/07/2026  
**Hora da entrega:** 00:38:52  
**Fuso horário:** `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch de elaboração:** `codex/apk-valley-rodada-004-2026-07-28`  
**Commit-base:** `77fa6fab5f1c881ba6289dc288dc64e20421614a`  
**Issue de orquestração:** `#55`  
**Classificação:** `Inovação > APK Valley Consumidor > Técnico e Produto`  
**Destino:** Codex e demais IAs desenvolvedoras autorizadas

## 1. Objetivo desta versão

Registrar a aprovação da Rodada 004 do APK Valley Consumidor, preservar as decisões do aprovador e orientar a evolução da vertical FastAPI criada nesta branch até a implantação real em produção.

A existência de contratos, rotas ou testes não autoriza declarar os 23 produtos como concluídos. Cada capacidade exige persistência, integração, segurança, homologação e evidência no ambiente correto.

## 2. Decisões obrigatórias da Rodada 004

1. Identity — implantar Carteira de Contextos Isolados.
2. Business — implantar Atendimento Adaptado sem Diagnóstico.
3. Permissions — implantar Orçamento Pessoal de Dados.
4. Finance — implantar Cofre de Objetivo Compartilhado por Regras.
5. Marketplace — implantar Conserte, Alugue ou Compre como `P0`.
6. Sobras produtivas — implantar no `Marketplace`, nunca no `STOCK` nesta rodada.
7. Delivery — implantar Ponto Móvel de Encontro Seguro.
8. Riders — implantar Rider Mentor em Modo Sombra.
9. Services — implantar contrato por resultado com prazo máximo de validação, prova de falha e liberação ao profissional quando não houver comprovação suficiente do cliente dentro do prazo.
10. Mobility — implantar por abrangência comprovada, sem alegação nacional sem API, bilhetagem e pagamento validados.
11. Jobs — implantar Prévia Realista da Vaga somente para empresas voluntárias em programa opt-in.
12. ERP — implantar Modo Continuidade do Pequeno Negócio.
13. WMS — implantar Despensa Doméstica e lista contínua de compras, sugestão por saldo ou data e baixa após confirmação da compra.
14. TMS — não implantar Cadeia de Custódia Sensorial nesta rodada.
15. CRM — implantar CRM por Intenção Declarada.
16. BPM — implantar Pausa Humana Obrigatória.
17. GED/ECM — implantar Documento em Áudio Navegável e Verificável.
18. HR — implantar Mapa Transparente de Crescimento.
19. Health — implantar acompanhamento pós-consulta e agenda de medicação somente a partir de prescrição verificada.
20. Legal — implantar Jornada Guiada de Direito do Consumidor.
21. Property — implantar Manual Portátil da Casa.
22. BI — implantar Índice de Fricção do Usuário.
23. AI Core — implantar Orçamento de Autonomia da Helena.
24. API Hub — implantar Malha Offline de Continuidade.

## 3. Entrega executável existente

Arquivos principais:

- `modules/valley_consumer/main.py`;
- `modules/valley_consumer/innovation_round_004.py`;
- `modules/valley_consumer/README.md`;
- `tests/test_valley_consumer_innovation_round_004.py`;
- `docs/inovacao/APK_Valley_Consumidor_Rodada_004_Implementacao_2026-07-28.md`.

A vertical atual oferece:

- catálogo das 24 decisões;
- bloqueio técnico da ideia 14;
- registro genérico para as ideias aprovadas;
- comparação P0 do Marketplace;
- sobras produtivas no Marketplace com bloqueio de material perigoso ou regulado;
- contrato de serviço por resultado e prazo;
- cadastro de prontidão de operadores de mobilidade;
- adesão voluntária ao piloto Jobs;
- lista de compras e baixa por transação;
- agenda de medicação baseada em prescrição verificada;
- orçamento de autonomia da Helena;
- fila offline idempotente.

## 4. Fontes de verdade

Antes de editar, consultar:

1. `AGENTS.md`;
2. este `tarefas.md`;
3. issue `#55`;
4. `docs/inovacao/APK_Valley_Consumidor_Rodada_004_Implementacao_2026-07-28.md`;
5. `config/module_catalog.json`;
6. `modules/shared/domain_rules.py`;
7. `modules/shared/runtime.py`;
8. testes existentes de integração dos módulos;
9. documentação oficial dos provedores externos utilizados.

## 5. Pré-requisitos obrigatórios

1. executar `git status --short --branch`;
2. buscar referências remotas permitidas;
3. executar `python3 scripts/multi_agent_sync_guard.py preflight --integrate`;
4. adquirir lock da atividade;
5. confirmar ausência de merge ou rebase em andamento;
6. trabalhar somente em branch dedicada;
7. preservar mudanças de outros agentes;
8. não versionar segredos, tokens, prescrições reais ou dados pessoais;
9. não publicar diretamente em `main`;
10. integrar somente por pull request e Squash and Merge.

## 6. Ordem de execução

### P0 — Marketplace: Conserte, Alugue ou Compre

- criar entidades persistentes para modalidades e ofertas;
- implementar cálculo de custo total;
- integrar disponibilidade, garantia, entrega e pagamento;
- criar ranking explicável e controle contra favorecimento;
- implementar telas no APK Valley;
- testar reparo, aluguel, recondicionado e compra nova ponta a ponta.

### P1 — Persistência e segurança da vertical

- substituir dicionários em memória por stores tipados;
- criar migrações PostgreSQL;
- integrar `actor_from_headers`, RBAC, ABAC, consentimento e auditoria;
- emitir eventos outbox com idempotência;
- proteger dados sensíveis e definir retenção.

### P1 — Services

- integrar escrow financeiro homologado;
- configurar prazo por categoria de serviço;
- definir padrões mínimos de evidência;
- criar revisão humana e contestação;
- impedir liberação duplicada;
- notificar cliente e profissional antes e após o prazo.

### P1 — Mobility

- criar inventário nacional por operador e município;
- verificar GTFS, GTFS Realtime, APIs proprietárias e SLA;
- verificar bilhetagem, NFC, QR Code, integração tarifária e conciliação;
- registrar evidências e data da última homologação;
- liberar comunicação pública somente nas áreas aprovadas;
- iniciar pilotos onde houver cobertura parcial útil e juridicamente permitida.

### P1 — Jobs

- criar termo de adesão empresarial;
- impedir ativação obrigatória;
- garantir que a simulação não produza trabalho real;
- impedir avaliação escondida sem consentimento;
- registrar versão do termo, empresa e vagas participantes.

### P1 — Lista de compras e despensa

- vincular compras confirmadas do Marketplace e varejo autorizado;
- criar correspondência segura entre item comprado e item da lista;
- sugerir revisão sem executar compra automaticamente;
- respeitar orçamento, consentimento e preferências de notificação;
- permitir desfazer baixa incorreta.

### P1 — Health

- integrar prescrição eletrônica e consentimento;
- validar autoria profissional;
- gerar agenda sem alterar conteúdo clínico;
- permitir confirmação, atraso, não tomada e observação;
- definir alertas seguros e escalonamento clínico;
- aplicar LGPD e interoperabilidade FHIR quando cabível.

### P1 — Demais ideias aprovadas

Para cada ideia de 1 a 24, exceto 14:

- criar entidades e eventos específicos;
- definir API e UX;
- implementar persistência;
- aplicar segurança e auditoria;
- escrever testes unitários, integração e jornada;
- documentar critérios de aceite;
- vincular commits e PRs à issue `#55`.

## 7. Testes mínimos

Executar:

```bash
pytest -q tests/test_valley_consumer_innovation_round_004.py
python3 scripts/validate_repository.py
```

Resultado local registrado na entrega inicial:

```text
8 passed
```

Esse resultado comprova somente os contratos e salvaguardas testados, não a implantação completa em produção.

## 8. Critérios de aceite

Cada ideia somente pode ser marcada como concluída quando houver:

- código integrado ao módulo correto;
- persistência e migração;
- autenticação, autorização e consentimento;
- testes reproduzíveis;
- evidência no ambiente homologado;
- observabilidade e auditoria;
- documentação de risco e abrangência;
- integração externa real quando aplicável;
- referência ao commit e pull request;
- ausência de regressão relevante;
- atualização da issue `#55` e deste arquivo.

## 9. Riscos e bloqueios

- a vertical inicial usa armazenamento em memória;
- escrow real depende de PSP e análise regulatória;
- mobilidade pública não possui cobertura técnica uniforme em todo o Brasil;
- pagamento por aproximação e QR Code varia por operador e equipamento;
- dados de saúde exigem proteção reforçada e validação clínica;
- IA autônoma exige rollback, recibos e limites por finalidade;
- eventos offline exigem assinatura real, armazenamento seguro e reconciliação distribuída;
- 23 ideias simultâneas não devem ser comunicadas como prontas apenas por possuírem contratos de API.

## 10. Entrega obrigatória da próxima IA

A próxima IA deve entregar:

1. resumo simples para o gestor;
2. capacidade escolhida e justificativa de prioridade;
3. arquivos alterados;
4. testes e comandos executados;
5. evidências e limitações;
6. commit e pull request;
7. atualização da issue `#55`;
8. incremento da versão deste arquivo;
9. integração por Squash and Merge somente após checks aprovados.

## 11. Histórico de versões

| Versão | Data e hora | Alteração principal |
|---|---|---|
| 1.0 | 26/07/2026 13:49:32 | Criação da diretriz permanente de Estudar, Pesquisa Avançada, versionamento e entrega do arquivo `tarefas.md`. |
| 1.1 | 26/07/2026 14:01:53 | Primeiro teste completo, consolidação v2.6, issue #43 e tarefas para checks, PRs, skills, ambiente público, Telegram, APK Admin e PDV Desktop. |
| 1.2 | 28/07/2026 00:38:52 | Aprovação da Rodada 004 do APK Valley, vertical FastAPI inicial, salvaguardas, testes e issue #55 para implantação progressiva. |
