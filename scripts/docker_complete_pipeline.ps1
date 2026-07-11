#!/usr/bin/env pwsh
# Script executável para completar build, tag e push
# Execução: .\scripts\docker_complete_pipeline.ps1

Set-Location "C:\Users\ereta\.codex\worktrees\all-in-one"

Write-Host "`n🚀 DOCKER PIPELINE: Build → Tag → Push" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Verificar se o Docker está rodando
try {
    docker ps >$null 2>&1
    Write-Host "✅ Docker daemon ativo`n" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker não está respondendo. Inicie Docker Desktop." -ForegroundColor Red
    exit 1
}

# Etapa 1: Verificar build em andamento
Write-Host "📊 Etapa 1: Verificando status do build..." -ForegroundColor Yellow
$buildingImages = docker ps --filter "status=running" --format "{{.Image}}" | Select-String "all-in-one"
if ($buildingImages) {
    Write-Host "⏳ Construção ainda em andamento. Aguardando..." -ForegroundColor Yellow
    Write-Host "   (Isso pode levar vários minutos - Continue em outro terminal se precisar)" -ForegroundColor Gray
}

# Etapa 2: Listar imagens construídas
Write-Host "`n📋 Etapa 2: Imagens construídas:" -ForegroundColor Yellow
$images = @(docker images --filter "reference=all-in-one*" --format "{{.Repository}}:{{.Tag}}" 2>$null)
if ($images.Count -eq 0) {
    Write-Host "   ⚠️  Nenhuma imagem encontrada. Aguarde o build terminar." -ForegroundColor Yellow
    exit 1
}
$images | ForEach-Object { Write-Host "   ✅ $_" -ForegroundColor Green }

# Etapa 3: Fazer tag com username
Write-Host "`n🏷️  Etapa 3: Tagueando imagens com 'andersoninterflow'..." -ForegroundColor Yellow
$tagCount = 0
$images | ForEach-Object {
    $local = $_
    $module = ($local -split "/")[-1] -replace ":latest", ""
    $cleanName = $module -replace "all-in-one-", ""
    $remote = "andersoninterflow/all-in-one-${cleanName}"

    docker tag "$local" "$remote:latest" 2>$null
    if ($?) {
        Write-Host "   ✅ $module" -ForegroundColor Green
        $tagCount++
    }
}
Write-Host "   Total: $tagCount imagens tagueadas`n" -ForegroundColor Cyan

# Etapa 4: Push para Docker Hub
Write-Host "📤 Etapa 4: Enviando para Docker Hub..." -ForegroundColor Yellow
$pushCount = 0
$images | ForEach-Object {
    $module = ($_ -split "/")[-1] -replace ":latest", ""
    $cleanName = $module -replace "all-in-one-", ""
    $remote = "andersoninterflow/all-in-one-${cleanName}:latest"

    Write-Host "   📤 all-in-one-$module..." -ForegroundColor Cyan -NoNewline

    $output = docker push "$remote" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " ✅" -ForegroundColor Green
        $pushCount++
    } else {
        Write-Host " ❌" -ForegroundColor Red
        Write-Host "      Erro: $output" -ForegroundColor Red
    }
}

# Resumo final
Write-Host "`n" + ("="*60) -ForegroundColor Cyan
Write-Host "✨ CONCLUÍDO" -ForegroundColor Green
Write-Host ("="*60) -ForegroundColor Cyan
Write-Host "✅ Imagens processadas: $pushCount" -ForegroundColor Green
Write-Host "🔗 Repositório: https://hub.docker.com/u/andersoninterflow" -ForegroundColor Blue
Write-Host "`n"

# Etapa 5: Sincronizar com Git
Write-Host "🔄 Etapa 5: Sincronizando com o repositorio Git..." -ForegroundColor Yellow
$activity = "chore(docker): tag and push images to Docker Hub ($pushCount pushed)"
try {
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts/git_auto_sync.ps1" -Activity $activity
} catch {
    Write-Host "   ⚠️  Falha na sincronizacao automatica com o Git. Execute manualmente se necessario." -ForegroundColor Yellow
}
