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
RUN adduser -S cremer -u 1001

# Crear directorio para logs si es necesario
RUN mkdir -p logs && chown -R cremer:nodejs logs

# Cambiar permisos del directorio
RUN chown -R cremer:nodejs /app
USER cremer

# Exponer puerto
EXPOSE 3002

# Variables de entorno por defecto
ENV NODE_ENV=production
ENV PORT=3002

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3002/health', (res) => { process.exit(res.statusCode === 200 ? 0 : 1) }).on('error', () => process.exit(1))"

# Comando de inicio
CMD ["npm", "start"]