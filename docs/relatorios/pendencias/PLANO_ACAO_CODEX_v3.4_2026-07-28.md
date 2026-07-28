# Plano de Ação Codex

**Versão:** 3.4  
**Data:** 28/07/2026  
**Fuso:** `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `codex/marketplace-fase1-descoberta-2026-07-28`  
**Issue mestra:** `#51`  
**Classificação:** `Pendências > Técnico > Equipe técnica`

## Objetivo

Concluir a primeira vertical funcional do Marketplace e integrá-la com segurança, sem iniciar nova evolução enquanto existirem workflows, merges, PRs, commits ou issues executáveis pendentes sem tratamento.

## Ordem obrigatória de execução

### Bloco 1 — fechamento da rodada atual

1. confirmar o diff da branch contra `main`;
2. validar ausência de segredos e alterações sensíveis inesperadas;
3. abrir PR em rascunho vinculada à issue #51;
4. executar Continuous Integration, Security, Database, Docker Compose Health Gate e OpenAPI aplicáveis;
5. analisar logs de qualquer job falho;
6. corrigir a causa na mesma branch;
7. repetir os gates no novo SHA;
8. verificar mergeabilidade, threads, revisões e mudança de head;
9. integrar somente por Squash and Merge;
10. atualizar a issue #51 com commit final e evidências.

### Bloco 2 — continuação do Marketplace

1. mapear o contrato atual do Stock para reserva de itens;
2. criar fluxo de checkout idempotente;
3. bloquear checkout com item indisponível ou preço divergente;
4. integrar Wallet e Orders sem lançar valor fora do ledger;
5. publicar eventos de reserva, pedido criado, pagamento e liberação;
6. implementar telemetria da promoção e do feed;
7. conectar a interface da issue #24 ao endpoint `/valley/promotions/today`;
8. executar testes de contrato e ponta a ponta.

### Bloco 3 — Stock

1. fonte única de saldo;
2. reservas com expiração;
3. movimentações e auditoria;
4. prevenção de estoque negativo;
5. concorrência e idempotência;
6. integração com Marketplace, PDV e Delivery.

### Bloco 4 — Delivery e Valley Rider

1. criar entrega a partir de pedido confirmado;
2. reservar e atribuir Rider;
3. atualizar rota, ETA e estados;
4. registrar prova e conclusão;
5. liberar repasse apenas após evento validado;
6. homologar o Valley Rider com Android, GPS e rede instável.

## Testes obrigatórios da rodada

```bash
python -m pytest -q tests/test_marketplace_discovery.py
python -m pytest -q tests/test_marketplace_support_metrics.py
python -m pytest -q tests/test_marketplace_commercial_metrics.py
python -m pytest -q --ignore=tests/e2e
python scripts/validate_repository.py
```

## Critérios de aceite

- catálogo expõe apenas lojas aprovadas e produtos publicados;
- busca, categoria, preço, estoque, geolocalização e raio funcionam;
- feed identifica conteúdo patrocinado;
- promoção possui fallback e não bloqueia a homepage;
- favoritos e carrinho são isolados por usuário;
- mutações geram auditoria e eventos;
- OpenAPI corresponde às rotas implementadas;
- nenhum segredo é versionado;
- gates obrigatórios ficam verdes no mesmo SHA;
- merge ocorre exclusivamente por Squash and Merge;
- issue #51 recebe evidências e referência do commit integrado.

## Regras de autonomia

- não pedir ao usuário decisão que possa ser tomada com evidência técnica;
- não interromper o ciclo entre diagnóstico e entrega quando as ferramentas permitirem concluir;
- solicitar intervenção somente para credencial inexistente, decisão legal ou comercial irreversível, indisponibilidade de ferramenta ou bloqueio externo comprovado;
- não iniciar outra frente enquanto esta PR, seus gates e seu merge estiverem pendentes;
- após integrar, revisar novamente todas as pendências antes do próximo desenvolvimento.
