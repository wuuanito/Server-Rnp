# Monitor de Botes - Versión Polling

## Descripción

Esta es una versión alternativa del monitor de botes que utiliza **polling** en lugar de **interrupciones GPIO** para detectar pulsos de los sensores. Esta versión está diseñada para resolver problemas comunes con GPIO en Raspberry Pi, especialmente el error "Failed to add edge detection".

## ¿Cuándo usar esta versión?

Usa la **versión polling** cuando:
- Experimentas errores "Failed to add edge detection"
- Los GPIO están siendo utilizados por otros procesos
- Hay problemas de permisos con `/dev/gpiomem`
- La versión con interrupciones no funciona correctamente
- Necesitas mayor control sobre la detección de pulsos

Usa la **versión con interrupciones** cuando:
- El sistema funciona correctamente con interrupciones
- Necesitas máxima eficiencia de CPU
- Los GPIO están disponibles exclusivamente para el monitor

## Diferencias principales

### Versión con Interrupciones (Original)
```python
# Usa RPi.GPIO con event detection
GPIO.add_event_detect(pin, GPIO.FALLING, callback=callback, bouncetime=300)
```

### Versión Polling (Esta versión)
```python
# Lee GPIO cada 10ms y detecta cambios
while self.running:
    current_state = self.read_gpio_value(pin)
    if self.last_state == 1 and current_state == 0:  # Flanco descendente
        self.process_pulse()
    time.sleep(0.01)  # 10ms polling
```

## Ventajas del Polling

1. **Mayor compatibilidad**: No depende de interrupciones del kernel
2. **Mejor control de errores**: Manejo granular de problemas GPIO
3. **Flexibilidad**: Fácil ajuste del tiempo de polling
4. **Debugging**: Más fácil de depurar problemas
5. **Robustez**: Continúa funcionando aunque haya errores temporales

## Desventajas del Polling

1. **Mayor uso de CPU**: Revisa GPIO cada 10ms constantemente
2. **Latencia**: Puede haber hasta 10ms de retraso en detectar pulsos
3. **Precisión**: Menos preciso para pulsos muy rápidos

## Instalación

### 1. Copiar archivos al Raspberry Pi

```bash
# Desde tu máquina de desarrollo
scp raspberry_botes_monitor_polling.py root@<IP_RASPBERRY>:/root/
scp config.py root@<IP_RASPBERRY>:/root/
scp install_ponderal_monitor_polling.sh root@<IP_RASPBERRY>:/root/
```

### 2. Ejecutar instalación

```bash
# En el Raspberry Pi como root
cd /root
chmod +x install_ponderal_monitor_polling.sh
./install_ponderal_monitor_polling.sh
```

### 3. Iniciar servicio

```bash
systemctl start ponderal-monitor-polling
systemctl status ponderal-monitor-polling
```

## Configuración

La configuración es la misma que la versión original en `config.py`:

```python
# GPIO Pins
GPIO_PIN_PONDERAL = 22
GPIO_PIN_EXPULSADOS = 23

# Timing
DEBOUNCE_TIME = 0.3  # 300ms debounce

# API Configuration
API_BASE_URL = "http://192.168.1.100:3000/api"
REQUEST_TIMEOUT = 5
```

## Monitoreo y Logs

### Ver logs del servicio
```bash
journalctl -u ponderal-monitor-polling -f
```

### Ver archivo de log
```bash
tail -f /root/botes_monitor.log
```

### Estado del servicio
```bash
systemctl status ponderal-monitor-polling
```

## Comandos de Control

```bash
# Iniciar servicio
systemctl start ponderal-monitor-polling

# Detener servicio
systemctl stop ponderal-monitor-polling

# Reiniciar servicio
systemctl restart ponderal-monitor-polling

# Habilitar inicio automático
systemctl enable ponderal-monitor-polling

# Deshabilitar inicio automático
systemctl disable ponderal-monitor-polling
```

## Diagnóstico de Problemas

### 1. Verificar permisos GPIO
```bash
ls -la /dev/gpiomem
ls -la /sys/class/gpio/
```

### 2. Verificar GPIO exportados
```bash
ls /sys/class/gpio/
```

### 3. Limpiar GPIO manualmente
```bash
echo 22 > /sys/class/gpio/unexport 2>/dev/null || true
echo 23 > /sys/class/gpio/unexport 2>/dev/null || true
```

### 4. Probar GPIO manualmente
```bash
# Exportar GPIO 22
echo 22 > /sys/class/gpio/export
echo in > /sys/class/gpio/gpio22/direction
cat /sys/class/gpio/gpio22/value

# Limpiar
echo 22 > /sys/class/gpio/unexport
```

## Migración desde la versión con interrupciones

### 1. Detener servicio anterior
```bash
systemctl stop ponderal-monitor
systemctl disable ponderal-monitor
```

### 2. Instalar versión polling
```bash
./install_ponderal_monitor_polling.sh
```

### 3. Iniciar nuevo servicio
```bash
systemctl start ponderal-monitor-polling
```

## Ajuste de Rendimiento

### Cambiar frecuencia de polling
En `raspberry_botes_monitor_polling.py`, línea ~180:

```python
# Polling cada 10ms (por defecto)
time.sleep(0.01)

# Para mayor precisión (5ms)
time.sleep(0.005)

# Para menor uso de CPU (20ms)
time.sleep(0.02)
```

### Ajustar debounce
En `config.py`:

```python
# Debounce más agresivo para señales ruidosas
DEBOUNCE_TIME = 0.5

# Debounce más rápido para señales limpias
DEBOUNCE_TIME = 0.1
```

## Logs de Ejemplo

```
2024-01-15 10:30:15,123 - INFO - === Monitor de Botes Iniciado (Versión Polling) ===
2024-01-15 10:30:15,124 - INFO - GPIO Pin Ponderal: 22
2024-01-15 10:30:15,125 - INFO - GPIO Pin Expulsados: 23
2024-01-15 10:30:15,126 - INFO - Permisos /dev/gpiomem: 666
2024-01-15 10:30:15,127 - INFO - GPIO 22 configurado para polling
2024-01-15 10:30:15,128 - INFO - GPIO 23 configurado para polling
2024-01-15 10:30:15,129 - INFO - Estados iniciales - Ponderal: 1, Expulsados: 1
2024-01-15 10:30:15,130 - INFO - Configuración GPIO polling completada
2024-01-15 10:30:15,131 - INFO - Orden activa encontrada: 123
2024-01-15 10:30:15,132 - INFO - Iniciando loop de polling GPIO
2024-01-15 10:30:15,133 - INFO - Monitor iniciado con polling. Presiona Ctrl+C para detener.
```

## Desinstalación

```bash
# Detener y deshabilitar servicio
systemctl stop ponderal-monitor-polling
systemctl disable ponderal-monitor-polling

# Eliminar archivos
rm -rf /root/ponderal-monitor
rm /etc/systemd/system/ponderal-monitor-polling.service
rm /root/botes_monitor.log

# Recargar systemd
systemctl daemon-reload
```

## Soporte

Si tienes problemas con esta versión:

1. Revisa los logs: `journalctl -u ponderal-monitor-polling -f`
2. Verifica la configuración en `/root/ponderal-monitor/config.py`
3. Ejecuta el diagnóstico GPIO: `python3 gpio_diagnostic.py`
4. Verifica la conectividad de red al API

## Comparación de Rendimiento

| Aspecto | Interrupciones | Polling |
|---------|----------------|----------|
| Uso CPU | Muy bajo | Bajo-Medio |
| Latencia | <1ms | ~10ms |
| Precisión | Alta | Media-Alta |
| Robustez | Media | Alta |
| Compatibilidad | Media | Alta |
| Debugging | Difícil | Fácil |

---

**Nota**: Esta versión polling es especialmente útil cuando la versión con interrupciones presenta problemas de "Failed to add edge detection" o conflictos con otros procesos que usan GPIO.