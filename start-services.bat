@echo off
echo ========================================
echo    Server RNP - Docker Services
echo ========================================
echo.

:: Verificar si Docker está instalado
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker no está instalado o no está en el PATH
    echo Por favor instala Docker Desktop y reinicia el terminal
    pause
    exit /b 1
)

:: Verificar si Docker está ejecutándose
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker no está ejecutándose
    echo Por favor inicia Docker Desktop
    pause
    exit /b 1
)

echo ✓ Docker está disponible
echo.

:: Verificar si existe el archivo .env
if not exist ".env" (
    echo ADVERTENCIA: No se encontró el archivo .env
    echo Copiando .env.example como .env...
    copy ".env.example" ".env" >nul
    echo ✓ Archivo .env creado
    echo.
    echo IMPORTANTE: Revisa y ajusta las variables en .env antes de continuar
    echo Presiona cualquier tecla para continuar o Ctrl+C para cancelar
    pause >nul
)

echo Iniciando servicios...
echo.

:: Construir y levantar servicios
echo 🔨 Construyendo imágenes...
docker-compose build
if %errorlevel% neq 0 (
    echo ERROR: Falló la construcción de las imágenes
    pause
    exit /b 1
)

echo.
echo 🚀 Levantando servicios...
docker-compose up -d
if %errorlevel% neq 0 (
    echo ERROR: Falló el inicio de los servicios
    pause
    exit /b 1
)

echo.
echo ⏳ Esperando que los servicios estén listos...
timeout /t 10 /nobreak >nul

echo.
echo 📊 Estado de los servicios:
docker-compose ps

echo.
echo ========================================
echo           SERVICIOS INICIADOS
echo ========================================
echo.
echo 🌐 Acceso a los servicios:
echo   • Página principal:    http://localhost/
echo   • Auth Service:        http://localhost/auth/
echo   • Cremer Backend:      http://localhost/cremer/
echo   • Tecnomaco Backend:   http://localhost/tecnomaco/
echo   • Servidor RPS:        http://localhost/rps/
echo.
echo 🔧 Acceso directo:
echo   • Auth Service:        http://localhost:4001
echo   • Cremer Backend:      http://localhost:3002
echo   • Tecnomaco Backend:   http://localhost:3005
echo   • Servidor RPS:        http://localhost:4000
echo.
echo 💾 Bases de datos:
echo   • MySQL Auth:          localhost:3307
echo   • MySQL Cremer:        localhost:3308
echo   • MySQL Tecnomaco:     localhost:3309
echo.
echo 📝 Comandos útiles:
echo   • Ver logs:            docker-compose logs -f
echo   • Parar servicios:     docker-compose down
echo   • Reiniciar:           docker-compose restart
echo.
echo ✅ Todos los servicios están ejecutándose
echo Presiona cualquier tecla para salir...
pause >nul