# All-in-One Extension Inventory

Date: 2026-08-12

## Verified Installed

| Name | ID | Version | Status | Notes |
| --- | --- | --- | --- | --- |
| ChatGPT | `openai.chatgpt` | `26.803.61601-linux-x64` | Installed | Present in server cache. |
| ChatGPT | `openai.chatgpt` | `26.727.40816-linux-x64` | Quarantined | Moved to `~/.vscode-server/extensions.disabled/` to avoid duplicate builds. |
| ChatGPT Copilot | `feiskyer.chatgpt-copilot` | `4.11.0` | Installed | Available locally. |
| Azure Developer CLI | `ms-azuretools.azure-dev` | `0.10.0` | Installed | Present in server cache. |
| Azure MCP Server | `ms-azuretools.vscode-azure-mcp-server` | `2.0.46-linux-x64` | Installed | Present in server cache. |
| Azure App Service | `ms-azuretools.vscode-azureappservice` | `0.27.0` | Installed | Present in server cache. |
| Azure Container Apps | `ms-azuretools.vscode-azurecontainerapps` | `0.11.2` | Installed | Present in server cache. |
| Azure Functions | `ms-azuretools.vscode-azurefunctions` | `1.22.0` | Installed | Present in server cache. |
| Azure Resource Groups | `ms-azuretools.vscode-azureresourcegroups` | `0.12.7` | Installed | Present in server cache. |
| Azure Static Web Apps | `ms-azuretools.vscode-azurestaticwebapps` | `0.13.3` | Installed | Present in server cache. |
| Azure Storage | `ms-azuretools.vscode-azurestorage` | `0.17.2` | Installed | Present in server cache. |
| Azure Virtual Machines | `ms-azuretools.vscode-azurevirtualmachines` | `0.6.11` | Installed | Present in server cache. |
| Azure GitHub Copilot | `ms-azuretools.vscode-azure-github-copilot` | `1.0.231-linux-x64` | Installed | Present in server cache. |
| Azure Cosmos DB | `ms-azuretools.vscode-cosmosdb` | `0.36.0` | Installed | Present in server cache. |
| Azure Containers | `ms-azuretools.vscode-containers` | `2.4.5` | Installed | Present in server cache. |
| GitHub Codespaces | `github.codespaces` | `1.18.15` | Installed | Present in server cache. |
| GitHub RemoteHub | `github.remotehub` | `0.64.0` | Installed | Present in server cache. |
| GitHub Actions | `github.vscode-github-actions` | `0.32.3` | Installed | Present in server cache. |
| GitHub Pull Requests | `github.vscode-pull-request-github` | `0.162.0` | Installed | Present in server cache. |
| Azure Repos | `ms-vscode.azure-repos` | `0.40.0` | Installed | Present in server cache. |
| Remote Repositories | `ms-vscode.remote-repositories` | `0.42.0` | Installed | Present in server cache. |
| Google Cloud Code | `googlecloudtools.cloudcode` | `2.40.0` | Installed | Present in server cache. |
| Google Cloud Data Cloud | `googlecloudtools.datacloud` | `0.8.1` | Installed | Present in server cache. |
| Docker | `docker.docker` | `0.18.0-linux-x64` | Installed | Present in server cache. |
| Flutter | `dart-code.flutter` | `3.140.0` | Installed | Present in server cache. |
| Dart | `dart-code.dart-code` | `3.140.0` | Installed | Present in server cache. |
| Python | `ms-python.python` | `2026.4.0-linux-x64` | Installed | Present in server cache. |
| Pylance | `ms-python.vscode-pylance` | `2026.3.1` | Installed | Present in server cache. |
| Python Env Tools | `ms-python.vscode-python-envs` | `1.36.0-linux-x64` | Installed | Present in server cache. |
| Jupyter | `ms-toolsai.jupyter` | `2025.9.1-linux-x64` | Installed | Present in server cache. |
| PostgreSQL | `ms-ossdata.vscode-pgsql` | `1.28.0-linux-x64` | Installed | Present in server cache. |
| Supabase | `supabase.vscode-supabase-extension` | `0.0.13` | Installed | Present in server cache. |
| Kubernetes | `ms-kubernetes-tools.vscode-kubernetes-tools` | `1.4.1` | Installed | Present in server cache. |
| YAML | `redhat.vscode-yaml` | `1.24.0` | Installed | Present in server cache. |
| Java | `redhat.java` | `1.55.0-linux-x64` | Installed | Present in server cache. |
| Rust Analyzer | `rust-lang.rust-analyzer` | `0.3.3008-linux-x64` | Installed | Present in server cache. |
| ESLint | `dbaeumer.vscode-eslint` | `3.0.34` | Installed | Present in server cache. |
| Prettier | `esbenp.prettier-vscode` | `12.4.0` | Installed | Present in server cache. |
| Markdownlint | `davidanson.vscode-markdownlint` | `0.62.1` | Installed | Present in server cache. |
| PowerShell | `ms-vscode.powershell` | `2025.4.0` | Installed | Present in server cache. |

## Requested But Not Verified As Installed

| Name | ID | Status | Notes |
| --- | --- | --- | --- |
| Codex - OpenAI coding agent | `unknown` | Not found | No `codex`-named extension dir found in the server cache. |
| Antigravity for VS Code | `unknown` | Not verified | Not found in the local cache snapshot. |
| Azure Tools | `unknown` | Partial | Azure sub-extensions are installed, but no single umbrella package was verified. |
| Google Cloud Data Agent Kit | `unknown` | Partial | `googlecloudtools.datacloud` extensions are installed, but the exact requested package name was not verified. |
| GitHub Copilot for Azure | `ms-azuretools.vscode-azure-github-copilot` | Installed | Present and likely satisfies the requested capability. |

## Audit Notes

- Verification is based on `~/.vscode-server/extensions`.
- The `code` CLI could not enumerate stable VS Code extensions from this shell, so profile-level installation could not be confirmed.
- This inventory should be refreshed from the real VS Code profile once the stable client is reachable.
