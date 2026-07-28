# Plano de Ação Estruturado para o Codex

**Versão:** 3.0  
**Data e hora:** 27/07/2026 07:12:49  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `fix/cicd-governanca-v2-8-2026-07-27`  
**PR:** `#50`  
**Issues:** `#49` e `#51`

## 1. Missão imediata

Concluir a regressão do head final de limpeza/documentação. Não alterar código, iniciar Marketplace ou remover novos arquivos enquanto os sete gates obrigatórios não terminarem.

## 2. Ordem obrigatória

1. Obter o head atual do PR `#50`.
2. Consultar somente workflows ligados exatamente ao head atual.
3. Confirmar:
   - Continuous Integration;
   - Security;
   - Database;
   - Docker Compose Health Gate;
   - OpenAPI;
   - Valley DAST;
   - Valley Android Security.
4. Ignorar como gate qualquer diagnóstico removido ou resultado de commit anterior.
5. Caso exista falha, corrigir somente a primeira causa reproduzível.
6. Não alterar nenhum arquivo depois que o head final estiver totalmente verde.

## 3. Critérios técnicos

### CI

- artefatos preservam a árvore;
- contrato Android v2.9 aprovado;
- auditoria e assinatura do APK aprovadas;
- suíte unitária completa aprovada.

### Security

- `pip-audit -r requirements-dev.txt` aprovado;
- Bandit aprovado com exceções delimitadas;
- JavaScript e Trivy aprovados;
- Android recompilado com `clean`, `--no-build-cache` e `--rerun-tasks`;
- CodeQL aprovado;
- SARIF publicado como artefato do Pull Request.

### Database

- migrations e triggers aprovados;
- contrato por DSN aprovado sem reaplicar DDL;
- stores e matriz aprovados;
- Jobs/CTPS aprovado;
- outbox/RabbitMQ aprovado.

### Plataforma

- Compose Health aprovado;
- OpenAPI aprovado;
- Valley DAST aprovado;
- Android independente aprovado.

## 4. Revisão após os gates

Quando todos os gates estiverem verdes no mesmo head:

1. listar threads e reviews do PR;
2. responder e resolver somente threads efetivamente atendidas;
3. revisar os arquivos alterados por domínio;
4. confirmar ausência dos workflows temporários;
5. confirmar ausência de secrets;
6. verificar que Vision permanece ausente;
7. atualizar issues e descrição do PR por comentário, sem criar novo commit;
8. marcar o PR pronto para revisão somente se não houver bloqueio pendente.

## 5. Integração

A integração só é permitida quando:

- todos os checks estiverem verdes;
- o head esperado não tiver mudado;
- não houver revisão solicitando alterações;
- o PR estiver pronto para revisão;
- a política permitir a ação;
- o método for `squash`.

Usar `expected_head_sha` para impedir merge sobre head alterado.

## 6. Próxima fase

Depois da integração da Fase 0:

1. Marketplace;
2. Stock;
3. Delivery.

Cada frente deve nascer com feature flag desligada e incluir contrato, migration reversível, autorização, auditoria, testes, telemetria, alerta e rollback.

## 7. Bloqueios que não devem ser mascarados

- configuração administrativa de métodos de merge;
- credenciais externas ausentes;
- ativo original Valley Riders ausente;
- Stitch sem sincronização comprovada;
- homologação de APK Admin e PDV Desktop;
- revisão técnica do escopo amplo do PR.
