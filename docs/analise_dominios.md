# Análise e Mapeamento de Domínios (Fase 1.2)

**Referência:** `docs/MEMORANDO_MESTRE_GEMINI_VARREDURA_DADOS_FORMULARIOS_ALL_IN_ONE.md`

Este documento estabelece a correspondência entre os 25 domínios oficiais do projeto, identificados no diretório `contracts/`, e o mapa de domínios funcional sugerido no memorando mestre. O objetivo é consolidar a visão do ecossistema e guiar a análise de dados subsequente.

## Tabela de Correspondência de Domínios

| Domínio Oficial (`contracts/`) | Domínios Funcionais Sugeridos no Memorando | Observações |
| :--- | :--- | :--- |
| `ai_core` | Inteligência Artificial, Analytics, Vision | Centraliza as capacidades de IA, incluindo machine learning, análise preditiva e processamento de visão. |
| `api_hub` | Eventos, Notificações, API Gateway | Responsável pela orquestração de eventos, distribuição de notificações e gerenciamento central de APIs. |
| `bi` | Relatórios, Analytics, Dashboards | Focado em Business Intelligence, geração de relatórios consolidados e visualização de dados. |
| `bpm` | Orquestração Helena, BPM, Workflows | Modela e executa processos de negócio, incluindo a orquestração de tarefas humanas e de sistema. |
| `business` | Empresas, Administração Interna, Grupos Econômicos | Gerencia a estrutura de entidades jurídicas, suas configurações e hierarquias dentro do sistema. |
| `crm` | CRM, Atendimento, Suporte, Vendas (parcial) | Abrange o relacionamento com o cliente, incluindo suporte, funil de vendas e interações. |
| `delivery` | Delivery, Entregas | Especializado na logística de entrega de produtos. |
| `document` | Documentos, Mídia | Gerencia o ciclo de vida de documentos e arquivos de mídia, incluindo armazenamento e versionamento. |
| `erp` | ERP, Compras, Vendas, Contabilidade, Fiscal | Núcleo de gestão empresarial, integrando operações de compra, venda, contábeis e fiscais. |
| `finance` | Financeiro, Pagamentos, Wallet, Escrow, Faturamento, Cobrança, Assinaturas, Planos | Domínio central para todas as operações financeiras, transações, carteiras digitais e faturamento. |
| `health` | Health, Agenda (Saúde) | Módulo especializado para a área da saúde, gerenciando dados de pacientes, agendamentos e prontuários. |
| `hr` | RH, Folha, Benefícios | Gestão de Recursos Humanos, incluindo dados de colaboradores, folha de pagamento e benefícios. |
| `identity` | Identidade, Usuários, Perfis, Autenticação, Consentimentos | Gerencia a identidade digital única, perfis, autenticação e consentimentos de usuários. |
| `jobs` | Jobs, Currículos, CTPS | Focado no mercado de trabalho, gerenciando vagas, candidaturas e informações profissionais. |
| `legal` | Compliance, Privacidade, Termos, Contratos | Domínio responsável pelos aspectos legais, conformidade, privacidade de dados e contratos. |
| `marketplace` | Marketplace, Pedidos (parcial) | Plataforma de marketplace, conectando compradores e vendedores e gerenciando o fluxo de pedidos. |
| `mobility` | Mobility, Transporte de Passageiros | Especializado em serviços de mobilidade e transporte de pessoas. |
| `permissions`| Autorização, RBAC, ABAC, Segurança | Controla o acesso a recursos e funcionalidades através de políticas de permissão. |
| `property` | Imóveis, Ativos Físicos | Domínio para gestão de propriedades e ativos imobiliários ou físicos. Não listado explicitamente no memorando funcional. |
| `riders` | Riders, Entregadores | Gerencia o cadastro e as operações de entregadores e motoristas parceiros. |
| `services` | Serviços, Planos de Serviço | Catálogo e gestão de serviços oferecidos na plataforma. |
| `stock` | Estoque, Catálogo, Produtos | Responsável pelo controle de inventário, catálogo de produtos e seus atributos. |
| `tms` | TMS (Transportation Management System) | Sistema de Gerenciamento de Transporte, complementa os domínios `delivery` e `mobility`. |
| `vision` | Vision (Computer Vision) | Subdomínio de `ai_core` para funcionalidades de visão computacional. |
| `wms` | WMS (Warehouse Management System) | Sistema de Gerenciamento de Armazém, complementa o domínio `stock`. |

## Domínios Funcionais Transversais

Alguns conceitos listados no memorando são transversais e atendidos por múltiplos domínios oficiais:

- **Segurança:** Atendido por `identity` (autenticação) e `permissions` (autorização).
- **Auditoria, Logs e Observabilidade:** Capacidades que devem ser implementadas em todos os domínios, com possível centralização de logs em `api_hub` ou `bi`.
- **Configurações:** Cada domínio possui suas próprias configurações, com um possível módulo de administração central.
- **Homologação e Compliance:** Processos que envolvem `bpm` para o fluxo e `legal` para as diretrizes.
