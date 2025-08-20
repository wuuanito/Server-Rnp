// Script de prueba para la funcionalidad de pausa fin máquina
const axios = require('axios');

const API_BASE_URL = 'http://localhost:3000/api';

async function testPausaFinMaquina() {
  try {
    console.log('🧪 Iniciando pruebas de pausa fin máquina...');
    
    // 1. Crear una orden de prueba
    console.log('\n1. Creando orden de prueba...');
    const nuevaOrden = {
      codigoOrden: 'TEST-PAUSA-FIN-' + Date.now(),
      codigoArticulo: 'ART-TEST-001',
      producto: 'Producto de Prueba Pausa Fin Máquina',
      cantidadProducir: 1000,
      numeroCajas: 10,
      botesPorCaja: 100,
      repercap: false
    };
    
    const responseCrear = await axios.post(`${API_BASE_URL}/ordenes-fabricacion`, nuevaOrden);
    const ordenId = responseCrear.data.orden.id;
    console.log(`✅ Orden creada con ID: ${ordenId}`);
    
    // 2. Iniciar la orden
    console.log('\n2. Iniciando orden...');
    await axios.post(`${API_BASE_URL}/ordenes-fabricacion/${ordenId}/iniciar`);
    console.log('✅ Orden iniciada');
    
    // 3. Simular algo de tiempo de trabajo
    console.log('\n3. Simulando tiempo de trabajo...');
    await new Promise(resolve => setTimeout(resolve, 2000)); // 2 segundos
    
    // 4. Crear una pausa normal para tener datos de pausa
    console.log('\n4. Creando pausa normal...');
    await axios.post(`${API_BASE_URL}/ordenes-fabricacion/${ordenId}/pausar`, {
      tipoPausa: 'Mantenimiento',
      comentario: 'Pausa de prueba antes de fin máquina'
    });
    console.log('✅ Pausa normal creada');
    
    // 5. Simular tiempo de pausa
    await new Promise(resolve => setTimeout(resolve, 1000)); // 1 segundo
    
    // 6. Reanudar la orden (finalizar pausa)
    console.log('\n5. Reanudando orden...');
    const pausas = await axios.get(`${API_BASE_URL}/pausas/orden/${ordenId}`);
    const pausaActiva = pausas.data.find(p => !p.horaFin);
    if (pausaActiva) {
      await axios.post(`${API_BASE_URL}/pausas/${pausaActiva.id}/finalizar`);
      console.log('✅ Pausa normal finalizada');
    }
    
    // 7. Simular más tiempo de trabajo
    await new Promise(resolve => setTimeout(resolve, 1000)); // 1 segundo
    
    // 8. Ejecutar pausa fin máquina
    console.log('\n6. Ejecutando pausa fin máquina...');
    const responsePausaFin = await axios.post(`${API_BASE_URL}/ordenes-fabricacion/${ordenId}/pausar`, {
      tipoPausa: 'pausa_fin_maquina',
      comentario: 'Pausa Fin Máquina'
    });
    
    console.log('✅ Pausa fin máquina ejecutada');
    console.log('📊 Tiempos calculados:', responsePausaFin.data.tiemposCalculados);
    
    // 9. Verificar que los tiempos se guardaron
    console.log('\n7. Verificando datos de pausa fin máquina...');
    const responsePausaFinInfo = await axios.get(`${API_BASE_URL}/ordenes-fabricacion/${ordenId}/pausa-fin-maquina`);
    console.log('✅ Datos de pausa fin máquina:', responsePausaFinInfo.data);
    
    // 10. Finalizar la orden
    console.log('\n8. Finalizando orden...');
    const responseFinalizar = await axios.post(`${API_BASE_URL}/ordenes-fabricacion/${ordenId}/finalizar`, {
      unidadesCierreFin: 950,
      unidadesNoOkFin: 50,
      numeroCorteSanitarioFinal: 1000
    });
    
    console.log('✅ Orden finalizada');
    console.log('📊 Usó pausa fin máquina:', responseFinalizar.data.usoPausaFinMaquina);
    console.log('📊 Mensaje:', responseFinalizar.data.message);
    
    // 11. Verificar los tiempos finales
    console.log('\n9. Verificando tiempos finales...');
    const ordenFinal = await axios.get(`${API_BASE_URL}/ordenes-fabricacion/${ordenId}`);
    const orden = ordenFinal.data;
    
    console.log('📊 Tiempos finales de la orden:');
    console.log(`   - Tiempo total: ${orden.tiempoTotal} minutos`);
    console.log(`   - Tiempo activo: ${orden.tiempoTotalActivo} minutos`);
    console.log(`   - Tiempo pausas: ${orden.tiempoTotalPausas} minutos`);
    console.log(`   - Hora pausa fin máquina: ${orden.horaPausaFinMaquina}`);
    console.log(`   - Tiempo hasta pausa fin máquina: ${orden.tiempoTotalHastaPausaFinMaquina} minutos`);
    
    console.log('\n🎉 ¡Todas las pruebas completadas exitosamente!');
    
  } catch (error) {
    console.error('❌ Error en las pruebas:', error.response?.data || error.message);
  }
}

// Ejecutar las pruebas
if (require.main === module) {
  testPausaFinMaquina();
}

module.exports = { testPausaFinMaquina };