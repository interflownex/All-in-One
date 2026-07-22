# WSL 2 + Docker Otimizado - Configuração Aplicada

**Data**: 2026-06-04  
**Idioma**: Português Brasileiro

---

## ✅ Configurações Aplicadas

### 1. WSL 2 Update

- ✅ Verificado - Versão mais recente instalada
- ✅ Subsistema Windows para Linux atualizado

### 2. Arquivo .wslconfig

**Localização**: `C:\Users\ereta\.wslconfig`

**Configurações Aplicadas**:

- **Memória**: 8 GB (ajustável)
- **CPUs**: 4 processadores
- **Swap**: 2 GB
- **Systemd**: Ativado (para melhor controle de serviços)
- **IPv6**: Ativado
- **Firewall integrado**: Ativado
- **Modo de rede**: Mirrored (experimental)
- **DNS Tunneling**: Ativado

### 3. Docker Daemon (daemon.json)

**Localização**: `C:\ProgramData\Docker\config\daemon.json`

**Otimizações Aplicadas**:

- **Log Driver**: json-file (melhor performance)
- **Log Format**: json (estruturado)
- **Max Downloads Simultâneos**: 5
- **Max Uploads Simultâneos**: 5
- **DNS Primários**:
  - 8.8.8.8 (Google)
  - 8.8.4.4 (Google)
  - 1.1.1.1 (Cloudflare)
- **Live Restore**: Ativado (preserva containers após restart)
- **Storage Driver**: windowsfilter (padrão Windows)
- **Registry Mirrors**: mirror.aliyun.com (cache chinês)
- **Builder GC**: Configurado com limpeza automática
- **Features**:
  - CDI: Ativado
  - Containerd Snapshotter: Desativado

### 4. Labels Docker

```json
"labels": [
  "os=windows",
  "platform=docker-desktop-wsl2"
]
```

---

## 🔄 Próximas Etapas

1. ✅ Reiniciar Docker Desktop (em andamento)
2. ✅ Verificar status: `docker info`
3. ✅ Testar push das 6 imagens falhadas
4. ✅ Sincronizar ao Git

---

## 📊 Benefícios da Configuração

| Aspecto            | Benefício                            |
| ------------------ | ------------------------------------ |
| **Performance**    | WSL 2 com 4 cores + 8GB RAM          |
| **Confiabilidade** | Live restore ativado                 |
| **Rede**           | DNS múltiplos + mirror de registry   |
| **Logs**           | JSON estruturado para melhor análise |
| **Construção**     | Builder GC com limpeza automática    |

---

## 🛠️ Comandos Úteis

```powershell
# Verificar configuração WSL
wsl --list --verbose

# Testar Docker
docker ps
docker images

# Limpar recursos
docker system prune -a

# Verificar status
docker info
```

---

## 📝 Notas Importantes

- A configuração `.wslconfig` requer **reinicialização completa do WSL** para entrar em vigor
- O `daemon.json` requer **reinício do Docker Desktop**
- A memória é alocada dinamicamente até 8 GB
- Swap ajuda em situações de pressão de memória

---

**Status**: ✅ Configuração Completa  
**Próximo**: Aguardar estabilização do Docker e retentar push das 6 imagens
