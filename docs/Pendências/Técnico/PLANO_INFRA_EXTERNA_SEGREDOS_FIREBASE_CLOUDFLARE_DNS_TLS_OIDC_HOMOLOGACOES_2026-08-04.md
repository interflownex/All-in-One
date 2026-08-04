# Plano de execução de infraestrutura externa

## Metadados

- **Projeto:** All in One + Valley
- **Classificação:** Pendências / Técnico / Equipe Técnica
- **Público-alvo:** Equipe Técnica
- **Versão:** 1.0
- **Data e hora:** 04/08/2026 17:32, `America/Sao_Paulo`
- **Repositório:** `interflownex/All-in-One`
- **Branch:** `codex/orquestrar-infra-externa-20260804`
- **Commit-base:** `e619655a3510f15d4bd3f859afa69224576536a5`
- **Issue de orquestração:** `#240`
- **Issue de segurança relacionada:** `#224`

## Visão geral

As seis frentes listadas dependem de duas camadas diferentes. A primeira pode ser preparada e validada pelo repositório: scripts, contratos, checklists, testes, políticas e documentação. A segunda exige acesso administrativo real aos provedores e aos dispositivos: Google Secret Manager, Firebase, Cloudflare, DNS, OIDC, rulesets do GitHub e aparelhos físicos.

A rotação de credenciais é prioridade P0 porque remover valores do código não revoga segredos já expostos. As demais frentes são P1 e devem seguir uma ordem segura: segredos, staging, origem/DNS/TLS, Cloudflare, OIDC, proteção da `main` e homologações finais.

## Especificação técnica

### 1. Rotação real de credenciais

1. Inventariar os segredos afetados sem registrar valores.
2. Revogar versões antigas nos respectivos provedores.
3. Criar novas versões no Google Secret Manager.
4. Atualizar referências dos workloads por nome lógico e versão.
5. Fazer rollout controlado dos serviços consumidores.
6. Invalidar sessões e tokens quando a rotação atingir assinatura JWT.
7. Validar banco, autenticação, emissão e verificação JWT, leitura de documentos e recriptografia/key wrapping.
8. Registrar apenas IDs de versão, timestamps, responsáveis, fingerprints e resultados sanitizados.

**Critério de aceite:** versões antigas revogadas, novas versões ativas, consumidores operacionais e nenhuma credencial em Git, logs, artefatos ou comentários.

### 2. Firebase staging

1. Criar ou confirmar um projeto Firebase exclusivo de staging.
2. Registrar apps Android e Web com identificadores próprios de staging.
3. Separar Auth, Firestore, Storage, FCM, App Check e domínios autorizados da produção.
4. Manter arquivos e parâmetros operacionais em cofre ou mecanismo seguro de distribuição.
5. Aplicar regras mínimas e negar acesso por padrão.
6. Testar login, logout, revogação, FCM, App Check, regras de dados e isolamento entre ambientes.

**Critério de aceite:** staging não compartilha credenciais, dados, usuários administrativos nem regras permissivas com produção.

### 3. Cloudflare

1. Confirmar conta, zona e origem corretas.
2. Validar a origem diretamente antes de ativar proxy.
3. Configurar SSL/TLS como `Full (strict)`.
4. Ativar HTTPS obrigatório e versão mínima de TLS compatível.
5. Definir WAF, rate limiting, bot protection e cache conforme o plano contratado.
6. Criar bypass de cache para APIs, autenticação, webhooks, `/health` e MCP Streamable HTTP.
7. Validar WebSocket, streaming, headers de origem e health checks.

**Critério de aceite:** Cloudflare protege a borda sem interromper APIs, autenticação, webhooks, streaming ou observabilidade.

### 4. DNS, TLS, OIDC e infraestrutura externa

1. Inventariar domínios, subdomínios, registros, origens e responsáveis.
2. Validar `A`, `AAAA`, `CNAME`, `TXT`, `MX` e `CAA` sem colisões.
3. Confirmar certificado, cadeia completa, SANs, renovação e ausência de mixed content.
4. Configurar OIDC com `issuer`, `audience`, redirect URIs e escopos mínimos.
5. Substituir credenciais estáticas por workload identity/OIDC onde suportado.
6. Testar resolução pública, handshake TLS, redirects, autenticação, expiração, revogação e rollback.

**Critério de aceite:** DNS e TLS passam em testes externos; OIDC rejeita audience, issuer e redirect inválidos; não há credenciais estáticas desnecessárias.

### 5. Proteção administrativa da `main`

Quando a API e as permissões de rulesets estiverem disponíveis:

1. Exigir Pull Request para alteração da `main`.
2. Exigir checks obrigatórios no mesmo SHA.
3. Exigir resolução de conversas.
4. Bloquear force push e exclusão da branch.
5. Preservar `Squash and Merge` como único método.
6. Restringir bypass a conta break-glass formalmente controlada.
7. Registrar evidência via API ou captura administrativa sanitizada.

**Critério de aceite:** nenhuma alteração direta ou integração sem os gates definidos.

### 6. Homologações em dispositivos, launchers e produção

1. Testar ao menos um aparelho Android ARM64 físico.
2. Testar um segundo ambiente compatível, preferencialmente outro fabricante ou versão Android.
3. Validar launchers relevantes, ícone adaptativo, fallback, nome, atualização e reinstalação.
4. Validar login, deep links, notificações, rede instável, background, retomada e rollback.
5. Separar contas e dados de staging e produção.
6. Registrar fabricante, modelo, Android, launcher, build, SHA, data e resultado sem dados pessoais.

**Critério de aceite:** matriz de homologação preenchida, falhas rastreadas e build produtivo aprovado no ambiente correto.

## Ordem obrigatória

1. Rotação de credenciais e contenção do incidente.
2. Firebase staging segregado.
3. Origem, DNS e TLS validados.
4. Cloudflare ativada e validada.
5. OIDC implantado e credenciais estáticas reduzidas.
6. Ruleset da `main` aplicado quando disponível.
7. Homologações físicas e produtivas.

## Evidências exigidas

- IDs de versões de segredos, nunca valores;
- logs sanitizados de rollout e testes;
- resultados de DNS/TLS/OIDC;
- configuração de staging identificada por projeto e ambiente;
- status da zona Cloudflare e testes de borda;
- ruleset ou bloqueio administrativo documentado;
- matriz de dispositivos e launchers;
- commit, workflow, ambiente, data e responsável por cada etapa.

## Bloqueios reais

A execução operacional depende de acesso autorizado aos provedores e dispositivos. Sem esses acessos, somente preparação, automação, documentação e validações locais podem ser concluídas. Nenhuma frente deve ser marcada como concluída por mera existência de código.

## Entrega no GitHub

- Issue mestra: `#240`.
- Issue P0 de rotação: `#224`.
- Branch desta documentação: `codex/orquestrar-infra-externa-20260804`.
- Integração permitida somente por Pull Request, gates verdes e Squash and Merge.
