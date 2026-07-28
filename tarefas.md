# Tarefas da IA Desenvolvedora

**Versão:** 1.8  
**Data e hora:** 28/07/2026 00:52:26  
**Fuso horário:** `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `codex/apk-valley-rodada-004-v2-2026-07-28`  
**Commit-base:** `21a6ba6b0fbeb4afeaa336b7b0bbec6c51a0a9ff`  
**Issue:** `#55`  
**Destino:** Codex e demais IAs desenvolvedoras autorizadas

## 1. Objetivo imediato

Evoluir a Rodada 004 do APK Valley Consumidor a partir da baseline v2.9 já integrada na `main`, preservando os 24 módulos oficiais, mantendo o Vision desativado e implementando progressivamente as 23 ideias aprovadas.

A ideia 5, **Conserte, Alugue ou Compre**, é `P0`. A ideia 14, **Cadeia de Custódia Sensorial**, permanece bloqueada e não deve ser implementada nesta rodada.

## 2. Estado implementado nesta branch

- aplicação FastAPI `modules/valley_consumer` criada;
- catálogo executável com as 24 decisões da Rodada 004;
- 23 ideias aprovadas e uma rejeitada;
- ideia 5 marcada como `P0`;
- ideia 6 redirecionada ao `Marketplace`, sem alteração funcional no `STOCK`;
- bloqueio técnico da ideia 14;
- contrato de comparação entre reparo, aluguel, empréstimo autorizado, recondicionado e compra nova;
- cadastro de sobras produtivas com bloqueio de materiais perigosos ou regulados;
- contrato de serviço por resultado com prazo máximo de validação, evidências e liberação protegida do pagamento;
- cadastro de abrangência de mobilidade por operador, estado, cidade, API e meio de pagamento;
- piloto Jobs exclusivamente voluntário para empresas;
- lista contínua de compras com sugestão por saldo/data e baixa após confirmação da transação;
- agenda de medicação derivada exclusivamente de prescrição verificada;
- orçamento de autonomia da Helena;
- fila de eventos offline com validade, assinatura, idempotência e deduplicação;
- oito testes funcionais específicos adicionados;
- documentação técnica e limites de produção registrados.

## 3. Decisões obrigatórias da Rodada 004

1. Identity — implantar Carteira de Contextos Isolados.
2. Business — implantar Atendimento Adaptado sem Diagnóstico.
3. Permissions — implantar Orçamento Pessoal de Dados.
4. Finance — implantar Cofre de Objetivo Compartilhado por Regras.
5. Marketplace — implantar Conserte, Alugue ou Compre como `P0`.
6. Sobras produtivas — implantar no `Marketplace`, nunca no `STOCK` nesta rodada.
7. Delivery — implantar Ponto Móvel de Encontro Seguro.
8. Riders — implantar Rider Mentor em Modo Sombra.
9. Services — implantar contrato por resultado com prazo máximo, prova de falha e liberação ao profissional quando o cliente não apresentar comprovação suficiente dentro do prazo.
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

## 4. Primeira ação obrigatória da próxima etapa

1. Obter o head mais recente desta branch.
2. Confirmar que a branch não ficou atrás da `main`.
3. Consultar somente workflows associados ao head atual.
4. Executar os testes específicos da Rodada 004.
5. Executar o gate de artefatos gerados da baseline v2.9.
6. Não integrar com gate vermelho, ausente, cancelado ou em processamento.

## 5. Ordem de execução

### P0 — Marketplace: Conserte, Alugue ou Compre

- criar entidades persistentes para modalidades, ofertas e disponibilidade;
- implementar cálculo de custo total;
- integrar garantia, entrega, pagamento e política de devolução;
- criar ranking explicável e proteção contra favorecimento;
- implementar telas no APK Valley;
- testar reparo, aluguel, recondicionado e compra nova ponta a ponta;
- iniciar com feature flag desligada.

### P1 — Persistência e segurança da vertical

- substituir armazenamento em memória por stores tipados;
- criar migrations PostgreSQL reversíveis;
- integrar autenticação, RBAC, ABAC, consentimento e auditoria;
- emitir eventos outbox com idempotência;
- definir retenção, anonimização e exclusão;
- adicionar telemetria, alertas e rollback.

### P1 — Services

- integrar escrow financeiro homologado;
- configurar prazo por categoria de serviço;
- definir padrões mínimos de evidência;
- implementar revisão humana e contestação;
- impedir liberação duplicada;
- notificar cliente e profissional antes e após o prazo.

### P1 — Mobility

- manter inventário por operador, município e estado;
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

Para cada ideia, exceto a 14:

- criar entidades e eventos específicos;
- definir API e UX;
- implementar persistência;
- aplicar segurança e auditoria;
- escrever testes unitários, de integração e de jornada;
- documentar critérios de aceite;
- vincular commits e pull requests à issue `#55`.

## 6. Testes mínimos

```bash
python -m pytest -q tests/test_valley_consumer_innovation_round_004.py
python scripts/check_generated_artifacts.py
python -m pytest -q --ignore=tests/e2e
```

Resultado local já obtido para a suíte específica da vertical:

```text
8 passed
```

Esse resultado comprova somente os contratos e salvaguardas testados. Não comprova a implantação integral dos 23 produtos em produção.

## 7. Gates obrigatórios

- Continuous Integration;
- Security;
- Database;
- Docker Compose Health Gate;
- OpenAPI;
- Valley DAST;
- Valley Android Security, quando o APK Android for alterado.

## 8. Critérios de aceite

Cada ideia somente pode ser marcada como concluída quando houver:

- código integrado ao módulo correto;
- feature flag e rollback;
- persistência e migration reversível;
- autenticação, autorização e consentimento;
- testes reproduzíveis;
- evidência no ambiente homologado;
- observabilidade e auditoria;
- documentação de risco e abrangência;
- integração externa real quando aplicável;
- referência ao commit e pull request;
- ausência de regressão relevante;
- atualização da issue `#55` e deste arquivo.

## 9. Proibições

- push direto na `main`;
- merge com gate vermelho, cancelado, ausente ou em processamento;
- reativar Vision;
- implantar a ideia 14 nesta rodada;
- cadastrar a ideia 6 no módulo `STOCK`;
- anunciar cobertura nacional de mobilidade sem evidência;
- incluir empresa no piloto Jobs sem adesão voluntária;
- gerar agenda de medicação sem prescrição verificada;
- executar compra automaticamente com base apenas na lista;
- liberar ou reter pagamento de serviço sem regra auditável;
- versionar segredos ou dados pessoais reais;
- sobrescrever trabalho paralelo;
- declarar produção concluída apenas pela existência de contratos de API.

## 10. Fontes de verdade

1. `AGENTS.md`;
2. `docs/governance/MANDATORY_INTEGRATION_POLICY.md`;
3. este `tarefas.md`, versão 1.8;
4. `docs/inovacao/APK_Valley_Consumidor_Rodada_004_Implementacao_2026-07-28.md`;
5. `config/module_catalog.json`;
6. issue `#55`;
7. `modules/valley_consumer/innovation_round_004.py`;
8. `tests/test_valley_consumer_innovation_round_004.py`;
9. documentação oficial dos provedores externos utilizados.

## 11. Riscos e bloqueios

- a vertical inicial ainda usa armazenamento em memória;
- escrow real depende de PSP e análise regulatória;
- mobilidade pública não possui cobertura técnica uniforme em todo o Brasil;
- pagamento por aproximação e QR Code varia por operador e equipamento;
- dados de saúde exigem proteção reforçada e validação clínica;
- IA autônoma exige rollback, recibos e limites por finalidade;
- eventos offline exigem assinatura real, armazenamento seguro e reconciliação distribuída;
- 23 ideias simultâneas não devem ser comunicadas como prontas apenas por possuírem contratos de API.

## 12. Histórico

| Versão | Data e hora | Alteração |
|---|---|---|
| 1.5 | 27/07/2026 04:29:44 | Plano inicial v2.9. |
| 1.6 | 27/07/2026 05:33:26 | Correções aplicadas e revalidação. |
| 1.7 | 27/07/2026 07:12:49 | Fase 0 implementada, diagnósticos removidos e regressão final preparada. |
| 1.8 | 28/07/2026 00:52:26 | Rodada 004 do APK Valley registrada sobre a baseline v2.9, com vertical executável, salvaguardas, testes e implantação progressiva pela issue #55. |
