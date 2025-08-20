-- Migración SQL directa para agregar campos de pausa fin máquina
-- Ejecutar este script directamente en MySQL si el script de Node.js falla

USE cremer;

-- Verificar si las columnas ya existen antes de agregarlas

-- Agregar columna horaPausaFinMaquina
SET @sql = IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_NAME = 'ordenes_fabricacion' 
     AND COLUMN_NAME = 'horaPausaFinMaquina' 
     AND TABLE_SCHEMA = DATABASE()) = 0,
    'ALTER TABLE ordenes_fabricacion ADD COLUMN horaPausaFinMaquina DATETIME NULL COMMENT "Hora en que se ejecutó la pausa fin máquina"',
    'SELECT "Columna horaPausaFinMaquina ya existe" as mensaje'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Agregar columna tiempoTotalHastaPausaFinMaquina
SET @sql = IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_NAME = 'ordenes_fabricacion' 
     AND COLUMN_NAME = 'tiempoTotalHastaPausaFinMaquina' 
     AND TABLE_SCHEMA = DATABASE()) = 0,
    'ALTER TABLE ordenes_fabricacion ADD COLUMN tiempoTotalHastaPausaFinMaquina INT NULL COMMENT "Tiempo total en minutos hasta la pausa fin máquina"',
    'SELECT "Columna tiempoTotalHastaPausaFinMaquina ya existe" as mensaje'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Agregar columna tiempoActivoHastaPausaFinMaquina
SET @sql = IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_NAME = 'ordenes_fabricacion' 
     AND COLUMN_NAME = 'tiempoActivoHastaPausaFinMaquina' 
     AND TABLE_SCHEMA = DATABASE()) = 0,
    'ALTER TABLE ordenes_fabricacion ADD COLUMN tiempoActivoHastaPausaFinMaquina INT NULL COMMENT "Tiempo activo en minutos hasta la pausa fin máquina"',
    'SELECT "Columna tiempoActivoHastaPausaFinMaquina ya existe" as mensaje'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Agregar columna tiempoPausasHastaPausaFinMaquina
SET @sql = IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_NAME = 'ordenes_fabricacion' 
     AND COLUMN_NAME = 'tiempoPausasHastaPausaFinMaquina' 
     AND TABLE_SCHEMA = DATABASE()) = 0,
    'ALTER TABLE ordenes_fabricacion ADD COLUMN tiempoPausasHastaPausaFinMaquina INT NULL COMMENT "Tiempo de pausas en minutos hasta la pausa fin máquina"',
    'SELECT "Columna tiempoPausasHastaPausaFinMaquina ya existe" as mensaje'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Verificar que las columnas se agregaron correctamente
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'ordenes_fabricacion' 
AND TABLE_SCHEMA = DATABASE()
AND COLUMN_NAME IN (
    'horaPausaFinMaquina',
    'tiempoTotalHastaPausaFinMaquina', 
    'tiempoActivoHastaPausaFinMaquina',
    'tiempoPausasHastaPausaFinMaquina'
)
ORDER BY COLUMN_NAME;

SELECT 'Migración de pausa fin máquina completada' as resultado;