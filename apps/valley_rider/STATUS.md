# Status: Valley Rider

**Estado:** `stitch_template_operational_beta`  
**Aplicação:** `apps/valley_rider`  
**Público principal:** Riders, equipe operacional e equipe técnica  
**Atualização:** 28/07/2026

## Implementado

- template oficial do agregador Stitch Valley Riders aplicado ao shell mobile;
- todas as oito famílias de telas do contrato Stitch representadas;
- cadastro, autenticação, perfil, documentos, KYC, veículo e homologação;
- Mapbox, geocodificação, Directions API, GPS, rota, distância e ETA;
- disponibilidade, ofertas, entregas, corridas, prova e proteção;
- wallet, ledger, ganhos, repasses, extrato e contestação;
- suporte, emergência, privacidade, histórico, avaliações e configurações;
- estados de loading, vazio, erro, sucesso, offline e bloqueio por validação;
- logomarca oficial Valley utilizada sem substituir a marca Valley Riders pendente.

## Sem botões mortos

Cada botão possui ação local verificável ou chamada para contrato existente. Controles dependentes de permissão/status ficam desabilitados com contexto visível. Nenhum endpoint fictício de Notifications ou Support foi criado: notificações usam a API do dispositivo e suporte é registrado pelo recurso auditável de disputas.

## Dependências de homologação

- configurar token público Mapbox com restrição de origem;
- injetar token Play Integrity pelo shell Android em produção;
- homologar provedor de KYC/OCR e armazenamento privado dos binários;
- homologar processamento financeiro do repasse após a solicitação auditável;
- executar testes reais em Android, rede instável e GPS de campo.
