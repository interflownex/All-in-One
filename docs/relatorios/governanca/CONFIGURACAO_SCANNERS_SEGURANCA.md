# Configuração persistente dos scanners de segurança

## Classificação

- Projeto: All in One + Valley
- Pasta lógica: Pendências
- Assunto: Técnico
- Público-alvo: Equipe Técnica
- Status: configuração de workflows implantada; integrações comerciais externas condicionais

## Princípio obrigatório

Um scanner externo só pode ser habilitado quando sua contratação, credenciais e alvo estiverem completos. Quando habilitado, ausência de qualquer pré-requisito deve falhar o workflow. Quando não contratado, o job permanece `skipped`, sem produzir falso marcador vermelho.

## Mayhem for API

Variável de ativação:

- `ENABLE_MAYHEM=true`

Variáveis obrigatórias:

- `MAYHEM_API_URL`
- `MAYHEM_API_SPEC`

Segredo obrigatório:

- `MAYHEM_TOKEN`

O alvo deve ser um ambiente de staging autorizado. Não apontar fuzzing para produção sem janela, limite e aprovação operacional.

## Fortify

Variável de ativação:

- `ENABLE_FORTIFY=true`

Variável opcional:

- `FOD_URL`, com padrão `https://ams.fortify.com`

Autenticação aceita:

1. `FOD_CLIENT_ID` e `FOD_CLIENT_SECRET`; ou
2. `FOD_TENANT`, `FOD_USER` e `FOD_PAT`.

O workflow exige espera do resultado, verificação de política, resumo do job e exportação de achados.

## Debricked

Variável de ativação:

- `ENABLE_DEBRICKED=true`

Segredo obrigatório:

- `DEBRICKED_TOKEN`

## Scanners locais obrigatórios

Os seguintes controles não dependem de contratação externa e permanecem ativos:

- CI principal e testes;
- gate regulatório F0.1;
- Security workflow;
- Docker Compose Health Gate;
- OSV-Scanner;
- CodeQL para Actions, Java/Kotlin, JavaScript/TypeScript, Python e Rust.

## Gestão de segredos

- nunca gravar tokens no repositório;
- utilizar GitHub Actions Secrets para credenciais;
- utilizar GitHub Actions Variables para flags e URLs não sigilosas;
- rotacionar imediatamente qualquer segredo exposto;
- manter menor privilégio e escopo por ambiente;
- registrar ativação e desativação em issue ou pull request.

## Critério de conclusão

A integração externa só muda de `conditional` para `implemented` após evidência de:

1. credencial válida;
2. alvo autorizado e acessível;
3. execução concluída;
4. resultado armazenado;
5. política de bloqueio definida;
6. responsável operacional identificado.
