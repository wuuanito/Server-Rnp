# 🐳 Server RNP - Configuración Docker

Este proyecto contiene una configuración completa de Docker para orquestar múltiples microservicios del sistema Server RNP.

## 📋 Servicios Incluidos

| Servicio | Puerto | Descripción | Base de Datos |
|----------|--------|-------------|---------------|
| **Auth Service** | 4001 | Servicio de autenticación y autorización | MySQL (Puerto 3307) |
| **Cremer Backend** | 3002 | Backend para gestión de órdenes Cremer | MySQL (Puerto 3308) |
| **Tecnomaco Backend** | 3005 | Backend para gestión de órdenes Tecnomaco | MySQL (Puerto 3309) |
| **Servidor RPS** | 4000 | Servidor para conexión con SQL Server RPS | SQL Server Externo |
| **Nginx Proxy** | 80/443 | Reverse proxy y balanceador de carga | - |

## 🚀 Inicio Rápido

### Prerrequisitos

- Docker Desktop instalado
- Docker Compose v3.8 o superior
- Al menos 4GB de RAM disponible
- Puertos 80, 3002, 3005, 4000, 4001, 3307, 3308, 3309 disponibles

### Instalación

1. **Clonar y navegar al directorio:**
   ```bash
   cd c:\Users\desarrollos\Desktop\Server-Rnp
   ```

2. **Configurar variables de entorno:**
   ```bash
   # Copiar el archivo de ejemplo
   copy .env.example .env
   
   # Editar las variables según tu entorno
   notepad .env
   ```

3. **Construir y levantar todos los servicios:**
   ```bash
   docker-compose up --build -d
   ```

4. **Verificar que todos los servicios estén funcionando:**
   ```bash
   docker-compose ps
   ```

## 🔧 Comandos Útiles

### Gestión de Servicios

```bash
# Levantar todos los servicios
docker-compose up -d

# Levantar un servicio específico
docker-compose up -d auth-service

# Parar todos los servicios
docker-compose down

# Parar y eliminar volúmenes
docker-compose down -v

# Reconstruir servicios
docker-compose build --no-cache

# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f cremer-backend
```

### Monitoreo y Debugging

```bash
# Ver estado de los contenedores
docker-compose ps

# Verificar salud de los servicios
docker-compose exec auth-service curl http://localhost:4001/health

# Acceder al shell de un contenedor
docker-compose exec auth-service sh

# Ver uso de recursos
docker stats
```

## 🌐 Acceso a los Servicios

### A través de Nginx (Recomendado)

- **Página Principal:** http://localhost:8080/
- **Auth Service:** http://localhost:8080/auth/
- **Cremer Backend:** http://localhost:8080/cremer/
- **Tecnomaco Backend:** http://localhost:8080/tecnomaco/
- **Servidor RPS:** http://localhost:8080/rps/

### Acceso Directo

- **Auth Service:** http://localhost:4001
- **Cremer Backend:** http://localhost:3002
- **Tecnomaco Backend:** http://localhost:3005
- **Servidor RPS:** http://localhost:4000

### Bases de Datos

- **MySQL Auth:** localhost:3307
- **MySQL Cremer:** localhost:3308
- **MySQL Tecnomaco:** localhost:3309

## 📁 Estructura del Proyecto

```
Server-Rnp/
├── docker-compose.yml          # Orquestación principal
├── .env.example               # Variables de entorno de ejemplo
├── README-Docker.md           # Esta documentación
├── nginx/
│   └── nginx.conf            # Configuración del reverse proxy
├── auth-service/
│   ├── Dockerfile            # Imagen del servicio de auth
│   └── ...
├── Cremer-Backend/
│   ├── Dockerfile            # Imagen del backend Cremer
│   └── ...
├── Tecnomaco-Backend/
│   ├── Dockerfile            # Imagen del backend Tecnomaco
│   └── ...
└── Servidor_rps/
    ├── Dockerfile            # Imagen del servidor RPS
    └── ...
```

## ⚙️ Configuración Avanzada

### Variables de Entorno Importantes

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `JWT_SECRET` | Clave secreta para JWT | `cambiar_en_produccion` |
| `NODE_ENV` | Entorno de ejecución | `production` |
| `DB_HOST` | Host de la base de datos | `mysql-*` |
| `SQL_SERVER` | Servidor SQL Server externo | `192.168.11.2` |

### Escalabilidad

Para escalar servicios específicos:

```bash
# Escalar el backend de Cremer a 3 instancias
docker-compose up -d --scale cremer-backend=3

# Escalar múltiples servicios
docker-compose up -d --scale cremer-backend=2 --scale tecnomaco-backend=2
```

### Persistencia de Datos

Los datos se almacenan en volúmenes Docker:

- `mysql_auth_data`: Datos del servicio de autenticación
- `mysql_cremer_data`: Datos del backend Cremer
- `mysql_tecnomaco_data`: Datos del backend Tecnomaco

### Backup de Datos

```bash
# Backup de la base de datos de auth
docker-compose exec mysql-auth mysqldump -u root -pRoot123! auth_service_db > backup_auth.sql

# Backup de la base de datos de Cremer
docker-compose exec mysql-cremer mysqldump -u root -proot cremer > backup_cremer.sql

# Backup de la base de datos de Tecnomaco
docker-compose exec mysql-tecnomaco mysqldump -u root -proot tecnomaco > backup_tecnomaco.sql
```

## 🔒 Seguridad

### Recomendaciones de Producción

1. **Cambiar contraseñas por defecto:**
   - Actualizar todas las contraseñas en el archivo `.env`
   - Generar un `JWT_SECRET` seguro y único

2. **Configurar HTTPS:**
   - Agregar certificados SSL en `nginx/ssl/`
   - Actualizar la configuración de Nginx

3. **Limitar acceso a bases de datos:**
   - Configurar firewalls
   - Usar redes Docker privadas

4. **Monitoreo y logs:**
   - Implementar agregación de logs
   - Configurar alertas de salud

## 🐛 Solución de Problemas

### Problemas Comunes

**Error: Puerto ya en uso**
```bash
# Verificar qué proceso usa el puerto
netstat -ano | findstr :4001

# Cambiar el puerto en docker-compose.yml
ports:
  - "4002:4001"  # Cambiar puerto externo
```

**Error: No se puede conectar a la base de datos**
```bash
# Verificar que el contenedor de MySQL esté funcionando
docker-compose ps mysql-auth

# Ver logs de la base de datos
docker-compose logs mysql-auth

# Reiniciar el servicio de base de datos
docker-compose restart mysql-auth
```

**Error: Servicio no responde**
```bash
# Verificar logs del servicio
docker-compose logs auth-service

# Verificar conectividad de red
docker-compose exec auth-service ping mysql-auth

# Reiniciar el servicio
docker-compose restart auth-service
```

### Health Checks

Todos los servicios incluyen health checks automáticos:

```bash
# Ver estado de salud
docker-compose ps

# Verificar health check manualmente
docker-compose exec auth-service curl http://localhost:4001/health
```

## 📊 Monitoreo

### Métricas Básicas

```bash
# Uso de CPU y memoria
docker stats

# Logs en tiempo real
docker-compose logs -f --tail=100

# Verificar conectividad entre servicios
docker-compose exec nginx curl http://auth-service:4001/health
```

## 🔄 Actualizaciones

### Actualizar un Servicio

```bash
# Parar el servicio
docker-compose stop cremer-backend

# Reconstruir la imagen
docker-compose build cremer-backend

# Levantar el servicio actualizado
docker-compose up -d cremer-backend
```

### Actualización Completa

```bash
# Parar todos los servicios
docker-compose down

# Reconstruir todas las imágenes
docker-compose build --no-cache

# Levantar todos los servicios
docker-compose up -d
```

## 📞 Soporte

Para problemas o preguntas:

1. Revisar los logs: `docker-compose logs [servicio]`
2. Verificar la configuración de red
3. Consultar la documentación de cada servicio individual
4. Verificar que todas las dependencias externas estén disponibles

---

**Nota:** Este sistema está diseñado para ser escalable y mantenible. Cada servicio puede ser actualizado, escalado o reemplazado independientemente.