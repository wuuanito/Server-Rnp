@echo off
REM Script para instalar Docker Compose como servicio de Windows
REM Requiere ejecutar como Administrador

echo ========================================
echo  Instalador de Servicio Server RNP
echo ========================================
echo.

REM Verificar privilegios de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Este script debe ejecutarse como Administrador
    echo.
    echo Haz clic derecho en el archivo y selecciona "Ejecutar como administrador"
    pause
    exit /b 1
)

set SERVICE_NAME=ServerRnpDockerCompose
set SERVICE_DISPLAY_NAME=Server RNP Docker Compose
set SERVICE_DESCRIPTION=Servicio para ejecutar automaticamente los contenedores Docker de Server RNP
set WORKING_DIR=%~dp0
set DOCKER_COMPOSE_FILE=%WORKING_DIR%docker-compose.yml

echo Verificando instalacion de Docker...
docker --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Docker no esta instalado o no esta en el PATH
    pause
    exit /b 1
)
echo Docker encontrado correctamente

echo Verificando instalacion de Docker Compose...
docker-compose --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Docker Compose no esta instalado o no esta en el PATH
    pause
    exit /b 1
)
echo Docker Compose encontrado correctamente

echo Verificando archivo docker-compose.yml...
if not exist "%DOCKER_COMPOSE_FILE%" (
    echo ERROR: No se encontro el archivo docker-compose.yml en %WORKING_DIR%
    pause
    exit /b 1
)
echo Archivo docker-compose.yml encontrado

echo.
echo Verificando si el servicio ya existe...
sc query "%SERVICE_NAME%" >nul 2>&1
if %errorLevel% equ 0 (
    echo El servicio ya existe. Deteniendolo y eliminandolo...
    sc stop "%SERVICE_NAME%" >nul 2>&1
    timeout /t 3 /nobreak >nul
    sc delete "%SERVICE_NAME%" >nul 2>&1
    timeout /t 2 /nobreak >nul
)

echo.
echo Creando scripts de servicio...

REM Crear script de inicio
echo @echo off > "%WORKING_DIR%start-docker-service.bat"
echo cd /d "%WORKING_DIR%" >> "%WORKING_DIR%start-docker-service.bat"
echo docker-compose up >> "%WORKING_DIR%start-docker-service.bat"

REM Crear script de parada
echo @echo off > "%WORKING_DIR%stop-docker-service.bat"
echo cd /d "%WORKING_DIR%" >> "%WORKING_DIR%stop-docker-service.bat"
echo docker-compose down >> "%WORKING_DIR%stop-docker-service.bat"

echo Scripts creados correctamente

echo.
echo Creando servicio de Windows...
sc create "%SERVICE_NAME%" binPath= "cmd.exe /c \"%WORKING_DIR%start-docker-service.bat\"" DisplayName= "%SERVICE_DISPLAY_NAME%" start= auto
if %errorLevel% neq 0 (
    echo ERROR: No se pudo crear el servicio
    pause
    exit /b 1
)

echo Configurando descripcion del servicio...
sc description "%SERVICE_NAME%" "%SERVICE_DESCRIPTION%"

echo Configurando reinicio automatico en caso de fallo...
sc failure "%SERVICE_NAME%" reset= 86400 actions= restart/5000/restart/5000/restart/5000

echo.
echo Iniciando el servicio...
sc start "%SERVICE_NAME%"
if %errorLevel% neq 0 (
    echo ADVERTENCIA: El servicio se creo pero no se pudo iniciar automaticamente
    echo Puedes iniciarlo manualmente con: sc start "%SERVICE_NAME%"
) else (
    echo Servicio iniciado correctamente
)

echo.
echo ========================================
echo   INSTALACION COMPLETADA
echo ========================================
echo.
echo El servicio '%SERVICE_DISPLAY_NAME%' ha sido instalado.
echo.
echo Comandos utiles:
echo   - Iniciar servicio:    sc start "%SERVICE_NAME%"
echo   - Detener servicio:    sc stop "%SERVICE_NAME%"
echo   - Estado del servicio: sc query "%SERVICE_NAME%"
echo   - Desinstalar:         uninstall-service.bat
echo.
echo El servicio se iniciara automaticamente al reiniciar Windows.
echo.
pause