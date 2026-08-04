# Configuração persistente do Cloudflare Pages

## Classificação

- Projeto: All in One + Valley
- Pasta lógica: Pendências
- Assunto: Técnico
- Público-alvo: Equipe Técnica
- Componente: `apps/all-in-one`
- Workflow: `.github/workflows/cloudflare-pages.yml`

## Regra de ativação

O deploy de produção somente é executado quando a GitHub Actions Variable abaixo estiver definida:

```text
ENABLE_CLOUDFLARE_PAGES=true
```

Sem a ativação explícita, o job permanece `skipped`. Quando ativado, qualquer configuração ausente é bloqueante.

## Configuração obrigatória

### GitHub Actions Variables

```text
ENABLE_CLOUDFLARE_PAGES=true
VITE_API_HUB_URL=https://endpoint-api-hub-autorizado
```

### GitHub Actions Secrets

```text
CLOUDFLARE_API_TOKEN
CLOUDFLARE_ACCOUNT_ID
```

### GitHub Environment

```text
cloudflare-pages-production
```

## Segurança

- usar token específico com privilégio mínimo para Pages;
- não utilizar Global API Key;
- não gravar token, account ID sensível ou credenciais em arquivos;
- proteger o environment de produção;
- manter HTTPS obrigatório na API e no endereço publicado;
- rotacionar imediatamente qualquer segredo exposto;
- validar domínio customizado, DNS e TLS somente com evidência da conta Cloudflare.

## Processo executável

1. validar secrets e variables;
2. executar checkout com `actions/checkout@v6`;
3. instalar dependências com `npm ci`;
4. executar testes existentes;
5. gerar build de produção;
6. validar `dist/index.html` e o marcador oficial;
7. publicar com `cloudflare/wrangler-action@v4` e Wrangler fixado;
8. exigir URL HTTPS retornada;
9. consultar a URL com repetição controlada;
10. confirmar o marcador oficial no conteúdo publicado;
11. encaminhar evidência por Telegram apenas quando os secrets opcionais estiverem presentes.

## Limite de confirmação

A presença do workflow comprova a preparação do repositório. Ela não comprova ativação da conta, domínio customizado, DNS, TLS ou deploy concluído. Esses pontos permanecem `conditional` até execução verde e evidência na issue #215.
