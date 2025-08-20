const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');

const OrdenFabricacion = sequelize.define('OrdenFabricacion', {
  // Identificación básica
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true,
    unique: true
  },
  
  // Datos básicos de creación
  codigoOrden: {
    type: DataTypes.STRING,
    allowNull: false,
    unique: true,
    validate: {
      notNull: {
        msg: 'El código de orden es obligatorio'
      },
      notEmpty: {
        msg: 'El código de orden no puede estar vacío'
      }
    }
  },
  codigoArticulo: {
    type: DataTypes.STRING,
    allowNull: false,
    validate: {
      notNull: {
        msg: 'El código de artículo es obligatorio'
      },
      notEmpty: {
        msg: 'El código de artículo no puede estar vacío'
      }
    }
  },
  producto: {
    type: DataTypes.STRING,
    allowNull: false,
    validate: {
      notNull: {
        msg: 'El nombre del producto es obligatorio'
      },
      notEmpty: {
        msg: 'El nombre del producto no puede estar vacío'
      }
    }
  },
  
  // NUEVOS CAMPOS AÑADIDOS
  formato: {
    type: DataTypes.STRING,
    allowNull: true,
    defaultValue: null,
    comment: 'Formato del producto'
  },
  tipo: {
    type: DataTypes.STRING,
    allowNull: true,
    defaultValue: null,
    comment: 'Tipo de producto'
  },
  udsBote: {
    type: DataTypes.INTEGER,
    allowNull: true,
    defaultValue: null,
    comment: 'Unidades por bote',
    validate: {
      min: {
        args: [0],
        msg: 'Las unidades por bote no pueden ser negativas'
      }
    }
  },
  tipoBote: {
    type: DataTypes.STRING,
    allowNull: true,
    defaultValue: null,
    comment: 'Tipo de bote utilizado'
  },
  
  // Tiempos
  horaInicio: {
    type: DataTypes.DATE,
    allowNull: true
  },
  horaFin: {
    type: DataTypes.DATE,
    allowNull: true
  },
  
  // Detalles de producción
  cantidadProducir: {
    type: DataTypes.INTEGER,
    allowNull: false,
    validate: {
      min: {
        args: [1],
        msg: 'La cantidad a producir debe ser mayor a 0'
      }
    }
  },
  numeroCajas: {
    type: DataTypes.INTEGER,
    allowNull: false,
    validate: {
      min: {
        args: [0],
        msg: 'El número de cajas no puede ser negativo'
      }
    }
  },
  botesPorCaja: {
    type: DataTypes.INTEGER,
    allowNull: true,
    defaultValue: null,
    validate: {
      min: {
        args: [0],
        msg: 'Los botes por caja no pueden ser negativos'
      }
    }
  },
  
  // Contador de cajas (durante producción)
  cajasContadas: {
    type: DataTypes.INTEGER,
    allowNull: false,
    defaultValue: 0,
    comment: 'Contador de cajas durante la producción'
  },
  
  // Botes buenos (calculado automáticamente)
  botesBuenos: {
    type: DataTypes.INTEGER,
    allowNull: false,
    defaultValue: 0,
    comment: 'Calculado automáticamente: cajasContadas * botesPorCaja'
  },
  
  // Repercap
  repercap: {
    type: DataTypes.BOOLEAN,
    allowNull: false,
    defaultValue: false
  },
  numeroCorteSanitarioInicial: {
    type: DataTypes.INTEGER,
    allowNull: true,
    defaultValue: null,
    validate: {
      min: {
        args: [0],
        msg: 'El número de corte sanitario inicial no puede ser negativo'
      }
    }
  },
  numeroCorteSanitarioFinal: {
    type: DataTypes.INTEGER,
    allowNull: true,
    defaultValue: null,
    validate: {
      min: {
        args: [0],
        msg: 'El número de corte sanitario final no puede ser negativo'
      }
    }
  },
  
  // Tiempo estimado
  tiempoEstimadoProduccion: {
    type: DataTypes.FLOAT,
    allowNull: true,
    comment: 'Tiempo estimado en minutos = unidades a producir / estándar teórico (33.3)'
  },
  
  // Tiempos reales (en minutos)
  tiempoTotalActivo: {
    type: DataTypes.INTEGER,
    allowNull: false,
    defaultValue: 0,
    comment: 'Tiempo activo en minutos'
  },
  tiempoTotalPausas: {
    type: DataTypes.INTEGER,
    allowNull: false,
    defaultValue: 0,
    comment: 'Tiempo de pausas en minutos'
  },
  tiempoTotal: {
    type: DataTypes.INTEGER,
    allowNull: false,
    defaultValue: 0,
    comment: 'Tiempo total en minutos'
  },
  
  // Campos específicos para pausa fin máquina
  horaPausaFinMaquina: {
    type: DataTypes.DATE,
    allowNull: true,
    comment: 'Hora en que se ejecutó la pausa fin máquina'
  },
  tiempoTotalHastaPausaFinMaquina: {
    type: DataTypes.INTEGER,
    allowNull: true,
    comment: 'Tiempo total en minutos hasta la pausa fin máquina'
  },
  tiempoActivoHastaPausaFinMaquina: {
    type: DataTypes.INTEGER,
    allowNull: true,
    comment: 'Tiempo activo en minutos hasta la pausa fin máquina'
  },
  tiempoPausasHastaPausaFinMaquina: {
    type: DataTypes.INTEGER,
    allowNull: true,
    comment: 'Tiempo de pausas en minutos hasta la pausa fin máquina'
  },
  
  // Unidades al cierre
  unidadesCierreFin: {
    type: DataTypes.INTEGER,
    allowNull: true,
    defaultValue: 0
  },
  unidadesNoOkFin: {
    type: DataTypes.INTEGER,
    allowNull: true,
    defaultValue: 0
  },
  totalUnidades: {
    type: DataTypes.INTEGER,
    allowNull: true,
    defaultValue: 0,
    comment: 'unidadesCierreFin + unidadesNoOkFin'
  },
  
  // Sistema ponderal
  botesPonderal: {
    type: DataTypes.INTEGER,
    defaultValue: 0,
    allowNull: false,
    comment: 'Contador de botes ponderal (activado por PIN 23)'
  },
  botesExpulsados: {
    type: DataTypes.INTEGER,
    defaultValue: 0,
    allowNull: false,
    comment: 'Contador de botes expulsados (activado por PIN 22)'
  },

  
  // Recirculación
  recirculacionRepercap: {
    type: DataTypes.INTEGER,
    allowNull: true,
    defaultValue: null,
    comment: 'Calculado automáticamente: (numeroCorteSanitarioFinal - numeroCorteSanitarioInicial) - totalUnidades'
  },
  recirculacionPonderal: {
    type: DataTypes.FLOAT,
    allowNull: true,
    defaultValue: null,
    comment: 'Recirculación ponderal = botesPonderal - totalUnidades'
  },
  
  // Métricas calculadas (porcentajes 0-100)
  porcentajeUnidadesOk: {
    type: DataTypes.FLOAT,
    allowNull: true,
    defaultValue: null
  },
  porcentajeUnidadesNoOk: {
    type: DataTypes.FLOAT,
    allowNull: true,
    defaultValue: null
  },
  porcentajePausas: {
    type: DataTypes.FLOAT,
    allowNull: true,
    defaultValue: null
  },
  porcentajeCompletado: {
    type: DataTypes.FLOAT,
    allowNull: true,
    defaultValue: null
  },
  
  // Tasas (porcentajes 0-100)
  tasaExpulsion: {
    type: DataTypes.FLOAT,
    allowNull: true,
    defaultValue: null,
    comment: '(botesExpulsados / totalUnidades) * 100'
  },
  tasaRecuperacionPonderal: {
    type: DataTypes.FLOAT,
    allowNull: true,
    defaultValue: null,
    comment: 'Tasa recuperación ponderal = (recirculacionPonderal / totalUnidades) * 100'
  },
  tasaRecuperacionRepercap: {
    type: DataTypes.FLOAT,
    allowNull: true,
    defaultValue: null,
    comment: '(recirculacionRepercap / totalUnidades) * 100'
  },
  
  // Estándares
  standardReal: {
    type: DataTypes.FLOAT,
    allowNull: true,
    defaultValue: null,
    comment: 'totalUnidades / tiempoTotalActivo'
  },
  standardRealVsTeorico: {
    type: DataTypes.FLOAT,
    allowNull: true,
    defaultValue: null,
    comment: '(standardReal - 33.3) / 33.3'
  },
  
  // Indicadores de rendimiento (valores decimales 0-1)
  disponibilidad: {
    type: DataTypes.FLOAT,
    allowNull: true,
    defaultValue: null,
    comment: 'tiempo activo / tiempo total (activo + pausas) - valor entre 0 y 1'
  },
  rendimiento: {
    type: DataTypes.FLOAT,
    allowNull: true,
    defaultValue: null,
    comment: 'total unidades / (tiempo activo * estándar teórico 33.3) - valor entre 0 y 1'
  },
  calidad: {
    type: DataTypes.FLOAT,
    allowNull: true,
    defaultValue: null,
    comment: 'unidades ok / unidades totales - valor entre 0 y 1'
  },
  
  // OEE (Overall Equipment Effectiveness) (valor decimal 0-1)
  oee: {
    type: DataTypes.FLOAT,
    allowNull: true,
    defaultValue: null,
    comment: 'calidad * rendimiento * disponibilidad (valor entre 0 y 1)'
  },
  
  // Estado de la orden
  estado: {
    type: DataTypes.ENUM('creada', 'iniciada', 'pausada', 'finalizada'),
    defaultValue: 'creada',
    allowNull: false
  }
}, {
  tableName: 'ordenes_fabricacion',
  timestamps: true,
  
  hooks: {
    beforeCreate: (orden, options) => {
      const { DateTime } = require('luxon');

// Guardar horaInicio en horario de Madrid (Europe/Madrid)
if (!orden.horaInicio) {
  orden.horaInicio = DateTime.now().setZone('Europe/Madrid').toJSDate();
}
      try {
        console.log('Hook beforeCreate ejecutándose...');
        console.log('Datos de orden:', JSON.stringify(orden.dataValues, null, 2));
        
        // Calcular tiempo estimado de producción
        if (orden.cantidadProducir && !orden.tiempoEstimadoProduccion) {
          orden.tiempoEstimadoProduccion = orden.cantidadProducir / 33.3;
        }
        
        // Calcular botes buenos automáticamente si hay datos
        if (orden.cajasContadas && orden.botesPorCaja) {
          orden.botesBuenos = orden.cajasContadas * orden.botesPorCaja;
          console.log(`Botes buenos calculados: ${orden.cajasContadas} cajas * ${orden.botesPorCaja} botes/caja = ${orden.botesBuenos} botes`);
        }
        
        // Manejo seguro de campos null/undefined para campos existentes
        if (orden.botesPorCaja === undefined) {
          orden.botesPorCaja = null;
        }
        
        if (orden.numeroCorteSanitarioInicial === undefined) {
          orden.numeroCorteSanitarioInicial = null;
        }
        
        if (orden.numeroCorteSanitarioFinal === undefined) {
          orden.numeroCorteSanitarioFinal = null;
        }
        
        // Manejo seguro de campos null/undefined para NUEVOS CAMPOS
        if (orden.formato === undefined) {
          orden.formato = null;
        }
        
        if (orden.tipo === undefined) {
          orden.tipo = null;
        }
        
        if (orden.udsBote === undefined) {
          orden.udsBote = null;
        }
        
        if (orden.tipoBote === undefined) {
          orden.tipoBote = null;
        }
        
        // Restablecer campos calculados a null
        orden.oee = null;
        orden.disponibilidad = null;
        orden.rendimiento = null;
        orden.calidad = null;
        orden.porcentajeUnidadesOk = null;
        orden.porcentajeUnidadesNoOk = null;
        orden.porcentajePausas = null;
        orden.porcentajeCompletado = null;
        orden.standardReal = null;
        orden.standardRealVsTeorico = null;
        orden.tasaExpulsion = null;
        orden.tasaRecuperacionPonderal = null;
        orden.tasaRecuperacionRepercap = null;
        orden.recirculacionRepercap = null;
        orden.recirculacionPonderal = null;

        
        console.log('Hook beforeCreate completado exitosamente');
      } catch (error) {
        console.error('Error en hook beforeCreate:', error);
        throw error;
      }
    },
    
    beforeSave: (orden, options) => {
      try {
        console.log('Hook beforeSave ejecutándose...');
        
        // Verificar si se está llamando desde el método finalizar con hooks: false
        if (options && options.hooks === false) {
          console.log('Hooks desactivados, saltando cálculos automáticos');
          return;
        }
        
        // CALCULAR BOTES BUENOS automáticamente
        if (orden.cajasContadas && orden.botesPorCaja) {
          const botesBuenosCalculados = orden.cajasContadas * orden.botesPorCaja;
          if (orden.botesBuenos !== botesBuenosCalculados) {
            orden.botesBuenos = botesBuenosCalculados;
            console.log(`Botes buenos recalculados: ${orden.cajasContadas} cajas * ${orden.botesPorCaja} botes/caja = ${orden.botesBuenos} botes`);
          }
        }
        

        
        // Calcular recirculación repercap
        if (orden.numeroCorteSanitarioFinal !== null && orden.numeroCorteSanitarioFinal !== undefined &&
            orden.numeroCorteSanitarioInicial !== null && orden.numeroCorteSanitarioInicial !== undefined &&
            orden.totalUnidades) {
          const corteFinal = Number(orden.numeroCorteSanitarioFinal);
          const corteInicial = Number(orden.numeroCorteSanitarioInicial);
          orden.recirculacionRepercap = (corteFinal - corteInicial) - orden.totalUnidades;
          console.log(`Recirculación Repercap calculada: (${corteFinal} - ${corteInicial}) - ${orden.totalUnidades} = ${orden.recirculacionRepercap}`);
        }
        

        
        // Calcular total de unidades
        if (orden.unidadesCierreFin !== null && orden.unidadesCierreFin !== undefined &&
            orden.unidadesNoOkFin !== null && orden.unidadesNoOkFin !== undefined) {
          orden.totalUnidades = orden.unidadesCierreFin + orden.unidadesNoOkFin;
          console.log(`Total unidades calculado: ${orden.totalUnidades}`);
        }
        
        // Calcular recirculación ponderal
        if (orden.botesPonderal !== undefined && orden.totalUnidades) {
          orden.recirculacionPonderal = orden.botesPonderal - orden.totalUnidades;
          console.log(`Recirculación ponderal calculada: ${orden.botesPonderal} - ${orden.totalUnidades} = ${orden.recirculacionPonderal}`);
          
          // Calcular tasa de recuperación ponderal
          if (orden.totalUnidades > 0) {
            orden.tasaRecuperacionPonderal = (orden.recirculacionPonderal / orden.totalUnidades) * 100;
          }
        }
        
        // Continuar con los cálculos de métricas solo si hay datos suficientes
        if (orden.tiempoTotal && orden.tiempoTotalActivo && orden.tiempoTotal > 0 && orden.tiempoTotalActivo > 0) {
          console.log('Calculando métricas de rendimiento...');
          
          // FÓRMULAS OEE CORREGIDAS:
          // Disponibilidad = tiempo activo / tiempo total (activo + pausas) (como decimal 0-1)
          orden.disponibilidad = orden.tiempoTotalActivo / orden.tiempoTotal;
          
          // Standard real (unidades por minuto)
          if (orden.totalUnidades && orden.tiempoTotalActivo > 0) {
            orden.standardReal = orden.totalUnidades / orden.tiempoTotalActivo;
            
            const standardTeorico = 33.3; // unidades por minuto
            orden.standardRealVsTeorico = (orden.standardReal - standardTeorico) / standardTeorico;
            
            // Rendimiento = total unidades / (tiempo activo * estándar teórico)
            orden.rendimiento = orden.totalUnidades / (orden.tiempoTotalActivo * standardTeorico);
          }
          
          // Calidad = unidades ok / unidades totales (como decimal 0-1)
          if (orden.totalUnidades && orden.unidadesCierreFin && orden.totalUnidades > 0) {
            orden.calidad = orden.unidadesCierreFin / orden.totalUnidades;
          }
          
          // OEE = Calidad * Rendimiento * Disponibilidad (como decimal 0-1)
          if (orden.disponibilidad !== null && orden.rendimiento !== null && orden.calidad !== null) {
            orden.oee = orden.disponibilidad * orden.rendimiento * orden.calidad;
          }
          
          // Porcentajes (como 0-100)
          if (orden.totalUnidades && orden.totalUnidades > 0) {
            orden.porcentajeUnidadesOk = (orden.unidadesCierreFin / orden.totalUnidades) * 100;
            orden.porcentajeUnidadesNoOk = (orden.unidadesNoOkFin / orden.totalUnidades) * 100;
            
            // Tasa de expulsión
            if (orden.botesExpulsados) {
              orden.tasaExpulsion = (orden.botesExpulsados / orden.totalUnidades) * 100;
            }
            
            // Tasa de recuperación repercap
            if (orden.recirculacionRepercap !== null) {
              orden.tasaRecuperacionRepercap = (orden.recirculacionRepercap / orden.totalUnidades) * 100;
            }
          }
          
          // Porcentaje de completado
          if (orden.cantidadProducir && orden.cantidadProducir > 0) {
            orden.porcentajeCompletado = (orden.unidadesCierreFin / orden.cantidadProducir) * 100;
          }
          
          // Porcentaje de pausas
          if (orden.tiempoTotal > 0) {
            orden.porcentajePausas = (orden.tiempoTotalPausas / orden.tiempoTotal) * 100;
          }
        }
        
        console.log('Hook beforeSave completado exitosamente');
      } catch (error) {
        console.error('Error en hook beforeSave:', error);
        throw error;
      }
    }
  }
});

module.exports = OrdenFabricacion;