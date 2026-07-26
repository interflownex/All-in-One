# Implementação das Inovações nos 24 Módulos

**Projeto:** All in One + Valley  
**Data da decisão:** 26/07/2026  
**Público:** equipe técnica, arquitetura, produto, segurança e responsáveis por homologação  
**Natureza:** técnica e conceitual  
**Situação:** implementação iniciada em base controlada  
**Branch:** `feature/innovation-wave-001-24-modules`

## 1. Decisão registrada

Foram aprovadas para implementação as propostas numeradas de 1 a 22, 24 e 25. A numeração 23 não integra a entrega porque correspondia ao Vision, módulo desativado e proibido nesta onda.

A aprovação não significa ativação automática em produção. Cada capacidade deve passar por contrato de dados, segurança, testes, observabilidade, homologação e aprovação humana antes de sua feature flag ser habilitada.

## 2. Entrega técnica já criada

1. catálogo versionado em `config/innovation_wave_001.json`;
2. runtime comum em `modules/shared/innovation_runtime.py`;
3. feature flag individual para cada iniciativa;
4. validação cruzada com `config/module_catalog.json`;
5. bloqueio explícito do módulo Vision;
6. gate executável em `scripts/validate_innovation_wave.py`;
7. testes em `tests/test_innovation_wave.py`.

## 3. Matriz de implementação

| ID | Módulo | Capacidade aprovada | Prioridade | Estado atual |
|---|---|---|---|---|
| INNOV-001 | Identity | Passaporte de Confiança Seletiva | P0 | Base registrada |
| INNOV-002 | Business | Gêmeo Operacional do CNPJ | P0 | Base registrada |
| INNOV-003 | Permissions | Alçada Dinâmica por Risco | P0 | Base registrada |
| INNOV-004 | Finance | Tesouraria Inteligente Multiobjetivo | P0 | Base registrada |
| INNOV-005 | API Hub | Bolsa de Capacidades Digitais | P0 | Base registrada |
| INNOV-006 | Marketplace | Compra por Missão | P0 | Base registrada |
| INNOV-007 | STOCK | Rede de Estoque Compartilhado | P0 | Base registrada |
| INNOV-008 | One Services | Contrato Vivo por Evidências | P0 | Base registrada |
| INNOV-009 | CRM | Memória de Relacionamento Consentida | P0 | Base registrada |
| INNOV-010 | GED/ECM | Documento Vivo | P0 | Base registrada |
| INNOV-011 | Jobs | Grafo de Competências Comprováveis | P0 | Base registrada |
| INNOV-012 | Riders | Carteira Portátil de Reputação | P1 | Base registrada |
| INNOV-013 | RH/HCM/ATS/LMS | Mercado Interno de Talentos | P1 | Base registrada |
| INNOV-014 | BPM | Processos que Aprendem com Exceções | P0 | Base registrada |
| INNOV-015 | AI Core | Conselho de Agentes Auditáveis | P0 | Base registrada |
| INNOV-016 | Delivery | Entrega Composta | P1 | Base registrada |
| INNOV-017 | Mobility | Jornada Garantida | P1 | Base registrada |
| INNOV-018 | WMS | Armazém Auto-organizável | P1 | Base registrada |
| INNOV-019 | TMS | Corredor Digital de Frete | P1 | Base registrada |
| INNOV-020 | ERP | Fechamento Contínuo por Exceção | P0 | Base registrada |
| INNOV-021 | BI | Livro de Decisões | P0 | Base registrada |
| INNOV-022 | Health | Plano de Cuidado Executável | P2 | Base registrada |
| INNOV-024 | Legal | Sistema Operacional de Obrigações | P1 | Base registrada |
| INNOV-025 | Property | Gêmeo Operacional do Imóvel | P2 | Base registrada |

## 4. Ondas de desenvolvimento

### Onda A: fundação transversal

Implementar primeiro Identity, Permissions, API Hub, AI Core, BI e Document. Esses componentes criam identidade verificável, consentimento, alçadas, interoperabilidade, auditoria, documentos vivos e governança de IA para as demais capacidades.

### Onda B: receita e operação empresarial

Implementar Finance, ERP, Business, Marketplace, STOCK, Services, CRM, Jobs e BPM. Essa onda concentra venda, contratação, estoque, automação, relacionamento e fechamento financeiro.

### Onda C: logística e força de trabalho

Implementar Riders, HR, Delivery, Mobility, WMS e TMS depois que identidade, permissões, pagamentos e eventos estiverem estáveis.

### Onda D: verticais reguladas

Implementar Health, Legal e Property com revisão jurídica, proteção reforçada de dados, responsabilidade profissional e homologações próprias.

## 5. Critério mínimo de conclusão por iniciativa

Uma iniciativa somente poderá mudar de `foundation_registered` para `implemented` quando possuir:

1. contrato de API e eventos versionado;
2. modelo de dados e migração reversível;
3. regras de autorização, consentimento e auditoria;
4. testes unitários, integração e jornada principal;
5. telemetria, alertas e tratamento de falha;
6. documentação de operação e rollback;
7. validação de segurança e privacidade;
8. feature flag testada em ambiente controlado;
9. homologação externa quando houver PSP, saúde, jurídico, fiscal ou transporte regulado.

## 6. Regras de segurança

- Todas as feature flags permanecem desligadas por padrão.
- Operações financeiras, divulgação de identidade, decisões médicas e decisões jurídicas exigem aprovação humana e responsabilidade identificada.
- Agentes de IA podem recomendar e preparar ações, mas não podem contornar permissões ou homologações.
- O Vision permanece desativado e não pode reaparecer no catálogo oficial, no runtime ou nas novas integrações.
- Nenhuma credencial, chave, custo interno ou margem privada deve ser versionada.

## 7. Verificação obrigatória

Executar antes de aceitar alterações relacionadas a esta onda:

```bash
python3 scripts/validate_innovation_wave.py
pytest -q tests/test_innovation_wave.py
python3 scripts/validate_repository.py
```

## 8. Pendências imediatas

- integrar o gate ao workflow de CI;
- remover referências residuais não históricas do Vision, especialmente no API Hub e scripts auxiliares;
- criar contratos de domínio e eventos para as iniciativas P0;
- definir migrations e stores por módulo;
- criar telas Stitch e jornadas de frontend somente após contrato funcional aprovado;
- gerar métricas de custo, prazo, risco e dependências por onda;
- executar testes completos na branch antes de qualquer merge.

## 9. Estado oficial desta entrega

A ordem de implementação está registrada no projeto, protegida por catálogo, runtime, feature flags e testes. As 24 capacidades ainda não estão integralmente prontas para produção. O incremento atual é a fundação técnica segura que permite desenvolvê-las em paralelo sem perder a fonte de verdade, reativar módulo excluído ou liberar comportamento incompleto.
