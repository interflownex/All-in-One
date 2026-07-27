# Pendências do Desenvolvedor

**Versão:** 2.9  
**Data e hora da atualização:** 27/07/2026 05:33:26  
**Fuso horário:** `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch de execução:** `fix/cicd-governanca-v2-8-2026-07-27`  
**Pull Request central:** `#50`  
**Issue operacional:** `#49`  
**Issue de orquestração funcional:** `#51`  
**Versão anterior consolidada:** 2.8  
**Classificação:** `Pendências > Técnico > Equipe técnica`  
**Públicos impactados:** Pessoa Física, Pessoa Jurídica, equipe técnica, gestão e investidores

## 1. Objetivo desta atualização

Registrar o resultado real da execução v2.9, preservar o PR `#50` como rascunho enquanto os gates são revalidados e impedir o início de Marketplace, Stock ou Delivery antes da conclusão segura da Fase 0.

## 2. Regras permanentes

1. Nenhuma alteração direta na `main`.
2. Nenhum merge com gate obrigatório vermelho ou em processamento.
3. Integração somente por **Squash and Merge**.
4. Nenhuma credencial, token, senha, chave ou certificado no Git.
5. O módulo Vision permanece excluído.
6. Nenhuma exclusão em massa sem inventário e justificativa.
7. Nenhuma tarefa é concluída apenas pela existência de código ou documento.
8. São obrigatórios teste reproduzível, evidência do ambiente correto, commit e Pull Request.
9. O arquivo `tarefas.md` deve ser atualizado em toda entrega técnica.
10. Marketplace somente começa após a conclusão segura da Fase 0 da issue `#51`.

## 3. Avanços executados e confirmados

### 3.1 Gate de artefatos e CI

- os quatro comandos do gate foram executados separadamente;
- foram identificados e criados `apps/valley_business/STATUS.md` e `apps/valley_rider/STATUS.md`;
- a baseline de 24 módulos foi preservada;
- foi criado `scripts/validate_repository_compat.py`, que mantém erros reais bloqueantes e compatibiliza apenas quatro regras legadas comprovadas;
- `scripts/check_generated_artifacts.py` passou a usar o adaptador compatível;
- o gate `Check generated artifacts` passou;
- o contrato Android e os testes de assinatura do CI principal passaram;
- a suíte unitária foi liberada e encontrou um falso negativo específico do checkout de Pull Request;
- `scripts/check_git_sync.py` foi corrigido para usar `HEAD^1` somente quando o GitHub confirma um merge de Pull Request para a mesma branch-base.

### 3.2 Segurança Python

- `pip-audit` e os scans Trivy das imagens API Hub, Identity e Jobs passaram;
- os achados Bandit foram reduzidos de 9 para 4;
- cinco chamadas externas foram endurecidas com validação central de HTTPS, porta, credenciais embutidas e allowlist de host;
- foram criados `scripts/secure_http.py` e `tests/test_secure_http.py`;
- os quatro achados restantes foram delimitados a três SQLs com allowlists literais e um parser de relatórios JUnit locais;
- foi criado `scripts/validate_bandit_scoped_exceptions.py`;
- o workflow mantém todas as demais regras Bandit ativas e excepciona somente B608/B314 nos arquivos revisados.

### 3.3 Android

- as tarefas Gradle genéricas e ambíguas foram substituídas por `productionDebug`;
- o pacote `productionDebug` foi alinhado ao cliente Firebase autorizado `com.example.valley`;
- os workflows `security.yml` e `valley-android-security.yml` foram alinhados ao mesmo flavor;
- o bloqueio de chave debug em release e a validação de manifesto seguro permanecem ativos;
- nova rodada de testes, lint, build e CodeQL foi disparada.

### 3.4 PostgreSQL

- migrations, triggers imutáveis e constantes contratuais passaram;
- o diagnóstico confirmou que a falha vinha da reaplicação de DDL de execução única sobre banco já migrado;
- `validate_postgres_real_dsn.py` passou a verificar presença, ordem e SHA-256 das migrations em vez de recriar tabelas;
- o workflow Database removeu `--repeat-migrations` da validação por DSN;
- nova rodada de contrato, stores e matriz foi disparada.

### 3.5 Gates já aprovados anteriormente

- OpenAPI;
- Valley DAST;
- Docker Compose Health Gate;
- auditoria das dependências Python;
- Trivy API Hub, Identity e Jobs;
- auditorias JavaScript;
- contrato Android.

## 4. Estado atual dos bloqueadores

### 4.1 CI principal

**Situação:** gate de artefatos resolvido. A suíte unitária foi liberada e o primeiro falso negativo Git foi corrigido. A nova execução está em processamento.

**Critério restante:** suíte unitária completa aprovada no head atual.

### 4.2 Segurança Python

**Situação:** chamadas de rede corrigidas e quatro achados delimitados por arquivo e regra, com validador próprio. A nova execução do Bandit e de `tests/test_security_gates.py` está em processamento.

**Critério restante:** workflow Security aprovado sem supressão genérica.

### 4.3 Android completo

**Situação:** package ID e tarefas Gradle foram alinhados ao `productionDebug`. A nova execução de testes, lint, assemble e CodeQL está em processamento.

**Critério restante:** os dois workflows Android aprovados no head atual.

### 4.4 PostgreSQL por DSN

**Situação:** semântica de repetição corrigida e workflow alinhado ao banco já migrado. A nova execução de contrato, stores e matriz está em processamento.

**Critério restante:** workflow Database aprovado do início ao fim.

## 5. Pendências altas após a Fase 0

1. Desabilitar administrativamente `merge commit` e `rebase merge`.
2. Atualizar, reconstruir ou encerrar PRs `#36`, `#37`, `#38`, `#40`, `#46` e `#48`.
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
| Estabilização PR #50 | Restaurar linha de integração | Revalidar correções no head atual | 5 | 88% | 1h30 | 12 | 10 | 2 |
| Artefatos gerados | Alinhar scaffold e validadores | Gate aprovado | 5 | 100% | concluído | 6 | 6 | 0 |
| Suíte unitária | Executar testes completos | Revalidar fallback Git de PR | 4 | 90% | 45min | 5 | 4 | 1 |
| Bandit | Tratar achados médios | Revalidar escopo por arquivo/regra | 5 | 85% | 45min | 7 | 6 | 1 |
| Android | Testes, lint, assemble e CodeQL | Revalidar `productionDebug` | 5 | 85% | 1h | 7 | 6 | 1 |
| PostgreSQL | Contrato real, stores e matriz | Revalidar sem reaplicar DDL | 5 | 88% | 1h | 9 | 8 | 1 |
| Compose | Subir serviços e validar health | Aprovado no ciclo anterior | 4 | 100% | concluído | 5 | 5 | 0 |
| OpenAPI | Validar contratos | Aprovado | 3 | 100% | concluído | 4 | 4 | 0 |
| Valley DAST | Validar superfície web | Aprovado | 4 | 100% | concluído | 4 | 4 | 0 |
| Governança Git | Exigir somente squash | Bloqueio administrativo | 4 | 55% | 1h | 5 | 3 | 2 |
| Marketplace | Primeira frente funcional | Bloqueado pela Fase 0 | 5 | 0% | próximo ciclo | 9 | 0 | 9 |

## 7. Contagem consolidada

| Classificação | Quantidade |
|---|---:|
| Críticas em revalidação | 4 |
| Altas após Fase 0 | 9 |
| Médias | 7 |
| Secundárias | 3 |
| Concluídas com evidência nesta execução | 10 |
| Bloqueadas por dependência externa ou administrativa | 4 |

## 8. Ordem mandatória restante

1. Concluir a rodada atual de CI, Security, Android e Database.
2. Corrigir somente a primeira falha concreta que permanecer.
3. Reexecutar todos os gates afetados.
4. Atualizar issues `#49` e `#51`, PR `#50`, relatório e `tarefas.md`.
5. Manter o PR em rascunho enquanto qualquer gate obrigatório falhar ou estiver em processamento.
6. Somente depois iniciar a Fase Marketplace.

## 9. Critérios de conclusão da Fase 0

- `check_generated_artifacts.py` aprovado;
- suíte unitária completa aprovada;
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
| 2.9 | 27/07/2026 05:33:26 | Execução técnica dos quatro bloqueadores, correções aplicadas e revalidação dos gates. |
