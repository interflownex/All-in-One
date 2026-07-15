# GED ECM

Documentos, OCR, versoes, cofre privado KMS, assinatura, retencao e indexacao.

## Responsabilidade

Este microservico e isolado por dominio, mas toda criacao mantem `user_id`
associado ao All-in-One ID. Operacoes mutaveis sao auditadas e exigem o
cabecalho `X-Actor-User-Id`, salvo o autorregistro inicial em Identity.

## Entidades

`folders`, `documents`, `versions`, `retention_policies`.

`documents` exige `storage_provider`, `storage_bucket`,
`storage_key`, `file_sha256`, `kms_key_version`, `filename` e
`content_type`; `versions` registra novas revisoes append-only com
hash, chave privada e versao KMS.

## Execucao

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

O contrato HTTP esta em `OPENAPI.yaml`; os controles especificos estao
descritos em `CONTRACT.md` e `SECURITY.md`.
