#!/usr/bin/env python3
"""
Script de diagnóstico para GPIO en Raspberry Pi
Verifica el estado de los pines GPIO 22 y 23
"""

import os
import sys
import subprocess

def check_gpio_permissions():
    """Verifica permisos de GPIO"""
    print("=== Verificando permisos GPIO ===")
    
    # Verificar /dev/gpiomem
    if os.path.exists('/dev/gpiomem'):
        stat = os.stat('/dev/gpiomem')
        print(f"/dev/gpiomem existe - Permisos: {oct(stat.st_mode)[-3:]}")
    else:
        print("/dev/gpiomem NO existe")
    
    # Verificar usuario actual
    print(f"Usuario actual: {os.getuid()} ({os.getlogin() if hasattr(os, 'getlogin') else 'unknown'})")
    
    # Verificar grupos
    try:
        result = subprocess.run(['groups'], capture_output=True, text=True)
        print(f"Grupos: {result.stdout.strip()}")
    except:
        print("No se pudieron obtener los grupos")

def check_gpio_usage():
    """Verifica si los GPIO están siendo usados"""
    print("\n=== Verificando uso de GPIO ===")
    
    gpio_pins = [22, 23]
    
    for pin in gpio_pins:
        # Verificar si el pin está exportado
        export_path = f"/sys/class/gpio/gpio{pin}"
        if os.path.exists(export_path):
            print(f"GPIO {pin}: EXPORTADO (en uso)")
            
            # Verificar dirección
            try:
                with open(f"{export_path}/direction", 'r') as f:
                    direction = f.read().strip()
                print(f"  Dirección: {direction}")
            except:
                print(f"  No se pudo leer dirección")
                
            # Verificar valor
            try:
                with open(f"{export_path}/value", 'r') as f:
                    value = f.read().strip()
                print(f"  Valor: {value}")
            except:
                print(f"  No se pudo leer valor")
        else:
            print(f"GPIO {pin}: No exportado")

def check_processes_using_gpio():
    """Busca procesos que puedan estar usando GPIO"""
    print("\n=== Verificando procesos que usan GPIO ===")
    
    try:
        # Buscar procesos con 'gpio' en el nombre
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        gpio_processes = []
        for line in lines:
            if 'gpio' in line.lower() or 'raspberry' in line.lower() or 'ponderal' in line.lower():
                gpio_processes.append(line)
        
        if gpio_processes:
            print("Procesos relacionados con GPIO:")
            for proc in gpio_processes:
                print(f"  {proc}")
        else:
            print("No se encontraron procesos relacionados con GPIO")
            
    except Exception as e:
        print(f"Error verificando procesos: {e}")

def test_gpio_basic():
    """Prueba básica de GPIO sin RPi.GPIO"""
    print("\n=== Prueba básica de GPIO ===")
    
    try:
        # Intentar exportar GPIO 23
        with open('/sys/class/gpio/export', 'w') as f:
            f.write('23')
        print("GPIO 23 exportado exitosamente")
        
        # Configurar como entrada
        with open('/sys/class/gpio/gpio23/direction', 'w') as f:
            f.write('in')
        print("GPIO 23 configurado como entrada")
        
        # Leer valor
        with open('/sys/class/gpio/gpio23/value', 'r') as f:
            value = f.read().strip()
        print(f"GPIO 23 valor: {value}")
        
        # Limpiar
        with open('/sys/class/gpio/unexport', 'w') as f:
            f.write('23')
        print("GPIO 23 limpiado")
        
    except Exception as e:
        print(f"Error en prueba básica: {e}")
        
        # Intentar limpiar en caso de error
        try:
            with open('/sys/class/gpio/unexport', 'w') as f:
                f.write('23')
        except:
            pass

def main():
    print("Diagnóstico GPIO para Raspberry Pi")
    print("=" * 40)
    
    check_gpio_permissions()
    check_gpio_usage()
    check_processes_using_gpio()
    test_gpio_basic()
    
    print("\n=== Recomendaciones ===")
    print("1. Si hay procesos usando GPIO, detenerlos antes de ejecutar el monitor")
    print("2. Si los GPIO están exportados, ejecutar: echo 22 > /sys/class/gpio/unexport && echo 23 > /sys/class/gpio/unexport")
    print("3. Verificar que el usuario tenga permisos adecuados")
    print("4. Reiniciar el sistema si es necesario")

if __name__ == "__main__":
    main()