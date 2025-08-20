@echo off
echo ========================================
echo   Server RNP - Parar Docker Services
echo ========================================
echo.

:: Verificar si Docker está instalado
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker no está instalado o no está en el PATH
    pause
    exit /b 1
)

echo Parando servicios de Server RNP...
echo.

:: Mostrar servicios actuales
echo 📊 Servicios actuales:
docker-compose ps
echo.

:: Parar servicios
echo 🛑 Parando todos los servicios...
docker-compose down
if %errorlevel% neq 0 (
    echo ERROR: Falló al parar los servicios
    pause
    exit /b 1
)

echo.
echo ✅ Todos los servicios han sido parados
echo.

:: Preguntar si eliminar volúmenes
set /p "remove_volumes=¿Deseas eliminar también los volúmenes de datos? (y/N): "
if /i "%remove_volumes%"=="y" (
    echo.
    echo 🗑️ Eliminando volúmenes de datos...
    docker-compose down -v
    echo ✅ Volúmenes eliminados
) else (
    echo 💾 Volúmenes de datos conservados
)

echo.
:: Preguntar si limpiar imágenes
set /p "remove_images=¿Deseas eliminar las imágenes Docker? (y/N): "
if /i "%remove_images%"=="y" (
    echo.
    echo 🧹 Eliminando imágenes...
    docker-compose down --rmi all
    echo ✅ Imágenes eliminadas
)

echo.
echo 📝 Para volver a iniciar los servicios, ejecuta:
echo    start-services.bat
echo.
echo Presiona cualquier tecla para salir...
pause >nul