# VS Code Workspace Policy (All-in-One)

Este workspace adota o modo `custo zero` com foco em desenvolvimento local.

## Stack Prioritario (ativo no core)

- Python (`.venv`, pytest, ruff, pylance)
- Web/Node (TypeScript/JavaScript, ESLint, Prettier)
- Docker e validacoes do repositorio
- YAML, GitHub Actions e ferramentas de governanca do projeto

## Stack Opcional (desativado por padrao)

- Java/Kotlin/Android

Essas configuracoes foram removidas do `settings.json` principal para evitar
indexacao, consumo de memoria e ruido no dia a dia de quem trabalha no core.

## Como reativar Java/Kotlin para frente mobile

1. Instale extensoes opcionais quando precisar:
   - `vscjava.vscode-java-pack`
   - `fwcd.kotlin`

2. Copie as configuracoes de exemplo para seu ambiente local:

```bash
cp .vscode/settings.mobile.example.json .vscode/settings.mobile.local.json
```

3. Ajuste `java.jdt.ls.java.home` para o caminho real do JDK na sua maquina.

4. Se quiser usar essas configuracoes sem afetar o time, aplique-as apenas no
   seu `User Settings` do VS Code ou mantenha o arquivo local fora de commit.

## Observacao

O arquivo `settings.mobile.example.json` e apenas referencia e nao altera o
comportamento do workspace enquanto nao for aplicado manualmente.
