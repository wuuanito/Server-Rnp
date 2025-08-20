# Usar imagen oficial de Node.js
FROM node:18-alpine

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar dependencias
RUN npm ci --only=production && npm cache clean --force

# Copiar código fuente
COPY . .

# Crear usuario no-root para seguridad
RUN addgroup -g 1001 -S nodejs
RUN adduser -S tecnomaco -u 1001

# Crear directorio para logs si es necesario
RUN mkdir -p logs && chown -R tecnomaco:nodejs logs

# Cambiar permisos del directorio
RUN chown -R tecnomaco:nodejs /app
USER tecnomaco

# Exponer puerto
EXPOSE 3005

# Variables de entorno por defecto
ENV NODE_ENV=production
ENV PORT=3005

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3005/health', (res) => { process.exit(res.statusCode === 200 ? 0 : 1) }).on('error', () => process.exit(1))"

# Comando de inicio
CMD ["npm", "start"]