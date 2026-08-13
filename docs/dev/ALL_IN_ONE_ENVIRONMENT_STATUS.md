# All-in-One Environment Status

Date: 2026-08-12

## VS Code / Profile

- `code` exists at `/home/eretazan/.local/bin/code`.
- `code --version` reports `1.129.1`.
- `code --list-extensions --show-versions` fails with: `No installation of Visual Studio Code stable was found.`
- The `all_in_one` profile cannot be verified from this shell because the stable VS Code installation is not detectable by the CLI.

## Workspace Settings

- `~/.config/Code/User/settings.json` currently contains only:
  - `python.terminal.useEnvFile: true`
- `~/.config/Code/User/mcp.json` exists and configures:
  - `MCP_DOCKER`
  - `context7`
  - `cloudflare-docs`
  - `cloudflare-api`
  - `datacloud_bigquery_toolbox`
  - `datacloud_spanner_toolbox`
  - `datacloud_alloydb-postgres-admin_toolbox`
  - `datacloud_alloydb-postgres_toolbox`
  - `datacloud_cloud-sql-postgresql-admin_toolbox`
  - `datacloud_cloud-sql-postgresql_toolbox`
  - `datacloud_knowledge_catalog_toolbox`
  - `datacloud_dataproc_toolbox`
  - `datacloud_serverless-spark_toolbox`

## CLIs

- `az` available at `/home/eretazan/.local/bin/az` and verified with `az version`.
- `azd` available at `/home/eretazan/.local/bin/azd` and verified with `azd version`.
- `git`, `python3`, `java`, `javac`, `flutter`, and `docker` are present.

## Extension Cache

Verified installed in `~/.vscode-server/extensions`:

- `openai.chatgpt-26.727.40816-linux-x64`
- `openai.chatgpt-26.803.61601-linux-x64`
- `feiskyer.chatgpt-copilot-4.11.0`
- `ms-azuretools.azure-dev-0.10.0`
- `ms-azuretools.vscode-azure-mcp-server-2.0.46-linux-x64`
- `ms-azuretools.vscode-azureappservice-0.27.0`
- `ms-azuretools.vscode-azurecontainerapps-0.11.2`
- `ms-azuretools.vscode-azurefunctions-1.22.0`
- `ms-azuretools.vscode-azureresourcegroups-0.12.7`
- `ms-azuretools.vscode-azurestaticwebapps-0.13.3`
- `ms-azuretools.vscode-azurestorage-0.17.2`
- `ms-azuretools.vscode-azurevirtualmachines-0.6.11`
- `ms-azuretools.vscode-azure-github-copilot-1.0.231-linux-x64`
- `ms-azuretools.vscode-cosmosdb-0.36.0`
- `ms-azuretools.vscode-containers-2.4.5`
- `ms-vscode.azure-repos-0.40.0`
- `ms-vscode.remote-repositories-0.42.0`
- `ms-vscode.powershell-2025.4.0`
- `github.codespaces-1.18.15`
- `github.remotehub-0.64.0`
- `github.vscode-github-actions-0.32.3`
- `github.vscode-pull-request-github-0.162.0`
- `googlecloudtools.cloudcode-2.40.0`
- `googlecloudtools.datacloud-0.7.2`
- `googlecloudtools.datacloud-0.8.1`
- `docker.docker-0.18.0-linux-x64`
- `dart-code.dart-code-3.140.0`
- `dart-code.flutter-3.140.0`
- `ms-python.python-2026.4.0-linux-x64`
- `ms-python.vscode-pylance-2026.3.1`
- `ms-python.debugpy-2026.6.0-linux-x64`
- `ms-python.vscode-python-envs-1.36.0-linux-x64`
- `ms-python.mypy-type-checker-2026.6.0`
- `ms-toolsai.jupyter-2025.9.1-linux-x64`
- `ms-toolsai.jupyter-keymap-1.1.2`
- `ms-toolsai.jupyter-renderers-1.3.0`
- `ms-toolsai.vscode-jupyter-cell-tags-0.1.9`
- `ms-toolsai.vscode-jupyter-slideshow-0.1.6`
- `ms-ossdata.vscode-pgsql-1.28.0-linux-x64`
- `supabase.vscode-supabase-extension-0.0.13`
- `ms-kubernetes-tools.vscode-kubernetes-tools-1.4.1`
- `redhat.vscode-yaml-1.24.0`
- `redhat.java-1.55.0-linux-x64`
- `rust-lang.rust-analyzer-0.3.2997-linux-x64`
- `rust-lang.rust-analyzer-0.3.3008-linux-x64`
- `dbaeumer.vscode-eslint-3.0.34`
- `esbenp.prettier-vscode-12.4.0`
- `davidanson.vscode-markdownlint-0.62.1`

## Status Summary

- Profile `all_in_one`: not verifiable from CLI in this shell.
- Azure MCP server extension: installed.
- Azure CLI tooling: installed locally in user scope.
- Azure Developer CLI tooling: installed locally in user scope.
- Codex extension bundle: not found in the server extension cache by name.
