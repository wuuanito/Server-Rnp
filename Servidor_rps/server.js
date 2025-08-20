// Importamos las dependencias
const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const sql = require('mssql');

// Configuración de la aplicación Express
const app = express();
const port = 4000;

// Middleware para CORS y parseo de JSON
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Configuración de conexión a SQL Server
const dbConfig = {
  user: 'rpsuser',
  password: 'rpsnext',
  server: '192.168.11.2',
  database: 'RpsNext',
  options: {
    encrypt: false, // Para Azure usar true
    trustServerCertificate: true, // Cambia a false en producción
  }
};

// Ruta para servir archivos estáticos (HTML, CSS, JS)
app.use(express.static('public'));

// Endpoint para buscar órdenes de fabricación
// Endpoint para buscar órdenes de fabricación
app.post('/api/search', async (req, res) => {
    try {
      const searchTerm = req.body.term || '';
      
      // Conectar a la base de datos
      await sql.connect(dbConfig);
      
      // Preparar y ejecutar la consulta actualizada con JOIN
      const query = `
        SELECT CPRManufacturingOrder.CodManufacturingOrder, 
               CPRManufacturingOrder.Description,
               CPRManufacturingOrder.Quantity, 
               STKArticle.CodArticle 
        FROM CPRManufacturingOrder 
        JOIN STKArticle ON CPRManufacturingOrder.IDArticle = STKArticle.IDArticle
        WHERE CPRManufacturingOrder.CodManufacturingOrder LIKE @searchTerm 
        ORDER BY CPRManufacturingOrder.CodManufacturingOrder
      `;
      
      const request = new sql.Request();
      request.input('searchTerm', sql.VarChar, '%' + searchTerm + '%');
      
      const result = await request.query(query);
      
      // Formatear los resultados para el autocompletado incluyendo el código de artículo
      const formattedResults = result.recordset.map(item => ({
        label: item.CodManufacturingOrder,
        value: item.CodManufacturingOrder,
        description: item.Description,
        quantity: item.Quantity,
        codArticle: item.CodArticle
      }));
      
      // Devolver los resultados como JSON
      res.json(formattedResults);
      
    } catch (err) {
      console.error('Error en la consulta:', err);
      res.status(500).json({ error: err.message });
    } finally {
      // Cerrar la conexión
      sql.close();
    }
  });
// Endpoint para probar la conexión
app.post('/api/test-connection', async (req, res) => {
  try {
    // Usar configuración desde el cliente o la predeterminada
    const config = req.body.config || dbConfig;
    
    // Intentar conectar
    await sql.connect(config);
    
    // Si llegamos aquí, la conexión fue exitosa
    res.json({ success: true, message: 'Conexión exitosa a la base de datos' });
  } catch (err) {
    console.error('Error de conexión:', err);
    res.status(500).json({ 
      success: false, 
      message: 'Error al conectar con la base de datos: ' + err.message 
    });
  } finally {
    // Cerrar la conexión
    sql.close();
  }
});

// Iniciar el servidor
app.listen(port, () => {
  console.log(`Servidor ejecutándose en http://localhost:${port}`);
});