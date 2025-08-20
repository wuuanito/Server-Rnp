// Script para verificar si las columnas de pausa fin máquina existen en la base de datos
require('dotenv').config({ path: require('path').join(__dirname, '..', '.env') });
const { sequelize } = require('../config/database');
const { QueryTypes } = require('sequelize');

async function verificarColumnas() {
  try {
    console.log('🔍 Verificando conexión a la base de datos...');
    
    // Probar conexión
    await sequelize.authenticate();
    console.log('✅ Conexión exitosa a la base de datos');
    
    console.log('\n🔍 Verificando columnas de pausa fin máquina...');
    
    // Verificar columnas existentes
    const columns = await sequelize.query(
      "SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_COMMENT FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'ordenes_fabricacion' AND TABLE_SCHEMA = DATABASE() ORDER BY COLUMN_NAME",
      { type: QueryTypes.SELECT }
    );
    
    const columnasRequeridas = [
      'horaPausaFinMaquina',
      'tiempoTotalHastaPausaFinMaquina',
      'tiempoActivoHastaPausaFinMaquina',
      'tiempoPausasHastaPausaFinMaquina'
    ];
    
    console.log('\n📋 Estado de las columnas requeridas:');
    
    columnasRequeridas.forEach(columna => {
      const existe = columns.find(col => col.COLUMN_NAME === columna);
      if (existe) {
        console.log(`✅ ${columna}: EXISTE (${existe.DATA_TYPE}, ${existe.IS_NULLABLE})`);
      } else {
        console.log(`❌ ${columna}: NO EXISTE`);
      }
    });
    
    const todasExisten = columnasRequeridas.every(columna => 
      columns.find(col => col.COLUMN_NAME === columna)
    );
    
    if (todasExisten) {
      console.log('\n🎉 Todas las columnas necesarias ya existen en la base de datos');
    } else {
      console.log('\n⚠️  Faltan algunas columnas. Ejecute la migración para agregarlas.');
      console.log('\nOpciones para ejecutar la migración:');
      console.log('1. Script Node.js: node scripts/migratePausaFinMaquina.js');
      console.log('2. Script SQL directo: Ejecutar scripts/migratePausaFinMaquinaSQL.sql en MySQL');
    }
    
    console.log('\n📊 Variables de entorno de DB:');
    console.log(`- DB_HOST: ${process.env.DB_HOST}`);
    console.log(`- DB_USER: ${process.env.DB_USER}`);
    console.log(`- DB_NAME: ${process.env.DB_NAME}`);
    console.log(`- DB_PASS: ${process.env.DB_PASS ? '[CONFIGURADA]' : '[NO CONFIGURADA]'}`);
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    
    if (error.message.includes('Access denied')) {
      console.log('\n🔧 Soluciones posibles:');
      console.log('1. Verificar credenciales en el archivo .env');
      console.log('2. Asegurar que MySQL esté ejecutándose');
      console.log('3. Verificar que el usuario tenga permisos');
      console.log('4. Probar conexión manual: mysql -u root -p');
    }
  } finally {
    await sequelize.close();
  }
}

// Ejecutar verificación si se llama directamente
if (require.main === module) {
  verificarColumnas()
    .then(() => {
      console.log('\n✅ Verificación completada');
      process.exit(0);
    })
    .catch((error) => {
      console.error('❌ Error en verificación:', error);
      process.exit(1);
    });
}

module.exports = { verificarColumnas };