# ARKHE | AIO — Fundação e Governança

Esta estrutura governa o ecossistema sem misturar superfícies públicas e privadas.

## Estrutura

```text
ARKHE | AIO
│
├── 00 · Fundação e Governança
├── 01 · AIO Público
│   ├── README
│   ├── ROADMAP
│   ├── CHANGELOG
│   └── Publicação e narrativa
├── 02 · All-in-One
├── 03 · Valley
├── 04 · Valley Riders
├── 05 · Arquitetura
├── 06 · Segurança e Saneamento
├── 07 · GitHub e CI/CD
├── 08 · Roadmaps
├── 09 · Releases
└── 10 · Decisões Arquiteturais
```

## 00 · Fundação e Governança

A Regra 01 é invariável: nenhum dado privado, segredo, credencial, token, chave API, chave de ambiente, comentário sensível, identificador operacional ou informação interna pode ser publicado.

## 01 · AIO Público

Este repositório é a superfície pública. Ele contém apenas narrativa, documentação, roadmap e changelog aprovados para divulgação.

## 02–04 · Produtos privados

All-in-One, Valley e Valley Riders permanecem em desenvolvimento privado. O repositório público não é espelho desses ambientes.

## 05 · Arquitetura

A arquitetura pública descreve conceitos e capacidades. Topologia, fornecedores, endpoints, identificadores, contratos internos e detalhes de implantação permanecem privados.

## 06 · Segurança e Saneamento

Toda publicação passa por saneamento automático e revisão humana. Segredos reais não devem ser versionados nem no repositório privado; runtime usa secret store/secret manager ou equivalente.

## 07 · GitHub e CI/CD

Mudanças públicas devem ocorrer por branch e PR. Gates de confidencialidade bloqueiam caminhos sensíveis e padrões de credenciais. Não há sincronização automática irrestrita do privado para o público.

## 08–10 · Planejamento, releases e decisões

Roadmaps públicos expõem direção, não dependências privadas. Releases públicas contêm apenas fatos aprovados para divulgação. Decisões arquiteturais completas permanecem privadas; somente versões sanitizadas podem ser promovidas.

## Critério de promoção para público

Um artefato só é publicável quando:

1. está explicitamente classificado como público;
2. não contém segredo, dado pessoal ou informação operacional;
3. não permite reconstruir acesso, topologia ou implementação proprietária;
4. passou pelos gates de CI de confidencialidade;
5. foi revisado em diff antes do merge.
