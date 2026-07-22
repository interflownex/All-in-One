# Fase 2: Plano de Leitura e Estratégia de Análise

**Referência:** `docs/MEMORANDO_MESTRE_GEMINI_VARREDURA_DADOS_FORMULARIOS_ALL_IN_ONE.md`, Seção 7.1

Este documento estabelece o plano de leitura e a estratégia de comparação para a varredura exaustiva do ecossistema All-in-One + Valley.

## 7.1 Matriz do Plano de Leitura

A matriz a seguir detalha as áreas a serem analisadas, os caminhos específicos a serem investigados, as evidências que se espera encontrar e o artefato que será gerado como resultado de cada etapa da análise.

| Ordem | Área           | Caminhos Analisados                                             | Evidências Esperadas                                                         | Resultado (Artefato Gerado)                                                                            | Status        |
| :---- | :------------- | :-------------------------------------------------------------- | :--------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------- | :------------ |
| 1     | Documentação   | `docs/`, `contracts/`, `README.md`, `STATUS.md`, `ROADMAP.md`   | Escopo, regras de negócio, arquitetura, domínios, personas e eventos.        | `docs/analise_dominios.md`, `docs/analise_personas_detalhada.md`, `docs/analise_eventos_de_negocio.md` | **Concluído** |
| 2     | Banco de Dados | `database/postgres/migrations/`, `database/mongodb/`            | Estruturas físicas de tabelas, coleções, índices, constraints e schemas.     | `docs/catalogo_fisico_dados.md`                                                                        | A Fazer       |
| 3     | Backend        | `modules/*/`, `contracts/*.md`                                  | Entidades de domínio, DTOs, regras de negócio, contratos de API e eventos.   | `docs/catalogo_logico_dados.md`                                                                        | A Fazer       |
| 4     | Frontend       | `apps/*/src/`, `desktop/*/src/`                                 | Componentes de UI, formulários, tabelas, filtros e campos utilizados.        | `docs/matriz_ui_dados.md`                                                                              | A Fazer       |
| 5     | Segurança      | `config/security/`, `modules/permissions/`, `modules/identity/` | Papéis, políticas de acesso, criptografia, logs de segurança, regras de MFA. | `docs/matriz_de_protecao_dados.md`                                                                     | A Fazer       |
| 6     | Testes         | `tests/`                                                        | Comportamento comprovado, casos de uso, exemplos válidos e inválidos.        | `docs/evidencias_de_comportamento.md`                                                                  | A Fazer       |
| 7     | Infraestrutura | `infra/`, `skaffold.yaml`, `*.dockerfile`, `cloudbuild.yaml`    | Ambientes, dependências, configuração de deploy e orquestração.              | `docs/mapa_operacional_infra.md`                                                                       | A Fazer       |
| 8     | Lacunas        | Comparação cruzada de todos os artefatos acima.                 | Inconsistências, divergências e funcionalidades faltantes.                   | `docs/registro_de_lacunas.md` (Backlog Obrigatório)                                                    | A Fazer       |

## 7.2 Estratégia de Comparação

A análise seguirá uma abordagem de validação cruzada para identificar divergências entre o que está documentado, o que está implementado e o que é testado. Toda divergência será registrada no `docs/registro_de_lacunas.md`. As principais comparações serão:

- **Documentação vs. Código:** O comportamento descrito nos `contracts` e `docs` corresponde à implementação nos `modules`?
- **Migration vs. ORM/Modelo:** A estrutura da tabela no banco (`migrations`) é idêntica à definição no código (e.g., Pydantic models, SQLAlchemy models)?
- **API vs. Frontend:** Os formulários e componentes no frontend (`apps`) consomem e enviam os dados conforme o contrato da API exposto pelo backend?
- **Validação (Frontend vs. Backend):** As regras de validação do frontend são um espelho das validações mandatórias no backend?
- **Permissão vs. Endpoint:** O acesso a cada endpoint é protegido pelas regras de permissão definidas na `permissions_enforcement_matrix.json`?
- **Dado Sensível vs. Criptografia:** Os campos marcados como sensíveis (e.g., dados de saúde, documentos pessoais) possuem uma estratégia de criptografia em repouso e em trânsito?
- **Teste vs. Implementação:** Os testes cobrem os cenários de sucesso, falha e borda descritos nos requisitos e implementados no código?

Este plano servirá como guia para as próximas fases da análise.
