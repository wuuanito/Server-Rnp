#!/bin/bash

# Script de instalación para el Monitor de Botes Ponderal
# Ejecutar con: sudo bash install_ponderal_monitor.sh

set -e

echo "=== Instalador del Monitor de Botes (Ponderal y Expulsados) ===
echo

# Verificar que se ejecuta como root
if [ "$EUID" -ne 0 ]; then
    echo "Error: Este script debe ejecutarse como root (usar sudo)"
    exit 1
fi

# Verificar que estamos en una Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "Advertencia: No se detectó una Raspberry Pi"
    read -p "¿Continuar de todos modos? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "1. Actualizando sistema..."
apt update
apt upgrade -y

echo "2. Instalando dependencias..."
apt install -y python3 python3-pip python3-rpi.gpio
pip3 install requests

echo "3. Creando directorio de trabajo..."
INSTALL_DIR="/root/ponderal-monitor"
mkdir -p "$INSTALL_DIR"

echo "4. Copiando archivos..."
# Copiar el script principal
cp raspberry_botes_monitor.py "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/raspberry_botes_monitor.py"

# Crear archivo de configuración
cat > "$INSTALL_DIR/config.py" << EOF
# Configuración del Monitor de Botes

# URL del servidor API (cambiar por la IP/URL correcta)
API_BASE_URL = "http://192.168.1.100:3000/api"  # CAMBIAR ESTA IP

# Pines GPIO para detectar pulsos
GPIO_PIN_PONDERAL = 23    # Pin para botes ponderal
GPIO_PIN_EXPULSADOS = 22  # Pin para botes expulsados

# Tiempo de debounce en segundos
DEBOUNCE_TIME = 0.5

# Timeout para peticiones HTTP
REQUEST_TIMEOUT = 5
EOF

echo "5. Configurando permisos..."
chown -R root:root "$INSTALL_DIR"

# Configurar permisos GPIO para root
chmod 666 /dev/gpiomem 2>/dev/null || true

echo "6. Instalando servicio systemd..."
cp ponderal-monitor.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable ponderal-monitor.service

echo "7. Creando directorio de logs..."
touch /root/botes_monitor.log
chown root:root /root/botes_monitor.log

echo
echo "=== Instalación completada ==="
echo
echo "IMPORTANTE: Antes de iniciar el servicio:"
echo "1. Edita el archivo de configuración:"
echo "   sudo nano $INSTALL_DIR/config.py"
echo "2. Cambia la URL del API por la IP correcta de tu servidor"
echo
echo "Para iniciar el servicio:"
echo "   sudo systemctl start ponderal-monitor"
echo
echo "Para ver el estado:"
echo "   sudo systemctl status ponderal-monitor"
echo
echo "Para ver los logs:"
echo "   journalctl -u ponderal-monitor -f"
echo "   tail -f /root/botes_monitor.log"
echo
echo "Para detener el servicio:"
echo "   sudo systemctl stop ponderal-monitor"
echo
echo "Para desinstalar:"
echo "   sudo systemctl stop ponderal-monitor"
echo "   sudo systemctl disable ponderal-monitor"
echo "   sudo rm /etc/systemd/system/ponderal-monitor.service"
echo "   sudo rm -rf $INSTALL_DIR"
echo