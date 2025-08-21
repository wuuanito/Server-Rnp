# 🔐 Guía de Implementación de Login para React App

## 📋 Configuración del Backend (Ya implementado)

**Servicio de Autenticación:**
- **URL Base:** `http://localhost:4001` (o `http://localhost:8080/auth/` a través de Nginx)
- **Base de datos:** MySQL con tabla `Users` y `Tokens`
- **Autenticación:** JWT con Access Token (1h) y Refresh Token (7d)

## 🚀 Endpoints Principales para React

### 1. **Login** 
```javascript
POST /api/auth/login
Content-Type: application/json

{
  "username": "usuario" || "email": "user@email.com",
  "password": "contraseña"
}
```

**Respuesta exitosa:**
```javascript
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "usuario",
      "email": "user@email.com",
      "firstName": "Nombre",
      "lastName": "Apellido",
      "role": "empleado", // director, administrador, empleado
      "department": "informatica",
      "jobTitle": "Desarrollador",
      "isActive": true
    },
    "accessToken": "eyJhbGciOiJIUzI1NiIs...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIs..."
  },
  "message": "Login successful"
}
```

### 2. **Refresh Token**
```javascript
POST /api/auth/refresh-token
{
  "refreshToken": "eyJhbGciOiJIUzI1NiIs..."
}
```

### 3. **Perfil de Usuario**
```javascript
GET /api/auth/profile
Authorization: Bearer {accessToken}
```

### 4. **Logout**
```javascript
POST /api/auth/logout
Authorization: Bearer {accessToken}
```

## 💻 Implementación en React

### 1. **Servicio de Autenticación (authService.js)**
```javascript
const API_BASE = 'http://localhost:4001/api/auth';
// o 'http://localhost:8080/auth/api/auth' si usas Nginx

class AuthService {
  async login(credentials) {
    const response = await fetch(`${API_BASE}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials)
    });
    
    const data = await response.json();
    
    if (data.success) {
      // Guardar tokens en localStorage
      localStorage.setItem('accessToken', data.data.accessToken);
      localStorage.setItem('refreshToken', data.data.refreshToken);
      localStorage.setItem('user', JSON.stringify(data.data.user));
      return data.data;
    }
    
    throw new Error(data.error || 'Login failed');
  }
  
  async refreshToken() {
    const refreshToken = localStorage.getItem('refreshToken');
    if (!refreshToken) throw new Error('No refresh token');
    
    const response = await fetch(`${API_BASE}/refresh-token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refreshToken })
    });
    
    const data = await response.json();
    if (data.success) {
      localStorage.setItem('accessToken', data.data.accessToken);
      localStorage.setItem('refreshToken', data.data.refreshToken);
      return data.data;
    }
    
    this.logout();
    throw new Error('Token refresh failed');
  }
  
  logout() {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
  }
  
  getCurrentUser() {
    return JSON.parse(localStorage.getItem('user') || 'null');
  }
  
  getAccessToken() {
    return localStorage.getItem('accessToken');
  }
}

export default new AuthService();
```

### 2. **Hook de Autenticación (useAuth.js)**
```javascript
import { createContext, useContext, useState, useEffect } from 'react';
import authService from './authService';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = () => {
      const savedUser = authService.getCurrentUser();
      if (savedUser) {
        setUser(savedUser);
      }
      setLoading(false);
    };
    
    initAuth();
  }, []);

  const login = async (credentials) => {
    try {
      const userData = await authService.login(credentials);
      setUser(userData.user);
      return userData;
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{
      user,
      login,
      logout,
      loading,
      isAuthenticated: !!user
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

### 3. **Componente de Login**
```javascript
import React, { useState } from 'react';
import { useAuth } from './useAuth';
import { useNavigate } from 'react-router-dom';

const LoginForm = () => {
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      await login(credentials);
      navigate('/dashboard'); // Redirigir después del login
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Usuario o Email:</label>
        <input
          type="text"
          value={credentials.username}
          onChange={(e) => setCredentials({
            ...credentials,
            username: e.target.value
          })}
          required
        />
      </div>
      
      <div>
        <label>Contraseña:</label>
        <input
          type="password"
          value={credentials.password}
          onChange={(e) => setCredentials({
            ...credentials,
            password: e.target.value
          })}
          required
        />
      </div>
      
      {error && <div className="error">{error}</div>}
      
      <button type="submit" disabled={loading}>
        {loading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
      </button>
    </form>
  );
};

export default LoginForm;
```

### 4. **Componente de Ruta Protegida**
```javascript
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from './useAuth';

const ProtectedRoute = ({ children, requiredRole = null }) => {
  const { user, loading, isAuthenticated } = useAuth();

  if (loading) {
    return <div>Cargando...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Verificar rol si es requerido
  if (requiredRole && user.role !== requiredRole) {
    return <div>No tienes permisos para acceder a esta página</div>;
  }

  return children;
};

export default ProtectedRoute;
```

### 5. **Interceptor para Axios (Opcional)**
```javascript
import axios from 'axios';
import authService from './authService';

// Configurar base URL
axios.defaults.baseURL = 'http://localhost:4001';
// o 'http://localhost:8080/auth' si usas Nginx

// Interceptor para agregar token automáticamente
axios.interceptors.request.use(
  (config) => {
    const token = authService.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para manejar token expirado
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        await authService.refreshToken();
        // Actualizar el token en la petición original
        const newToken = authService.getAccessToken();
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return axios(originalRequest);
      } catch (refreshError) {
        authService.logout();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default axios;
```

### 6. **Configuración de Rutas en App.js**
```javascript
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './hooks/useAuth';
import LoginForm from './components/LoginForm';
import Dashboard from './components/Dashboard';
import ProtectedRoute from './components/ProtectedRoute';
import AdminPanel from './components/AdminPanel';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/login" element={<LoginForm />} />
            
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/admin" 
              element={
                <ProtectedRoute requiredRole="administrador">
                  <AdminPanel />
                </ProtectedRoute>
              } 
            />
            
            <Route path="/" element={<Navigate to="/dashboard" />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
```

## 🔒 Características de Seguridad Implementadas

- **Tokens JWT** con expiración automática (1 hora)
- **Refresh Tokens** para renovación automática (7 días)
- **Validación de roles** (director, administrador, empleado)
- **Middleware de autenticación** para rutas protegidas
- **Encriptación de contraseñas** con bcrypt
- **Validación de entrada** con express-validator
- **Logs de seguridad** para auditoría
- **Renovación automática de tokens** con interceptores

## 📱 Roles y Permisos

### Roles disponibles:
- **director**: Acceso completo al sistema
- **administrador**: Gestión de usuarios y configuración
- **empleado**: Acceso básico a funcionalidades

### Departamentos disponibles:
- informatica
- administracion
- internacional
- compras
- gerencia
- oficina_tecnica
- calidad
- laboratorio
- rrhh
- logistica
- mantenimiento
- softgel
- produccion
- sin_departamento

## 🛠️ Instalación y Configuración

### 1. Instalar dependencias
```bash
npm install axios react-router-dom
```

### 2. Variables de entorno (.env)
```env
REACT_APP_API_URL=http://localhost:4001
# o REACT_APP_API_URL=http://localhost:8080/auth si usas Nginx
```

### 3. Uso en componentes
```javascript
import { useAuth } from './hooks/useAuth';

const MyComponent = () => {
  const { user, isAuthenticated, logout } = useAuth();
  
  if (!isAuthenticated) {
    return <div>No autenticado</div>;
  }
  
  return (
    <div>
      <h1>Bienvenido, {user.firstName}!</h1>
      <p>Rol: {user.role}</p>
      <p>Departamento: {user.department}</p>
      <button onClick={logout}>Cerrar Sesión</button>
    </div>
  );
};
```

## 🔧 Endpoints Adicionales

### Registro de Usuario
```javascript
POST /api/auth/register
{
  "username": "nuevo_usuario",
  "email": "usuario@email.com",
  "password": "contraseña123",
  "firstName": "Nombre",
  "lastName": "Apellido",
  "department": "informatica",
  "role": "empleado",
  "jobTitle": "Desarrollador"
}
```

### Cambio de Contraseña
```javascript
PUT /api/auth/change-password
Authorization: Bearer {accessToken}
{
  "currentPassword": "contraseña_actual",
  "newPassword": "nueva_contraseña"
}
```

### Recuperación de Contraseña
```javascript
POST /api/auth/forgot-password
{
  "email": "usuario@email.com"
}
```

## 📚 Documentación Adicional

- **Postman Collection**: Ver `POSTMAN_USER_MANAGEMENT.md` para ejemplos completos
- **Docker**: El servicio está dockerizado y disponible en `http://localhost:4001`
- **Nginx**: Acceso a través del proxy en `http://localhost:8080/auth/`
- **Logs**: Los logs de autenticación se guardan en `auth-service/logs/`

## 🚨 Consideraciones de Seguridad

1. **Nunca** almacenes tokens en cookies sin configuración segura
2. **Siempre** valida tokens en el backend
3. **Implementa** logout en el servidor para invalidar tokens
4. **Usa HTTPS** en producción
5. **Configura CORS** correctamente
6. **Implementa rate limiting** para endpoints de login
7. **Valida** todas las entradas del usuario

## 🔄 Flujo de Autenticación

1. Usuario envía credenciales al endpoint `/login`
2. Backend valida credenciales y genera tokens JWT
3. Frontend almacena tokens en localStorage
4. Para cada petición, se envía el Access Token en el header Authorization
5. Si el token expira, se usa el Refresh Token para obtener uno nuevo
6. Si el Refresh Token también expira, se redirige al login

---

**¡Listo!** Con esta implementación tendrás un sistema de autenticación completo y seguro para tu aplicación React.