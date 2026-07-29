# Plano de Ação Codex v3.6

**Classificação:** Pendências > Técnico > Equipe Técnica  
**Público:** Equipe Técnica  
**Janela:** até 8 horas, tolerância operacional de 4 horas

## Sequência

1. publicar painel e backend autenticados;
2. executar QA E2E e corrigir falhas automaticamente;
3. preservar a logomarca oficial e gerar densidades Android por redimensionamento;
4. habilitar OAuth em janela secundária da WebView;
5. atualizar versão, manifesto, README e workflow;
6. gerar APK debug e SHA-256;
7. abrir pull request com evidências;
8. integrar apenas com gates verdes.

## Critérios de parada

- erro de autenticação real;
- segredo detectado;
- divergência de marca;
- lint, teste ou build vermelho;
- conflito com `main`;
- head SHA alterado após aprovação.

## Evidências esperadas

- QA AppDeploy 5/5;
- workflow GitHub verde;
- artefato `AIO-Admin-2.0.0-debug.apk`;
- checksum correspondente;
- PR sem conflito;
- diff e commit de referência registrados.
