# Relatório de Varredura e Status

**Versão:** 2.5  
**Data:** 26/07/2026  
**Repositório:** `interflownex/All-in-One`  
**Branch verificada:** branch de trabalho atual  
**Commit de referência:** `cbbe7bd61bdf13604f5d71167dc5b54f7435cffa`  
**Issue de orquestração:** `#28`  
**Destino:** Codex e equipe técnica

## Resultado geral

Desde a versão 2.4, foi executada a remoção completa do módulo Vision: 72 arquivos alterados, módulo retirado do catálogo, do back-end, dos aplicativos web, da infraestrutura Kubernetes, dos testes e dos contratos. O STOCK foi reposicionado para a primeira etapa. O site Valley teve título e favicon corrigidos.

O catálogo `config/module_catalog.json` está consolidado em 24 módulos. A remoção do Vision está concluída em princípio, mas o relatório de remoção identificou aproximadamente 40 arquivos com referências residuais que ainda precisam ser eliminadas.

`MODULE_NAMES` em `modules/business/module_settings.py` possui 21 entradas. Os módulos `legal`, `property` e `ai_core` constam no catálogo, mas não na configuração Business.

As pendências de implantação Render, PR `#27`, GitHub Actions sem checks, automação Telegram, auditor v7, APK e PDV permanecem abertas e sem alteração de estado desde v2.4.

## Evidências confirmadas

- `config/module_catalog.json` registra exatamente 24 módulos (vision ausente, legal/property/ai_core presentes).
- `modules/business/module_settings.py` `MODULE_NAMES` possui 21 entradas (faltam: legal, property, ai_core).
- `database/migrations/030_remove_vision_module.sql` criado e versionado.
- Relatório de remoção publicado em `docs/relatorios/remocao-vision/RELATORIO_REMOCAO_VISION_STOCK_2026-07-25.md`.
- `apps/valley/index.html` com título e favicon atualizados.
- `STATUS.md` reflete 24 módulos e 171 telas.
- `render.yaml` aponta para `main`, Python 3.12, Uvicorn e `/health`.
- `main.py` importa o aplicativo de `modules.api_hub.main`.
- O commit atual não apresenta status checks ou workflow associado.
- PR `#27` continua aberto com estado anterior ao commit atual.
- Issues abertas: `#24` (Promoção do Dia) e `#28` (Orquestração Codex).

## Referências residuais ao Vision identificadas

O relatório de remoção listou aproximadamente 40 arquivos com menções que ainda precisam ser corrigidas. Exemplos de maior impacto técnico imediato:

- `modules/api_hub/main.py`
- `modules/identity/main.py`
- `modules/shared/valley_catalog.py`
- `apps/valley/src/lib/valleyPlatform.ts`
- `apps/all-in-one/src/components/Navigation.tsx`
- `apps/all-in-one/src/components/ModuleDashboard.tsx`
- `apps/all-in-one/src/components/SmartCRUD.tsx`
- `apps/all-in-one-business/src/components/SmartCRUD.tsx`
- `tests/test_retention_jobs.py`
- `tests/test_compliance_matrix.py`
- `.github/workflows/database.yml`

## Quadro consolidado

| Nome da atividade | Descrição | Passo sendo executado | Dificuldade [1 a 5] | % concluído | Tempo previsto | Etapas [Total] | Concluídas [X] | Pendentes [Y] |
|---|---|---|---:|---:|---|---:|---:|---:|
| Limpeza residual Vision | Remover referências remanescentes | Editar ~40 arquivos identificados | 3 | 0% | 1h | 3 | 0 | 3 |
| Catálogo de módulos | Sincronizar MODULE_NAMES | Incluir legal, property, ai_core | 4 | 65% | 1h | 5 | 3 | 2 |
| Publicação externa | Homologar domínio e ambiente | Validar Render e registrar URL | 5 | 50% | 2h | 6 | 3 | 3 |
| API Hub público | Publicar backend e conectar front-end | Executar deploy e `/health` | 5 | 60% | 2h | 7 | 4 | 3 |
| Bootstrap Render | Validar Blueprint, build e start | Executar implantação e arquivar logs | 4 | 70% | 1h30 | 6 | 4 | 2 |
| PR Render #27 | Evitar regressão e duplicidade | Comparar com a `main` atual | 3 | 20% | 30min | 4 | 1 | 3 |
| GitHub Actions | Tornar checks obrigatórios | Executar workflows no commit atual | 5 | 25% | 2h | 5 | 1 | 4 |
| Governança Git | Exigir branch, PR e squash | Impor configurações administrativas | 4 | 40% | 1h | 5 | 2 | 3 |
| Backlog oficial | Converter pendências em issues | Expandir a partir de `#24` e `#28` | 3 | 20% | 1h30 | 6 | 2 | 4 |
| Auditoria das rotas | Validar 325 rotas | Aguardar API Hub homologado | 5 | 35% | 2h30 | 6 | 2 | 4 |
| Automação Telegram | Implementar eventos e relatórios | Criar executor e testes | 4 | 35% | 2h | 6 | 2 | 4 |
| Auditoria v7 | Restaurar varredura reproduzível | Recriar script e gate | 4 | 30% | 1h30 | 5 | 1 | 4 |
| Promoção do Dia | Implementar modal comercial | Executar issue `#24` no Stitch | 4 | 5% | 3h | 7 | 0 | 7 |
| Valley Riders | Incorporar ativo oficial | Obter e versionar PNG original | 3 | 35% | 45min | 4 | 1 | 3 |
| Núcleo do PDV | Consolidar venda presencial | Definir domínio e jornada mínima | 5 | 15% | 4h | 8 | 1 | 7 |
| Venda offline | Sincronizar sem duplicidade | Projetar fila e reconciliação | 5 | 5% | 4h | 7 | 0 | 7 |
| Assinatura Android | Proteger assinatura de produção | Definir cofre e recuperação | 5 | 45% | 1h30 | 4 | 2 | 2 |
| Login Google | Homologar autenticação real | Executar com conta de teste | 4 | 55% | 1h30 | 5 | 3 | 2 |

## Contagem

| Classificação | Quantidade |
|---|---:|
| Críticas | 5 |
| Altas | 18 |
| Médias | 7 |
| Secundárias | 2 |
| Resolvidas em princípio, aguardando evidência final | 2 |

## Riscos imediatos

1. declarar o deploy Render concluído apenas pela existência do Blueprint;
2. integrar o PR `#27` sobre arquivos mais recentes da `main`;
3. manter referências residuais ao Vision em módulos críticos (`api_hub`, `identity`);
4. continuar sem checks associados aos commits mais recentes;
5. deixar pendências importantes somente em documentos, sem issues rastreáveis.

## Diretriz ao Codex

O Codex deve iniciar pelo plano v2.5, trabalhar em branch própria, atualizar a issue `#28`, registrar evidências e não declarar conclusão sem validação reproduzível.
