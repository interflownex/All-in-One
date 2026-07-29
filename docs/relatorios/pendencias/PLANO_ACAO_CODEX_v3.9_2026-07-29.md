# Plano de Ação Codex v3.9

**Data e hora:** 29/07/2026 20:25, `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `codex/aio-admin-android-total-2026-07-29`  
**Pull request:** `#88`  
**Classificação:** `Pendências > Técnico > Equipe Técnica`  
**Público:** Equipe Técnica e gestão administrativa  
**Janela:** até 8 horas, tolerância operacional de 4 horas

## 1. Objetivo

Concluir a entrega reproduzível do AIO Admin Android 2.0.0 sem apagar documentos anteriores e sem interferir na próxima prioridade funcional de Stock.

## 2. Sequência executada

1. auditar o repositório, o manifesto administrativo e o instalador Android existente;
2. localizar a logomarca oficial no Google Drive;
3. publicar painel e backend autenticados no AppDeploy;
4. executar cinco testes E2E e corrigir falhas automaticamente;
5. preservar a marca e gerar densidades Android por redimensionamento proporcional;
6. habilitar OAuth em janela secundária da WebView;
7. atualizar versão, manifesto, README e workflow;
8. gerar APK debug e SHA-256;
9. abrir PR com evidências;
10. restaurar documentos históricos que não poderiam ser substituídos;
11. integrar apenas com todos os gates verdes no mesmo SHA.

## 3. Critérios de parada

- erro de autenticação real;
- segredo detectado;
- divergência de marca;
- lint, teste ou build vermelho;
- conflito com `main`;
- head SHA alterado após aprovação;
- substituição ou exclusão de documento histórico.

## 4. Evidências exigidas

- QA AppDeploy 5/5;
- workflow `AIO Admin Android APK` verde;
- `Continuous Integration`, `Security`, `A1 Admin Template` e `Docker Compose Health Gate` verdes;
- artefato `AIO-Admin-2.0.0-debug.apk`;
- checksum correspondente;
- PR sem conflito;
- diff e commit de referência registrados;
- `tarefas.md` preservando integralmente a frente Stock.

## 5. Procedimento de integração

1. confirmar o head do PR;
2. confirmar todos os workflows concluídos;
3. verificar reviews e threads;
4. revisar o diff final;
5. executar Squash and Merge com `expected_head_sha`;
6. registrar o commit integrado e disponibilizar o APK e a especificação técnica.
