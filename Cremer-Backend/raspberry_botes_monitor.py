#!/usr/bin/env python3
"""
Monitor de Botes para Raspberry Pi
Detecta pulsos en GPIO 23 (botes ponderal) y GPIO 22 (botes expulsados)
e incrementa los contadores correspondientes a través del API REST.
"""

import RPi.GPIO as GPIO
import requests
import time
import json
import logging
from datetime import datetime
import threading

# Configuración
GPIO_PIN_PONDERAL = 23  # Pin GPIO para botes ponderal
GPIO_PIN_EXPULSADOS = 22  # Pin GPIO para botes expulsados
API_BASE_URL = "http://192.168.11.18:3002/api"  # Cambiar por la IP correcta del servidor
DEBOUNCE_TIME = 0.5  # Tiempo de debounce en segundos
REQUEST_TIMEOUT = 5  # Timeout para peticiones HTTP
ORDEN_CHECK_INTERVAL = 30  # Intervalo para verificar orden activa (segundos)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/root/botes_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PonderalMonitor:
    def __init__(self):
        self.last_pulse_time_ponderal = 0
        self.last_pulse_time_expulsados = 0
        self.orden_activa_id = None
        self.running = False
        
    def cleanup_gpio_system(self, pin):
        """Limpia GPIO usando el sistema de archivos"""
        try:
            # Intentar unexport el pin si está exportado
            with open('/sys/class/gpio/unexport', 'w') as f:
                f.write(str(pin))
            logger.info(f"GPIO {pin} limpiado via sistema de archivos")
        except Exception as e:
            logger.debug(f"No se pudo limpiar GPIO {pin} via sistema: {e}")
    
    def setup_gpio(self):
        """Configura los GPIO para detectar pulsos"""
        try:
            # Limpiar GPIO usando sistema de archivos primero
            logger.info("Limpiando GPIO via sistema de archivos...")
            self.cleanup_gpio_system(GPIO_PIN_PONDERAL)
            self.cleanup_gpio_system(GPIO_PIN_EXPULSADOS)
            
            # Limpiar cualquier configuración GPIO previa con RPi.GPIO
            try:
                GPIO.cleanup()
                logger.info("GPIO limpiado con RPi.GPIO")
            except Exception as e:
                logger.debug(f"Advertencia limpiando GPIO: {e}")
            
            # Verificar permisos
            import os
            if os.path.exists('/dev/gpiomem'):
                stat = os.stat('/dev/gpiomem')
                logger.info(f"Permisos /dev/gpiomem: {oct(stat.st_mode)[-3:]}")
            else:
                logger.warning("/dev/gpiomem no existe")
            
            GPIO.setmode(GPIO.BCM)
            logger.info("Modo GPIO BCM establecido")
            
            # Configurar GPIO para botes ponderal
            try:
                logger.info(f"Configurando GPIO {GPIO_PIN_PONDERAL}...")
                GPIO.setup(GPIO_PIN_PONDERAL, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                logger.info(f"GPIO {GPIO_PIN_PONDERAL} configurado como entrada")
                
                GPIO.add_event_detect(GPIO_PIN_PONDERAL, GPIO.FALLING, 
                                    callback=self.on_pulse_detected, 
                                    bouncetime=int(DEBOUNCE_TIME * 1000))
                logger.info(f"GPIO {GPIO_PIN_PONDERAL} detección de eventos configurada")
                
            except Exception as e:
                logger.error(f"Error configurando GPIO {GPIO_PIN_PONDERAL}: {e}")
                logger.error(f"Tipo de error: {type(e).__name__}")
                raise
            
            # Configurar GPIO para botes expulsados
            try:
                logger.info(f"Configurando GPIO {GPIO_PIN_EXPULSADOS}...")
                GPIO.setup(GPIO_PIN_EXPULSADOS, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                logger.info(f"GPIO {GPIO_PIN_EXPULSADOS} configurado como entrada")
                
                GPIO.add_event_detect(GPIO_PIN_EXPULSADOS, GPIO.FALLING, 
                                    callback=self.on_pulse_detected, 
                                    bouncetime=int(DEBOUNCE_TIME * 1000))
                logger.info(f"GPIO {GPIO_PIN_EXPULSADOS} detección de eventos configurada")
                
            except Exception as e:
                logger.error(f"Error configurando GPIO {GPIO_PIN_EXPULSADOS}: {e}")
                logger.error(f"Tipo de error: {type(e).__name__}")
                raise
                
            logger.info("Configuración GPIO completada exitosamente")
                
        except Exception as e:
            logger.error(f"Error configurando GPIO: {e}")
            logger.error(f"Tipo de error: {type(e).__name__}")
            
            # Intentar limpiar en caso de error
            try:
                GPIO.cleanup()
                logger.info("GPIO limpiado después del error")
            except Exception as cleanup_error:
                logger.error(f"Error limpiando GPIO: {cleanup_error}")
            raise
    
    def get_orden_activa(self):
        """Obtiene la orden de fabricación activa"""
        try:
            response = requests.get(
                f"{API_BASE_URL}/ordenes-fabricacion",
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            ordenes = response.json()
            # Buscar orden con estado 'iniciada' o 'pausada'
            for orden in ordenes:
                if orden.get('estado') in ['iniciada', 'pausada']:
                    return orden['id']
            
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error obteniendo orden activa: {e}")
            return None
        except Exception as e:
            logger.error(f"Error procesando respuesta: {e}")
            return None
    
    def incrementar_botes_ponderal(self, orden_id):
        """Incrementa los botes ponderal en la orden especificada"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/ordenes-fabricacion/{orden_id}/incrementar-botes-ponderal",
                json={"cantidad": 1},
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Botes ponderal incrementado. Orden {orden_id}: {result.get('orden', {}).get('botesPonderal', 'N/A')} botes")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error incrementando botes ponderal: {e}")
            return False
        except Exception as e:
            logger.error(f"Error procesando incremento: {e}")
            return False
    
    def incrementar_botes_expulsados(self, orden_id):
        """Incrementa los botes expulsados en la orden especificada"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/ordenes-fabricacion/{orden_id}/incrementar-botes-expulsados",
                json={"cantidad": 1},
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Botes expulsados incrementado. Orden {orden_id}: {result.get('orden', {}).get('botesExpulsados', 'N/A')} botes")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error incrementando botes expulsados: {e}")
            return False
        except Exception as e:
            logger.error(f"Error procesando incremento: {e}")
            return False
    
    def on_pulse_detected(self, channel):
        """Callback ejecutado cuando se detecta un pulso en cualquier GPIO"""
        current_time = time.time()
        
        # Determinar qué tipo de pulso es y aplicar debounce específico
        if channel == GPIO_PIN_PONDERAL:
            if current_time - self.last_pulse_time_ponderal < DEBOUNCE_TIME:
                return
            self.last_pulse_time_ponderal = current_time
            # Ejecutar en hilo separado para no bloquear la detección de GPIO
            threading.Thread(target=self.process_pulse_ponderal, daemon=True).start()
            
        elif channel == GPIO_PIN_EXPULSADOS:
            if current_time - self.last_pulse_time_expulsados < DEBOUNCE_TIME:
                return
            self.last_pulse_time_expulsados = current_time
            # Ejecutar en hilo separado para no bloquear la detección de GPIO
            threading.Thread(target=self.process_pulse_expulsados, daemon=True).start()
    
    def process_pulse_ponderal(self):
        """Procesa el pulso detectado para botes ponderal"""
        logger.info(f"Pulso detectado en GPIO {GPIO_PIN_PONDERAL} (Botes Ponderal)")
        
        # Obtener orden activa si no la tenemos o verificar que sigue activa
        if not self.orden_activa_id:
            self.orden_activa_id = self.get_orden_activa()
        
        if not self.orden_activa_id:
            logger.warning("No hay orden activa. Pulso ponderal ignorado.")
            return
        
        # Incrementar botes ponderal
        success = self.incrementar_botes_ponderal(self.orden_activa_id)
        
        if not success:
            # Si falla, intentar obtener nueva orden activa
            logger.info("Reintentando con nueva orden activa...")
            self.orden_activa_id = self.get_orden_activa()
            if self.orden_activa_id:
                self.incrementar_botes_ponderal(self.orden_activa_id)
    
    def process_pulse_expulsados(self):
        """Procesa el pulso detectado para botes expulsados"""
        logger.info(f"Pulso detectado en GPIO {GPIO_PIN_EXPULSADOS} (Botes Expulsados)")
        
        # Obtener orden activa si no la tenemos o verificar que sigue activa
        if not self.orden_activa_id:
            self.orden_activa_id = self.get_orden_activa()
        
        if not self.orden_activa_id:
            logger.warning("No hay orden activa. Pulso expulsados ignorado.")
            return
        
        # Incrementar botes expulsados
        success = self.incrementar_botes_expulsados(self.orden_activa_id)
        
        if not success:
            # Si falla, intentar obtener nueva orden activa
            logger.info("Reintentando con nueva orden activa...")
            self.orden_activa_id = self.get_orden_activa()
            if self.orden_activa_id:
                self.incrementar_botes_expulsados(self.orden_activa_id)
    
    def monitor_orden_status(self):
        """Monitorea el estado de la orden activa cada 30 segundos"""
        while self.running:
            try:
                if self.orden_activa_id:
                    # Verificar si la orden sigue activa
                    response = requests.get(
                        f"{API_BASE_URL}/ordenes-fabricacion/{self.orden_activa_id}",
                        timeout=REQUEST_TIMEOUT
                    )
                    
                    if response.status_code == 200:
                        orden = response.json()
                        if orden.get('estado') not in ['iniciada', 'pausada']:
                            logger.info(f"Orden {self.orden_activa_id} ya no está activa. Buscando nueva orden...")
                            self.orden_activa_id = None
                    else:
                        logger.warning(f"No se pudo verificar orden {self.orden_activa_id}")
                        self.orden_activa_id = None
                
                # Si no hay orden activa, buscar una
                if not self.orden_activa_id:
                    nueva_orden = self.get_orden_activa()
                    if nueva_orden:
                        self.orden_activa_id = nueva_orden
                        logger.info(f"Nueva orden activa detectada: {self.orden_activa_id}")
                
            except Exception as e:
                logger.error(f"Error monitoreando estado de orden: {e}")
            
            time.sleep(30)  # Verificar cada 30 segundos
    
    def start(self):
        """Inicia el monitor"""
        try:
            logger.info("=== Monitor de Botes Iniciado ===")
            logger.info(f"API URL: {API_BASE_URL}")
            logger.info(f"GPIO Pin Ponderal: {GPIO_PIN_PONDERAL}")
            logger.info(f"GPIO Pin Expulsados: {GPIO_PIN_EXPULSADOS}")
            logger.info(f"Debounce Time: {DEBOUNCE_TIME}s")
            logger.info("Iniciando monitor de botes...")
            
            # Configurar GPIO
            self.setup_gpio()
            
            # Obtener orden activa inicial
            self.orden_activa_id = self.get_orden_activa()
            if self.orden_activa_id:
                logger.info(f"Orden activa encontrada: {self.orden_activa_id}")
            else:
                logger.warning("No se encontró orden activa")
            
            # Iniciar monitoreo de estado en hilo separado
            self.running = True
            monitor_thread = threading.Thread(target=self.monitor_orden_status, daemon=True)
            monitor_thread.start()
            
            logger.info("Monitor iniciado. Presiona Ctrl+C para detener.")
            
            # Mantener el programa corriendo
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Deteniendo monitor...")
        except Exception as e:
            logger.error(f"Error en monitor: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Detiene el monitor y limpia recursos"""
        self.running = False
        try:
            GPIO.cleanup()
            logger.info("Monitor detenido y GPIO limpiado")
        except Exception as e:
            logger.error(f"Error limpiando GPIO: {e}")

def main():
    """Función principal"""
    monitor = PonderalMonitor()
    monitor.start()

if __name__ == "__main__":
    main()