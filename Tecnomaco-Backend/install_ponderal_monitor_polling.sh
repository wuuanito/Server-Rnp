#!/bin/bash

# Script de instalación del Monitor de Botes (Versión Polling)
# Para Raspberry Pi con estructura de directorios en /root

set -e

echo "=== Instalación del Monitor de Botes (Versión Polling) ==="
echo "Esta versión usa polling en lugar de interrupciones GPIO"
echo "para evitar problemas con 'Failed to add edge detection'"
echo

# Verificar que se ejecuta como root
if [ "$EUID" -ne 0 ]; then
    echo "Error: Este script debe ejecutarse como root"
    echo "Uso: sudo $0"
    exit 1
fi

# Crear directorio de instalación
echo "Creando directorio de instalación..."
mkdir -p /root/ponderal-monitor

# Copiar archivos
echo "Copiando archivos..."
cp raspberry_botes_monitor_polling.py /root/ponderal-monitor/
cp config.py /root/ponderal-monitor/
cp ponderal-monitor.service /etc/systemd/system/

# Establecer permisos
echo "Configurando permisos..."
chown -R root:root /root/ponderal-monitor
chmod +x /root/ponderal-monitor/raspberry_botes_monitor_polling.py

# Crear archivo de log
echo "Configurando archivo de log..."
touch /root/botes_monitor.log
chown root:root /root/botes_monitor.log
chmod 644 /root/botes_monitor.log

# Verificar permisos GPIO
echo "Verificando permisos GPIO..."
if [ -e "/dev/gpiomem" ]; then
    chmod 666 /dev/gpiomem
    echo "Permisos GPIO configurados"
else
    echo "Advertencia: /dev/gpiomem no encontrado"
fi

# Verificar acceso a /sys/class/gpio
if [ -d "/sys/class/gpio" ]; then
    echo "Directorio GPIO del sistema encontrado"
else
    echo "Advertencia: /sys/class/gpio no encontrado"
fi

# Crear servicio systemd modificado para polling
echo "Creando servicio systemd para versión polling..."
cat > /etc/systemd/system/ponderal-monitor-polling.service << 'EOF'
[Unit]
Description=Monitor de Botes Ponderal y Expulsados (Polling)
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/root/ponderal-monitor
ExecStart=/usr/bin/python3 /root/ponderal-monitor/raspberry_botes_monitor_polling.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Variables de entorno
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# Recargar systemd
echo "Recargando configuración systemd..."
systemctl daemon-reload

# Habilitar servicio
echo "Habilitando servicio..."
systemctl enable ponderal-monitor-polling.service

echo
echo "=== Instalación completada ==="
echo
echo "El monitor de botes (versión polling) ha sido instalado exitosamente."
echo
echo "Comandos útiles:"
echo "  Iniciar servicio:    systemctl start ponderal-monitor-polling"
echo "  Detener servicio:    systemctl stop ponderal-monitor-polling"
echo "  Estado del servicio: systemctl status ponderal-monitor-polling"
echo "  Ver logs:            journalctl -u ponderal-monitor-polling -f"
echo "  Ver archivo de log:  tail -f /root/botes_monitor.log"
echo
echo "Configuración:"
echo "  Directorio:          /root/ponderal-monitor"
echo "  Archivo de log:      /root/botes_monitor.log"
echo "  Configuración:       /root/ponderal-monitor/config.py"
echo
echo "Para iniciar el servicio ahora:"
echo "  systemctl start ponderal-monitor-polling"
echo
echo "NOTA: Esta versión usa polling en lugar de interrupciones GPIO"
echo "      para evitar problemas de 'Failed to add edge detection'"
echo