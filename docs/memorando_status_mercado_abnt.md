# MEMORANDO TÉCNICO-COMERCIAL

**Projeto:** All-in-One
**Assunto:** Status de progresso, módulos, serviços, microserviços, concorrência, preços e estratégia de entrada no mercado brasileiro
**Data-base:** 01 de junho de 2026
**Origem:** Levantamento do repositório local e pesquisa de mercado em fontes públicas
**Formato:** Memorando em padrão ABNT simplificado, com seções numeradas, resumo, desenvolvimento, recomendações e referências.

## RESUMO

Este memorando consolida o estado atual da plataforma All-in-One (~62% global). O backend estabilizou a persistência PostgreSQL, mas identificou gargalos de validação nos módulos ERP e TMS. A estratégia comercial foca em preços 20% abaixo do mercado nacional e entrada com custo de aquisição zero via parcerias com contadores e associações.

O projeto possui 25 microserviços. A camada de infraestrutura local está em 95%. O backend está próximo da beta técnica; as lacunas residem em interfaces Stitch e homologações de provedores reais de pagamento e KYC.

## 1 INTRODUÇÃO

O All-in-One foi desenhado como uma plataforma modular brasileira para operar identidades, pagamentos, marketplace, delivery, serviços, mobilidade, jobs, ERP, WMS, TMS, CRM, saúde, jurídico, documentos, BI, IA e verticais operacionais em uma única base técnica. A arquitetura adota API Hub, Identity, Permissions, PostgreSQL para dinheiro, auditoria, contratos e identidade, MongoDB para memória/telemetria volumosa, RabbitMQ para eventos e microserviços FastAPI por domínio.

O objetivo de mercado é concorrer com soluções nacionais fragmentadas, oferecendo uma suíte integrada, modular e mais barata do que a média nacional. A proposta de precificação deste documento segue a regra solicitada: sugerir preços no mínimo 20% abaixo dos preços públicos ou faixas de referência identificadas no mercado brasileiro, preservando margem por meio de automação, onboarding digital, freemium controlado e venda por módulos.

## 2 STATUS GERAL DO DESENVOLVIMENTO

| Área                       | Conclusão | Situação atual                                                                                    | Próximos passos naturais                                             |
| -------------------------- | --------: | ------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| Git e sincronização remota |      100% | Fluxo de entrega remoto previsto e automação local disponível em `scripts/git_auto_sync.ps1`.     | Adicionar gate de divergência entre `origin`, `fork` e branch local. |
| Contratos de microserviços |      100% | 25 domínios com contrato, OpenAPI, README, STATUS e testes-base.                                  | Congelar contratos beta e versionar mudanças breaking.               |
| Docker e runtime local     |      100% | 13 serviços FastAPI principais saudáveis em Docker Compose, com PostgreSQL e RabbitMQ.            | Criar gate CI de compose e healthcheck em ambiente limpo.            |
| PostgreSQL estrutural      |       80% | Migrations SQL, `BasePostgresStore`, stores especializados e stores gerados para cobertura ampla. | Validar CRUD, idempotência, audit e outbox em todos os módulos.      |
| Runtime FastAPI modular    |       85% | Autorização, auditoria, outbox, runtime comum e carregamento dinâmico por DSN.                    | Ampliar testes E2E e testes negativos por permissão.                 |
| Mensageria e outbox        |       75% | RabbitMQ, dispatcher, publisher confirms e testes críticos já validados.                          | Validar eventos reais por todos os domínios e criar métricas.        |
| MongoDB e NoSQL            |       55% | Uso previsto para IA, social, telemetria e memória consentida.                                    | Validar coleções, índices, retenção e governança LGPD.               |
| Apps/frontend              |       35% | 6 apps definidos e plano Stitch com 25 projetos e 177 telas.                                      | Implementar shell funcional, integrar endpoints e Playwright E2E.    |
| Integrações externas       |       20% | Contratos e pontos de extensão existem.                                                           | Homologar KYC/KYB, Pix/PSP, fiscal, CTPS, mapas, IA e saúde.         |
| Produção e compliance      |       20% | Documentação inicial de segurança e operação.                                                     | LGPD/DPIA, pentest, carga, backup/restore, SLOs e runbooks.          |

## 3 MÓDULOS, SERVIÇOS E MICROSSERVIÇOS

| Módulo      |   % | Serviço/microserviço                                | Estado técnico                                                                                    | Próximos passos naturais                                                      |
| ----------- | --: | --------------------------------------------------- | ------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| Identity    | 86% | Identidade, usuários, login, KYC, MFA, audit        | Mais maduro entre os módulos centrais; cadastro, login JWT, KYC e MFA testados em container real. | Homologar KYC/KYB/liveness, OIDC real, testes negativos e consentimento LGPD. |
| Jobs        | 84% | Vagas, currículo, CTPS, recrutamento, cofre privado | CTPS PDF, cofre AES-256-GCM, outbox e PostgreSQL tipado avançados.                                | Integrar verificador oficial CTPS e jornada candidato -> vaga -> recrutador.  |
| API Hub     | 78% | Gateway, API keys, webhooks, rate limit             | Contratos e SQL refinados; container saudável.                                                    | Testar API key, webhook assinado, OAuth2 real e rate limit produtivo.         |
| Business    | 74% | Empresas, memberships, aprovação, usuários PJ       | Store tipado, companies, memberships e idempotência.                                              | Fluxo KYB, aprovação operacional e convite de usuários.                       |
| Finance     | 72% | Wallet, ledger, escrow, billing, fiscal             | Wallet, ledger, escrow e store tipado.                                                            | PSP/Pix, split, refund, conciliação, fiscal e antifraude em sandbox.          |
| Marketplace | 68% | Catálogo, pedidos, checkout, sellers                | Catálogo e pedidos com store tipado.                                                              | Jornada produto -> carrinho -> pedido -> pagamento -> fulfillment.            |
| Delivery    | 68% | Entregas, riders, veículos, POD                     | Entregas e veículos com store tipado.                                                             | Tracking, matching, prova de entrega e cotação real.                          |
| Services    | 68% | Prestadores, visitas, orçamento, contratos          | Prestadores e contratos com store tipado.                                                         | Escrow, evidências, anti-burla e jornada visita -> contrato.                  |
| Mobility    | 68% | Corridas, tickets, fare rules, QR/NFC               | Rides e tickets com store tipado.                                                                 | ETA, mapas, QR/NFC, antifraude e tarifas reais.                               |
| Permissions | 64% | RBAC/ABAC, escopos, políticas                       | Modelo de autorização e store gerado.                                                             | Matriz de permissões e enforcement profundo em todos endpoints.               |
| Stock       | 62% | Dropshipping, fornecedores, catálogo, margem        | Fornecedores e dropshipping modelados.                                                            | Integrar fornecedores sandbox e regras de margem/estoque real.                |
| Riders      | 62% | Cadastro entregador/motorista, documentos, ganhos   | Candidatura, documentos e veículos modelados.                                                     | Onboarding rider, aprovação, carteira de ganhos e antifraude.                 |
| ERP         | 60% | Fiscal, financeiro operacional, contas, compras     | Fluxos fiscais/contábeis modelados e store gerado.                                                | Tipar store ERP e testar contas a pagar/receber e emissão fiscal.             |
| WMS         | 60% | Armazém, inventário, recebimento, picking           | Armazém e inventário modelados.                                                                   | Tipar store WMS e testar recebimento, picking, ruptura e inventário.          |
| TMS         | 60% | Fretes, transportadoras, torre de controle          | Fretes e transportadoras modelados.                                                               | Tipar store TMS, cotação, tracking, POD e SLA por transportadora.             |
| CRM         | 60% | Leads, oportunidades, pipeline, campanhas           | Leads e oportunidades modelados.                                                                  | Tipar store CRM e validar lead -> oportunidade -> proposta.                   |
| Health      | 60% | Paciente, agenda, prontuário, telemedicina          | Pacientes, agenda e prontuário modelados.                                                         | Consentimento, TISS, teleconsulta, assinatura e segurança clínica.            |
| BPM         | 58% | Workflows, processos, SLAs, escalonamento           | Processos e workflows modelados.                                                                  | Engine real com timers, SLA, escalonamento e auditoria.                       |
| Document    | 58% | GED/ECM, OCR, assinatura, versionamento             | Documentos e assinatura modelados.                                                                | Upload, versionamento, OCR, storage privado e assinatura ICP-Brasil.          |
| HR          | 58% | HCM, ATS, LMS, folha, ponto                         | HCM/ATS/LMS modelado.                                                                             | Colaborador -> folha -> treinamento, ponto, férias e performance.             |
| AI Core     | 55% | Memória consentida, moderação, model runs           | Memória, moderação e execuções de modelo modeladas.                                               | Providers IA, orçamento por execução, governança e trilha de decisão.         |
| BI          | 55% | Datasets, dashboards, métricas, analytics           | Datasets e dashboards modelados.                                                                  | ETL auditável, permissões analíticas e primeiro dashboard executivo.          |
| Vision      | 55% | Dispositivos, streams, alertas, IA visual           | Dispositivos e alertas modelados.                                                                 | Prova de stream, ingestão de vídeo, detecção e alertas.                       |
| Legal       | 55% | Casos, prazos, audiências, documentos               | Casos e prazos modelados.                                                                         | Integrações com calendário/tribunais e alerta de prazo.                       |
| Property    | 55% | Imóveis, unidades, locações, manutenção             | Imóveis e locações modelados.                                                                     | Fluxo locação/manutenção, boletos, chamados e vistoria.                       |

## 4 APPS E JORNADAS DE PRODUTO

| App                 | Status | Jornadas prioritárias                                     | Próximos passos                                                           |
| ------------------- | ------ | --------------------------------------------------------- | ------------------------------------------------------------------------- |
| all-in-one-user     | 35%    | Cadastro, wallet, busca, compra, delivery, jobs.          | Implementar interface real e jornada `identity -> wallet -> marketplace`. |
| all-in-one-business | 35%    | Empresa, aprovação, usuários, jobs, ERP, relatórios.      | Implementar onboarding PJ, KYB, convite e dashboard.                      |
| all-in-one-riders   | 35%    | Candidatura, documento, veículo, entrega/corrida, ganhos. | Criar fluxo de aprovação, tracking e carteira de ganhos.                  |
| all-in-one-services | 35%    | Prestador, visita, orçamento, contrato, evidência.        | Implementar agenda, orçamento, escrow e evidências.                       |
| all-in-one-health   | 35%    | Paciente, agenda, prontuário, consulta.                   | Implementar agenda clínica, consentimento e teleconsulta.                 |
| all-in-one-mobility | 35%    | Corrida, ticket, QR/NFC, histórico.                       | Implementar solicitação de corrida, ticket e validação QR/NFC.            |

## 5 CONCORRENTES, PREÇOS E ESTRATÉGIAS OBSERVADAS

| Área All-in-One        | Concorrentes no Brasil                                                    | Preços públicos/faixas observadas                                                                                                                  | Estratégia de atração dos concorrentes                                                                 | Preço All-in-One sugerido, 20% abaixo                                                                         |
| ---------------------- | ------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------- |
| ERP/Finance/WMS básico | Conta Azul, Bling, Omie, Tiny/Olist                                       | Conta Azul: R$159,90 a R$719,90/mês; Bling: R$55 a R$650/mês; Omie e Tiny variam por perfil, com planos e módulos.                                 | Teste grátis, gestão fiscal/financeira simples, marca forte, contador parceiro, integrações ecommerce. | ERP Starter R$44/mês; ERP Pro R$127/mês; ERP Scale R$320/mês; add-on fiscal IA R$159/mês.                     |
| CRM                    | RD Station CRM, PipeRun, Pipedrive, Zoho, HubSpot                         | RD Station CRM: Free, R$73/usuário/mês e R$131/usuário/mês; PipeRun e Pipedrive operam por usuário; Zoho parte de US$14/usuário/mês.               | Freemium, automação comercial, funil pronto, integrações WhatsApp/email, marca de marketing.           | CRM Free até 2 usuários; CRM Pro R$58/usuário/mês; CRM Advanced R$104/usuário/mês.                            |
| Marketplace/ecommerce  | Nuvemshop, Yampi, Loja Integrada, Shopify, Mercado Livre/Shopee           | Nuvemshop: grátis, R$69, R$164 e R$449/mês; Yampi: grátis com 2,5% por pedido, R$47/mês, R$157/mês e planos sob medida.                            | Plano grátis, checkout de alta conversão, meios de pagamento/envio próprios, apps e templates.         | Marketplace Free com 1,8% por pedido; Pro R$38/mês + 1,6%; Scale R$126/mês + 1,2%.                            |
| Delivery/restaurantes  | iFood, Aiqfome, Rappi, Delivery Much                                      | iFood: comissão típica 12% entrega própria, 23% logística iFood, taxa online 3,2%, mensalidade R$110 ou R$150 acima de R$1.800/mês.                | Grande base de consumidores, logística, marketing, cupons e visibilidade.                              | Delivery Próprio 9,6% + pagamento; Delivery Logístico 18,4%; mensalidade R$88/R$120 só acima de R$1.800.      |
| Logística/TMS          | Loggi, Melhor Envio, Frete Rápido, Intelipost, Frenet                     | Loggi informa frete nacional a partir de R$5,89; contratos B2B podem ser personalizados. TMS enterprise costuma ser sob consulta.                  | Preço por envio, integração com ecommerce, rastreio e negociação por volume.                           | TMS SaaS R$79/mês + frete via parceiros; etiqueta a partir de preço do parceiro menos comissão negociada.     |
| Mobilidade             | Uber, 99, InDrive, Vá de Táxi                                             | Preço dinâmico por viagem; Uber Empresas usa preço antecipado e fatura mensal quando elegível. Taxa da plataforma varia por viagem.                | Base de motoristas, preço dinâmico, conveniência, faturamento corporativo.                             | Mobility corporativo sem mensalidade no beta, taxa plataforma 12% a 18% por corrida; passe urbano R$7,90/mês. |
| Saúde/consultórios     | iClinic, Feegow, Ninsaúde Apolo, Prontio, Doctoralia                      | iClinic: R$99, R$129, R$169 e R$299 por profissional/mês; Feegow: R$129, R$199 e R$249 por profissional/mês; Ninsaúde: R$199 por profissional/mês. | Prontuário, agenda, WhatsApp, TISS, teleconsulta, IA e segurança LGPD.                                 | Health Starter R$79/profissional/mês; Health Pro R$135; Health Premium R$239.                                 |
| Jobs/RH/ATS            | Gupy, Sólides, Catho Empresas, InfoJobs, LinkedIn                         | Gupy e Sólides trabalham majoritariamente sob demonstração/consulta; referências públicas mostram planos por solução e proposta consultiva.        | Marca empregadora, IA de triagem, banco de talentos, marketplace de vagas, demo consultiva.            | Jobs Starter R$79/mês + 3 vagas; Jobs Pro R$239/mês; vaga avulsa R$39.                                        |
| Document/GED           | DocuSign, Clicksign, D4Sign, TOTVS ECM, ZapSign                           | Mercado varia por envelopes/documentos e planos sob consulta ou por assinatura.                                                                    | Assinatura eletrônica, validade jurídica, automação documental e integração.                           | GED R$39/mês + R$1,20/documento assinado; OCR R$0,08/página.                                                  |
| BI                     | Power BI, Looker Studio, Tableau, Zoho Analytics                          | Looker Studio tem base gratuita; Power BI Pro costuma operar por usuário/mês; enterprise sob consulta.                                             | Dashboards rápidos, conectores, baixo atrito inicial.                                                  | BI Starter gratuito com 2 dashboards; BI Pro R$39/usuário/mês; embed R$149/mês.                               |
| AI Core/Vision         | Azure AI, Google Cloud AI, AWS Rekognition, OpenAI integradores nacionais | Precificação por uso, token, imagem, minuto ou chamada; valores variam por provedor.                                                               | Baixo investimento inicial, escala por uso, APIs prontas, ecossistema.                                 | IA com repasse de custo + 15%; Vision R$49/câmera/mês no beta, alertas R$0,03/evento.                         |
| Legal/Property         | Astrea, ProJuris, QuintoAndar, Superlógica, Group Software                | Jurídico, imóveis e condomínios costumam usar planos por usuário, unidade ou sob consulta.                                                         | Especialização vertical, automação de prazos, cobrança, portais e rede de imóveis.                     | Legal R$49/usuário/mês; Property R$0,80/unidade/mês ou R$79/mês mínimo.                                       |

## 6 ESTRATÉGIA DE PREÇOS POR MÓDULO

A política comercial é o "Preço de Desestabilização" (20% abaixo do mercado). O custo de entrada para o cliente é zero através de migração assistida de planilhas.

| Módulo      |                                          Preço de entrada recomendado | Monetização adicional                        | Estratégia de menor custo possível                                          |
| ----------- | --------------------------------------------------------------------: | -------------------------------------------- | --------------------------------------------------------------------------- |
| Identity    | Gratuito para usuários finais; R$0,05 por verificação interna no beta | KYC real repassado + 15%                     | Começar com verificação documental manual e provedores sandbox.             |
| Business    |                                                  R$49/mês por empresa | Usuários extras, KYB, storage e SLA          | Onboarding self-service, aprovação manual por fila.                         |
| Permissions |                                             Incluído nos planos pagos | Add-on auditoria avançada R$29/mês           | Usar como diferencial de segurança, não como módulo isolado inicial.        |
| Finance     |                                         R$39/mês + taxa PSP repassada | Escrow 1,2%, split 0,5%, conciliação Pro     | Primeiro integrar um PSP com Pix/cartão, sem virar instituição financeira.  |
| Marketplace |                                                    R$0 + 1,8% no beta | Destaque, ads, relatórios, checkout          | Atrair vendedores com loja grátis e taxa menor que marketplace tradicional. |
| Stock       |                                                              R$49/mês | Margem fornecedor, campanhas e automação     | Começar com integração CSV/API de fornecedores já existentes.               |
| Delivery    |                                               9,6% a 18,4% por pedido | Seguro, urgência, ajudante e ads local       | Foco inicial em entrega própria do lojista e parceiros locais.              |
| Riders      |                                                  Gratuito para riders | Taxa por saque instantâneo e seguro opcional | Cadastro simples e aprovação manual até haver volume.                       |
| Services    |                                          R$0 + 8% por serviço fechado | Visita paga, destaque e assinatura Pro R$39  | Lançar em nichos locais com prestadores verificados.                        |
| Mobility    |                                                 12% a 18% por corrida | Passe, corporativo, ads e cancelamento       | Iniciar com mobilidade corporativa/local, não disputar massa com Uber/99.   |
| Jobs        |                                                    R$79/mês + 3 vagas | Vaga avulsa R$39, hunting e triagem IA       | Atacar PMEs que não conseguem pagar ATS consultivo.                         |
| API Hub     |                                                              R$49/mês | API calls, webhooks, SLA e sandbox           | Oferecer portal dev simples para parceiros.                                 |
| ERP         |                                                              R$44/mês | Fiscal, BI, conciliação, usuários extras     | Posicionar como ERP modular para operação integrada.                        |
| WMS         |                                                              R$69/mês | Leitores, etiquetas, integrações             | Começar com picking simples via app web/mobile.                             |
| TMS         |                                                              R$79/mês | Cotações, etiquetas, tracking, POD           | Integrar transportadoras via agregadores antes de contrato direto.          |
| CRM         |                                                      R$58/usuário/mês | WhatsApp, automações, assinatura e propostas | Oferecer free para 2 usuários e migração de planilhas.                      |
| BPM         |                                                              R$49/mês | Workflows extras e SLA                       | Modelos prontos de aprovação, compras, onboarding e suporte.                |
| Document    |                                                              R$39/mês | OCR, assinatura e storage                    | Usar storage barato, OCR por demanda e assinatura parceira.                 |
| HR          |                                                              R$79/mês | Ponto, folha, LMS e performance              | Começar com ATS + documentos, depois folha/ponto.                           |
| Health      |                                                 R$79/profissional/mês | Teleconsulta, TISS, assinatura, WhatsApp     | Entrar por médico solo e pequenas clínicas.                                 |
| Vision      |                                                       R$49/câmera/mês | Alertas, retenção, IA por evento             | Começar com câmeras IP existentes e processamento sob demanda.              |
| Legal       |                                                      R$49/usuário/mês | Prazos, documentos, assinatura e BI          | Entrar em escritórios pequenos com importação de planilhas.                 |
| Property    |                                            R$79/mês ou R$0,80/unidade | Boletos, chamados, vistoria e assinatura     | Entrar em imobiliárias e condomínios pequenos.                              |
| BI          |                             Grátis até 2 dashboards; R$39/usuário/mês | Embed, conectores e relatórios premium       | Entregar dashboards nativos por módulo antes de vender BI isolado.          |
| AI Core     |                                               Custo do provedor + 15% | Agentes, moderação, resumo e classificação   | Usar providers sob demanda, cache e limites por plano.                      |

## 7 ESTRATÉGIA DE ENTRADA NO MERCADO

### 7.1 Posicionamento

O All-in-One deve entrar como uma suíte modular para PMEs brasileiras que hoje dependem de várias ferramentas desconectadas: ERP, CRM, loja virtual, delivery, jobs, documentos, financeiro e BI. A mensagem comercial central deve ser: "uma operação inteira, por módulos, com preço menor que contratar ferramentas separadas".

### 7.2 Tática de aquisição com custo próximo de zero

- Lançar beta fechado por cidade/nicho com 20 a 50 empresas reais.
- Oferecer setup gratuito em troca de depoimento, métricas e autorização de case.
- Criar conteúdo comparativo de custo: "quanto sua empresa paga empilhando ERP + CRM + loja + delivery".
- Usar WhatsApp, comunidades locais, contadores, associações comerciais e coworkings como canais gratuitos.
- Priorizar PMEs com dor clara: restaurante com taxa alta, loja online com ERP caro, clínica pequena, prestador local e empresa contratando por planilha.
- Criar programa de indicação: cliente indica cliente e ganha 2 meses de módulo Pro.
- Fazer migração assistida de planilhas, CSV e cadastros como oferta de entrada.
- Evitar mídia paga no início; investir esforço em SEO, vídeos curtos, demonstrações gravadas e parcerias.

### 7.3 Ordem comercial recomendada

1. CRM + Business + Identity: menor risco regulatório, implantação rápida e ROI visível.
2. Marketplace + Stock + Delivery próprio: captura receita transacional e diferencia por taxa menor.
3. Jobs + HR: alto apelo para PMEs e boa diferenciação com CTPS/cofre/auditoria.
4. Health e Legal: entrar com cuidado por dados sensíveis e compliance.
5. Finance completo, Mobility e Vision: só escalar após sandbox, antifraude, segurança e parceiros.

### 7.4 Estratégia contra concorrentes

Contra ERPs e CRMs tradicionais, vender integração nativa entre módulos, preço menor e ausência de implantação pesada. Contra marketplaces e delivery, vender take rate menor e autonomia do lojista. Contra healthtechs e ATS consultivos, vender preço público, rápido onboarding e pacote para pequenas operações. Contra big techs de IA, vender governança, custo previsível e integração aos dados operacionais do cliente.

### 7.5 Estratégia de Custo Zero para Entrada

Para cada módulo, a estratégia de entrada com custo zero de marketing foca em:

- **Identity/Business:** Parceria com Juntas Comerciais e Contadores (onboarding nativo).
- **Finance:** Cashback de transação para cobrir mensalidade (receita transacional paga o SaaS).
- **Jobs:** Integração com currículos universitários e centros de tecnologia.
- **Health:** Modelo freemium para médicos residentes e pequenas clínicas de bairro.
- **Marketplace/Delivery:** "Taxa Zero" nos primeiros 90 dias para lojistas que migrarem do iFood/Nuvemshop.

## 8 RISCOS E BLOQUEADORES

Os principais riscos técnicos são integrações externas, compliance LGPD, segurança de dados sensíveis, maturidade dos apps, testes E2E e observabilidade. Os principais riscos comerciais são subprecificação sem controle de custo, tentar atacar todos os mercados ao mesmo tempo, competir diretamente com plataformas gigantes em aquisição paga e assumir responsabilidades regulatórias antes de homologar parceiros.

A mitigação recomendada é lançar por módulos de baixo risco, manter limites de uso no freemium, cobrar por transação onde há valor claro, usar provedores homologados em vez de internalizar serviços regulados e medir CAC, churn, margem por módulo e tempo de implantação desde o beta.

## 9 CONCLUSÃO

O All-in-One está tecnicamente avançado como plataforma backend modular, com contratos completos, runtime saudável, infraestrutura local estável e base de dados em expansão. O percentual consolidado de maturidade técnica pode ser estimado em aproximadamente 62%, com backend e infraestrutura acima da média do conjunto e apps/integrações/compliance ainda abaixo do necessário para produção.

Para entrar no mercado com força e baixo custo, a recomendação é transformar a modularidade em vantagem comercial: começar com CRM, Business, Marketplace, Delivery próprio, Jobs e Health Starter, oferecendo preços públicos 20% menores que alternativas nacionais, onboarding simples e migração gratuita. A produção ampla deve aguardar gates de CI, E2E, segurança, LGPD, provedores reais e observabilidade.

## REFERÊNCIAS

BLING. Alteração nos planos e preços do Bling em abril de 2026. Disponível em: https://ajuda.bling.com.br/hc/pt-br/articles/30224184866583-Altera%C3%A7%C3%A3o-nos-planos-e-pre%C3%A7os-do-Bling-em-abril-de-2026. Acesso em: 30 maio 2026.

CONTA AZUL. Planos e Preços Conta Azul para um Sistema de Gestão Completo. Disponível em: https://contaazul.com/planos. Acesso em: 30 maio 2026.

FEEGOW. Preços e Planos. Disponível em: https://feegowclinic.com.br/precos-e-planos. Acesso em: 30 maio 2026.

IFOOD. Taxas do iFood: entenda planos, comissão e taxa de serviço para restaurantes. Disponível em: https://blog-parceiros.ifood.com.br/taxas-ifood/. Acesso em: 30 maio 2026.

ICLINIC. Planos e preços. Disponível em: https://lps.iclinic.com.br/planos-e-precos/. Acesso em: 30 maio 2026.

LOGGI. Fretes baratos, rápidos e envios para todo o Brasil. Disponível em: https://www.loggi.com/enviar-agora-v2/. Acesso em: 30 maio 2026.

NUVEMSHOP. Planos e preços da Nuvemshop. Disponível em: https://www.nuvemshop.com.br/planos-e-precos. Acesso em: 30 maio 2026.

RD STATION. Planos e preços do RD Station CRM. Disponível em: https://www.rdstation.com/precos-crm/. Acesso em: 30 maio 2026.

UBER. Preços da Uber para Empresas. Disponível em: https://www.uber.com/br/pt-br/business/platform/pricing/. Acesso em: 30 maio 2026.

YAMPI. Planos Yampi. Disponível em: https://www.yampi.com.br/planos. Acesso em: 30 maio 2026.
