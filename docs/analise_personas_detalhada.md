# Análise Detalhada de Personas, Permissões e Contextos (Fase 1.3)

**Referência:** `docs/MEMORANDO_MESTRE_GEMINI_VARREDURA_DADOS_FORMULARIOS_ALL_IN_ONE.md`, `docs/data-audit/03_MAPA_DE_PERSONAS.md`, `config/security/permissions_enforcement_matrix.json`

Este documento detalha as capacidades de cada persona principal do sistema, com base na análise dos papéis (roles) e políticas de acesso (access policies) definidos nos artefatos do projeto.

---

## 1. Administrador da Plataforma / Tenant (Owner)

-   **Papéis Associados:** `owner` (Sistema)
-   **Dados Acessíveis:**
    -   Acesso de leitura a todos os recursos do módulo `permissions` (`roles`, `permissions`, `user_roles`, `access_policies`, `approval_limits`).
    -   Acesso de leitura a todos os recursos sensíveis dos módulos `identity`, `finance`, `document`, e `hr`.
    -   Acesso irrestrito aos demais módulos (implícito pelo `deny_by_default: false` para o `owner`).
-   **Dados Editáveis:**
    -   Acesso de escrita a todos os recursos do módulo `permissions`.
    -   Pode gerenciar os limites de aprovação (`approval_limits`), exigindo MFA.
-   **Ações Permitidas:**
    -   Gerenciar papéis e permissões.
    -   Conceder e revogar acesso.
    -   Definir e modificar políticas de acesso.
    -   Gerenciar limites de aprovação financeira.
-   **Limites e Aprovações:** Exige autenticação multifator (MFA) para alterar `approval_limits`.
-   **Trilha de Auditoria:** Todas as ações de escrita geram eventos de auditoria.
-   **Segregação de Funções:** Concentra os maiores privilégios. O risco é mitigado pela exigência de MFA para ações críticas e pela trilha de auditoria.
-   **Riscos:** Potencial máximo para abuso de privilégios. Uma conta comprometida de `owner` representa o maior risco para a plataforma.

---

## 2. Administrador de Empresa (Administrator)

-   **Papéis Associados:** `administrator` (Sistema / Dinâmico)
-   **Dados Acessíveis:**
    -   Similar ao `owner`, possui acesso de leitura aos recursos do módulo `permissions` e aos dados sensíveis dos principais domínios.
-   **Dados Editáveis:**
    -   Possui acesso de escrita aos recursos do módulo `permissions`, incluindo a criação de papéis dinâmicos para a empresa.
-   **Ações Permitidas:**
    -   Gerenciar usuários e papéis dentro do escopo de sua empresa.
    -   Configurar políticas de acesso para sua empresa.
-   **Limites e Aprovações:** Também necessita de MFA para gerenciar `approval_limits`.
-   **Trilha de Auditoria:** Todas as ações de escrita são auditadas.
-   **Segregação de Funções:** Atua como o principal gestor de uma empresa, mas não tem o poder global de um `owner` de plataforma.
-   **Riscos:** Comprometimento de conta pode levar ao controle total de uma empresa, mas não de todo o sistema.

---

## 3. Auditor e Compliance

-   **Papéis Associados:** `auditor`, `compliance_officer`, `data_protection_officer` (Sistema)
-   **Dados Acessíveis:**
    -   Acesso de **leitura** a todos os recursos do módulo `permissions`.
    -   Acesso de **leitura** a todos os recursos sensíveis (`identity`, `finance`, `document`, `hr`, `jobs`, `health`).
-   **Dados Editáveis:**
    -   `auditor` e `data_protection_officer` **não possuem permissão de escrita** no módulo `permissions`, garantindo a segregação de funções.
    -   `compliance_officer` possui permissão de escrita, indicando um papel híbrido de auditoria e configuração.
-   **Ações Permitidas:**
    -   Visualizar todas as configurações de permissão, políticas e logs.
    -   Verificar a conformidade das operações.
    -   (`compliance_officer`): Aprovar e configurar políticas.
-   **Trilha de Auditoria:** O acesso a dados sensíveis por estes papéis deve gerar logs de auditoria de leitura (conforme seção 11.2 do memorando).
-   **Segregação de Funções:** O papel de `auditor` é estritamente de leitura, o que é uma prática de segurança fundamental.
-   **Riscos:** Risco de vazamento de informações, já que possuem acesso de leitura a uma vasta gama de dados sensíveis. O controle de acesso e a auditoria de leitura são mitigações cruciais.

---

## 4. Gestor de RH e Recrutador

-   **Papéis Associados:** `hr_manager`, `recruiter` (Sistema / Dinâmico)
-   **Dados Acessíveis:**
    -   Acesso especializado aos recursos sensíveis do módulo `jobs` (`resumes`, `applications`, etc.), conforme a regra `RECRUITER_ROLES`.
    -   `hr_manager` provavelmente possui acesso também aos recursos do módulo `hr` (`employees`, `payroll_runs`).
-   **Dados Editáveis:** A matriz de permissões não especifica escrita, mas é implícito que possam gerenciar vagas e candidaturas dentro do módulo `jobs`.
-   **Ações Permitidas:**
    -   Publicar vagas.
    -   Analisar currículos e candidaturas.
    -   Gerenciar o processo seletivo.
-   **Mascaramento:** Dados pessoais de candidatos não diretamente relevantes para a vaga devem ser mascarados.
-   **Riscos:** Vazamento de dados pessoais de candidatos. O acesso deve ser estritamente limitado ao contexto de recrutamento.

---

## 5. Profissional de Saúde

-   **Papéis Associados:** `medical_admin`, `doctor`, `nurse` (Sistema)
-   **Dados Acessíveis:**
    -   Acesso especializado e restrito aos recursos sensíveis do módulo `health` (`patients`, `medical_records`, etc.), conforme a regra `MEDICAL_ROLES`.
-   **Dados Editáveis:** Apenas os profissionais de saúde envolvidos no atendimento do paciente podem editar o prontuário.
-   **Ações Permitidas:**
    -   Visualizar e atualizar prontuários de pacientes sob seus cuidados.
    -   Agendar consultas e procedimentos.
    -   Prescrever medicamentos.
-   **Trilha de Auditoria:** O acesso a prontuários é uma ação de altíssima sensibilidade e deve gerar logs de auditoria de leitura detalhados.
-   **Segregação de Funções:** Acesso estritamente segregado por paciente e por nível de permissão (médico vs. enfermeiro vs. administrativo).
-   **Riscos:** O maior risco é o vazamento de dados de saúde (dados sensíveis por definição legal). A criptografia e a auditoria rigorosa são mandatórias.

---

## 6. Personas Operacionais (Vendedor, Estoquista, etc.)

-   **Papéis Associados:** Papéis dinâmicos customizados (e.g., `store_manager`, `vendedor`).
-   **Dados Acessíveis:** O acesso é definido dinamicamente pelas `access_policies` criadas pelo `administrator` da empresa. O acesso a dados sensíveis de outros domínios é negado por padrão (`deny_by_default`).
-   **Ações Permitidas:**
    -   **Vendedor:** Criar pedidos, consultar produtos e clientes.
    -   **Estoquista:** Gerenciar movimentações de estoque, consultar saldos.
    -   **Caixa:** Processar pagamentos.
-   **Conclusão:** Essas personas não possuem papéis fixos no sistema, refletindo a flexibilidade do modelo de permissões dinâmicas. A segurança depende da configuração correta das políticas de acesso por parte dos administradores de cada empresa.
