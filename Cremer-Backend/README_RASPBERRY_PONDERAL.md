# Monitor de Botes - Raspberry Pi

Este sistema permite detectar automáticamente pulsos en los GPIO 23 (botes ponderal) y GPIO 22 (botes expulsados) de una Raspberry Pi e incrementar los contadores correspondientes en la orden de fabricación activa a través del API REST.

## Características

- ✅ Detección automática de pulsos en GPIO 23 (botes ponderal)
- ✅ Detección automática de pulsos en GPIO 22 (botes expulsados)
- ✅ Incremento automático de contadores vía API REST
- ✅ Detección automática de orden activa
- ✅ Monitoreo continuo del estado de la orden
- ✅ Sistema de logs detallado
- ✅ Servicio systemd para ejecución automática
- ✅ Manejo de errores y reconexión automática
- ✅ Debounce independiente para cada GPIO

## Requisitos

- Raspberry Pi con Raspbian/Raspberry Pi OS
- Python 3.7 o superior
- Acceso a GPIO (usuario en grupo `gpio`)
- Conexión de red al servidor del API
- Sensor/dispositivo conectado al GPIO 23

## Instalación

### Opción 1: Instalación automática (recomendada)

1. Copia los archivos a la Raspberry Pi:
```bash
scp raspberry_ponderal_monitor.py root@<IP_RASPBERRY>:/root/
scp ponderal-monitor.service root@<IP_RASPBERRY>:/root/
scp install_ponderal_monitor.sh root@<IP_RASPBERRY>:/root/
```

2. Conecta por SSH a la Raspberry Pi:
```bash
ssh root@<IP_RASPBERRY>
```

3. Ejecuta el instalador:
```bash
cd /root
bash install_ponderal_monitor.sh
```

4. Configura la URL del servidor:
```bash
nano /root/ponderal-monitor/config.py
```

Cambia la línea:
```python
API_BASE_URL = "http://192.168.1.100:3000/api"  # CAMBIAR ESTA IP
```

Por la IP correcta de tu servidor.

### Opción 2: Instalación manual

1. Instalar dependencias:
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-rpi.gpio
sudo pip3 install requests
```

2. Crear directorio y copiar archivos:
```bash
mkdir -p /root/ponderal-monitor
cp raspberry_ponderal_monitor.py /root/ponderal-monitor/
chmod +x /root/ponderal-monitor/raspberry_ponderal_monitor.py
```

3. Configurar servicio:
```bash
sudo cp ponderal-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ponderal-monitor
```

## Configuración

### Configuración del Hardware

**Conexión de sensores a los GPIO:**

```
# Sensor de Botes Ponderal
Raspberry Pi GPIO 23 (Pin 16) ←→ Señal del sensor ponderal
Raspberry Pi GND (Pin 6)      ←→ GND del sensor ponderal
Raspberry Pi 3.3V (Pin 1)     ←→ VCC del sensor ponderal

# Sensor de Botes Expulsados
Raspberry Pi GPIO 22 (Pin 15) ←→ Señal del sensor expulsados
Raspberry Pi GND (Pin 14)     ←→ GND del sensor expulsados
Raspberry Pi 3.3V (Pin 17)    ←→ VCC del sensor expulsados
```

### Configuración del Software

Edita el archivo de configuración:
```bash
nano /root/ponderal-monitor/config.py
```

Parámetros configurables:
- `API_BASE_URL`: URL del servidor API
- `GPIO_PIN_PONDERAL`: Pin GPIO para botes ponderal (por defecto 23)
- `GPIO_PIN_EXPULSADOS`: Pin GPIO para botes expulsados (por defecto 22)
- `DEBOUNCE_TIME`: Tiempo de debounce en segundos
- `REQUEST_TIMEOUT`: Timeout para peticiones HTTP

## Uso

### Iniciar el servicio
```bash
sudo systemctl start ponderal-monitor
```

### Verificar estado
```bash
sudo systemctl status ponderal-monitor
```

### Ver logs en tiempo real
```bash
sudo journalctl -u ponderal-monitor -f
```

### Detener el servicio
```bash
sudo systemctl stop ponderal-monitor
```

### Reiniciar el servicio
```bash
sudo systemctl restart ponderal-monitor
```

## Funcionamiento

1. **Detección de pulsos**: El sistema monitorea continuamente GPIO 23 y GPIO 22
2. **Identificación**: Determina si el pulso es de botes ponderal o expulsados
3. **Debounce**: Evita múltiples detecciones del mismo pulso (independiente por GPIO)
4. **Orden activa**: Busca automáticamente órdenes con estado 'iniciada' o 'pausada'
5. **Incremento**: Llama al endpoint correspondiente:
   - `POST /api/ordenes-fabricacion/{id}/incrementar-botes-ponderal` (GPIO 23)
   - `POST /api/ordenes-fabricacion/{id}/incrementar-botes-expulsados` (GPIO 22)
6. **Monitoreo**: Verifica cada 30 segundos el estado de la orden activa
7. **Logs**: Registra todas las actividades para debugging

## Logs

Los logs se guardan en:
- **Archivo**: `/root/botes_monitor.log`
- **Systemd**: `journalctl -u ponderal-monitor`

Ejemplo de logs:
```
2024-01-15 10:30:15 - INFO - Monitor iniciado. Orden activa: 123
2024-01-15 10:30:45 - INFO - Pulso detectado en GPIO 23 (Botes Ponderal)
2024-01-15 10:30:45 - INFO - Botes ponderal incrementado. Orden 123: 45 botes
2024-01-15 10:31:12 - INFO - Pulso detectado en GPIO 22 (Botes Expulsados)
2024-01-15 10:31:12 - INFO - Botes expulsados incrementado. Orden 123: 8 botes
```

## Troubleshooting

### El servicio no inicia
```bash
# Verificar logs de error
sudo journalctl -u ponderal-monitor -n 50

# Verificar permisos GPIO
groups pi  # Debe incluir 'gpio'

# Probar manualmente
cd /root/ponderal-monitor
python3 raspberry_ponderal_monitor.py
```

### No detecta pulsos
```bash
# Verificar conexión del sensor
# Probar con un LED y resistencia en GPIO 23

# Verificar configuración GPIO
pinout  # Comando para ver pinout de la Raspberry Pi
```

### Error de conexión al API
```bash
# Verificar conectividad
ping <IP_SERVIDOR>
curl http://<IP_SERVIDOR>:3000/api/ordenes-fabricacion

# Verificar configuración
cat /root/ponderal-monitor/config.py
```

### No encuentra orden activa
```bash
# Verificar que hay una orden iniciada
curl http://<IP_SERVIDOR>:3000/api/ordenes-fabricacion

# Verificar logs del servidor
```

## Desinstalación

```bash
sudo systemctl stop ponderal-monitor
sudo systemctl disable ponderal-monitor
sudo rm /etc/systemd/system/ponderal-monitor.service
rm -rf /root/ponderal-monitor
sudo rm /var/log/ponderal_monitor.log
sudo systemctl daemon-reload
```

## API Endpoints Utilizados

**POST** `/api/ordenes-fabricacion/{id}/incrementar-botes-ponderal`
- **Descripción**: Incrementa el contador de botes ponderal en 1
- **Parámetros**: `id` - ID de la orden de fabricación
- **Respuesta**: JSON con el nuevo valor de `botesPonderal`

**POST** `/api/ordenes-fabricacion/{id}/incrementar-botes-expulsados`
- **Descripción**: Incrementa el contador de botes expulsados en 1
- **Parámetros**: `id` - ID de la orden de fabricación
- **Respuesta**: JSON con el nuevo valor de `botesExpulsados`

## Esquema de Conexión

```
┌─────────────────┐    GPIO 23    ┌──────────────┐
│   Raspberry Pi  │◄──────────────┤    Sensor    │
│                 │               │   Ponderal   │
│  GPIO 23 (Pin16)│               │              │
│  GND (Pin 6)    │◄──────────────┤     GND      │
│  3.3V (Pin 1)   │◄──────────────┤     VCC      │
│                 │               └──────────────┘
│                 │    GPIO 22    ┌──────────────┐
│                 │◄──────────────┤    Sensor    │
│                 │               │  Expulsados  │
│  GPIO 22 (Pin15)│               │              │
│  GND (Pin 14)   │◄──────────────┤     GND      │
│  3.3V (Pin 17)  │◄──────────────┤     VCC      │
└─────────────────┘               └──────────────┘
         │
         │ Ethernet/WiFi
         │
         ▼
┌─────────────────┐
│  Servidor API   │
│   Puerto 3000   │
└─────────────────┘
```

## Notas Importantes

- ⚠️ **Configurar la IP correcta** del servidor en `config.py`
- ⚠️ **Verificar la conexión de ambos sensores** antes de usar
- ⚠️ **El usuario pi debe estar en el grupo gpio**
- ⚠️ **Usar resistencias pull-up/pull-down** según el tipo de sensor
- ⚠️ **No conectar voltajes superiores a 3.3V** al GPIO

## Soporte

Para problemas o mejoras, revisar los logs y verificar:
1. Conexión de red al servidor
2. Estado de la orden de fabricación
3. Configuración del GPIO
4. Permisos del usuario