# Diretrizes técnicas e operação

Este documento apresenta uma visão pública das regras de domínio, integridade, execução e organização técnica do All-in-One + Valley.

O código-fonte completo, os segredos, as credenciais e os detalhes internos de infraestrutura permanecem no repositório privado.

## Diretriz de domínio `brasildesconto.com.br`

Toda alteração que envolva `brasildesconto.com.br` deve seguir o contrato versionado em:

```text
config/autonomy/brasildesconto_domain_policy.json
```

A operação do domínio segue estas regras:

- automação priorizada por Terraform;
- sincronização com Cloudflare;
- validações obrigatórias de DNS;
- validação de HTTPS;
- validação de CORS;
- validação de headers;
- validação de cache;
- validação de logs;
- validação de monitoramento;
- proibição de segredos no Git.

O gate abaixo verifica o contrato automaticamente antes da sincronização:

```bash
python3 scripts/validate_repository.py
```

## Identidade e integridade

`identity.users.id` é o vínculo central dos recursos de domínio.

Wallets, cartões NFC/LED, perfis Rider e escrows usam foreign keys compostas para impedir que uma operação referencie a wallet de outro usuário.

Recursos financeiros e logs de auditoria rejeitam operações de `UPDATE` e `DELETE`.

## Execução local

```bash
python -m pip install -r requirements-dev.txt
python scripts/scaffold_modules.py --check
python scripts/validate_repository.py
python -m pytest --import-mode=importlib
docker compose -f infra/docker/docker-compose.yml up --build
```

### Exemplo isolado

```bash
cd modules/identity
pip install -r requirements.txt
uvicorn main:app --port 8000
```

## Organização

| Caminho | Conteúdo |
|---|---|
| `apps/` | Contratos das seis experiências cliente |
| `modules/` | Microserviços funcionais e testes |
| `contracts/` | Contratos de domínio espelhados e versionáveis |
| `database/` | Migrações PostgreSQL e validações MongoDB |
| `docs/` | Arquitetura, segurança, eventos, operação e roadmap |
| `infra/` | Docker, Kubernetes e Terraform inicial |
| `workers/` | Dispatchers e consumidores assíncronos da plataforma |
| `.github/workflows/` | Gates e automações de entrega |

## Estado

O motor de domínio torna todos os módulos inicializáveis e testáveis.

Integrações reguladas ou externas permanecem bloqueadas para produção até que existam credenciais, homologação, DPIA/LGPD e testes E2E documentados.

Isso inclui:

- Pix e cartões;
- fiscal oficial;
- biometria;
- assinatura;
- OCR;
- IA produtiva;
- hospitais;
- GPS de concessionárias.

A referência de evolução e liberação permanece documentada em:

```text
docs/ROADMAP.md
```

## Segurança de publicação

Este documento não contém:

- credenciais;
- tokens;
- chaves privadas;
- segredos de infraestrutura;
- dados pessoais;
- detalhes operacionais sensíveis.

As referências de caminhos indicam contratos e estruturas da implementação privada, sem expor seus conteúdos internos.