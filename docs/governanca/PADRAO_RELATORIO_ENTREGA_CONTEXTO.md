# Padrão de Relatório de Entrega de Contexto

**Versão:** 1.1.0  
**Data:** 30/07/2026  
**Fuso:** `America/Sao_Paulo`  
**Classificação:** `Apresentações > Conceitual`  
**Público-alvo:** Pessoa Física (B2C), Pessoa Jurídica (B2B) e Equipe Técnica

## Objetivo

Padronizar o encerramento de todas as atividades do projeto All in One + Valley, deixando claro o que foi solicitado, o que foi realmente concluído, o que continua pendente, por que continua pendente e como resolver.

## Estrutura obrigatória

### 1. Atividade

Explicar, em linguagem simples, qual foi o objetivo da atividade e qual escopo foi trabalhado.

### 2. Entregue

Listar apenas itens efetivamente concluídos e comprovados por código, teste, publicação, validação, evidência ou documentação aplicável.

### 3. Não entregue

Listar tudo que permaneceu pendente. Quando não houver pendência, declarar expressamente: `Nenhum item permaneceu não entregue.`

### 4. O que não foi entregue e por quê

Explicar a causa concreta de cada pendência, identificando nominalmente bloqueios como:

- ausência de credencial;
- acesso externo indisponível;
- DNS;
- billing;
- IAM;
- aprovação legal ou comercial;
- dependência técnica;
- workflow ainda em execução ou falho;
- ferramenta sem permissão para concluir a ação.

### 5. Como resolver

Apresentar a solução recomendada para cada item pendente, sem linguagem vaga e sem transferir decisões técnicas que o agente consiga tomar sozinho.

### 6. Passo a passo detalhado

Numerar as ações em ordem de execução. Cada etapa deve informar de forma simples:

1. qual site, aplicativo, arquivo ou sistema abrir;
2. qual menu selecionar;
3. qual botão pressionar;
4. qual campo preencher;
5. qual valor usar, quando seguro e aplicável;
6. como salvar;
7. como validar que a etapa funcionou;
8. o que fazer se aparecer erro.

### 7. Links exatos de acesso

Sempre fornecer a URL completa e direta de qualquer site, painel, sistema, repositório, issue, pull request, documentação ou ferramenta necessária.

Regras:

- não informar apenas o nome do site quando o endereço puder ser fornecido;
- conferir o link antes da entrega quando a ferramenta permitir;
- quando não houver URL interna permanente, fornecer o endereço principal e o caminho exato dos menus;
- nunca incluir tokens, credenciais ou segredos na URL;
- links de GitHub devem apontar diretamente para a issue, PR, commit, workflow ou arquivo relevante quando conhecidos.

## Modelo obrigatório

```markdown
# Relatório de Entrega de Contexto

## Atividade
[Objetivo e escopo executado.]

## Entregue
[Resultados concluídos e comprovados.]

## Não entregue
[Itens pendentes ou declaração de ausência de pendências.]

## O que não foi entregue e por quê
[Causa concreta de cada pendência.]

## Como resolver
[Solução recomendada para cada pendência.]

## Passo a passo detalhado
1. [Primeira ação.]
2. [Segunda ação.]
3. [Validação final.]

## Links exatos de acesso
- [Nome e finalidade]: https://endereco-completo.example/
```

## Critério de verdade

Código criado, plano, documento, commit isolado ou tela desenhada não comprovam por si só uma entrega funcional. A seção `Entregue` deve refletir somente o que estiver confirmado no ambiente correto.

## Fonte versionada

A política técnica autoritativa está em:

`config/autonomy/delivery_context_report_policy.json`
