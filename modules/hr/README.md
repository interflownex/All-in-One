# HR HCM ATS LMS

Colaboradores, folha, ponto, recrutamento, treinamento e saude ocupacional.

## Responsabilidade

Este microservico e isolado por dominio, mas toda criacao mantem `user_id`
associado ao All-in-One ID. Operacoes mutaveis sao auditadas e exigem o
cabecalho `X-Actor-User-Id`, salvo o autorregistro inicial em Identity.

## Entidades

`employees`, `payroll_runs`, `candidates`, `courses`, `occupational_records`.

`employees` registra admissao; `payroll_runs` fecha folha com
aprovacao MFA; `courses` acompanha treinamento obrigatorio ate a
conclusao auditavel.

## Execucao

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

O contrato HTTP esta em `OPENAPI.yaml`; os controles especificos estao
descritos em `CONTRACT.md` e `SECURITY.md`.
