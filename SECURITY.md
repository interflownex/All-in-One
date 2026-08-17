# Política de Segurança

> **Regra fundamental ARKHE | AIO:** proteção de segredos e separação entre conteúdo público e privado têm precedência sobre conveniência, velocidade de publicação ou automação.

A segurança do All-in-One é responsabilidade contínua e compartilhada.

## Regra 01 — nada sensível no repositório público

É proibido publicar, commitar, anexar a issues, PRs ou discussões públicas qualquer material que revele ou permita inferir acesso operacional, incluindo:

- senhas, tokens, chaves API, chaves privadas, certificados, cookies de sessão ou credenciais;
- arquivos `.env`, configurações locais e variáveis de ambiente com valores reais;
- identificadores de cloud, contas de serviço, projetos, tenants, endpoints internos ou topologia operacional;
- dados pessoais, documentos, informações de clientes, parceiros ou colaboradores;
- implementação proprietária, contratos internos, regras antifraude, mecanismos de autorização e critérios privados de liberação;
- comentários, logs, dumps, artefatos, screenshots ou exemplos que contenham material sensível;
- detalhes privados de All-in-One, Valley, Valley Riders, Stitch, Flutter, infraestrutura, CI/CD ou ambientes internos.

No conteúdo público, use apenas placeholders neutros e documentação sanitizada.

## Regra 02 — repositório privado não é cofre de segredos

O repositório privado pode conter implementação e documentação interna, mas **não deve armazenar credenciais reais versionadas**. Segredos de runtime devem residir em secret managers, variáveis protegidas do ambiente ou mecanismos equivalentes. Arquivos versionados devem conter referências ou placeholders.

Qualquer segredo encontrado no histórico deve ser tratado como potencialmente comprometido e submetido a rotação/revogação conforme o sistema de origem.

## Regra 03 — publicação é um processo de promoção

Material privado só pode chegar ao repositório público após revisão específica de publicação. Não deve existir sincronização automática irrestrita entre os repositórios.

Antes de publicar:

1. confirmar o repositório e branch de destino;
2. revisar arquivos adicionados e removidos;
3. executar os gates de confidencialidade;
4. remover dados operacionais e substituir valores por placeholders;
5. revisar diff e CI por PR;
6. publicar apenas conteúdo explicitamente classificado como público.

## Como relatar uma vulnerabilidade

Não divulgue vulnerabilidades, provas de conceito, credenciais ou detalhes técnicos sensíveis em issues públicas, discussões ou pull requests.

Inclua somente as informações necessárias para avaliação, sem dados pessoais ou credenciais.

## Escopo deste repositório

Este repositório contém somente material aprovado para divulgação pública. Código-fonte privado, infraestrutura, contratos internos e documentação operacional permanecem fora dele.

A ausência de um componente neste repositório não significa que ele esteja fora do programa de segurança do projeto.

## Boa-fé

Pesquisadores que atuem de boa-fé, evitem acesso indevido, minimizem coleta de dados e respeitem divulgação coordenada serão tratados com seriedade e respeito.

Esta política não autoriza testes destrutivos, engenharia social, indisponibilidade de serviços, acesso a contas de terceiros ou extração de dados.
