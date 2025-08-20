# Script para desinstalar el servicio de Docker Compose
# Requiere ejecutar como Administrador

# Verificar si se ejecuta como administrador
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "Este script debe ejecutarse como Administrador" -ForegroundColor Red
    Write-Host "Presiona cualquier tecla para salir..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

$serviceName = "ServerRnpDockerCompose"
$serviceDisplayName = "Server RNP Docker Compose"
$workingDirectory = "c:\Users\desarrollos\Desktop\Server-Rnp"

Write-Host "Desinstalando servicio de Windows para Docker Compose..." -ForegroundColor Yellow

# Verificar si el servicio existe
$existingService = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
if (-not $existingService) {
    Write-Host "El servicio $serviceName no existe." -ForegroundColor Yellow
} else {
    Write-Host "Servicio encontrado: $($existingService.DisplayName)" -ForegroundColor Green
    
    # Detener el servicio si esta ejecutandose
    if ($existingService.Status -eq 'Running') {
        Write-Host "Deteniendo el servicio..." -ForegroundColor Yellow
        try {
            # Primero intentar parar los contenedores Docker
            Set-Location $workingDirectory
            docker-compose down
            Write-Host "Contenedores Docker detenidos" -ForegroundColor Green
        } catch {
            Write-Host "Advertencia: No se pudieron detener los contenedores Docker" -ForegroundColor Yellow
        }
        
        Stop-Service -Name $serviceName -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 3
    }
    
    # Eliminar el servicio
    Write-Host "Eliminando el servicio..." -ForegroundColor Yellow
    try {
        $deleteResult = sc.exe delete $serviceName
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Servicio eliminado exitosamente" -ForegroundColor Green
        } else {
            Write-Host "Error al eliminar el servicio. Codigo de salida: $LASTEXITCODE" -ForegroundColor Red
        }
    } catch {
        Write-Host "Error al eliminar el servicio: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Eliminar scripts de servicio
$startScriptPath = "$workingDirectory\start-docker-service.bat"
$stopScriptPath = "$workingDirectory\stop-docker-service.bat"

if (Test-Path $startScriptPath) {
    Remove-Item $startScriptPath -Force
    Write-Host "Script de inicio eliminado: $startScriptPath" -ForegroundColor Green
}

if (Test-Path $stopScriptPath) {
    Remove-Item $stopScriptPath -Force
    Write-Host "Script de parada eliminado: $stopScriptPath" -ForegroundColor Green
}

Write-Host "" -ForegroundColor Green
Write-Host "=== DESINSTALACION COMPLETADA ===" -ForegroundColor Green
Write-Host "El servicio '$serviceDisplayName' ha sido desinstalado." -ForegroundColor Green
Write-Host "" -ForegroundColor Green
Write-Host "Para volver a instalar el servicio, ejecuta: .\install-service.ps1" -ForegroundColor Cyan
Write-Host "" -ForegroundColor Green

Write-Host "Presiona cualquier tecla para continuar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")