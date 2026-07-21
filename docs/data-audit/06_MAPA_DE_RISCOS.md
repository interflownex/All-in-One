# Mapa de Riscos de Alto Nível

Este documento resume as principais categorias de risco identificadas na fase de idealização do projeto de varredura de dados, com base na análise dos documentos `SECURITY.md`, `COMPLIANCE.md` e outras fontes de arquitetura.

Este mapa não é exaustivo, mas serve como ponto de partida para a análise detalhada nas próximas fases.

## 1. Risco de Acesso Indevido a Dados

Risco de que usuários ou sistemas acessem dados para os quais não têm autorização.

- **Descrição:** Inclui tanto a "escalada de privilégios vertical" (um usuário comum acessando funções de administrador) quanto a "quebra de isolamento horizontal" (um usuário acessando dados de outro usuário no mesmo nível).
- **Controles Identificados:**
    - **Autenticação Forte:** Identidade única, MFA obrigatório para ações sensíveis, e provedores externos para KYC/KYB.
    - **Autorização Robusta (RBAC/ABAC):** O módulo `permissions` implementa um controle de acesso baseado em papéis e atributos.
    - **Papéis de Sistema Privilegiados:** Definições explícitas de papéis como `SENSITIVE_ROLES`, `MEDICAL_ROLES`, e `APPROVER_ROLES` em `modules/shared/domain_rules.py`.
    - **Revisão de Permissões:** O arquivo `config/security/sensitive_permissions_review.json` formaliza a política de acesso a dados sensíveis, adotando um modelo *deny-by-default*.
    - **API Gateway:** O API Hub valida tokens (JWT) e escopos antes de encaminhar requisições para os módulos internos.

## 2. Risco de Não Conformidade (LGPD)

Risco de violar a Lei Geral de Proteção de Dados, resultando em multas, sanções e danos à reputação.

- **Descrição:** Abrange o tratamento inadequado de dados pessoais, falha em atender aos direitos dos titulares e retenção de dados além do necessário.
- **Controles Identificados:**
    - **Mapeamento e Classificação de Dados:** O arquivo `config/compliance/data_classification.json` classifica os dados de todos os 25 módulos.
    - **Gestão de Direitos do Titular:** Um fluxo de trabalho definido em `config/compliance/data_subject_rights.json` para lidar com solicitações de acesso, correção, exclusão, etc.
    - **Política de Retenção:** Jobs e políticas definidas em `config/compliance/retention_jobs.json` e implementadas no worker `retention_worker` para anonimizar ou descartar dados de forma segura.
    - **Minimização de Dados:** O princípio é aplicado em todo o sistema, com payloads de eventos minimizados e acesso restrito por padrão.

## 3. Risco de Perda de Integridade Financeira e de Auditoria

Risco de que transações financeiras ou registros de auditoria sejam alterados, perdidos ou corrompidos.

- **Descrição:** Erros em cálculos, estornos indevidos, ou a incapacidade de provar que uma determinada ação ocorreu.
- **Controles Identificados:**
    - **Ledger e Logs Append-Only:** Tabelas de `ledger` (financeiro) e `audit` (auditoria) são projetadas para serem somente de inserção (append-only), com triggers de banco de dados para garantir a imutabilidade.
    - **Separação de Funções (Segregation of Duties):** Ações críticas (ex: aprovações, liberações de pagamento) exigem papéis específicos (`APPROVER_ROLES`).
    - **Idempotência:** Chaves de idempotência são usadas em transações financeiras e criação de eventos para prevenir duplicidade.

## 4. Risco de Vulnerabilidades de Segurança na Aplicação

Risco de que falhas no código (web, mobile, backend) sejam exploradas por atacantes.

- **Descrição:** Inclui vulnerabilidades como Injeção de SQL, XSS, CSRF, e falhas em dependências.
- **Controles Identificados:**
    - **Pipeline de Segurança (CI/CD):** O workflow `.github/workflows/security.yml` automatiza a verificação de segurança com ferramentas SAST (CodeQL, Bandit), SCA (pip-audit, npm audit) e DAST (OWASP ZAP).
    - **Segurança Mobile (MASVS-R):** O aplicativo Android possui defesas contra engenharia reversa, depuração e execução em ambientes não seguros (root), com validação complementar no backend via Play Integrity API.
    - **Pentest Obrigatório:** A documentação estipula a necessidade de testes de invasão manuais antes de lançamentos públicos significativos.

## 5. Risco Operacional e de Negócio

Risco de que o sistema permita ações que violem as regras de negócio ou causem prejuízo.

- **Descrição:** Inclui a publicação de conteúdo indevido, comunicação com clientes fora da plataforma, erros de precificação, etc.
- **Controles Identificados:**
    - **Política Anti-Burla:** O sistema bloqueia ativamente a inserção de contatos (WhatsApp, e-mail) e links em campos de conteúdo gerado pelo usuário (`OFF_PLATFORM_PATTERNS`).
    - **Fluxos de Aprovação:** Processos de negócio críticos, como o cadastro de empresas (`business.companies`) ou a publicação de produtos (`marketplace.products`), passam por fluxos de revisão e aprovação com papéis designados.
    - **Validação de Backend:** A lógica de negócio e as validações são sempre executadas no backend, tratando o frontend como uma interface não confiável.
