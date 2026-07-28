# Tarefas da IA Desenvolvedora

**Versão:** 2.0
**Data e hora:** 28/07/2026 14:51:13
**Fuso horário:** `America/Sao_Paulo`
**Repositório:** `interflownex/All-in-One`
**Branch:** `codex/auditoria-valley-rider-2026-07-28`
**Commit-base:** `5cf3a1ad34ae2c33cd3722d95c341bd49b0e999f`
**Pull Request:** `#62`
**Issue de orquestração:** `#51`
**Aplicação:** `apps/valley_rider`

## 1. Objetivo

Homologar tecnicamente o Valley Rider implementado pelo PR `#61`, mantendo o contrato Stitch `VALLEY RIDERS APK - Template Completo` (`Project ID 370812414211795487`), corrigindo falhas reproduzíveis dos gates locais e preparando as integrações externas sem controles falsos.

## 2. Contexto e estado atual

- o código funcional do PR `#61` está integrado em `main` no commit `3834bec`;
- a auditoria encontrou 8 erros e 1 aviso no lint e um erro TypeScript no build;
- as correções desta branch removem atualizações síncronas de estado em efeitos, evitam leitura de `ref` durante render, tornam o estado do GPS explícito, corrigem expressões sem efeito e usam `BufferSource` no helper SHA-256;
- `npm run lint`, `npm run build` e os testes contratuais passaram após as correções;
- a prova visual/interativa foi concluída por Playwright com Chromium local, HTTP 200, marca oficial, ausência de overlay, interação login/cadastro e capturas desktop/mobile;
- a execução `push` do CI revelou dois testes de sincronização Git dependentes das referências ambientais do checkout; os testes foram tornados determinísticos e a suíte local completa aprovou 907 testes;
- não há token Mapbox, credencial KYC, cofre privado, PSP de repasse, aparelho Android real nem binário oficial Valley Riders versionados.

## 3. Escopo

### Incluído

1. preservar os oito grupos funcionais Stitch;
2. manter Mapbox, GPS, geocodificação, rota, distância, ETA e Haversine;
3. manter cadastro, autenticação, KYC, motorista, veículo e homologação;
4. manter entregas, corridas, prova obrigatória e seguro;
5. manter wallet, ledger idempotente, repasse via `finance/splits`, cancelamento e contestação;
6. manter segurança, suporte, offline, notificações e privacidade;
7. validar código, marca e aplicação renderizada;
8. documentar e evidenciar bloqueios externos.

### Fora do escopo sem credenciais ou contratos

- emitir token público Mapbox;
- contratar ou homologar provedor KYC/OCR;
- criar cofre de arquivos privados;
- processar repasses reais;
- gerar Play Integrity legítimo;
- fabricar logomarca Valley Riders;
- declarar GPS/rede instável homologados sem aparelho real.

## 4. Fontes de verdade

1. `AGENTS.md`;
2. diretriz técnica anexada em 28/07/2026;
3. `config/stitch/screen_manifest.json`;
4. `config/stitch/sync_state.json`;
5. `config/branding/authorized_assets.json`;
6. `config/branding/brand_identity.json`;
7. `assets/brand/README.md`;
8. `apps/valley_rider/README.md`;
9. `apps/valley_rider/STATUS.md`;
10. contratos OpenAPI dos módulos Identity, Riders, Delivery, Mobility, Finance e Marketplace;
11. documentação oficial vigente de Mapbox, provedores KYC, Play Integrity e PSP que forem contratados.

## 5. Pré-requisitos

- branch de trabalho atualizada com `origin/main`;
- lock multiagente adquirido no escopo `valley-rider-auditoria`;
- Node e npm compatíveis com o lockfile;
- `.venv` do projeto para pytest;
- segredos somente em variáveis de ambiente ou cofre;
- Playwright e Chromium local disponíveis para a prova renderizada;
- aparelho Android real autorizado para GPS e rede instável.

## 6. Sequência de execução e prioridades

### P0 — finalizar esta correção

1. repetir `npm ci`, lint e build;
2. executar testes Stitch e de marca;
3. executar `check_brand_integrity.py` e `validate_repository.py`;
4. revisar o diff e procurar segredos;
5. commitar e publicar a branch;
6. abrir PR para `main`;
7. aguardar todos os gates obrigatórios no mesmo SHA;
8. atualizar a issue `#51` com SHA, PR, testes e bloqueios.

### P1 — prova renderizada

1. disponibilizar o navegador integrado;
2. abrir a aplicação local;
3. validar identidade da página, conteúdo não vazio e ausência de overlay;
4. conferir console;
5. alternar login/cadastro;
6. autenticar somente com conta de teste autorizada;
7. validar estados bloqueados de Mapbox/KYC/PSP sem credenciais;
8. capturar evidências desktop e mobile.

### P1 — homologações externas

1. cadastrar token público Mapbox restrito por origem;
2. homologar KYC/OCR e cofre privado;
3. homologar PSP para consumir solicitações `split_type: rider_payout`;
4. integrar Play Integrity pelo shell Android;
5. testar GPS em campo e rede instável;
6. ingerir apenas o binário oficial aprovado da marca Valley Riders.

## 7. Testes

```bash
cd apps/valley_rider
npm ci
npm run lint
npm run build
cd ../..
.venv/bin/pytest -q tests/test_valley_rider_stitch_contract.py
.venv/bin/pytest -q tests/test_branding_assets.py
python3 scripts/check_brand_integrity.py
python3 scripts/validate_repository.py
```

Gates remotos obrigatórios:

- Continuous Integration;
- Docker Compose Health Gate;
- Security.

## 8. Critérios de aceite

- lint e build aprovados no checkout limpo;
- testes Stitch e de marca aprovados;
- integridade de marca e validação do repositório aprovadas;
- nenhuma credencial ou dado pessoal real versionado;
- nenhuma transição incompatível com o estado do recurso;
- entrega não conclui sem prova obrigatória;
- repasse usa `split_type: rider_payout`;
- nenhum lançamento negativo é criado em `ledger_entries`;
- estados externos indisponíveis aparecem bloqueados e explicados;
- prova renderizada concluída no navegador integrado;
- branch publicada, PR aberto e gates verdes no mesmo commit;
- evidência vinculada à issue de orquestração.

## 9. Riscos e bloqueios

| Item | Estado | Tratamento |
|---|---|---|
| Navegador integrado `iab` | bloqueado nesta sessão | repetir QA quando a instância estiver disponível |
| Token Mapbox | externo | usar token público restrito, nunca versionar |
| KYC/OCR e cofre | externo | bloquear submissão produtiva até homologação |
| PSP de repasse | externo | manter solicitação auditável sem simular liquidação |
| Play Integrity | externo | injetar pelo shell Android |
| GPS/rede instável | externo | testar em aparelho real |
| Marca Valley Riders | binário ausente | não fabricar substituto |
| Vulnerabilidades npm de desenvolvimento | 2 altas reportadas por `npm ci` | analisar no gate Security; produção apresentou 0 vulnerabilidades |

## 10. Evidências esperadas

- saída dos comandos de teste;
- SHA do commit;
- URL e número do PR;
- checks do GitHub vinculados ao SHA;
- screenshots desktop/mobile;
- DOM e console sem erros relevantes;
- identificação do aparelho Android, atividade executada e captura de tela;
- configuração de restrição do token Mapbox sem expor o token;
- comprovantes de homologação KYC/cofre/PSP sem segredos.

## 11. Pendências restantes

1. publicar o commit final com a correção determinística do gate Git;
2. executar gates remotos no novo SHA;
3. homologar todas as dependências externas;
4. integrar somente por Squash and Merge após aprovação.

## 12. Procedimento de entrega

1. confirmar branch e diff;
2. executar todos os testes locais;
3. atualizar documentação com SHA e PR;
4. usar mensagem de commit concisa em português;
5. publicar somente a branch de trabalho;
6. abrir PR para `main`;
7. registrar testes, limitações e evidências no PR;
8. aguardar gates verdes;
9. não alterar o commit já em validação;
10. integrar exclusivamente por Squash and Merge.

## 13. Histórico

| Versão | Data e hora | Alteração |
|---|---|---|
| 1.7 | 27/07/2026 07:12:49 | Fase 0 implementada e regressão final preparada. |
| 1.8 | 28/07/2026 00:52:26 | Rodada 004 do APK Valley registrada. |
| 1.9 | 28/07/2026 08:39:01 | Auditoria do Valley Rider, correção dos gates locais e plano de homologação externa. |
| 2.0 | 28/07/2026 14:51:13 | PR #62 aberto, QA desktop/mobile concluída e testes do gate Git tornados determinísticos. |
