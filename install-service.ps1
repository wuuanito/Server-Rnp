# Script para instalar Docker Compose como servicio de Windows
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
$serviceDescription = "Servicio para ejecutar automaticamente los contenedores Docker de Server RNP"
$workingDirectory = "c:\Users\desarrollos\Desktop\Server-Rnp"
$dockerComposePath = "docker-compose.yml"

Write-Host "Instalando servicio de Windows para Docker Compose..." -ForegroundColor Green

# Verificar si Docker esta instalado
try {
    $dockerVersion = docker --version
    Write-Host "Docker encontrado: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Docker no esta instalado o no esta en el PATH" -ForegroundColor Red
    exit 1
}

# Verificar si Docker Compose esta instalado
try {
    $composeVersion = docker-compose --version
    Write-Host "Docker Compose encontrado: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Docker Compose no esta instalado o no esta en el PATH" -ForegroundColor Red
    exit 1
}

# Verificar si el archivo docker-compose.yml existe
if (-not (Test-Path "$workingDirectory\$dockerComposePath")) {
    Write-Host "Error: No se encontro el archivo docker-compose.yml en $workingDirectory" -ForegroundColor Red
    exit 1
}

# Verificar si el servicio ya existe
$existingService = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
if ($existingService) {
    Write-Host "El servicio $serviceName ya existe. Deteniendolo y eliminandolo..." -ForegroundColor Yellow
    Stop-Service -Name $serviceName -Force -ErrorAction SilentlyContinue
    sc.exe delete $serviceName
    Start-Sleep -Seconds 2
}

# Crear el script de inicio del servicio
$startScript = @"
@echo off
cd /d "$workingDirectory"
docker-compose up
"@

$startScriptPath = "$workingDirectory\start-docker-service.bat"
$startScript | Out-File -FilePath $startScriptPath -Encoding ASCII

# Crear el script de parada del servicio
$stopScript = @"
@echo off
cd /d "$workingDirectory"
docker-compose down
"@

$stopScriptPath = "$workingDirectory\stop-docker-service.bat"
$stopScript | Out-File -FilePath $stopScriptPath -Encoding ASCII

Write-Host "Scripts de servicio creados en:" -ForegroundColor Green
Write-Host "  - $startScriptPath" -ForegroundColor Cyan
Write-Host "  - $stopScriptPath" -ForegroundColor Cyan

# Crear el servicio usando sc.exe
try {
    $createResult = sc.exe create $serviceName binPath= "cmd.exe /c `"$startScriptPath`"" DisplayName= "$serviceDisplayName" start= auto
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Servicio creado exitosamente" -ForegroundColor Green
        
        # Configurar descripcion del servicio
        sc.exe description $serviceName "$serviceDescription"
        
        # Configurar el servicio para reiniciarse automaticamente en caso de fallo
        sc.exe failure $serviceName reset= 86400 actions= restart/5000/restart/5000/restart/5000
        
        Write-Host "Configurando el servicio..." -ForegroundColor Green
        
        # Intentar iniciar el servicio
        Write-Host "Iniciando el servicio..." -ForegroundColor Green
        Start-Service -Name $serviceName
        
        Write-Host "" -ForegroundColor Green
        Write-Host "=== INSTALACION COMPLETADA ==="  -ForegroundColor Green
        Write-Host "El servicio '$serviceDisplayName' ha sido instalado y iniciado." -ForegroundColor Green
        Write-Host "" -ForegroundColor Green
        Write-Host "Comandos utiles:" -ForegroundColor Yellow
        Write-Host "  - Iniciar servicio: Start-Service -Name $serviceName" -ForegroundColor Cyan
        Write-Host "  - Detener servicio: Stop-Service -Name $serviceName" -ForegroundColor Cyan
        Write-Host "  - Estado del servicio: Get-Service -Name $serviceName" -ForegroundColor Cyan
        Write-Host "  - Desinstalar servicio: .\uninstall-service.ps1" -ForegroundColor Cyan
        Write-Host "" -ForegroundColor Green
        
    } else {
        Write-Host "Error al crear el servicio. Codigo de salida: $LASTEXITCODE" -ForegroundColor Red
        exit 1
    }
    
} catch {
    Write-Host "Error al crear el servicio: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "Presiona cualquier tecla para continuar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")