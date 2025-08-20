#!/usr/bin/env python3
"""
Monitor de Botes (Ponderal y Expulsados) - Versión Polling
Versión alternativa que usa polling en lugar de interrupciones GPIO
para evitar problemas con 'Failed to add edge detection'
"""

import time
import threading
import logging
import requests
from config import *

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

class PonderalMonitorPolling:
    def __init__(self):
        self.orden_activa_id = None
        self.running = False
        
        # Estados anteriores de los pines para detectar cambios
        self.last_state_ponderal = 1  # Asumimos pull-up, estado alto por defecto
        self.last_state_expulsados = 1
        
        # Control de debounce
        self.last_pulse_time_ponderal = 0
        self.last_pulse_time_expulsados = 0
    
    def read_gpio_value(self, pin):
        """Lee el valor de un pin GPIO usando el sistema de archivos"""
        try:
            # Exportar el pin si no está exportado
            export_path = f"/sys/class/gpio/gpio{pin}"
            if not os.path.exists(export_path):
                with open('/sys/class/gpio/export', 'w') as f:
                    f.write(str(pin))
                time.sleep(0.1)  # Esperar a que se configure
                
                # Configurar como entrada
                with open(f"{export_path}/direction", 'w') as f:
                    f.write('in')
            
            # Leer valor
            with open(f"{export_path}/value", 'r') as f:
                return int(f.read().strip())
                
        except Exception as e:
            logger.error(f"Error leyendo GPIO {pin}: {e}")
            return 1  # Valor por defecto (pull-up)
    
    def setup_gpio_polling(self):
        """Configura GPIO para polling (sin interrupciones)"""
        try:
            import os
            
            # Verificar permisos
            if os.path.exists('/dev/gpiomem'):
                stat = os.stat('/dev/gpiomem')
                logger.info(f"Permisos /dev/gpiomem: {oct(stat.st_mode)[-3:]}")
            
            # Configurar pines GPIO
            for pin in [GPIO_PIN_PONDERAL, GPIO_PIN_EXPULSADOS]:
                try:
                    # Limpiar pin si está exportado
                    export_path = f"/sys/class/gpio/gpio{pin}"
                    if os.path.exists(export_path):
                        with open('/sys/class/gpio/unexport', 'w') as f:
                            f.write(str(pin))
                        time.sleep(0.1)
                    
                    # Exportar y configurar
                    with open('/sys/class/gpio/export', 'w') as f:
                        f.write(str(pin))
                    time.sleep(0.1)
                    
                    with open(f"{export_path}/direction", 'w') as f:
                        f.write('in')
                    
                    logger.info(f"GPIO {pin} configurado para polling")
                    
                except Exception as e:
                    logger.error(f"Error configurando GPIO {pin}: {e}")
                    raise
            
            # Leer estados iniciales
            self.last_state_ponderal = self.read_gpio_value(GPIO_PIN_PONDERAL)
            self.last_state_expulsados = self.read_gpio_value(GPIO_PIN_EXPULSADOS)
            
            logger.info(f"Estados iniciales - Ponderal: {self.last_state_ponderal}, Expulsados: {self.last_state_expulsados}")
            logger.info("Configuración GPIO polling completada")
            
        except Exception as e:
            logger.error(f"Error configurando GPIO polling: {e}")
            raise
    
    def gpio_polling_loop(self):
        """Loop principal de polling GPIO"""
        logger.info("Iniciando loop de polling GPIO")
        
        while self.running:
            try:
                current_time = time.time()
                
                # Leer estados actuales
                current_state_ponderal = self.read_gpio_value(GPIO_PIN_PONDERAL)
                current_state_expulsados = self.read_gpio_value(GPIO_PIN_EXPULSADOS)
                
                # Detectar flanco descendente en GPIO ponderal (1 -> 0)
                if (self.last_state_ponderal == 1 and current_state_ponderal == 0):
                    if current_time - self.last_pulse_time_ponderal >= DEBOUNCE_TIME:
                        self.last_pulse_time_ponderal = current_time
                        logger.info(f"Pulso detectado en GPIO {GPIO_PIN_PONDERAL} (Botes Ponderal)")
                        threading.Thread(target=self.process_pulse_ponderal, daemon=True).start()
                
                # Detectar flanco descendente en GPIO expulsados (1 -> 0)
                if (self.last_state_expulsados == 1 and current_state_expulsados == 0):
                    if current_time - self.last_pulse_time_expulsados >= DEBOUNCE_TIME:
                        self.last_pulse_time_expulsados = current_time
                        logger.info(f"Pulso detectado en GPIO {GPIO_PIN_EXPULSADOS} (Botes Expulsados)")
                        threading.Thread(target=self.process_pulse_expulsados, daemon=True).start()
                
                # Actualizar estados anteriores
                self.last_state_ponderal = current_state_ponderal
                self.last_state_expulsados = current_state_expulsados
                
                # Esperar antes del siguiente polling (10ms)
                time.sleep(0.01)
                
            except Exception as e:
                logger.error(f"Error en polling GPIO: {e}")
                time.sleep(0.1)  # Esperar más tiempo en caso de error
    
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
    
    def process_pulse_ponderal(self):
        """Procesa el pulso detectado para botes ponderal"""
        # Obtener orden activa si no la tenemos
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
        # Obtener orden activa si no la tenemos
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
            logger.info("=== Monitor de Botes Iniciado (Versión Polling) ===")
            logger.info(f"API URL: {API_BASE_URL}")
            logger.info(f"GPIO Pin Ponderal: {GPIO_PIN_PONDERAL}")
            logger.info(f"GPIO Pin Expulsados: {GPIO_PIN_EXPULSADOS}")
            logger.info(f"Debounce Time: {DEBOUNCE_TIME}s")
            logger.info("Iniciando monitor de botes con polling...")
            
            # Configurar GPIO
            self.setup_gpio_polling()
            
            # Obtener orden activa inicial
            self.orden_activa_id = self.get_orden_activa()
            if self.orden_activa_id:
                logger.info(f"Orden activa encontrada: {self.orden_activa_id}")
            else:
                logger.warning("No se encontró orden activa")
            
            # Iniciar hilos
            self.running = True
            
            # Hilo de monitoreo de estado de orden
            monitor_thread = threading.Thread(target=self.monitor_orden_status, daemon=True)
            monitor_thread.start()
            
            # Hilo de polling GPIO
            gpio_thread = threading.Thread(target=self.gpio_polling_loop, daemon=True)
            gpio_thread.start()
            
            logger.info("Monitor iniciado con polling. Presiona Ctrl+C para detener.")
            
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
            import os
            # Limpiar GPIO exportados
            for pin in [GPIO_PIN_PONDERAL, GPIO_PIN_EXPULSADOS]:
                try:
                    with open('/sys/class/gpio/unexport', 'w') as f:
                        f.write(str(pin))
                except:
                    pass
            logger.info("Monitor detenido y GPIO limpiado")
        except Exception as e:
            logger.error(f"Error limpiando GPIO: {e}")

def main():
    """Función principal"""
    monitor = PonderalMonitorPolling()
    monitor.start()

if __name__ == "__main__":
    main()