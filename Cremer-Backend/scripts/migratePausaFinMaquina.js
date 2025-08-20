// Migración para agregar campos de pausa fin máquina
require('dotenv').config({ path: require('path').join(__dirname, '..', '.env') });
const { sequelize } = require('../config/database');
const { QueryTypes } = require('sequelize');

async function migratePausaFinMaquina() {
  const transaction = await sequelize.transaction();
  
  try {
    console.log('Iniciando migración para pausa fin máquina...');
    
    // Verificar si las columnas ya existen
    const columns = await sequelize.query(
      "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'ordenes_fabricacion' AND TABLE_SCHEMA = DATABASE()",
      { type: QueryTypes.SELECT, transaction }
    );
    
    const existingColumns = columns.map(col => col.COLUMN_NAME);
    
    // Agregar columna horaPausaFinMaquina si no existe
    if (!existingColumns.includes('horaPausaFinMaquina')) {
      await sequelize.query(
        'ALTER TABLE ordenes_fabricacion ADD COLUMN horaPausaFinMaquina DATETIME NULL COMMENT "Hora en que se ejecutó la pausa fin máquina"',
        { transaction }
      );
      console.log('✓ Columna horaPausaFinMaquina agregada');
    } else {
      console.log('- Columna horaPausaFinMaquina ya existe');
    }
    
    // Agregar columna tiempoTotalHastaPausaFinMaquina si no existe
    if (!existingColumns.includes('tiempoTotalHastaPausaFinMaquina')) {
      await sequelize.query(
        'ALTER TABLE ordenes_fabricacion ADD COLUMN tiempoTotalHastaPausaFinMaquina INT NULL COMMENT "Tiempo total en minutos hasta la pausa fin máquina"',
        { transaction }
      );
      console.log('✓ Columna tiempoTotalHastaPausaFinMaquina agregada');
    } else {
      console.log('- Columna tiempoTotalHastaPausaFinMaquina ya existe');
    }
    
    // Agregar columna tiempoActivoHastaPausaFinMaquina si no existe
    if (!existingColumns.includes('tiempoActivoHastaPausaFinMaquina')) {
      await sequelize.query(
        'ALTER TABLE ordenes_fabricacion ADD COLUMN tiempoActivoHastaPausaFinMaquina INT NULL COMMENT "Tiempo activo en minutos hasta la pausa fin máquina"',
        { transaction }
      );
      console.log('✓ Columna tiempoActivoHastaPausaFinMaquina agregada');
    } else {
      console.log('- Columna tiempoActivoHastaPausaFinMaquina ya existe');
    }
    
    // Agregar columna tiempoPausasHastaPausaFinMaquina si no existe
    if (!existingColumns.includes('tiempoPausasHastaPausaFinMaquina')) {
      await sequelize.query(
        'ALTER TABLE ordenes_fabricacion ADD COLUMN tiempoPausasHastaPausaFinMaquina INT NULL COMMENT "Tiempo de pausas en minutos hasta la pausa fin máquina"',
        { transaction }
      );
      console.log('✓ Columna tiempoPausasHastaPausaFinMaquina agregada');
    } else {
      console.log('- Columna tiempoPausasHastaPausaFinMaquina ya existe');
    }
    
    await transaction.commit();
    console.log('\n✅ Migración completada exitosamente');
    
  } catch (error) {
    await transaction.rollback();
    console.error('❌ Error durante la migración:', error);
    throw error;
  }
}

// Ejecutar migración si se llama directamente
if (require.main === module) {
  migratePausaFinMaquina()
    .then(() => {
      console.log('Migración ejecutada correctamente');
      process.exit(0);
    })
    .catch((error) => {
      console.error('Error ejecutando migración:', error);
      process.exit(1);
    });
}

module.exports = { migratePausaFinMaquina };