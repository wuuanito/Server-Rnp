#!/usr/bin/env python3
"""
Script de prueba para los endpoints de incrementar botes
Este script simula el comportamiento de la Raspberry Pi para testing
(tanto botes ponderal como botes expulsados)
"""

import requests
import json
import time
import sys

# Configuración
API_BASE_URL = "http://localhost:3000/api"  # Cambiar por la URL correcta
TEST_ORDEN_ID = None  # Se detectará automáticamente

def obtener_orden_activa():
    """Obtiene la orden de fabricación activa (iniciada o pausada)"""
    try:
        response = requests.get(f"{API_BASE_URL}/ordenes-fabricacion", timeout=5)
        response.raise_for_status()
        
        ordenes = response.json()
        
        # Buscar orden activa
        for orden in ordenes:
            if orden.get('estado') in ['iniciada', 'pausada']:
                return orden
        
        return None
        
    except Exception as e:
        print(f"Error al obtener órdenes: {e}")
        return None

def incrementar_botes_ponderal(orden_id, cantidad=1):
    """Incrementa los botes ponderal de una orden"""
    try:
        url = f"{API_BASE_URL}/ordenes-fabricacion/{orden_id}/incrementar-botes-ponderal"
        data = {"cantidad": cantidad}
        
        response = requests.post(url, json=data, timeout=5)
        response.raise_for_status()
        
        result = response.json()
        return result
        
    except Exception as e:
        print(f"Error al incrementar botes ponderal: {e}")
        return None

def incrementar_botes_expulsados(orden_id, cantidad=1):
    """Incrementa los botes expulsados de una orden"""
    try:
        url = f"{API_BASE_URL}/ordenes-fabricacion/{orden_id}/incrementar-botes-expulsados"
        data = {"cantidad": cantidad}
        
        response = requests.post(url, json=data, timeout=5)
        response.raise_for_status()
        
        result = response.json()
        return result
        
    except Exception as e:
        print(f"Error al incrementar botes expulsados: {e}")
        return None

def obtener_estado_orden(orden_id):
    """Obtiene el estado actual de una orden"""
    try:
        response = requests.get(f"{API_BASE_URL}/ordenes-fabricacion/{orden_id}", timeout=5)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        print(f"Error al obtener estado de orden: {e}")
        return None

def test_endpoint():
    """Ejecuta las pruebas de ambos endpoints"""
    print("=== Test de Endpoints de Botes ===")
    print(f"URL del API: {API_BASE_URL}")
    print()
    
    # 1. Obtener orden activa
    print("1. Buscando orden activa...")
    orden_activa = obtener_orden_activa()
    
    if not orden_activa:
        print("❌ No se encontró ninguna orden activa (iniciada o pausada)")
        print("   Crea una orden y ponla en estado 'iniciada' para continuar")
        return False
    
    orden_id = orden_activa['id']
    botes_ponderal_inicial = orden_activa.get('botesPonderal', 0)
    botes_expulsados_inicial = orden_activa.get('botesExpulsados', 0)
    
    print(f"✅ Orden activa encontrada: ID {orden_id}")
    print(f"   Estado: {orden_activa['estado']}")
    print(f"   Botes ponderal inicial: {botes_ponderal_inicial}")
    print(f"   Botes expulsados inicial: {botes_expulsados_inicial}")
    print()
    
    # 2. Probar incremento botes ponderal
    print("2. Probando incremento botes ponderal (+1)...")
    resultado = incrementar_botes_ponderal(orden_id, 1)
    
    if not resultado:
        print("❌ Error al incrementar botes ponderal")
        return False
    
    print(f"✅ Incremento ponderal exitoso")
    print(f"   Mensaje: {resultado.get('message', 'N/A')}")
    print(f"   Botes ponderal actual: {resultado.get('orden', {}).get('botesPonderal', 'N/A')}")
    print()
    
    # 3. Probar incremento botes expulsados
    print("3. Probando incremento botes expulsados (+1)...")
    resultado = incrementar_botes_expulsados(orden_id, 1)
    
    if not resultado:
        print("❌ Error al incrementar botes expulsados")
        return False
    
    print(f"✅ Incremento expulsados exitoso")
    print(f"   Mensaje: {resultado.get('message', 'N/A')}")
    print(f"   Botes expulsados actual: {resultado.get('orden', {}).get('botesExpulsados', 'N/A')}")
    print()
    
    # 4. Verificar estado actualizado
    print("4. Verificando estado actualizado...")
    estado_actual = obtener_estado_orden(orden_id)
    
    if estado_actual:
        botes_ponderal_actual = estado_actual.get('botesPonderal', 0)
        botes_expulsados_actual = estado_actual.get('botesExpulsados', 0)
        
        ponderal_esperado = botes_ponderal_inicial + 1
        expulsados_esperado = botes_expulsados_inicial + 1
        
        if (botes_ponderal_actual == ponderal_esperado and 
            botes_expulsados_actual == expulsados_esperado):
            print(f"✅ Estado verificado correctamente")
            print(f"   Botes ponderal: {botes_ponderal_inicial} → {botes_ponderal_actual}")
            print(f"   Botes expulsados: {botes_expulsados_inicial} → {botes_expulsados_actual}")
        else:
            print(f"❌ Estado inconsistente")
            print(f"   Ponderal esperado: {ponderal_esperado}, actual: {botes_ponderal_actual}")
            print(f"   Expulsados esperado: {expulsados_esperado}, actual: {botes_expulsados_actual}")
            return False
    else:
        print("❌ No se pudo verificar el estado")
        return False
    
    print()
    
    # 5. Probar incrementos múltiples
    print("5. Probando incrementos múltiples...")
    
    # Incrementar ponderal +3
    resultado_p = incrementar_botes_ponderal(orden_id, 3)
    # Incrementar expulsados +2
    resultado_e = incrementar_botes_expulsados(orden_id, 2)
    
    if resultado_p and resultado_e:
        botes_ponderal_final = resultado_p.get('orden', {}).get('botesPonderal', 0)
        botes_expulsados_final = resultado_e.get('orden', {}).get('botesExpulsados', 0)
        
        print(f"✅ Incrementos múltiples exitosos")
        print(f"   Botes ponderal final: {botes_ponderal_final}")
        print(f"   Botes expulsados final: {botes_expulsados_final}")
        print(f"   Total ponderal incrementado: {botes_ponderal_final - botes_ponderal_inicial}")
        print(f"   Total expulsados incrementado: {botes_expulsados_final - botes_expulsados_inicial}")
    else:
        print("❌ Error en incrementos múltiples")
        return False
    
    print()
    print("=== Todas las pruebas completadas exitosamente ===")
    return True

def simular_pulsos_gpio():
    """Simula pulsos de ambos GPIO como lo haría la Raspberry Pi"""
    print("=== Simulación de Pulsos GPIO ===")
    print("Simulando detección de pulsos alternados cada 2 segundos...")
    print("GPIO 23 (ponderal) y GPIO 22 (expulsados)")
    print("Presiona Ctrl+C para detener")
    print()
    
    # Obtener orden activa
    orden_activa = obtener_orden_activa()
    if not orden_activa:
        print("❌ No hay orden activa para simular")
        return
    
    orden_id = orden_activa['id']
    contador = 0
    
    try:
        while True:
            contador += 1
            
            # Alternar entre ponderal y expulsados
            if contador % 2 == 1:
                print(f"Pulso #{contador} detectado en GPIO 23 (Botes Ponderal - simulado)")
                resultado = incrementar_botes_ponderal(orden_id, 1)
                
                if resultado:
                    botes_actual = resultado.get('orden', {}).get('botesPonderal', 'N/A')
                    print(f"✅ Botes ponderal incrementado a: {botes_actual}")
                else:
                    print("❌ Error al incrementar ponderal")
            else:
                print(f"Pulso #{contador} detectado en GPIO 22 (Botes Expulsados - simulado)")
                resultado = incrementar_botes_expulsados(orden_id, 1)
                
                if resultado:
                    botes_actual = resultado.get('orden', {}).get('botesExpulsados', 'N/A')
                    print(f"✅ Botes expulsados incrementado a: {botes_actual}")
                else:
                    print("❌ Error al incrementar expulsados")
            
            print()
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n🛑 Simulación detenida por el usuario")
        print(f"Total de pulsos simulados: {contador}")

def main():
    """Función principal"""
    if len(sys.argv) > 1 and sys.argv[1] == "--simulate":
        simular_pulsos_gpio()
    else:
        test_endpoint()
        print()
        print("💡 Para simular pulsos continuos, ejecuta:")
        print(f"   python3 {sys.argv[0]} --simulate")

if __name__ == "__main__":
    main()