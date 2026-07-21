# Diretriz mandatória de marca e interfaces de dados

**Vigência:** 20/07/2026  
**Escopo:** todos os aplicativos, shells, páginas públicas, painéis administrativos e builds móveis do ecossistema All-in-One.

## 1. Logomarca oficial

O único asset autorizado para a marca All-in-One no shell empresarial é:

`/assets/brand/all-in-one-logo-light-official.png`

Regras obrigatórias:

1. Renderizar a logomarca em todas as telas por meio do shell compartilhado.
2. Preservar integralmente linhas, cores, tipografia, proporção e composição.
3. Permitir somente redimensionamento proporcional.
4. Proibir filtros, recortes, máscaras, mudança de cor, rotação, distorção, opacidade decorativa, reconstrução em CSS ou substituição por texto.
5. Utilizar o componente compartilhado `BrandLogo` em novas implementações.
6. Executar `python scripts/check_brand_integrity.py` na validação do repositório e no CI.
7. Tratar qualquer divergência como falha bloqueante de release.

## 2. Dashboards

Todo dashboard deve ser uma superfície de decisão, não uma coleção decorativa de cartões. Deve conter:

- escopo e período;
- indicadores com origem e atualização;
- exceções e alertas;
- tendências relevantes;
- ações recomendadas;
- acesso ao detalhe;
- estados de carregamento, vazio, erro e permissão;
- alternativa tabular acessível para visualizações.

Métricas inventadas, sem fonte ou sem contrato de back-end são proibidas.

## 3. Relatórios

Todo relatório deve possuir filtros, resumo, visualização adequada, tabela equivalente, detalhamento, exportação, origem dos dados, horário de atualização e controle de permissão no servidor.

## 4. Listas e tabelas

Toda entidade operacional deve possuir uma tela de listagem quando fizer sentido ao fluxo. O padrão mínimo inclui:

- pesquisa;
- filtros;
- visualizações salvas;
- ordenação;
- paginação;
- seleção e ações em massa quando seguras;
- estados vazios distintos;
- tratamento de erro;
- acesso à criação, edição, visualização e auditoria conforme permissão.

## 5. Formulários

Nenhum campo necessário ao contrato de domínio deve ser omitido. A riqueza de metadados, contudo, deve ser organizada com divulgação progressiva para não transformar a interface em um labirinto.

Cada campo deve possuir rótulo visível, indicação de obrigatoriedade, validação local e no servidor, mensagem específica em português do Brasil, autocomplete, acesso por teclado, persistência de rascunho e proteção contra envio duplicado.

Formulários extensos devem usar seções ou etapas coerentes:

1. dados essenciais;
2. dados operacionais;
3. documentos;
4. configurações avançadas;
5. revisão;
6. confirmação.

## 6. Contrato verificável

O arquivo `config/apps/data_ui_contract.json` é a fonte versionada dos requisitos mínimos de telas de visão geral, relatórios, listas e formulários.

Toda nova tela ou gerador de telas deve consumir ou validar esse contrato. Divergências devem ser registradas com justificativa arquitetural e teste correspondente.

## 7. Português do Brasil

Todo texto de interface deve seguir `pt-BR`, preservando apenas marcas, siglas e termos estrangeiros amplamente adotados. Botões devem descrever ações reais, por exemplo: “Criar empresa”, “Salvar alterações”, “Publicar vaga”, “Emitir documento fiscal” e “Tentar novamente”.

## 8. Critérios de conclusão

Uma tela somente está concluída quando:

- a logomarca oficial está presente e fiel;
- todas as ações possuem comportamento real;
- os contratos de API estão conectados;
- autorização é validada no servidor;
- todos os estados obrigatórios existem;
- textos estão em português do Brasil;
- desktop e mobile foram verificados;
- acessibilidade WCAG 2.2 AA foi testada;
- testes unitários, de componente e E2E aplicáveis passaram;
- não há dados fictícios em produção;
- evidências e pendências foram documentadas.
