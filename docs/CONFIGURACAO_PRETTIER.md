# Guia de Configuração e Uso do Prettier

Este documento descreve como instalar, configurar e utilizar o **Prettier** como o formatador padrão para arquivos Web (HTML, CSS, JS, TS) e de configuração (JSON, YAML, Markdown) no projeto **All-in-One**.

## 1. Instalação

### Pré-requisitos
- Node.js (v18 ou superior)
- npm ou yarn

### Instalação no Projeto
Para garantir que todos usem a mesma versão, o Prettier deve ser instalado como uma dependência de desenvolvimento:

```bash
npm install --save-dev --save-exact prettier
```

## 2. Configuração do Projeto

O projeto já possui um arquivo `.prettierrc` na raiz com as definições oficiais de estilo:

```json
{
  "semi": true,
  "trailingComma": "all",
  "singleQuote": false,
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "endOfLine": "lf"
}
```

### Arquivos Ignorados
Crie um arquivo `.prettierignore` para evitar a formatação de artefatos de build ou dependências:

```text
node_modules
dist
build
.venv
__pycache__
*.sqlite3
```

## 3. Integração com VS Code

Para uma experiência automatizada, siga estas etapas:

1.  Instale a extensão: **Prettier - Code formatter** (`esbenp.prettier-vscode`).
2.  O arquivo `.vscode/settings.json` já está configurado para usar o Prettier como formatador padrão:
    - `"editor.defaultFormatter": "esbenp.prettier-vscode"`
    - `"editor.formatOnSave": true`

## 4. Uso via Linha de Comando (CLI)

Você pode formatar todos os arquivos suportados manualmente:

```bash
# Verificar arquivos (sem alterar)
npx prettier . --check

# Formatar e salvar alterações
npx prettier . --write
```

## 5. Boas Práticas e Restrições

- **Não utilize outros estilizadores:** Conforme definido no `GEMINI.md`, ferramentas como `delegua.estilizador` são proibidas.
- **Formatação no Commit:** O Prettier é executado automaticamente em arquivos Web antes do deploy/sincronização.
- **Conflitos:** Em caso de conflito com o `EditorConfig`, o Prettier possui precedência para as regras de estilo que ele gerencia.

---
*Este documento é parte integrante das diretrizes de engenharia do All-in-One.*
