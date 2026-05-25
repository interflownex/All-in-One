# Jobs: Curriculo E CTPS Digital

## Jornada Do Usuario

1. O usuario cria sua identidade por `POST /api/v1/identity/registrations`.
2. Com identidade autenticada, cria o curriculo em
   `POST /api/v1/jobs/resources/resumes`, escolhendo visibilidade
   `private` ou `business_recruiters`.
3. Pode adicionar experiencias, atividades informais e descricoes próprias em
   `employment_records`; esses itens sempre exibem o selo
   `self_declared_unverified`.
4. Pode importar a Carteira de Trabalho Digital em PDF em
   `POST /api/v1/jobs/resumes/{resume_id}/imports/ctps-digital`.
5. Pode rever seu proprio PDF importado em
   `GET /api/v1/jobs/resumes/{resume_id}/documents/{document_id}/content`.
6. Busca vagas publicadas por `GET /api/v1/jobs/vacancies` e registra
   candidatura em `applications`.

## Classificacao Visivel

| Origem | Selo exibido | Significado |
| --- | --- | --- |
| Informacao extraida do PDF CTPS importado | `validated_by_document_import` | O campo veio do documento cujo SHA-256 foi preservado. |
| Experiencia ou descricao digitada pelo usuario | `self_declared_unverified` | O campo foi declarado pelo titular e nao foi extraido do PDF. |

O campo `official_verification_status` nasce como
`not_verified_externally`. Um integrador autorizado futuro podera verificar
autenticidade externa do documento sem apagar a origem histórica de cada
informacao.

## Controle De Acesso

O candidato decide se o curriculo e pesquisavel por empresas. Os endpoints
`/recruiting/resumes` somente aceitam ator com:

- `X-Business-Id` de empresa cadastrada;
- `X-Business-Status: active`;
- papel `recruiter`, `hr_manager`, `administrator`, `owner` ou `auditor`;
- escopo `jobs:resumes:read` ou `jobs:manage`.

Toda abertura individual do curriculo cria `jobs.resume_access_logs`, tabela
append-only. O gateway assina esses atributos em producao para impedir que
cabecalhos sejam forjados fora da borda confiavel.

Recrutadores recebem somente os selos de procedencia; nunca recebem o PDF
CTPS ou sua chave de storage. O download do PDF e exclusivo do titular e gera
evento de auditoria `document_content_read`.

## Persistencia E Auditoria

`database/postgres/migrations/006_jobs_recruitment_ctps.sql` implementa
curriculos, documentos, experiencias, vagas, candidaturas e acessos. Uma
constraint impede classificar declaracao manual como documento importado.
PDFs sao armazenados em storage privado cifrado com AES-256-GCM; o banco
preserva referencia, hash, extracao e status, nunca publica o arquivo para
recrutadores. Em producao, `ALL_IN_ONE_DOCUMENT_ENCRYPTION_KEY` deve ser
provido por vault/KMS; a inicializacao falha sem esse segredo.
