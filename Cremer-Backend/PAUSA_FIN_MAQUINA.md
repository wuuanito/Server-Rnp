# Funcionalidad Pausa Fin Máquina

## Descripción

La funcionalidad **Pausa Fin Máquina** permite calcular y registrar los tiempos de producción (tiempo total, tiempo activo y tiempo de pausas) en el momento en que se registra una pausa de tipo `pausa_fin_maquina`, en lugar de esperar hasta la finalización de la orden.

## Características Principales

### 1. Nuevo Tipo de Pausa
- **Tipo**: `pausa_fin_maquina`
- **Computa tiempo**: Sí
- **Propósito**: Capturar el estado de tiempos de producción en un momento específico

### 2. Campos Añadidos al Modelo OrdenFabricacion

```javascript
// Nuevos campos en la tabla ordenes_fabricacion
horaPausaFinMaquina: DataTypes.DATE,
tiempoTotalHastaPausaFinMaquina: DataTypes.INTEGER,
tiempoActivoHastaPausaFinMaquina: DataTypes.INTEGER,
tiempoPausasHastaPausaFinMaquina: DataTypes.INTEGER
```

### 3. Comportamiento Modificado

#### Al Registrar Pausa Fin Máquina
Cuando se registra una pausa de tipo `pausa_fin_maquina`:

1. Se calculan los tiempos hasta ese momento:
   - **Tiempo Total**: Desde inicio de orden hasta la pausa
   - **Tiempo Activo**: Tiempo total menos tiempo de pausas
   - **Tiempo Pausas**: Solo pausas que computan tiempo

2. Se guardan estos tiempos en los nuevos campos de la orden

3. Se registra la hora exacta de la pausa fin máquina

#### Al Finalizar la Orden
Cuando se finaliza una orden que tiene pausa fin máquina:

1. **Se utilizan los tiempos ya calculados** en la pausa fin máquina
2. **NO se recalculan** los tiempos desde el inicio
3. Se indica en la respuesta que se usaron los tiempos de pausa fin máquina

## API Endpoints

### 1. Registrar Pausa Fin Máquina

```http
POST /api/ordenes-fabricacion/:id/pausar
Content-Type: application/json

{
  "tipoPausa": "pausa_fin_maquina",
  "comentario": "Pausa Fin Máquina"
}
```

**Respuesta:**
```json
{
  "message": "Pausa fin máquina registrada correctamente",
  "pausa": { /* datos de la pausa */ },
  "tiemposCalculados": {
    "horaPausaFinMaquina": "2024-01-15T10:30:00.000Z",
    "tiempoTotalMinutos": 120,
    "tiempoActivoMinutos": 100,
    "tiempoPausasMinutos": 20
  }
}
```

### 2. Obtener Información de Pausa Fin Máquina

```http
GET /api/ordenes-fabricacion/:id/pausa-fin-maquina
```

**Respuesta:**
```json
{
  "horaPausaFinMaquina": "2024-01-15T10:30:00.000Z",
  "tiempoTotalHastaPausaFinMaquina": 120,
  "tiempoActivoHastaPausaFinMaquina": 100,
  "tiempoPausasHastaPausaFinMaquina": 20,
  "pausaFinMaquina": {
    "id": 123,
    "horaInicio": "2024-01-15T10:30:00.000Z",
    "tipoPausa": "pausa_fin_maquina",
    "comentario": "Pausa Fin Máquina"
  }
}
```

### 3. Finalizar Orden (Comportamiento Modificado)

```http
POST /api/ordenes-fabricacion/:id/finalizar
Content-Type: application/json

{
  "unidadesCierreFin": 1000,
  "unidadesNoOkFin": 50,
  "numeroCorteSanitarioFinal": 1050
}
```

**Respuesta (con pausa fin máquina):**
```json
{
  "message": "Orden de fabricación finalizada correctamente usando tiempos de pausa fin máquina",
  "usoPausaFinMaquina": true,
  "orden": { /* datos completos de la orden */ }
}
```

## Flujo de Trabajo Recomendado

1. **Crear e Iniciar Orden**
   ```http
   POST /api/ordenes-fabricacion
   POST /api/ordenes-fabricacion/:id/iniciar
   ```

2. **Trabajar y Registrar Pausas Normales** (opcional)
   ```http
   POST /api/ordenes-fabricacion/:id/pausar
   ```

3. **Registrar Pausa Fin Máquina** (momento clave)
   ```http
   POST /api/ordenes-fabricacion/:id/pausar
   {
     "tipoPausa": "pausa_fin_maquina",
     "comentario": "Fin de producción en máquina"
   }
   ```

4. **Finalizar Orden** (usará tiempos de pausa fin máquina)
   ```http
   POST /api/ordenes-fabricacion/:id/finalizar
   ```

## Migración de Base de Datos

Para aplicar los cambios en la base de datos, ejecutar:

```bash
node migratePausaFinMaquina.js
```

Este script añade las nuevas columnas necesarias a la tabla `ordenes_fabricacion`.

## Pruebas

Para probar la funcionalidad completa:

```bash
node test_pausa_fin_maquina.js
```

Este script ejecuta un flujo completo de prueba que incluye:
- Creación e inicio de orden
- Registro de pausas normales
- Registro de pausa fin máquina
- Finalización de orden
- Verificación de tiempos

## Ventajas

1. **Precisión**: Los tiempos se capturan en el momento exacto de fin de máquina
2. **Flexibilidad**: Permite continuar con otras actividades después del fin de máquina
3. **Consistencia**: Los tiempos no cambian entre el fin de máquina y la finalización administrativa
4. **Trazabilidad**: Se mantiene registro de cuándo ocurrió el fin de máquina
5. **Compatibilidad**: Las órdenes sin pausa fin máquina siguen funcionando como antes

## Consideraciones

- Solo puede haber una pausa fin máquina por orden
- La pausa fin máquina debe registrarse antes de finalizar la orden
- Los tiempos calculados en pausa fin máquina son definitivos para la finalización
- Si no hay pausa fin máquina, se mantiene el comportamiento original de cálculo de tiempos