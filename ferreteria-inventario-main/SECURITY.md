# 🔐 Guía de Seguridad - Configuración de Secretos

## ⚠️ IMPORTANTE: Antes de Ejecutar el Proyecto

Este proyecto **requiere** variables de entorno para funcionar de manera segura. **NO** uses valores por defecto en producción.

---

## 🚀 Configuración Rápida (Desarrollo Local)

### 1. Generar Claves Seguras

Ejecuta el script generador:

```bash
cd ferreteria-inventario-main
python generate_secrets.py
```

**Salida esperada:**
```
============================================================
🔐 GENERADOR DE CLAVES SEGURAS
============================================================

⚠️  IMPORTANTE: Copiar estos valores en tu archivo .env

SECRET_KEY=a1b2c3d4e5f6...
JWT_SECRET_KEY=x7y8z9...
ADMIN_PASSWORD=Xy9kL-mNpQ2rSt
VENDEDOR_PASSWORD=Ab3cD-eFgH4iJ
```

### 2. Crear Archivo .env

Copia `.env.example` a `.env`:

```bash
cp .env.example .env
```

### 3. Configurar Variables

Edita `.env` y pega las claves generadas:

```env
# 🔐 SEGURIDAD
SECRET_KEY=<pegar_clave_generada>
JWT_SECRET_KEY=<pegar_clave_generada>
ADMIN_PASSWORD=<pegar_password_generado>
VENDEDOR_PASSWORD=<pegar_password_generado>

# Base de datos
DATABASE_URL=mysql+pymysql://root:root@localhost/ferreteria_db
```

---

## 🔒 Generación Manual de Claves

Si prefieres generar claves manualmente:

```bash
# SECRET_KEY (64 caracteres)
python -c "import secrets; print(secrets.token_hex(32))"

# JWT_SECRET_KEY (64 caracteres)
python -c "import secrets; print(secrets.token_hex(32))"

# Passwords (24 caracteres URL-safe)
python -c "import secrets; print(secrets.token_urlsafe(16))"
```

---

## 🏭 Configuración para Producción

### 1. Variables de Entorno del Sistema

**Linux/Mac:**
```bash
export SECRET_KEY="tu_clave_super_secreta"
export JWT_SECRET_KEY="tu_jwt_clave_secreta"
export ADMIN_PASSWORD="password_admin_seguro"
export DATABASE_URL="mysql+pymysql://user:pass@host/db"
```

**Windows (PowerShell):**
```powershell
$env:SECRET_KEY="tu_clave_super_secreta"
$env:JWT_SECRET_KEY="tu_jwt_clave_secreta"
$env:ADMIN_PASSWORD="password_admin_seguro"
```

### 2. Docker

En `docker-compose.yml`:

```yaml
environment:
  - SECRET_KEY=${SECRET_KEY}
  - JWT_SECRET_KEY=${JWT_SECRET_KEY}
  - ADMIN_PASSWORD=${ADMIN_PASSWORD}
```

### 3. Servicios Cloud

**Heroku:**
```bash
heroku config:set SECRET_KEY="tu_clave"
heroku config:set JWT_SECRET_KEY="tu_jwt_clave"
```

**AWS Elastic Beanstalk:**
```bash
eb setenv SECRET_KEY="tu_clave" JWT_SECRET_KEY="tu_jwt_clave"
```

**Google Cloud:**
```bash
gcloud run services update SERVICE --set-env-vars SECRET_KEY="tu_clave"
```

---

## 🛡️ Mejores Prácticas de Seguridad

### ✅ Hacer

- ✅ Usar `generate_secrets.py` para generar claves aleatorias
- ✅ Mantener `.env` en `.gitignore` (ya configurado)
- ✅ Usar diferentes claves para dev/staging/production
- ✅ Rotar claves cada 90 días en producción
- ✅ Usar gestores de secretos (AWS Secrets Manager, Vault, etc.)
- ✅ Cambiar contraseñas de admin después del primer login
- ✅ Usar HTTPS en producción
- ✅ Configurar Redis para producción (caché + rate limiting)

### ❌ Nunca Hacer

- ❌ **NUNCA** hardcodear secretos en el código
- ❌ **NUNCA** subir `.env` al repositorio
- ❌ **NUNCA** usar contraseñas simples (admin123, password, etc.)
- ❌ **NUNCA** compartir claves por email/chat
- ❌ **NUNCA** usar las mismas claves en múltiples ambientes
- ❌ **NUNCA** commitear secretos accidentalmente
- ❌ **NUNCA** exponer SECRET_KEY en logs

---

## 🔍 Verificar Configuración

Ejecuta este comando para verificar que todo esté configurado:

```bash
python -c "
import os
print('✅ SECRET_KEY configurada' if os.getenv('SECRET_KEY') else '❌ Falta SECRET_KEY')
print('✅ JWT_SECRET_KEY configurada' if os.getenv('JWT_SECRET_KEY') else '❌ Falta JWT_SECRET_KEY')
print('✅ ADMIN_PASSWORD configurada' if os.getenv('ADMIN_PASSWORD') else '⚠️  Se generará temporalmente')
"
```

---

## 🚨 Qué Hacer si un Secreto se Compromete

### 1. Revocar Inmediatamente

```bash
# Generar nuevas claves
python generate_secrets.py

# Actualizar .env con nuevas claves
# Reiniciar la aplicación
```

### 2. Revisar Logs

- Buscar accesos no autorizados
- Identificar posibles usos maliciosos
- Verificar intentos de login fallidos

### 3. Notificar

- Informar al equipo de seguridad
- Cambiar contraseñas de todos los usuarios
- Revisar auditorías de la base de datos

### 4. Prevenir Futuro

- Implementar rotación automática de secretos
- Usar un vault (HashiCorp Vault, AWS Secrets Manager)
- Configurar alertas de seguridad

---

## 📚 Recursos Adicionales

- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/latest/security/)
- [Python Secrets Module](https://docs.python.org/3/library/secrets.html)

---

## ✅ Checklist de Seguridad

Antes de desplegar a producción:

- [ ] SECRET_KEY configurada desde variable de entorno
- [ ] JWT_SECRET_KEY diferente a SECRET_KEY
- [ ] ADMIN_PASSWORD cambiada del valor por defecto
- [ ] DATABASE_URL no contiene credenciales hardcodeadas
- [ ] `.env` está en `.gitignore`
- [ ] HTTPS habilitado
- [ ] Redis configurado para producción
- [ ] Backups configurados
- [ ] Monitoreo de seguridad activo
- [ ] Rate limiting configurado
- [ ] CORS configurado correctamente

---

**🔐 La seguridad es responsabilidad de todos. Si encuentras alguna vulnerabilidad, repórtala inmediatamente.**
