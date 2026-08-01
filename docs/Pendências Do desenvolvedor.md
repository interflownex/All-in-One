# Pendências do Desenvolvedor

**Versão:** 5.0  
**Data e hora da atualização:** 01/08/2026 03:52  
**Fuso horário:** `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch de execução:** `codex/corrigir-inconsistencias-mandatorias-20260801`  
**Commit-base da `main`:** `63ceb867c6342a3706e82a650e6072522facfbd7`  
**Issue de orquestração:** `#51`  
**Classificação:** `Pendências > Técnico > Equipe Técnica`  
**Públicos impactados:** Pessoa Física, Pessoa Jurídica, Equipe Técnica, gestão e investidores

## 1. Situação executiva

A fundação técnica está avançada e estabilizada, mas o ecossistema ainda não está homologado para operação produtiva completa de ponta a ponta.

Estado confirmado:

- zero Pull Request aberta antes desta correção;
- nove issues abertas;
- Merge Commit e Rebase Merge desativados;
- Squash and Merge habilitado como único método de integração;
- auto-merge desativado;
- 24 módulos ativos;
- Vision inativo;
- 28 branches remotas divergentes preservadas por conterem commits exclusivos;
- Stock transacional integrado;
- checkout idempotente integrado;
- Wallet interna, escrow hold, ledger e compensação técnica integrados;
- checkout produtivo desligado por feature flag;
- pagamentos produtivos, liquidação e reconciliação ainda não homologados;
- deploy GKE bloqueado externamente por faturamento GCP desativado.

## 2. Correções aplicadas nesta rodada

| Inconsistência | Correção persistente |
|---|---|
| Documento apontava para branch encerrada | Atualizado para a branch desta correção e `main` atual |
| Commit-base estava desatualizado | Atualizado para `63ceb867...` |
| PR #50 era descrita como aberta/sem merge | Afirmação removida por ser histórica e falsa no estado atual |
| Total de issues abertas estava em oito | Corrigido para nove, incluindo `#107` |
| Issue #51 marcava fases integradas como pendentes | Corpo reconciliado com PRs #65, #92, #94, #105 e #106 |
| Issue #55 apontava para branch inicial substituída | Referência corrigida para a entrega integrada pela PR #57 |
| Escopo de repositório não tinha trava própria | Criada política e gate automatizado |
| Risco de mistura entre fontes de código | Bloqueado por `repository_scope_policy.json` e teste de regressão |
| Máquina local era tratada como verificada sem acesso direto | Estado alterado para “não verificado”; inspeção não destrutiva documentada |

## 3. Pendências abertas por prioridade

### P0 — Bloqueios do caminho produtivo

#### #95 — PSP, webhooks, liquidação e reconciliação

**Estado:** executável em código e sandbox, sem ativação produtiva.

Pendências:

- interface de PSP independente;
- adaptador sandbox separado de produção;
- assinatura e proteção contra replay de webhooks;
- autorização, captura, cancelamento, estorno e chargeback idempotentes;
- ledger de liquidação;
- reconciliação entre PSP, pedido, escrow e ledger;
- bloqueio automático diante de divergência;
- segredos exclusivamente em Secret Manager;
- testes de falha e compensação;
- feature flag desligada até homologação.

#### #107 — faturamento GCP e deploy GKE

**Estado:** bloqueio externo.

A autenticação OIDC funciona, mas o Google Cloud retorna HTTP 403 na obtenção das credenciais do cluster porque o faturamento do projeto `all-in-one-498012` está desativado.

Ação permitida:

- habilitar billing legitimamente;
- confirmar IAM e APIs;
- repetir o workflow no SHA atual;
- exigir rollout verde sem desativar gates.

### P1 — Convergência e segurança operacional

#### Auditoria do repositório local

**Estado:** não verificado neste ambiente.

O worktree local está apontado para `/home/eretazan/all-in-one`, mas o diretório não está acessível por esta execução remota. Ainda é necessário verificar:

- branch e HEAD locais;
- arquivos staged, unstaged e untracked;
- exclusões preparadas;
- commits locais não publicados;
- merge, rebase ou cherry-pick em andamento;
- diferença para `origin/main`.

Nenhum pull, reset, clean, descarte, commit ou push deve ocorrer antes da inspeção e do backup em patch.

#### #89 — fonte produtiva do AIO Admin

**Estado:** aplicação publicada e Android conectado, mas a fonte operacional ainda precisa convergir com o repositório.

Pendências:

- separar claramente template visual, fonte produtiva e empacotamento Android;
- versionar ou documentar o adaptador produtivo;
- preservar autenticação, auditoria, persistência e tempo real;
- registrar rollback e processo de publicação;
- repetir E2E e gates Android.

#### Branches remotas divergentes

**Estado:** 28 branches preservadas, nenhuma apta a merge direto.

Regras:

- comparar semanticamente com a `main`;
- identificar código já integrado ou substituído;
- extrair apenas conteúdo exclusivo válido;
- reconstruir em branch nova;
- nunca trazer migrations antigas ou lockfiles obsoletos por merge cego;
- arquivar somente após prova de preservação.

Riscos já confirmados:

- `feature/primicias-selecionadas-v1` contém migration 031 incompatível com a numeração atual;
- branches de Cloudflare, branding, Dependabot e integrações Stock estão dezenas ou centenas de commits atrás;
- várias branches pertencem a PRs encerradas ou substituídas.

### P2 — Produtos e capacidades

#### #51 — Marketplace → Stock → Finance → Delivery

Concluído tecnicamente:

- catálogo, busca, filtros, geolocalização, feed, promoção, favoritos e carrinho;
- inventário e reservas Stock;
- prevenção de estoque negativo;
- checkout idempotente;
- Wallet interna, escrow hold, ledger e compensação.

Pendente:

- issue #95;
- homologação produtiva;
- Delivery e Rider iniciados somente após pagamento comprovado.

#### #47 — Health Watch + SafeZone

Pendente:

- companion Android e Wear OS compiláveis;
- consentimento e vínculo de cuidado;
- proteção contra rastreamento oculto;
- geofence, incidentes e modo offline;
- migrações, OpenAPI, eventos e auditoria;
- testes de revogação, troca de dispositivo e perda de conexão.

#### #55 — Rodada 004

A vertical inicial foi integrada. Permanecem:

- persistência;
- autenticação e autorização;
- integrações reais;
- interfaces móveis completas;
- homologações regulatórias e externas;
- ativação seletiva por funcionalidade.

#### #39 — Onda de inovação dos 24 módulos

A fundação, catálogo e feature flags estão integrados. Cada capacidade continua pendente até cumprir:

- contrato e eventos;
- dados e migration reversível;
- autorização, consentimento e auditoria;
- testes unitários, integração e jornada;
- telemetria, rollback e segurança;
- homologação externa quando necessária.

#### #69 — Rodada 002

**Estado:** bloqueada por fonte funcional ainda não versionada no GitHub.

Condição para retomar:

- fonte HTML/JavaScript ou equivalente estruturado;
- dados das 24 ideias e 120 decisões;
- observações, validação e gerador de PDF;
- testes reproduzíveis;
- Vision explicitamente excluído.

#### #24 — Promoção do Dia

Backend de elegibilidade e contratos do Marketplace avançaram, mas a issue permanece aberta até comprovar:

- uso da tela correta do Stitch;
- modal funcional após login;
- frequência, fechamento e CTA reais;
- acessibilidade e responsividade;
- eventos idempotentes;
- isolamento por tenant;
- evidências visuais e E2E.

## 4. Regras permanentes

1. O único repositório oficial está definido em `config/autonomy/repository_scope_policy.json`.
2. Valley permanece dentro do monorepo oficial.
3. Vision não pode ser reativado sem ordem explícita.
4. Nenhuma alteração direta na `main`.
5. Nenhum merge com gate vermelho, ausente, cancelado ou em processamento.
6. Integração somente por Squash and Merge e head SHA validado.
7. Nenhuma credencial, token, senha, chave, certificado ou DSN de produção no Git.
8. Nenhuma exclusão em massa sem inventário e justificativa.
9. Nenhuma branch antiga pode ser mesclada diretamente.
10. Nenhuma migration pode reutilizar os números 031 ou 032.
11. `MARKETPLACE_CHECKOUT_V1_ENABLED` deve permanecer desligada até homologação financeira.
12. Delivery e Rider não podem iniciar sem pagamento confirmado e reconciliado.
13. Nenhuma tarefa é concluída somente porque existe código ou documento.
14. `tarefas.md` deve ser atualizado em toda entrega técnica.

## 5. Plano de execução seguro

1. validar esta correção documental e o gate de escopo;
2. abrir PR para `main`;
3. aguardar CI e Security no mesmo SHA;
4. integrar somente por Squash and Merge;
5. auditar o worktree local sem comandos destrutivos;
6. preservar patches e branch de backup caso existam mudanças locais;
7. executar a issue #95 em branch exclusiva;
8. habilitar billing e comprovar a issue #107 externamente;
9. executar a convergência da issue #89;
10. revisar branches antigas por extração seletiva;
11. avançar Delivery e Rider somente após o gate financeiro.

## 6. Critérios de conclusão desta rodada

- documentos autoritativos atualizados;
- issue #51 reconciliada;
- issue #55 reconciliada;
- política de escopo criada;
- validador e testes criados;
- nenhuma alteração de produto, banco ou marca;
- PR aberta;
- checks verdes no mesmo SHA;
- merge somente após validação.

## 7. Histórico resumido

- v3.4: inventário relacional, E2E, dependências e branches;
- v5.0: consolidação autoritativa após PRs #105/#106, inclusão da issue #107 e trava permanente de escopo.
