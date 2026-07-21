# MEMORANDO MESTRE DE VARREDURA EXAUSTIVA DE DADOS, FORMULÁRIOS E TEMPLATES

## Projeto All-in-One + Valley

### Diretriz mandatória para execução pelo Gemini e demais IAs desenvolvedoras

**Classificação:** Documento técnico interno e mandatório
**Projeto:** All-in-One + Valley
**Destinatário principal:** Gemini
**Destinatários complementares:** Codex, Stitch, agentes de arquitetura, banco de dados, backend, frontend, segurança, qualidade e documentação
**Idioma obrigatório dos artefatos funcionais:** Português do Brasil
**Documento de ordem operacional:** `docs/EXECUTION_PLAN.md`
**Princípio de cobertura:** trabalhar pelo excesso de análise, nunca pela falta
**Status:** orientação para idealização, planejamento, construção, validação, documentação e geração de templates frontend

---

# 1. ORDEM EXECUTIVA

O Gemini deverá realizar uma varredura completa, minuciosa, rastreável e comprovável de todo o ecossistema All-in-One + Valley.

A análise não poderá se limitar aos bancos de dados já implementados, às tabelas existentes ou aos campos atualmente visíveis nos formulários. A missão é identificar:

1. tudo o que já existe;
2. tudo o que está parcialmente implementado;
3. tudo o que está declarado apenas em documentação;
4. tudo o que está implícito no código, nos fluxos, nas APIs, nos eventos e nas regras de negócio;
5. tudo o que será necessário para evitar futuras alterações destrutivas, retrabalho de banco, duplicação de dados, quebra de contratos, formulários incompletos ou migrações emergenciais;
6. todas as possibilidades realistas de uso de cada módulo;
7. os campos, relacionamentos, cálculos, validações, auditorias, permissões, unidades, tributos, estados e exceções necessários a cada operação.

A entrega somente poderá ser considerada concluída quando houver evidência de cobertura de todos os módulos, bancos, schemas, tabelas, coleções, views, índices, constraints, campos, documentos, eventos, endpoints, formulários, relatórios, filtros, importações, exportações, integrações e registros de auditoria.

A expressão “não localizado” não encerra a análise. Sempre que algo não for localizado, o Gemini deverá:

- procurar em outras camadas do projeto;
- comparar código, documentação, testes, migrations, DTOs, APIs, telas e eventos;
- registrar a lacuna;
- propor a estrutura necessária;
- indicar o risco de manter a lacuna;
- criar a coordenada de implementação;
- vincular a pendência a um módulo, responsável técnico sugerido e critério de aceite.

---

# 2. OBJETIVO PRINCIPAL

Produzir um inventário definitivo e utilizável do modelo de dados do ecossistema, descrevendo, para cada estrutura:

- banco de dados;
- finalidade;
- tecnologia;
- schema ou namespace;
- tabela, coleção, view ou estrutura equivalente;
- campo;
- nome técnico;
- nome funcional em português do Brasil;
- descrição;
- finalidade;
- origem;
- destino;
- tipo de dado;
- tamanho;
- precisão;
- escala;
- formato;
- máscara;
- obrigatoriedade;
- valor padrão;
- domínio de valores;
- enumerações;
- exemplos válidos;
- exemplos inválidos;
- regras de validação;
- regra de cálculo;
- unidade de medida;
- regra de conversão;
- tratamento tributário;
- relacionamento;
- chave primária;
- chave estrangeira;
- índice;
- unicidade;
- sensibilidade;
- classificação LGPD;
- criptografia;
- mascaramento;
- retenção;
- versionamento;
- histórico;
- auditoria;
- rastreabilidade;
- controle de acesso;
- comportamento no backend;
- comportamento no frontend;
- comportamento em APIs;
- comportamento em eventos;
- comportamento em importações e exportações;
- tratamento de erro;
- impacto em relatórios;
- impacto em integrações;
- impacto em cálculos;
- impacto financeiro, fiscal ou operacional;
- condição para criação;
- condição para alteração;
- condição para exclusão lógica;
- condição para arquivamento;
- condição para restauração.

A partir desse inventário, o Gemini deverá gerar também um memorando de coordenadas para os formulários, dashboards, tabelas, filtros, telas de detalhe, assistentes de cadastro e templates que deverão ser construídos no frontend e orientados ao Stitch.

---

# 3. PRINCÍPIOS NÃO NEGOCIÁVEIS

## 3.1 Cobertura antes de velocidade

Nenhum módulo poderá ser documentado superficialmente para acelerar a entrega. Campos genéricos como `metadata`, `extra`, `payload`, `details`, `data` ou JSON livre não poderão ser usados como depósito indiscriminado para requisitos ainda não modelados.

Campos flexíveis somente serão aceitos quando:

- houver justificativa arquitetural;
- houver schema de validação;
- houver versionamento;
- houver definição de proprietário;
- houver limite claro de uso;
- houver indexação planejada quando necessária;
- houver política de migração;
- houver documentação das chaves permitidas;
- não substituírem dados estruturados essenciais.

## 3.2 Fonte única de verdade

Cada dado deve possuir uma fonte oficial de verdade.

O Gemini deverá marcar explicitamente:

- onde o dado nasce;
- qual serviço é proprietário;
- quais serviços podem ler;
- quais serviços podem alterar;
- quais serviços apenas replicam;
- como ocorre a sincronização;
- qual evento comunica a alteração;
- como conflitos são resolvidos;
- como inconsistências são detectadas;
- como o dado é reconciliado.

## 3.3 Compatibilidade com arquitetura modular

O All-in-One + Valley é um ecossistema modular. O modelo de dados deverá respeitar:

- isolamento por domínio;
- contratos explícitos;
- baixo acoplamento;
- integração por APIs e eventos;
- identidade única All-in-One ID;
- multiempresa;
- multitenancy;
- perfis pessoais e empresariais;
- RBAC e ABAC;
- auditoria;
- outbox;
- idempotência;
- mensageria;
- rastreabilidade ponta a ponta.

## 3.4 Nenhuma operação sem auditoria adequada

Toda criação, alteração, aprovação, rejeição, homologação, publicação, cancelamento, reversão, exclusão lógica, restauração, importação, exportação, cálculo, configuração e mudança de permissão deverá gerar rastreabilidade.

## 3.5 Português do Brasil no frontend

Os identificadores técnicos poderão permanecer em inglês quando isso for padrão de engenharia, mas todo rótulo, ajuda, mensagem, validação, descrição e conteúdo destinado ao usuário deverá ser produzido em português do Brasil.

Termos estrangeiros já incorporados ao uso brasileiro, como dashboard, login, marketplace e workflow, poderão ser mantidos quando fizerem sentido. Sempre preferir clareza e consistência.

## 3.6 Nenhum botão morto

Todo elemento interativo descrito para os templates deverá possuir:

- ação;
- permissão;
- estado habilitado;
- estado desabilitado;
- estado de carregamento;
- retorno de sucesso;
- retorno de erro;
- log;
- teste;
- destino funcional.

---

# 4. ESCOPO DE VARREDURA

O Gemini deverá percorrer todo o repositório e todos os artefatos vinculados ao projeto.

## 4.1 Fontes obrigatórias

Varrer, no mínimo:

- `README.md`;
- `STATUS.md`;
- `docs/ROADMAP.md`;
- `docs/EXECUTION_PLAN.md`;
- RFCs;
- ADRs;
- documentação de arquitetura;
- documentação de segurança;
- documentação de UI/UX;
- migrations SQL;
- models ORM;
- schemas Pydantic, Zod, Joi ou equivalentes;
- entidades de domínio;
- value objects;
- DTOs;
- commands;
- queries;
- handlers;
- repositories;
- services;
- controllers;
- rotas;
- OpenAPI;
- GraphQL schemas, se houver;
- protobufs, se houver;
- eventos;
- consumers;
- producers;
- filas;
- tópicos;
- outbox;
- jobs agendados;
- seeds;
- fixtures;
- testes unitários;
- testes de integração;
- testes E2E;
- mocks;
- adaptadores;
- integrações;
- configurações;
- variáveis de ambiente;
- Docker;
- Kubernetes;
- Terraform ou equivalente;
- workflows GitHub Actions;
- aplicativos web;
- aplicativos mobile;
- aplicativos desktop;
- templates Stitch;
- contratos de UI;
- componentes;
- formulários;
- tabelas;
- filtros;
- relatórios;
- dashboards;
- arquivos de tradução;
- regras de autorização;
- políticas de acesso;
- logs;
- observabilidade;
- arquivos de importação;
- exportações;
- armazenamento de objetos;
- documentos PDF;
- imagens;
- anexos;
- arquivos fiscais;
- catálogos;
- integrações externas;
- contratos de sandbox;
- feature flags;
- configurações por tenant;
- configurações por empresa;
- configurações por módulo.

## 4.2 Bancos e tecnologias

Documentar todos os mecanismos de persistência encontrados ou previstos, incluindo:

- PostgreSQL;
- MongoDB;
- Redis;
- armazenamento de objetos;
- filas e persistência de mensageria;
- índices de busca;
- cache;
- armazenamento local web;
- armazenamento local mobile;
- cofres criptográficos;
- data lake;
- data warehouse;
- mecanismos analíticos;
- event store;
- logs estruturados;
- catálogos de configuração;
- arquivos temporários;
- sessões;
- tokens;
- backups;
- réplicas;
- materialized views.

Para cada tecnologia, explicar por que ela existe, quais dados armazena, qual é o proprietário, qual é a política de retenção e qual é o mecanismo de recuperação.

---

# 5. FASES OBRIGATÓRIAS

A execução seguirá exatamente estas seis fases:

1. **IDEALIZAR**
2. **PLANEJAR**
3. **CONSTRUIR**
4. **VALIDAR**
5. **DOCUMENTAR**
6. **ORIENTAR TEMPLATE FRONTEND IA STITCH**

Nenhuma fase poderá ser eliminada. Nenhuma construção deverá começar sem inventário e planejamento mínimos. Nenhuma documentação poderá ser considerada final sem validação.

---

# 6. FASE 1 — IDEALIZAR

## 6.1 Compreensão do ecossistema

O Gemini deverá formar uma visão integral do All-in-One + Valley como SuperApp modular, organizado para permitir que uma identidade única atue nas capacidades de:

- transacionar;
- trabalhar;
- consumir serviços;
- administrar empresas;
- operar módulos especializados;
- integrar dados, pagamentos, documentos, pessoas, produtos, serviços e processos.

## 6.2 Mapa de domínios

Criar um mapa oficial de domínios, incluindo os módulos existentes e os módulos previstos.

Considerar, no mínimo:

- Identidade;
- Usuários;
- Empresas;
- Perfis;
- Autenticação;
- Autorização;
- RBAC;
- ABAC;
- Marketplace;
- Catálogo;
- Produtos;
- Serviços;
- Estoque;
- Compras;
- Vendas;
- Pedidos;
- Pagamentos;
- Wallet;
- Escrow;
- Faturamento;
- Fiscal;
- Financeiro;
- Contabilidade;
- ERP;
- CRM;
- RH;
- Jobs;
- Currículos;
- CTPS;
- Delivery;
- Riders;
- Mobility;
- Health;
- Agenda;
- Notificações;
- Documentos;
- Mídia;
- Atendimento;
- Suporte;
- Assinaturas;
- Planos;
- Cobrança;
- Configurações;
- Auditoria;
- Eventos;
- Observabilidade;
- Relatórios;
- Analytics;
- Inteligência artificial;
- Orquestração Helena;
- Administração interna;
- Homologação;
- Compliance;
- Privacidade;
- Segurança.

Se o projeto possuir 25 domínios oficiais, produzir uma correspondência entre os 25 domínios atuais e o mapa acima. Não criar domínios redundantes sem justificativa.

## 6.3 Personas e contextos

Mapear as personas que criam, consultam ou alteram dados:

- usuário pessoa física;
- consumidor;
- trabalhador;
- candidato;
- prestador de serviço;
- entregador;
- motorista;
- profissional de saúde;
- operador;
- caixa;
- vendedor;
- comprador;
- estoquista;
- fiscal;
- contador;
- financeiro;
- RH;
- gestor;
- administrador da empresa;
- administrador do tenant;
- suporte;
- auditor;
- homologador;
- administrador da plataforma;
- integração externa;
- serviço automatizado;
- agente de IA.

Para cada persona, documentar:

- dados acessíveis;
- dados editáveis;
- ações permitidas;
- limites;
- aprovações necessárias;
- trilha de auditoria;
- mascaramento;
- segregação de funções;
- riscos.

## 6.4 Eventos de negócio

Antes de definir tabelas, listar os eventos relevantes de cada domínio.

Exemplos:

- usuário criado;
- identidade verificada;
- empresa cadastrada;
- módulo ativado;
- produto criado;
- variante criada;
- unidade convertida;
- preço alterado;
- estoque movimentado;
- lote recebido;
- pedido confirmado;
- pagamento autorizado;
- pagamento recusado;
- carteira debitada;
- escrow reservado;
- nota fiscal emitida;
- formulário criado;
- formulário submetido;
- formulário homologado;
- formulário publicado;
- formulário alterado;
- configuração modificada;
- permissão concedida;
- permissão revogada;
- documento enviado;
- documento validado;
- dado sensível acessado.

Para cada evento, definir:

- nome;
- versão;
- produtor;
- consumidores;
- payload;
- dados proibidos no payload;
- chave de idempotência;
- correlação;
- causação;
- timestamp;
- tenant;
- usuário;
- origem;
- retenção;
- tratamento de falha;
- replay;
- compatibilidade retroativa.

---

# 7. FASE 2 — PLANEJAR

## 7.1 Plano de leitura

Criar uma matriz com:

| Ordem | Área           | Caminhos analisados                           | Evidências esperadas      | Resultado           |
| ----: | -------------- | --------------------------------------------- | ------------------------- | ------------------- |
|     1 | Documentação   | README, STATUS, ROADMAP, EXECUTION_PLAN, RFCs | escopo e ordem mandatória | mapa inicial        |
|     2 | Banco          | migrations, schemas, models                   | estruturas físicas        | catálogo físico     |
|     3 | Backend        | entidades, DTOs, APIs, eventos                | contratos e regras        | catálogo lógico     |
|     4 | Frontend       | telas, forms, filtros, tabelas                | campos usados             | matriz UI x dados   |
|     5 | Segurança      | auth, RBAC, criptografia, logs                | restrições                | matriz de proteção  |
|     6 | Testes         | unitários, integração, E2E                    | comportamento comprovado  | evidências          |
|     7 | Infraestrutura | Docker, Kubernetes, CI/CD                     | ambientes e dependências  | mapa operacional    |
|     8 | Lacunas        | comparação cruzada                            | inconsistências           | backlog obrigatório |

## 7.2 Estratégia de comparação

O Gemini deverá comparar:

- documentação x código;
- migration x ORM;
- ORM x API;
- API x formulário;
- formulário x validação;
- validação x regra de negócio;
- evento x modelo;
- teste x implementação;
- permissão x endpoint;
- campo sensível x criptografia;
- campo fiscal x cálculo;
- campo monetário x precisão;
- unidade de estoque x unidade comercial;
- exclusão lógica x consultas;
- tenant x isolamento;
- auditoria x alterações;
- frontend x backend;
- configuração declarada x configuração aplicada.

Toda divergência deverá gerar item no Registro de Lacunas.

## 7.3 Critérios de prioridade

Classificar pendências como:

- **P0 Bloqueante:** risco de perda de dados, falha de segurança, cálculo financeiro/fiscal incorreto, ausência de isolamento, quebra de integridade.
- **P1 Crítica:** funcionalidade central incompleta, formulário sem dados necessários, ausência de auditoria, integração inconsistente.
- **P2 Alta:** experiência incompleta, relatório insuficiente, validação parcial, automação ausente.
- **P3 Média:** melhoria de usabilidade, otimização, padronização.
- **P4 Baixa:** refinamento estético ou melhoria não bloqueante.

## 7.4 Proibição de decisões silenciosas

Toda decisão estrutural deverá ser registrada em ADR ou memorando equivalente.

Exemplos:

- escolha de PostgreSQL ou MongoDB;
- modelagem relacional ou documental;
- uso de enum ou tabela de domínio;
- uso de exclusão lógica;
- precisão monetária;
- regra de arredondamento;
- estratégia de unidades;
- estratégia tributária;
- fonte de verdade;
- ownership;
- retenção;
- criptografia;
- versionamento;
- histórico;
- cobrança por formulário customizado.

---

# 8. FASE 3 — CONSTRUIR O CATÁLOGO DE DADOS

## 8.1 Catálogo por banco

Para cada banco, produzir uma seção com:

1. nome;
2. tecnologia;
3. versão;
4. finalidade;
5. ambientes;
6. proprietários;
7. serviços usuários;
8. schemas;
9. tabelas ou coleções;
10. views;
11. índices;
12. constraints;
13. procedures;
14. triggers;
15. extensões;
16. políticas de acesso;
17. política de backup;
18. política de restore;
19. criptografia;
20. retenção;
21. replicação;
22. observabilidade;
23. riscos;
24. pendências.

## 8.2 Catálogo por tabela ou coleção

Para cada tabela ou coleção, documentar:

- nome físico;
- nome lógico;
- descrição funcional;
- domínio;
- serviço proprietário;
- banco;
- schema;
- tipo de estrutura;
- estimativa de volume;
- crescimento;
- frequência de leitura;
- frequência de escrita;
- criticidade;
- classificação;
- tenant scope;
- estratégia de particionamento;
- estratégia de arquivamento;
- chaves;
- relacionamentos;
- índices;
- constraints;
- triggers;
- auditoria;
- eventos;
- APIs;
- telas;
- relatórios;
- integrações;
- importações;
- exportações;
- regras de deleção;
- regras de anonimização;
- política de retenção;
- riscos.

## 8.3 Dicionário obrigatório por campo

Para cada campo, criar uma linha contendo, no mínimo:

| Grupo         | Informação obrigatória                                        |
| ------------- | ------------------------------------------------------------- |
| Identificação | banco, schema, tabela, campo físico, campo lógico             |
| Semântica     | descrição completa, finalidade, contexto                      |
| Tipo          | tipo físico, tipo lógico, tamanho, precisão, escala           |
| Preenchimento | obrigatório, opcional, condicional, padrão                    |
| Domínio       | valores permitidos, enumeração, referência                    |
| Validação     | regras, regex, limites, consistência                          |
| Exemplo       | valor válido, inválido e caso limite                          |
| Relação       | PK, FK, unique, índice, dependências                          |
| Cálculo       | fórmula, operandos, arredondamento, momento do cálculo        |
| Unidade       | unidade base, unidade de entrada, unidade de saída, conversão |
| Fiscal        | incidência, classificação, regras tributárias                 |
| Segurança     | classificação LGPD, criptografia, mascaramento                |
| Acesso        | quem vê, quem cria, quem altera, quem aprova                  |
| Auditoria     | autor, data, hora, IP, sessão, origem, motivo                 |
| Ciclo de vida | criação, alteração, exclusão, restauração, retenção           |
| Backend       | entidade, DTO, endpoint, serviço, evento                      |
| Frontend      | formulário, componente, máscara, ajuda, ordem                 |
| Testes        | unitário, integração, contrato, E2E                           |
| Status        | existente, parcial, ausente, proposto, legado                 |
| Evidência     | arquivo e linha, migration, endpoint, tela                    |

## 8.4 Campos transversais recomendados

Avaliar em cada tabela se são necessários:

- `id`;
- `tenant_id`;
- `organization_id`;
- `company_id`;
- `branch_id`;
- `external_id`;
- `legacy_id`;
- `source_system`;
- `correlation_id`;
- `version`;
- `status`;
- `created_at`;
- `created_by`;
- `updated_at`;
- `updated_by`;
- `deleted_at`;
- `deleted_by`;
- `deletion_reason`;
- `restored_at`;
- `restored_by`;
- `approved_at`;
- `approved_by`;
- `rejected_at`;
- `rejected_by`;
- `rejection_reason`;
- `effective_from`;
- `effective_to`;
- `timezone`;
- `locale`;
- `currency_code`;
- `metadata_schema_version`;
- `row_hash`;
- `idempotency_key`.

Esses campos não deverão ser incluídos automaticamente em todas as tabelas. O Gemini deverá justificar a presença ou ausência.

## 8.5 Data e tempo

Toda data e hora deverá ter semântica definida.

Documentar:

- se representa instante ou data civil;
- timezone de origem;
- timezone de armazenamento;
- timezone de exibição;
- precisão;
- horário de verão;
- formato;
- nulabilidade;
- regra de atualização;
- relógio confiável;
- compatibilidade com auditoria;
- ordenação;
- uso em expiração;
- uso em SLA.

Preferir instantes em UTC no backend e exibição localizada no frontend. Datas civis, como nascimento ou vencimento sem horário, devem ser tratadas como datas, não como timestamps.

## 8.6 Valores monetários

Nunca usar ponto flutuante binário para valores monetários.

Documentar:

- moeda;
- valor bruto;
- desconto;
- acréscimo;
- imposto;
- frete;
- seguro;
- taxa;
- comissão;
- valor líquido;
- precisão;
- escala;
- regra de arredondamento;
- momento do arredondamento;
- distribuição de centavos;
- origem da taxa;
- data da taxa;
- moeda de liquidação;
- moeda de apresentação;
- estorno;
- conciliação.

## 8.7 Identificadores

Definir para cada identificador:

- tecnologia;
- formato;
- unicidade;
- escopo;
- geração;
- exposição pública;
- ordenação;
- previsibilidade;
- compatibilidade offline;
- migração;
- segurança.

Não expor IDs sequenciais sensíveis sem avaliação.

---

# 9. MODELAGEM EXAUSTIVA DE PRODUTOS, UNIDADES, ESTOQUE E TRIBUTOS

Esta seção é mandatória e deverá ser tratada como referência para o nível de profundidade exigido em todos os módulos.

## 9.1 Separação de conceitos

Não modelar “produto” como uma única tabela simplificada.

Separar, conforme necessidade:

- produto mestre;
- variante;
- SKU;
- categoria;
- marca;
- fabricante;
- fornecedor;
- atributos;
- opções;
- composição;
- kit;
- bundle;
- embalagem;
- unidade;
- conversão;
- código de barras;
- classificação fiscal;
- preço;
- custo;
- estoque;
- lote;
- série;
- validade;
- localização;
- disponibilidade;
- canal de venda;
- mídia;
- documento;
- garantia;
- rastreabilidade;
- restrição;
- regulamentação.

## 9.2 Produto mestre

Campos a avaliar:

- identificador;
- tenant;
- empresa;
- código interno;
- nome;
- nome comercial;
- descrição curta;
- descrição completa;
- tipo;
- subtipo;
- categoria;
- subcategoria;
- marca;
- fabricante;
- modelo;
- coleção;
- linha;
- origem;
- status;
- ativo;
- produto físico, digital, serviço, assinatura, kit ou insumo;
- vendável;
- comprável;
- estocável;
- fabricável;
- retornável;
- perecível;
- controlado por lote;
- controlado por série;
- exige validade;
- exige pesagem;
- exige medição;
- permite fracionamento;
- permite quantidade negativa;
- permite backorder;
- exige autorização;
- exige receita ou documento;
- idade mínima;
- restrição geográfica;
- canais;
- tags;
- SEO;
- observações;
- anexos;
- auditoria.

## 9.3 SKU e variantes

Documentar:

- SKU;
- atributos da variante;
- cor;
- tamanho;
- voltagem;
- capacidade;
- material;
- acabamento;
- sabor;
- fragrância;
- dimensões;
- peso;
- códigos de barras;
- GTIN/EAN/UPC;
- código fornecedor;
- código fabricante;
- status;
- substitutos;
- equivalentes;
- compatibilidades;
- estoque;
- preço;
- custo;
- imagens;
- documentos.

## 9.4 Unidades de medida

Criar catálogo de unidades com, no mínimo:

- código;
- símbolo;
- nome singular;
- nome plural;
- categoria dimensional;
- sistema de medida;
- precisão;
- escala;
- permite fracionamento;
- unidade base;
- status;
- equivalência normativa;
- regras regionais.

Categorias possíveis:

- unidade;
- massa;
- volume;
- comprimento;
- área;
- tempo;
- energia;
- potência;
- temperatura;
- quantidade;
- embalagem;
- dose;
- concentração;
- densidade;
- velocidade;
- pressão;
- unidade fiscal;
- unidade comercial personalizada.

## 9.5 Múltiplas unidades por produto

Cada produto poderá possuir:

- unidade de cadastro;
- unidade base de estoque;
- unidade de compra;
- unidade de venda;
- unidade de consumo;
- unidade de produção;
- unidade de transporte;
- unidade fiscal;
- unidade de exibição;
- unidade de conferência;
- unidade de inventário.

Exemplo:

- produto adquirido em tonelada;
- armazenado em quilograma;
- vendido em saco;
- baixado em quilograma;
- contado em unidade;
- transportado em pallet;
- faturado em caixa.

A modelagem deverá permitir conversões controladas e auditáveis.

## 9.6 Conversões

Criar uma estrutura equivalente a `product_unit_conversions` com:

- produto;
- variante;
- unidade de origem;
- unidade de destino;
- fator multiplicador;
- fator divisor;
- fórmula;
- precisão;
- arredondamento;
- tolerância;
- validade inicial;
- validade final;
- contexto;
- empresa;
- estabelecimento;
- fornecedor;
- embalagem;
- densidade;
- temperatura de referência, quando aplicável;
- aprovação;
- status;
- versão;
- auditoria.

Exemplos:

- 1 caixa = 12 unidades;
- 1 pacote = 500 gramas;
- 1 litro = conversão dependente de densidade para quilogramas;
- 1 rolo = 100 metros;
- 1 pallet = 48 caixas;
- 1 dose = 5 mililitros.

Conversões dimensionalmente incompatíveis não deverão ser permitidas sem fórmula e contexto técnico explícitos.

## 9.7 Precisão e arredondamento

Para cada operação, definir:

- quantidade de casas decimais;
- arredondamento comercial;
- arredondamento fiscal;
- arredondamento de estoque;
- truncamento permitido ou proibido;
- tolerância;
- diferença aceitável;
- ajuste;
- responsável;
- log.

## 9.8 Movimentação de estoque

Nunca depender apenas de um campo de saldo atualizado diretamente.

Modelar um livro-razão de movimentações, contendo:

- identificador;
- produto;
- SKU;
- lote;
- série;
- local;
- origem;
- destino;
- tipo de movimento;
- quantidade informada;
- unidade informada;
- quantidade convertida;
- unidade base;
- fator usado;
- saldo anterior;
- saldo posterior;
- custo;
- valor;
- motivo;
- documento;
- pedido;
- compra;
- venda;
- produção;
- transferência;
- ajuste;
- perda;
- avaria;
- devolução;
- inventário;
- reserva;
- liberação;
- usuário;
- data;
- correlação;
- idempotência;
- auditoria.

## 9.9 Lotes, séries e validade

Prever:

- lote;
- sublote;
- número de série;
- fabricação;
- validade;
- recebimento;
- fornecedor;
- origem;
- qualidade;
- inspeção;
- quarentena;
- liberação;
- bloqueio;
- recall;
- rastreabilidade;
- FEFO;
- FIFO;
- LIFO, se permitido;
- custo específico;
- status;
- documentação.

## 9.10 Tributação de produtos e serviços

O Gemini deverá mapear a necessidade fiscal por cenário, sem assumir que uma única configuração atende a todos.

Avaliar:

- país;
- estado;
- município;
- regime tributário;
- natureza da operação;
- tipo de cliente;
- contribuinte;
- não contribuinte;
- consumidor final;
- origem e destino;
- canal;
- produto ou serviço;
- finalidade;
- benefício fiscal;
- substituição tributária;
- monofásico;
- retenção;
- isenção;
- imunidade;
- diferimento;
- redução de base;
- alíquota;
- base;
- crédito;
- arredondamento;
- vigência.

Campos brasileiros a avaliar conforme aplicabilidade:

- NCM;
- CEST;
- CFOP;
- CST;
- CSOSN;
- origem da mercadoria;
- ICMS;
- ICMS-ST;
- FCP;
- DIFAL;
- IPI;
- PIS;
- COFINS;
- ISS;
- CNAE;
- código de serviço;
- retenções;
- benefícios;
- enquadramentos;
- ANP, quando aplicável;
- GTIN;
- unidade tributável;
- quantidade tributável;
- valor unitário tributável.

Não duplicar regra tributária diretamente em cada produto sem estratégia de perfil fiscal, vigência e exceção.

## 9.11 Perfis fiscais

Criar estruturas para:

- perfil fiscal;
- regra;
- condição;
- prioridade;
- vigência;
- jurisdição;
- regime;
- operação;
- produto;
- categoria;
- cliente;
- fornecedor;
- estabelecimento;
- exceção;
- cálculo;
- fundamento;
- versão;
- homologação;
- auditoria.

## 9.12 Preços e custos

Prever:

- tabela de preço;
- canal;
- região;
- cliente;
- segmento;
- quantidade mínima;
- unidade;
- moeda;
- preço base;
- preço promocional;
- custo médio;
- custo FIFO;
- custo específico;
- custo de reposição;
- margem;
- markup;
- comissão;
- imposto estimado;
- frete;
- vigência;
- prioridade;
- aprovação;
- histórico.

---

# 10. OUTROS DOMÍNIOS MÍNIMOS A DETALHAR

O mesmo nível de profundidade aplicado a produtos deverá ser replicado nos demais domínios.

## 10.1 Identidade e usuários

Cobrir:

- All-in-One ID;
- pessoa;
- perfil;
- credenciais;
- provedores de login;
- MFA;
- passkeys;
- biometria;
- dispositivos;
- sessões;
- tokens;
- refresh tokens;
- consentimentos;
- termos;
- preferências;
- contatos;
- endereços;
- documentos;
- verificação;
- status;
- bloqueios;
- recuperação;
- riscos;
- auditoria.

## 10.2 Empresas e estabelecimentos

Cobrir:

- organização;
- tenant;
- grupo econômico;
- empresa;
- filial;
- unidade;
- estabelecimento;
- CNPJ;
- inscrição;
- CNAE;
- regime;
- endereço;
- contatos;
- responsáveis;
- contas;
- módulos;
- plano;
- limites;
- configurações;
- branding;
- políticas;
- horários;
- calendários;
- documentos;
- licenças;
- homologações;
- status.

## 10.3 Pessoas, clientes e fornecedores

Separar identidade de papéis comerciais.

Cobrir:

- pessoa física;
- pessoa jurídica;
- cliente;
- fornecedor;
- parceiro;
- contato;
- dependente;
- beneficiário;
- representante;
- relacionamento;
- classificação;
- limite;
- risco;
- crédito;
- preferências;
- consentimentos;
- documentos;
- histórico.

## 10.4 Pedidos, vendas e compras

Cobrir:

- cabeçalho;
- itens;
- quantidades;
- unidades;
- conversões;
- preços;
- descontos;
- impostos;
- frete;
- seguro;
- comissão;
- reserva;
- entrega;
- faturamento;
- pagamento;
- devolução;
- cancelamento;
- alteração;
- aprovação;
- status;
- histórico;
- documentos;
- integrações.

## 10.5 Wallet, pagamentos e escrow

Cobrir:

- carteira;
- conta;
- saldo;
- saldo disponível;
- saldo bloqueado;
- ledger;
- lançamento;
- débito;
- crédito;
- reserva;
- captura;
- estorno;
- chargeback;
- escrow;
- beneficiários;
- split;
- taxas;
- conciliação;
- liquidação;
- moeda;
- risco;
- antifraude;
- idempotência;
- auditoria.

## 10.6 Jobs, currículos e CTPS

Cobrir:

- candidato;
- currículo;
- experiências;
- competências;
- formação;
- certificações;
- idiomas;
- vagas;
- candidaturas;
- triagem;
- entrevistas;
- propostas;
- contratações;
- importação CTPS;
- proveniência;
- documentos;
- criptografia;
- permissões;
- consulta restrita;
- consentimento;
- retenção;
- histórico.

## 10.7 Serviços, Delivery, Riders e Mobility

Cobrir:

- solicitação;
- oferta;
- prestador;
- rota;
- parada;
- endereço;
- geolocalização;
- distância;
- preço;
- taxa;
- comissão;
- veículo;
- condutor;
- entrega;
- coleta;
- prova;
- status;
- SLA;
- cancelamento;
- ocorrência;
- avaliação;
- suporte;
- pagamento;
- segurança;
- auditoria.

## 10.8 Saúde

Cobrir com proteção reforçada:

- paciente;
- profissional;
- estabelecimento;
- agenda;
- atendimento;
- prontuário;
- consentimento;
- prescrição;
- exame;
- laudo;
- documento;
- histórico;
- acesso emergencial;
- auditoria de leitura;
- retenção;
- criptografia;
- segregação;
- anonimização;
- conformidade.

## 10.9 ERP, CRM e RH

Cobrir:

- plano de contas;
- centros de custo;
- lançamentos;
- contas a pagar;
- contas a receber;
- conciliação;
- fluxo de caixa;
- orçamento;
- ativo;
- contratos;
- oportunidades;
- funil;
- atividades;
- campanhas;
- colaboradores;
- cargos;
- jornadas;
- folha;
- benefícios;
- férias;
- ponto;
- avaliações;
- documentos;
- permissões.

## 10.10 Documentos e mídia

Cobrir:

- arquivo;
- tipo;
- MIME;
- tamanho;
- hash;
- armazenamento;
- versão;
- proprietário;
- vínculo;
- classificação;
- criptografia;
- retenção;
- expiração;
- assinatura;
- validação;
- vírus;
- metadados;
- miniaturas;
- permissões;
- download;
- auditoria.

---

# 11. AUDITORIA, LOGS E RASTREABILIDADE

## 11.1 Auditoria de alteração

Criar estrutura imutável contendo:

- evento;
- entidade;
- entidade ID;
- tenant;
- empresa;
- usuário;
- papel;
- sessão;
- dispositivo;
- IP;
- agente;
- origem;
- canal;
- operação;
- estado anterior;
- estado posterior;
- campos alterados;
- motivo;
- correlação;
- causação;
- data e hora;
- resultado;
- erro;
- aprovação;
- assinatura ou hash;
- retenção.

Dados sensíveis não deverão ser gravados em texto aberto no log.

## 11.2 Auditoria de leitura

Para dados especialmente sensíveis, registrar:

- quem consultou;
- qual dado;
- quando;
- por qual finalidade;
- em qual contexto;
- qual autorização;
- qual resultado;
- se houve exportação;
- se houve impressão;
- se houve compartilhamento.

## 11.3 Logs técnicos

Separar:

- log técnico;
- log de segurança;
- log de auditoria;
- log de negócio;
- métrica;
- trace;
- evento de integração.

Definir correlação entre todos.

## 11.4 Retenção e imutabilidade

Documentar:

- prazo;
- justificativa;
- armazenamento;
- integridade;
- acesso;
- expurgo;
- anonimização;
- obrigação legal;
- restauração;
- investigação.

---

# 12. CONSTRUTOR DE FORMULÁRIOS DINÂMICOS SOB MEDIDA

Esta funcionalidade é obrigatória e deverá ser tratada como um produto pago interno do ecossistema.

## 12.1 Objetivo

Permitir que um usuário empresarial autorizado personalize formulários de inserção de dados usando campos previamente permitidos pelo sistema, sem acesso direto ao banco de dados e sem capacidade de decidir livremente a tabela física de destino.

O usuário poderá:

- escolher o contexto funcional;
- selecionar campos disponíveis;
- organizar campos;
- arrastar e soltar;
- criar blocos;
- criar seções;
- criar abas;
- ordenar;
- definir largura;
- definir visibilidade;
- tornar campo obrigatório dentro dos limites permitidos;
- criar cálculos permitidos;
- criar validações permitidas;
- definir textos de ajuda;
- definir condições;
- visualizar;
- testar;
- enviar para homologação;
- publicar versão aprovada.

O usuário não poderá:

- criar acesso direto a tabela;
- escolher coluna física arbitrária;
- acessar campo não autorizado;
- escrever SQL;
- escrever código executável;
- alterar schema;
- remover validação estrutural obrigatória;
- enfraquecer segurança;
- alterar ownership;
- desativar auditoria;
- alterar cálculo fiscal oficial;
- publicar sem homologação;
- sobrescrever uma versão publicada sem versionamento.

## 12.2 Arquitetura de metadados

Criar estruturas equivalentes a:

### `form_definitions`

- `id`;
- `tenant_id`;
- `company_id`;
- `module_id`;
- `business_context`;
- `name`;
- `description`;
- `status`;
- `current_version_id`;
- `created_by`;
- `created_at`;
- `updated_by`;
- `updated_at`.

### `form_versions`

- `id`;
- `form_definition_id`;
- `version_number`;
- `schema_version`;
- `status`;
- `change_summary`;
- `created_by`;
- `created_at`;
- `submitted_at`;
- `submitted_by`;
- `approved_at`;
- `approved_by`;
- `rejected_at`;
- `rejected_by`;
- `rejection_reason`;
- `published_at`;
- `published_by`;
- `retired_at`;
- `checksum`.

### `form_blocks`

- seção;
- grupo;
- aba;
- coluna;
- ordem;
- título;
- descrição;
- largura;
- colapso;
- visibilidade;
- repetição;
- estilo permitido.

### `form_fields`

- identificador;
- versão;
- catálogo de campo;
- binding lógico;
- componente;
- rótulo;
- ajuda;
- placeholder;
- obrigatório;
- somente leitura;
- oculto;
- ordem;
- largura;
- máscara;
- formato;
- valor padrão;
- origem do valor;
- unidade;
- permissões;
- visibilidade;
- validações;
- auditoria.

### `field_catalog`

Catálogo controlado de campos que podem ser utilizados no construtor:

- domínio;
- entidade lógica;
- campo lógico;
- tipo;
- descrição;
- componente permitido;
- validações obrigatórias;
- sensibilidade;
- permissões;
- binding autorizado;
- operações permitidas;
- cálculos permitidos;
- unidade;
- formatação;
- status;
- versão.

### `field_bindings`

O binding deverá apontar para uma abstração lógica ou comando do domínio, nunca permitir que o usuário selecione tabela e coluna física diretamente.

Campos:

- field catalog;
- command;
- API;
- DTO;
- path lógico;
- tipo;
- transformação;
- versão;
- validação;
- política;
- status.

### `form_calculations`

- nome;
- resultado;
- operandos;
- operação;
- expressão declarativa segura;
- ordem;
- precisão;
- arredondamento;
- gatilho;
- condição;
- unidade;
- tratamento de nulo;
- tratamento de divisão por zero;
- visibilidade;
- validação;
- status;
- versão.

Operações permitidas:

- soma;
- subtração;
- multiplicação;
- divisão;
- percentual;
- média;
- mínimo;
- máximo;
- contagem;
- diferença de datas;
- conversão de unidade;
- arredondamento;
- regra condicional;
- composição de texto controlada.

Proibir execução arbitrária de JavaScript, SQL, shell ou expressões não validadas.

### `form_validations`

- campo;
- tipo;
- parâmetros;
- mensagem;
- severidade;
- condição;
- execução frontend;
- execução backend;
- status;
- versão.

### `form_visibility_rules`

- alvo;
- condição;
- operador;
- valor;
- resultado;
- prioridade;
- combinação;
- status.

### `form_permissions`

- formulário;
- versão;
- papel;
- atributo;
- visualizar;
- criar;
- editar;
- aprovar;
- publicar;
- exportar;
- imprimir;
- acessar sensível.

### `form_homologations`

- versão;
- solicitante;
- data;
- checklist;
- resultado;
- aprovador;
- observações;
- problemas;
- correções;
- revalidação;
- evidências;
- status.

### `form_publications`

- versão;
- ambiente;
- data;
- responsável;
- rollout;
- rollback;
- tenants;
- canais;
- checksum;
- status.

### `form_submissions`

- formulário;
- versão;
- usuário;
- tenant;
- contexto;
- entidade alvo;
- status;
- início;
- conclusão;
- origem;
- correlação;
- idempotência;
- validação;
- auditoria.

### `form_submission_values`

Usar apenas quando o caso exigir persistência intermediária, rascunho ou submissão desacoplada. Não utilizar como substituto permanente do modelo de domínio.

Registrar:

- submission;
- field catalog;
- tipo;
- valor normalizado;
- valor exibido;
- unidade;
- origem;
- validação;
- sensibilidade;
- criptografia;
- versão.

## 12.3 Fluxo de criação

1. Usuário inicia um novo formulário.
2. Sistema cria rascunho.
3. Usuário escolhe contexto.
4. Sistema apresenta campos permitidos.
5. Usuário arrasta campos.
6. Usuário cria blocos.
7. Usuário configura cálculos e regras permitidas.
8. Sistema valida continuamente.
9. Autosaves técnicos preservam o rascunho.
10. Usuário conclui a edição.
11. Sistema gera prévia.
12. Usuário envia para homologação.
13. Homologador executa checklist.
14. Erros retornam ao usuário.
15. Correções geram nova versão ou revisão.
16. Aprovação permite publicação.
17. Publicação gera versão imutável.
18. Toda alteração posterior gera nova versão.
19. Todas as ações geram log.

## 12.4 Homologação

Verificar:

- campos obrigatórios;
- campos proibidos;
- conflitos;
- cálculos;
- precisão;
- unidades;
- permissões;
- segurança;
- dados sensíveis;
- acessibilidade;
- responsividade;
- tradução;
- máscaras;
- validações;
- fluxos;
- erros;
- integração;
- API;
- persistência;
- auditoria;
- performance;
- testes;
- rollback.

## 12.5 Versionamento

Estados mínimos:

- `draft`;
- `editing`;
- `submitted`;
- `under_review`;
- `changes_requested`;
- `approved`;
- `published`;
- `suspended`;
- `retired`;
- `rejected`.

Uma versão publicada não poderá ser alterada in-place.

## 12.6 Cobrança e eventos faturáveis

Preparar a arquitetura para cobrança por serviço sem exibir preço ao usuário neste momento.

Registrar eventos como:

- criação de solicitação de formulário;
- envio para homologação;
- homologação aprovada;
- publicação inicial;
- solicitação de alteração;
- nova homologação;
- publicação de nova versão;
- manutenção especial;
- suporte técnico;
- customização avançada.

Separar:

- autosave técnico;
- gravação de rascunho;
- submissão formal;
- homologação;
- publicação;
- alteração publicada.

A política comercial deverá ser configurável por plano, contrato, tenant e tipo de alteração.

> **NOTA INTERNA PARA REVISÃO COMERCIAL:** definir posteriormente o valor da criação, homologação, publicação e alteração de formulários sob medida. Não exibir preços, regras de margem ou estratégia comercial ao usuário final até aprovação formal.

---

# 13. SEGURANÇA DO CONSTRUTOR DE FORMULÁRIOS

Aplicar:

- allowlist de campos;
- allowlist de componentes;
- allowlist de operadores;
- parser seguro;
- validação backend obrigatória;
- limite de complexidade;
- limite de dependências;
- detecção de ciclos;
- proteção contra expressão maliciosa;
- rate limit;
- segregação por tenant;
- RBAC;
- ABAC;
- aprovação;
- versionamento;
- assinatura;
- checksum;
- auditoria;
- rollback;
- testes automatizados;
- sandbox de prévia.

Cálculos nunca poderão confiar apenas no frontend. O backend deverá recalcular e validar.

---

# 14. MEMORANDO DE COORDENADAS PARA FORMULÁRIOS FRONTEND

Para cada entidade ou processo que aceite dados, gerar uma especificação completa de tela.

## 14.1 Identificação do formulário

- código;
- nome;
- módulo;
- rota;
- persona;
- objetivo;
- entidade;
- comando backend;
- API;
- versão;
- status;
- prioridade.

## 14.2 Estrutura visual

Definir:

- cabeçalho;
- breadcrumbs;
- título;
- subtítulo;
- contexto;
- abas;
- etapas;
- seções;
- blocos;
- colunas;
- ordem;
- agrupamento;
- resumo lateral;
- rodapé;
- ações.

## 14.3 Matriz de campos

Para cada campo:

| Item            | Descrição                                |
| --------------- | ---------------------------------------- |
| Campo lógico    | nome funcional                           |
| Rótulo          | texto pt-BR                              |
| Tipo            | texto, número, moeda, data, seleção etc. |
| Componente      | componente visual                        |
| Obrigatoriedade | sempre, nunca ou condicional             |
| Máscara         | CPF, CNPJ, telefone, CEP, moeda etc.     |
| Ajuda           | orientação ao usuário                    |
| Placeholder     | exemplo de preenchimento                 |
| Validação       | frontend e backend                       |
| Fonte           | digitado, API, cálculo, seleção          |
| Dependência     | campos condicionantes                    |
| Visibilidade    | regra                                    |
| Permissão       | papel ou atributo                        |
| Unidade         | entrada, exibição e conversão            |
| Cálculo         | regra                                    |
| Persistência    | binding lógico                           |
| Auditoria       | evento                                   |
| Erro            | mensagem                                 |
| Acessibilidade  | label, hint, foco, leitor de tela        |
| Testes          | casos                                    |

## 14.4 Tipos de componentes

Avaliar:

- texto curto;
- texto longo;
- número inteiro;
- decimal;
- moeda;
- percentual;
- quantidade;
- unidade;
- data;
- hora;
- data e hora;
- duração;
- CPF;
- CNPJ;
- documento;
- telefone;
- e-mail;
- URL;
- endereço;
- CEP;
- geolocalização;
- seleção simples;
- seleção múltipla;
- autocomplete;
- busca remota;
- radio;
- checkbox;
- switch;
- upload;
- imagem;
- vídeo;
- assinatura;
- código de barras;
- QR code;
- editor de itens;
- tabela editável;
- bloco repetível;
- cálculo;
- resumo;
- status;
- aprovação.

## 14.5 Estados

Toda tela deverá contemplar:

- carregamento;
- vazio;
- sucesso;
- erro;
- erro de validação;
- indisponibilidade;
- sem permissão;
- conflito;
- versão desatualizada;
- rascunho;
- salvamento automático;
- offline;
- reconexão;
- submissão;
- aprovação;
- rejeição;
- publicação;
- cancelamento;
- rollback.

## 14.6 Ações

Para cada ação:

- rótulo;
- ícone;
- permissão;
- pré-condição;
- confirmação;
- payload;
- endpoint;
- idempotência;
- loading;
- sucesso;
- erro;
- log;
- teste;
- efeito na navegação.

## 14.7 Listagens e tabelas

Definir:

- colunas;
- ordenação;
- filtros;
- busca;
- paginação;
- seleção;
- ações em lote;
- exportação;
- densidade;
- personalização;
- salvamento de visão;
- estados;
- responsividade;
- permissão;
- auditoria;
- dados sensíveis;
- totalizadores;
- subtotais;
- drill-down.

## 14.8 Filtros

Para cada filtro:

- campo;
- tipo;
- operador;
- domínio;
- valor padrão;
- múltipla seleção;
- dependência;
- consulta backend;
- indexação;
- URL;
- compartilhamento;
- salvamento;
- reset;
- auditoria quando necessário.

## 14.9 Dashboards

Definir:

- objetivo;
- persona;
- indicadores;
- fórmula;
- fonte;
- atualização;
- período;
- filtros;
- comparação;
- meta;
- alerta;
- drill-down;
- permissão;
- exportação;
- vazio;
- erro;
- atraso de dados;
- timezone;
- moeda;
- unidade;
- precisão.

---

# 15. ORIENTAÇÃO PARA IA STITCH

## 15.1 Papel do Stitch

O Stitch deverá ser utilizado como padrão de layout, composição, responsividade e organização visual.

A colorimetria atual aprovada do projeto deverá ser preservada.

## 15.2 Entradas obrigatórias para o Stitch

Cada solicitação deverá incluir:

- módulo;
- objetivo;
- persona;
- rota;
- dados;
- campos;
- validações;
- ações;
- permissões;
- estados;
- tabelas;
- filtros;
- cálculos;
- unidades;
- mensagens;
- acessibilidade;
- responsividade;
- integrações;
- critérios de aceite.

## 15.3 Saídas esperadas

O Stitch deverá gerar:

- tela completa;
- desktop;
- tablet;
- mobile;
- estado vazio;
- estado preenchido;
- erro;
- loading;
- validação;
- modal;
- confirmação;
- detalhamento;
- listagem;
- formulário;
- dashboard;
- componentes reutilizáveis.

## 15.4 Regras de frontend

- português do Brasil;
- nenhuma ação sem destino;
- nenhuma tabela sem dados coerentes;
- nenhum formulário sem validação;
- nenhum cálculo apenas visual;
- nenhum campo sem binding;
- nenhuma permissão apenas cosmética;
- acessibilidade;
- navegação por teclado;
- foco;
- contraste;
- leitores de tela;
- responsividade;
- feedback imediato;
- prevenção de erro;
- mensagens claras;
- confirmação para ações destrutivas;
- recuperação;
- autosave quando aplicável;
- evidência de testes.

## 15.5 Integração

Cada template deverá indicar:

- endpoint;
- método;
- request;
- response;
- paginação;
- erro;
- cache;
- invalidação;
- optimistic update;
- idempotência;
- autorização;
- auditoria;
- eventos;
- observabilidade.

---

# 16. FASE 4 — VALIDAR

## 16.1 Validação estrutural

Executar:

- comparação migration x banco;
- comparação ORM x migration;
- comparação DTO x ORM;
- comparação API x DTO;
- comparação frontend x API;
- detecção de campos órfãos;
- detecção de tabelas órfãs;
- detecção de índices ausentes;
- detecção de FKs ausentes;
- detecção de tipos incompatíveis;
- detecção de nulos indevidos;
- detecção de duplicidade;
- detecção de enum divergente;
- detecção de timezone incorreto;
- detecção de moeda incorreta;
- detecção de precisão inadequada.

## 16.2 Validação funcional

Para cada formulário:

- criar;
- editar;
- salvar rascunho;
- cancelar;
- excluir;
- restaurar;
- aprovar;
- rejeitar;
- exportar;
- importar;
- buscar;
- filtrar;
- ordenar;
- paginar;
- calcular;
- converter unidade;
- aplicar imposto;
- registrar log;
- validar permissão;
- testar concorrência;
- testar idempotência.

## 16.3 Validação de produto

Criar testes com:

- produto por unidade;
- produto por peso;
- produto por volume;
- produto por comprimento;
- produto por área;
- produto fracionado;
- produto em caixa;
- produto em pallet;
- produto com conversão;
- produto com densidade;
- lote;
- série;
- validade;
- imposto normal;
- substituição;
- isenção;
- preço por quantidade;
- desconto;
- devolução;
- ajuste;
- venda em unidade diferente da compra.

## 16.4 Validação do formulário dinâmico

Testar:

- arrastar e soltar;
- blocos;
- seções;
- abas;
- campos obrigatórios;
- campos proibidos;
- cálculo;
- divisão por zero;
- ciclos;
- visibilidade;
- permissão;
- homologação;
- rejeição;
- publicação;
- versionamento;
- rollback;
- cobrança;
- auditoria;
- isolamento por tenant;
- tentativa de acesso a campo não autorizado;
- tentativa de injeção;
- tentativa de expressão maliciosa.

## 16.5 Validação de segurança

Executar:

- autorização horizontal;
- autorização vertical;
- isolamento de tenant;
- exposição de dados;
- logs sensíveis;
- criptografia;
- tokens;
- sessões;
- upload;
- malware;
- injeção;
- mass assignment;
- IDOR;
- rate limit;
- replay;
- CSRF;
- XSS;
- SSRF;
- proteção de APIs;
- trilha de auditoria.

---

# 17. FASE 5 — DOCUMENTAR

## 17.1 Estrutura obrigatória de entrega

Gerar, no mínimo:

```text
docs/data-audit/
├── 00_RESUMO_EXECUTIVO.md
├── 01_METODOLOGIA.md
├── 02_MAPA_DE_DOMINIOS.md
├── 03_CATALOGO_DE_BANCOS.md
├── 04_DICIONARIO_DE_DADOS_MESTRE.md
├── 05_RELACIONAMENTOS_E_ERD.md
├── 06_UNIDADES_E_CONVERSOES.md
├── 07_TRIBUTACAO.md
├── 08_AUDITORIA_E_LOGS.md
├── 09_FORMULARIOS_FRONTEND.md
├── 10_FORMULARIOS_DINAMICOS.md
├── 11_PERMISSOES_E_SEGURANCA.md
├── 12_APIS_EVENTOS_E_INTEGRACOES.md
├── 13_VALIDACAO_E_TESTES.md
├── 14_REGISTRO_DE_LACUNAS.md
├── 15_BACKLOG_DE_IMPLEMENTACAO.md
├── 16_COORDENADAS_STITCH.md
├── 17_DECISOES_ARQUITETURAIS.md
├── 18_MATRIZ_DE_RASTREABILIDADE.md
├── 19_CRITERIOS_DE_ACEITE.md
└── databases/
    └── <banco>/
        ├── README.md
        ├── schemas/
        ├── tables/
        ├── collections/
        ├── views/
        └── diagrams/
```

## 17.2 Formatos complementares

Além de Markdown, gerar:

- CSV do dicionário de dados;
- JSON estruturado;
- Mermaid ERD;
- matriz formulário x campo;
- matriz API x campo;
- matriz evento x campo;
- matriz permissão x ação;
- matriz risco x controle;
- checklist de cobertura;
- relatório de divergências.

## 17.3 Evidências

Cada afirmação sobre algo existente deverá citar:

- caminho;
- arquivo;
- linha;
- migration;
- classe;
- função;
- endpoint;
- teste;
- tela;
- workflow;
- commit, quando disponível.

Cada proposta deverá ser marcada como “proposta”, nunca como existente.

---

# 18. FASE 6 — ORIENTAR TEMPLATE FRONTEND IA STITCH

Para cada tela identificada, gerar um bloco padronizado:

```markdown
## TEMPLATE: Cadastro de Produto

### Contexto

- Módulo:
- Persona:
- Rota:
- Entidade:
- Objetivo:

### Dados

- Tabelas:
- APIs:
- Eventos:
- Permissões:

### Layout

- Cabeçalho:
- Abas:
- Blocos:
- Ordem:
- Responsividade:

### Campos

| Ordem | Campo | Rótulo | Componente | Obrigatório | Validação | Unidade | Cálculo | Binding |
| ----: | ----- | ------ | ---------- | ----------- | --------- | ------- | ------- | ------- |

### Ações

| Ação | Permissão | Endpoint | Confirmação | Log | Estado |
| ---- | --------- | -------- | ----------- | --- | ------ |

### Estados

- loading:
- vazio:
- erro:
- sucesso:
- sem permissão:
- conflito:

### Critérios de aceite

- [ ] ...
```

O prompt destinado ao Stitch deverá ser suficientemente detalhado para evitar interpretação aberta sobre dados, regras, ações ou validações.

---

# 19. MATRIZ DE RASTREABILIDADE

Criar vínculo entre:

- requisito;
- domínio;
- entidade;
- tabela;
- campo;
- API;
- evento;
- formulário;
- componente;
- permissão;
- teste;
- evidência;
- status.

Exemplo:

| Requisito                                       | Tabela                   | Campo             | API                          | Formulário                     | Teste        | Status   |
| ----------------------------------------------- | ------------------------ | ----------------- | ---------------------------- | ------------------------------ | ------------ | -------- |
| Produto vendido em unidade diferente do estoque | product_unit_conversions | conversion_factor | `/products/{id}/conversions` | Cadastro de produto > Unidades | E2E-PROD-014 | Pendente |

---

# 20. REGISTRO DE LACUNAS

Cada lacuna deverá conter:

- ID;
- título;
- módulo;
- descrição;
- evidência;
- impacto;
- risco;
- prioridade;
- proposta;
- dependências;
- arquivos afetados;
- migration;
- backend;
- frontend;
- testes;
- documentação;
- critério de aceite;
- status.

Não usar frases vagas como “melhorar banco” ou “adicionar campos”. Descrever exatamente o que falta.

---

# 21. CRITÉRIOS DE CONCLUSÃO

A tarefa somente poderá ser marcada como concluída quando:

- 100% dos bancos forem catalogados;
- 100% dos schemas forem catalogados;
- 100% das tabelas e coleções forem catalogadas;
- 100% dos campos forem descritos;
- 100% dos relacionamentos forem descritos;
- 100% dos campos usados no frontend tiverem binding;
- 100% dos campos sensíveis tiverem classificação;
- 100% das alterações relevantes tiverem auditoria;
- 100% dos cálculos tiverem fórmula, precisão e teste;
- 100% das unidades tiverem regra;
- 100% das regras fiscais tiverem vigência e contexto;
- 100% dos formulários tiverem coordenada de frontend;
- 100% dos botões tiverem ação;
- 100% das permissões tiverem enforcement backend;
- 100% das lacunas tiverem backlog;
- os testes críticos estiverem passando;
- a documentação estiver versionada;
- houver evidência de validação.

“Cobertura estimada” não substitui comprovação.

---

# 22. RELATÓRIO FINAL DO GEMINI

O relatório final deverá conter:

## 22.1 Resumo executivo

- situação atual;
- cobertura;
- principais riscos;
- principais lacunas;
- decisões;
- prioridades;
- próximos passos.

## 22.2 Indicadores

- bancos analisados;
- schemas;
- tabelas;
- coleções;
- campos;
- relacionamentos;
- índices;
- APIs;
- eventos;
- formulários;
- dashboards;
- relatórios;
- lacunas;
- P0;
- P1;
- testes;
- cobertura.

## 22.3 Declaração de limitações

O Gemini deverá declarar claramente:

- o que não conseguiu abrir;
- o que não conseguiu executar;
- o que depende de credencial;
- o que depende de ambiente;
- o que é inferência;
- o que é proposta;
- o que precisa de decisão humana.

## 22.4 Próxima ação executável

O relatório deverá terminar com uma fila ordenada de execução, alinhada a `docs/EXECUTION_PLAN.md`.

---

# 23. COORDENADA DIRETA PARA O GEMINI

> Execute uma varredura exaustiva de todo o projeto All-in-One + Valley. Leia documentação, código, banco, migrations, APIs, eventos, testes, frontend, templates Stitch, segurança, infraestrutura e integrações. Produza um catálogo físico e lógico de todos os bancos, schemas, tabelas, coleções, views, índices, constraints e campos. Para cada campo, descreva finalidade, tipo, tamanho, precisão, nulabilidade, padrão, domínio, validação, exemplo, relacionamento, unidade, conversão, cálculo, regra fiscal, segurança, LGPD, auditoria, API, evento, frontend, teste e evidência. Compare todas as camadas para detectar divergências. Não omita possibilidades futuras realistas. Modele produtos com múltiplas unidades de compra, estoque, venda, consumo, transporte e tributação, incluindo conversões, precisão, lotes, séries, validade, custos, preços e impostos. Defina auditoria de usuário, data, hora, sessão, IP, dispositivo, motivo, estado anterior e posterior. Especifique um construtor pago de formulários dinâmicos por metadados, com arrastar e soltar, blocos, campos autorizados, cálculos seguros, regras, permissões, homologação, publicação, versionamento, cobrança configurável e logs imutáveis. O usuário não poderá escolher tabela física ou coluna arbitrária. Gere coordenadas completas para cada formulário, tabela, dashboard, filtro e template frontend em português do Brasil. Oriente o Stitch preservando a colorimetria atual e usando-o como padrão de layout. Nenhum botão poderá ficar sem função. Siga as fases IDEALIZAR, PLANEJAR, CONSTRUIR, VALIDAR, DOCUMENTAR e ORIENTAR TEMPLATE FRONTEND IA STITCH. Não declare conclusão sem evidência de 100% de cobertura ou sem registrar cada lacuna e sua coordenada de implementação.

---

# 24. CHECKLIST MANDATÓRIO

## Idealizar

- [ ] Mapear ecossistema.
- [ ] Mapear domínios.
- [ ] Mapear personas.
- [ ] Mapear eventos.
- [ ] Mapear fontes de verdade.
- [ ] Mapear riscos.

## Planejar

- [ ] Definir ordem de leitura.
- [ ] Definir matriz de comparação.
- [ ] Definir prioridades.
- [ ] Definir entregáveis.
- [ ] Definir critérios de aceite.

## Construir

- [ ] Catalogar bancos.
- [ ] Catalogar tabelas.
- [ ] Catalogar campos.
- [ ] Catalogar unidades.
- [ ] Catalogar impostos.
- [ ] Catalogar cálculos.
- [ ] Catalogar logs.
- [ ] Catalogar permissões.
- [ ] Catalogar APIs.
- [ ] Catalogar eventos.
- [ ] Catalogar formulários.
- [ ] Modelar formulário dinâmico.

## Validar

- [ ] Validar schema.
- [ ] Validar integridade.
- [ ] Validar regras.
- [ ] Validar unidades.
- [ ] Validar tributos.
- [ ] Validar cálculos.
- [ ] Validar segurança.
- [ ] Validar auditoria.
- [ ] Validar frontend.
- [ ] Validar E2E.

## Documentar

- [ ] Gerar Markdown.
- [ ] Gerar CSV.
- [ ] Gerar JSON.
- [ ] Gerar ERD.
- [ ] Gerar matrizes.
- [ ] Gerar backlog.
- [ ] Gerar registro de lacunas.
- [ ] Gerar evidências.

## Orientar Stitch

- [ ] Gerar coordenada por tela.
- [ ] Gerar campos.
- [ ] Gerar componentes.
- [ ] Gerar validações.
- [ ] Gerar ações.
- [ ] Gerar estados.
- [ ] Gerar responsividade.
- [ ] Gerar acessibilidade.
- [ ] Gerar integração.
- [ ] Gerar critérios de aceite.

---

# 25. NOTA FINAL DE GOVERNANÇA

Este memorando não autoriza alterações destrutivas automáticas em produção.

Antes de alterar banco existente, o Gemini deverá:

1. gerar diagnóstico;
2. gerar proposta;
3. gerar migration reversível;
4. avaliar dados existentes;
5. definir backfill;
6. definir compatibilidade;
7. definir rollback;
8. criar testes;
9. registrar impacto;
10. submeter à validação técnica.

Nenhuma tabela deverá ser removida, renomeada ou dividida sem plano de migração e preservação de dados.

Nenhum campo deverá mudar de tipo sem análise de compatibilidade.

Nenhum formulário deverá ser publicado sem homologação.

Nenhum cálculo financeiro, fiscal, de estoque ou conversão deverá depender apenas do frontend.

Nenhuma regra de autorização deverá existir somente na interface.

Nenhuma personalização paga deverá revelar internamente custos, margem ou estratégia comercial antes da revisão definida na nota interna.

---

**FIM DO MEMORANDO**
