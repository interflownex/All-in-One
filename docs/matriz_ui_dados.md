# Matriz de UI de Dados (Análise de Frontend)

**Referência:** `docs/plano_de_leitura.md`, Ordem 4

Este documento mapeia a utilização dos campos de dados nos componentes de interface do usuário (UI), como formulários, listas e tabelas. A análise é baseada nos arquivos de componentes encontrados em `apps/all-in-one/src/pages/`.

O objetivo é criar uma rastreabilidade entre o modelo de dados lógico e sua representação visual, identificando quais campos são apresentados ao usuário, quais são editáveis e quais são usados para filtragem.

---

## 1. Domínio: Identity

### 1.1 Entidade: User

#### **Componente de Lista: `pages/identity/UsersList.tsx`**

- **Campos Exibidos na Tabela:**
  - `full_name`
  - `email`
  - `status`
  - `created_at`
- **Ações Disponíveis:** Editar, Detalhes
- **Filtros:**
  - `status`

#### **Componente de Formulário: `pages/identity/UsersForm.tsx`**

- **Campos para Criação/Edição:**
  - `full_name` (Input Text)
  - `email` (Input Email)
  - `cpf_document` (Input Text com Máscara)
  - `birth_date` (Input Date)
  - `phone_e164` (Input Text com Máscara)
  - `password` (Input Password, apenas na criação)
  - `status` (Select/Dropdown)

### 1.2 Entidade: Document

#### **Componente de Lista: `pages/identity/DocumentsList.tsx`**

- **Campos Exibidos na Tabela:** A ser definido
- **Ações Disponíveis:** A ser definido
- **Filtros:** A ser definido

#### **Componente de Formulário: `pages/identity/DocumentsForm.tsx`**

- **Campos para Criação/Edição:** A ser definido

---

_(Nota: Esta matriz será preenchida progressivamente com a análise de cada um dos componentes de UI identificados no arquivo `App.tsx`.)_
