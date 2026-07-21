# Mapa de Personas e Papéis

Este documento descreve as personas e os papéis (roles) que governam o acesso e as permissões dentro do ecossistema All-in-One + Valley. A análise baseia-se no "MEMORANDO MESTRE", na estrutura do banco de dados do módulo `permissions` e nas regras de negócio definidas em `modules/shared/domain_rules.py`.

## Modelo de Permissões: Uma Abordagem Híbrida

O sistema utiliza um modelo híbrido:

1.  **Papéis de Sistema (System Roles):** Um conjunto de papéis fixos com privilégios elevados ou responsabilidades transversais (cross-cutting). Estes papéis são definidos diretamente no código (ex: `modules/shared/domain_rules.py`) e são usados para controlar o acesso a dados sensíveis e ações críticas, como aprovações.
2.  **Papéis Dinâmicos (Dynamic Roles):** O sistema fornece uma interface de gerenciamento (`/permissions/roles`) que permite a criação de papéis customizados no escopo de uma empresa (`business.companies`). Estes são referidos como `BUSINESS_MEMBERSHIP_ROLES` e permitem um controle de acesso granular dentro de cada organização.

## Papéis de Sistema Identificados

Os seguintes papéis de sistema foram identificados no código-fonte, principalmente no arquivo `modules/shared/domain_rules.py`.

| Papel (Role) | Propósito Inferido e Capacidades |
| :--- | :--- |
| `owner` | O mais alto nível de privilégio. Provavelmente o "dono" de uma empresa ou tenant. Tem acesso a dados sensíveis e pode aprovar/escrever permissões. |
| `administrator` | Papel administrativo com amplos privilégios, incluindo acesso a dados sensíveis, aprovações e gerenciamento de membros da empresa. |
| `legal_representative` | Representante Legal de uma empresa. Um tipo de aprovador. |
| `compliance_officer` | Responsável pela conformidade. Tem acesso a dados sensíveis e é um aprovador em fluxos críticos. |
| `data_protection_officer`| Papel focado em privacidade e proteção de dados (LGPD), com acesso a dados sensíveis. |
| `auditor` | Papel de auditoria, com acesso de leitura a dados sensíveis para fins de revisão e verificação. |
| `hr_manager` | Gerente de RH, com acesso a dados do módulo `jobs` (currículos). |
| `recruiter` | Recrutador, com acesso a dados do módulo `jobs`. |
| `medical_admin` | Administrador de uma unidade de saúde. |
| `doctor` | Médico, com acesso a dados de saúde. |
| `nurse` | Enfermeiro(a), com acesso a dados de saúde. |

### Papéis de Sistema (Google Cloud IAM)
Os seguintes identificadores são papéis do Google Cloud IAM, usados para autorizar serviços e não representam usuários da aplicação:
- `roles/apihub.admin`
- `roles/apihub.runtimeProjectServiceAgent`
- `roles/cloudkms.cryptoKeyEncrypterDecrypter`

## Papéis Dinâmicos (Business Membership Roles)

Estes papéis são criados dinamicamente para gerenciar membros de uma empresa. A lista abaixo representa os papéis *sugeridos* ou *padrão* para um novo negócio:

- `owner`
- `administrator`
- `finance_manager`
- `hr_manager`
- `operations_manager`
- `recruiter`
- `store_manager`
- `viewer`

## Mapeamento de Personas Conceituais para Papéis

A tabela a seguir mapeia as personas descritas no memorando para os papéis de sistema ou para a categoria de papéis dinâmicos.

| Persona (Memorando) | Papel Implementado (Provável) | Tipo | Notas |
| :--- | :--- | :--- | :--- |
| **administrador da plataforma** | `owner` ou `administrator` (global) | Sistema | Papel com os mais altos privilégios no sistema. |
| **administrador do tenant** | `owner` ou `administrator` | Sistema | Papel com altos privilégios no escopo de um tenant/empresa. |
| **administrador da empresa** | `administrator` | Sistema / Dinâmico | Gerencia uma empresa específica. |
| **gestor** | `operations_manager`, `store_manager` | Dinâmico | Papel de gerenciamento, provavelmente customizável. |
| **auditor** | `auditor` | Sistema | Acesso de leitura para fins de auditoria. |
| **homologador** | `compliance_officer` ou `administrator` | Sistema | Responsável por aprovar novos fluxos, formulários, etc. |
| **suporte** | `administrator` (limitado) ou papel dinâmico | Dinâmico | Acesso para resolver problemas de clientes. |
| **usuário pessoa física** | `N/A` | Conceito | Representa o usuário final sem papel específico. |
| **consumidor** | `N/A` | Conceito | Papel base de um usuário autenticado que consome serviços. |
| **trabalhador** / **candidato** | `N/A` (associado a `jobs.resumes`) | Conceito | Usuário interagindo com o módulo de `jobs`. |
| **prestador de serviço** | `N/A` (associado a `services.providers`)| Conceito | Usuário que oferece serviços na plataforma. |
| **entregador** | `rider_profiles` | Conceito | Usuário do módulo `riders`. |
| **motorista** | `rider_profiles` | Conceito | Usuário do módulo `mobility`. |
| **profissional de saúde** | `doctor`, `nurse` | Sistema | Papéis com acesso a dados médicos. |
| **operador** / **caixa** | Papel dinâmico customizado | Dinâmico | Funções operacionais dentro de uma empresa. |
| **vendedor** | Papel dinâmico customizado | Dinâmico | Função de vendas dentro de uma empresa. |
| **comprador** | Papel dinâmico customizado | Dinâmico | Função de compras dentro de uma empresa. |
| **estoquista** | Papel dinâmico customizado | Dinâmico | Função de gerenciamento de estoque. |
| **fiscal** / **contador** | `finance_manager` ou papel dinâmico | Dinâmico | Acesso a dados financeiros e fiscais. |
| **financeiro** | `finance_manager` | Dinâmico | Gerente financeiro de uma empresa. |
| **RH** | `hr_manager`, `recruiter` | Sistema / Dinâmico | Papéis relacionados à gestão de recursos humanos. |
| **integração externa** | `api_clients` (API Key) | Sistema | Acesso via API, não um usuário humano. |
| **serviço automatizado**| `api_clients` (API Key) | Sistema | Acesso via API para automações. |
| **agente de IA** | `api_clients` (API Key) | Sistema | Acesso via API para o agente de IA. |

Este mapa servirá de base para a análise de permissões em cada campo e operação do sistema.
