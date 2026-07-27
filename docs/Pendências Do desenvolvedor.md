# Pendências do Desenvolvedor

**Versão:** 2.9  
**Data e hora da verificação:** 27/07/2026 04:29:44  
**Fuso horário:** `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch de execução:** `fix/cicd-governanca-v2-8-2026-07-27`  
**Commit-base:** `77fa6fab5f1c881ba6289dc288dc64e20421614a`  
**Commit verificado:** `fb49ba0c334054817fbbb129dfbf38f2cf741761`  
**Pull Request central:** `#50`  
**Issue operacional:** `#49`  
**Issue de orquestração funcional:** `#51`  
**Versão anterior consolidada:** 2.8  
**Classificação:** `Pendências > Técnico > Equipe técnica`  
**Públicos impactados:** Pessoa Física, Pessoa Jurídica, equipe técnica, gestão e investidores

## 1. Objetivo desta versão

Consolidar o estado real após o ciclo v2.8, atualizar a fonte oficial de pendências e executar a continuação da estabilização sem iniciar Marketplace, Stock ou Delivery enquanto a linha de integração permanecer vermelha.

## 2. Regras permanentes

1. Nenhuma alteração direta na `main`.
2. Nenhum merge com gate obrigatório vermelho.
3. Integração somente por **Squash and Merge**.
4. Nenhuma credencial, token, senha, chave ou certificado no Git.
5. O módulo Vision permanece excluído.
6. Nenhuma exclusão em massa sem inventário e justificativa.
7. Nenhuma tarefa é concluída apenas pela existência de código ou documento.
8. São obrigatórios teste reproduzível, evidência do ambiente correto, commit e Pull Request.
9. O arquivo `tarefas.md` deve ser atualizado em toda entrega técnica.
10. Marketplace somente começa após a conclusão segura da Fase 0 da issue `#51`.

## 3. Avanços confirmados no ciclo v2.8

### 3.1 Governança

- PR `#50` aberta como rascunho e tecnicamente mesclável;
- PR `#34` encerrada sem merge por substituição pela `#37`;
- PRs `#36` e `#38` convertidas para rascunho;
- matriz de destino das PRs registrada na issue `#49`;
- nenhum merge ou auto-merge executado;
- métodos `merge commit` e `rebase merge` continuam habilitados administrativamente.

### 3.2 Artefatos, contratos e dependências

- artefatos canônicos foram regenerados;
- `pypdf` foi atualizado para `6.14.2`;
- auditoria das dependências declaradas passou;
- imagens API Hub, Identity e Jobs passaram no Trivy;
- auditorias JavaScript passaram;
- OpenAPI passou;
- Valley DAST passou;
- Docker Compose Health Gate passou no head verificado.

### 3.3 Banco, Android e Vision

- etapa operacional do Vision foi removida do workflow Database;
- migração `029_unified_immutable_audit.sql` foi corrigida para a coluna reservada `"authorization"`;
- writer PostgreSQL de auditoria foi alinhado;
- contrato Android passou;
- permissão de execução do `gradlew` foi corrigida no workflow.

## 4. Bloqueadores atuais

### 4.1 Crítico: Continuous Integration

O job ainda falha em `Check generated artifacts`, bloqueando o contrato Android no CI principal, os testes de assinatura e a suíte unitária completa.

**Próxima ação:** executar isoladamente:

```bash
python scripts/scaffold_modules.py --check
python scripts/generate_domain_event_fixtures.py --check
python scripts/validate_openapi.py
python scripts/validate_repository.py
```

Corrigir o primeiro comando com código diferente de zero.

### 4.2 Crítico: Bandit

A auditoria Python de dependências passou, mas o Bandit falha antes de `tests/test_security_gates.py`.

O relatório registra 114 achados totais, com grupos relevantes em SQL dinâmico, abertura de URL sem restrição de esquema e parsing XML inseguro.

**Regra:** nenhuma supressão genérica. Cada achado médio ou alto deve ser corrigido ou justificado individualmente, com teste.

### 4.3 Crítico: Android completo

O contrato Android passou, mas o job `valley-android-security` falha em `Validar, testar, analisar e empacotar Android`.

**Próxima ação:** isolar se a falha está em testes, lint, assemble ou CodeQL.

### 4.4 Crítico: PostgreSQL por DSN

As migrations foram aplicadas e os triggers imutáveis passaram. A falha ocorre em `Validate PostgreSQL real contract by DSN`. Todos os stores posteriores foram ignorados.

**Próxima ação:** capturar a mensagem exata do validador, corrigir o primeiro contrato divergente e repetir a matriz.

## 5. Pendências altas após os quatro bloqueadores

1. Desabilitar administrativamente `merge commit` e `rebase merge`.
2. Atualizar ou reconstruir PRs `#36`, `#37`, `#38`, `#40`, `#46` e `#48`.
3. Homologar APK Admin com build, instalação, hash e smoke test.
4. Homologar PDV Desktop com instalador, hashes e operação offline.
5. Rebasear o executor Telegram do PR `#46` sobre a base estabilizada.
6. Homologar domínio público, identidade, API Hub e `/health`.
7. Sincronizar Stitch com credencial legítima.
8. Incorporar o PNG original autorizado da Valley Riders.
9. Iniciar Marketplace somente após os gates obrigatórios da PR `#50`.

## 6. Quadro obrigatório de acompanhamento

| Nome da atividade | Descrição | Passo sendo executado | Dificuldade [1 a 5] | % concluído | Tempo previsto | Etapas [Total] | Concluídas [X] | Pendentes [Y] |
|---|---|---|---:|---:|---|---:|---:|---:|
| Estabilização PR #50 | Restaurar linha de integração | Isolar quatro bloqueadores | 5 | 72% | 4h | 11 | 8 | 3 |
| Artefatos gerados | Alinhar scaffold e validadores | Executar comandos separados | 5 | 70% | 1h | 6 | 4 | 2 |
| Bandit | Tratar achados médios e altos | Priorizar grupos reais | 5 | 35% | 2h | 6 | 2 | 4 |
| Android | Validar testes, lint, assemble e CodeQL | Isolar subetapa falha | 5 | 70% | 1h30 | 6 | 4 | 2 |
| PostgreSQL | Validar contrato real por DSN | Capturar divergência exata | 5 | 75% | 1h30 | 8 | 6 | 2 |
| Compose | Subir serviços e validar health | Gate aprovado no head atual | 4 | 100% | concluído | 5 | 5 | 0 |
| OpenAPI | Validar contratos | Gate aprovado | 3 | 100% | concluído | 4 | 4 | 0 |
| Valley DAST | Validar superfície web | Gate aprovado | 4 | 100% | concluído | 4 | 4 | 0 |
| Segurança de imagens | Trivy API Hub, Identity e Jobs | Gates aprovados | 4 | 100% | concluído | 6 | 6 | 0 |
| Governança Git | Exigir somente squash | Bloqueio administrativo | 4 | 55% | 1h | 5 | 3 | 2 |
| Marketplace | Primeira frente funcional | Bloqueado pela Fase 0 | 5 | 0% | próximo ciclo | 9 | 0 | 9 |
| Stock | Segunda frente funcional | Aguardar Marketplace | 5 | 0% | futuro | 9 | 0 | 9 |
| Delivery | Terceira frente funcional | Aguardar Stock | 5 | 0% | futuro | 9 | 0 | 9 |

## 7. Contagem consolidada

| Classificação | Quantidade |
|---|---:|
| Críticas | 4 |
| Altas | 9 |
| Médias | 7 |
| Secundárias | 3 |
| Concluídas com evidência neste ciclo | 6 |
| Bloqueadas por dependência externa ou administrativa | 4 |

## 8. Ordem mandatória

1. Isolar `Check generated artifacts`.
2. Validar e corrigir Bandit.
3. Isolar o erro Android.
4. Isolar o erro PostgreSQL por DSN.
5. Reexecutar todos os gates.
6. Atualizar issue `#49`, issue `#51`, PR `#50`, relatórios e `tarefas.md`.
7. Manter o PR em rascunho enquanto qualquer gate obrigatório falhar.
8. Somente depois iniciar a Fase Marketplace.

## 9. Critérios de conclusão da Fase 0

- `check_generated_artifacts.py` aprovado;
- suíte unitária executada e aprovada;
- Bandit e `tests/test_security_gates.py` aprovados;
- Android aprovado em contrato, testes, lint, assemble e CodeQL;
- Database aprovado em migrations, contrato por DSN, stores e matriz;
- Compose, OpenAPI e DAST permanecem verdes;
- ausência de Vision operacional;
- ausência de segredos;
- documentação e evidências atualizadas;
- configuração exclusiva de Squash and Merge comprovada ou registrada como bloqueio administrativo;
- integração final por Squash and Merge.

## 10. Histórico

| Versão | Data e hora | Alteração principal |
|---|---|---|
| 2.6 | 26/07/2026 14:01:53 | Primeiro teste completo de orquestração. |
| 2.7 | 26/07/2026 23:06:33 | Consolidação documental e início do executor Telegram. |
| 2.8 | 27/07/2026 02:17:29 | Estabilização parcial da PR #50 e evidências de gates. |
| 2.9 | 27/07/2026 04:29:44 | Estado real atualizado, quatro bloqueadores isolados e continuidade executiva da Fase 0. |
