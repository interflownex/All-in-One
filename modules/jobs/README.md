# Jobs

Curriculos do usuario final, importacao rastreavel da CTPS Digital PDF, experiencias autodeclaradas, vagas e candidaturas com acesso Business controlado.

## Responsabilidade

Este microservico e isolado por dominio, mas toda criacao mantem `user_id`
associado ao All-in-One ID. Operacoes mutaveis sao auditadas e exigem o
cabecalho `X-Actor-User-Id`, salvo o autorregistro inicial em Identity.

## Entidades

`resumes`, `employment_records`, `resume_documents`, `job_postings`, `applications`, `resume_access_logs`.

## Execucao

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

O contrato HTTP esta em `OPENAPI.yaml`; os controles especificos estao
descritos em `CONTRACT.md` e `SECURITY.md`.
