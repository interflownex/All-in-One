# 🐳 DOCKER PUSH - STATUS CONSOLIDADO

**Data**: 2026-06-04  
**Projeto**: All-in-One (14 microserviços)  
**Usuário Docker Hub**: andersoninterflow  
**Repositório**: https://hub.docker.com/u/andersoninterflow

---

## ✅ SUCESSO (8/14) - Imagens Publicadas

| #   | Microserviço | Status       | URL                                                               |
| --- | ------------ | ------------ | ----------------------------------------------------------------- |
| 1   | api-hub      | ✅ Publicado | https://hub.docker.com/r/andersoninterflow/all-in-one-api-hub     |
| 2   | finance      | ✅ Publicado | https://hub.docker.com/r/andersoninterflow/all-in-one-finance     |
| 3   | identity     | ✅ Publicado | https://hub.docker.com/r/andersoninterflow/all-in-one-identity    |
| 4   | delivery     | ✅ Publicado | https://hub.docker.com/r/andersoninterflow/all-in-one-delivery    |
| 5   | services     | ✅ Publicado | https://hub.docker.com/r/andersoninterflow/all-in-one-services    |
| 6   | marketplace  | ✅ Publicado | https://hub.docker.com/r/andersoninterflow/all-in-one-marketplace |
| 7   | erp          | ✅ Publicado | https://hub.docker.com/r/andersoninterflow/all-in-one-erp         |
| 8   | jobs         | ✅ Publicado | https://hub.docker.com/r/andersoninterflow/all-in-one-jobs        |

---

## ⏳ EM RETENTATIVA (6/14) - Última Tentativa em Andamento

| #   | Microserviço      | Tentativas | Status           |
| --- | ----------------- | ---------- | ---------------- |
| 9   | wms               | 4+         | ⏳ Retentando... |
| 10  | tms               | 4+         | ⏳ Retentando... |
| 11  | mobility          | 3+         | ⏳ Retentando... |
| 12  | crm               | 3+         | ⏳ Retentando... |
| 13  | health            | 3+         | ⏳ Retentando... |
| 14  | outbox-dispatcher | 3+         | ⏳ Retentando... |

**ETA**: ~4 minutos (retentativa sequencial com delay de 30s)

---

## 📊 ESTATÍSTICAS

- **Build Docker**: ✅ 14/14 (100%)
- **Push Sucesso**: ✅ 8/14 (57%)
- **Push Pendente**: ⏳ 6/14 (43%)
- **Erro Comum**: TLS handshake timeout com Docker Hub

---

## 🔧 Comandos para Testar

```powershell
# Testar pull de uma imagem publicada
docker pull andersoninterflow/all-in-one-api-hub:latest

# Listar todas as imagens do seu repositório
docker search andersoninterflow

# Inspecionar uma imagem publicada
docker inspect andersoninterflow/all-in-one-finance:latest
```

---

## 📝 Próximos Passos

1. ⏳ Aguardar conclusão da retentativa final (6/14)
2. ✅ Se falharem novamente, as 8 imagens publicadas são funcionais
3. ✅ Sincronizar alterações ao Git com `scripts/git_auto_sync.ps1`
4. ✅ Executar `docker compose up --pull always` para usar imagens de produção
5. ✅ Considerar usar Docker Registry alternativo (GitHub Container Registry, etc) para os 6 restantes

---

**Última Atualização**: 2026-06-04 ~13:50 UTC  
**Job Ativo**: job_1780581255_23 (Retentativa sequencial com delay)
