@echo off
REM Script para desinstalar el servicio de Docker Compose
REM Requiere ejecutar como Administrador

echo ========================================
echo  Desinstalador de Servicio Server RNP
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
set WORKING_DIR=%~dp0

echo Verificando si el servicio existe...
sc query "%SERVICE_NAME%" >nul 2>&1
if %errorLevel% neq 0 (
    echo El servicio '%SERVICE_NAME%' no existe.
    goto :cleanup_files
)

echo Servicio encontrado: %SERVICE_DISPLAY_NAME%

echo.
echo Deteniendo contenedores Docker...
cd /d "%WORKING_DIR%"
docker-compose down
if %errorLevel% equ 0 (
    echo Contenedores Docker detenidos correctamente
) else (
    echo ADVERTENCIA: No se pudieron detener los contenedores Docker
)

echo.
echo Deteniendo el servicio...
sc stop "%SERVICE_NAME%" >nul 2>&1
if %errorLevel% equ 0 (
    echo Servicio detenido
) else (
    echo El servicio ya estaba detenido o no se pudo detener
)

echo Esperando a que el servicio se detenga completamente...
timeout /t 5 /nobreak >nul

echo Eliminando el servicio...
sc delete "%SERVICE_NAME%"
if %errorLevel% equ 0 (
    echo Servicio eliminado correctamente
) else (
    echo ERROR: No se pudo eliminar el servicio
)

:cleanup_files
echo.
echo Eliminando scripts de servicio...

if exist "%WORKING_DIR%start-docker-service.bat" (
    del "%WORKING_DIR%start-docker-service.bat"
    echo Script de inicio eliminado
)

if exist "%WORKING_DIR%stop-docker-service.bat" (
    del "%WORKING_DIR%stop-docker-service.bat"
    echo Script de parada eliminado
)

echo.
echo ========================================
echo   DESINSTALACION COMPLETADA
echo ========================================
echo.
echo El servicio '%SERVICE_DISPLAY_NAME%' ha sido desinstalado.
echo.
echo Para volver a instalar el servicio:
echo   - Ejecuta: install-service.bat (como Administrador)
echo.
pause