# 🧪 Tests del Sistema de Ferretería

## Ejecución de Tests

### Instalación de dependencias
```bash
pip install -r requirements.txt
```

### Ejecutar todos los tests
```bash
pytest tests/
```

### Ejecutar tests específicos
```bash
pytest tests/test_api.py
pytest tests/test_auth.py
```

### Con cobertura
```bash
pytest --cov=app tests/
```

## 🔐 Seguridad en Tests

### Contraseñas de Prueba

Los tests utilizan variables de entorno para las credenciales de prueba. Por defecto:
- Si NO configuras variables de entorno, los tests generan contraseñas aleatorias seguras automáticamente
- Si SÍ configuras variables de entorno (para CI/CD), usa secretos seguros

### Variables de Entorno (Opcional)

```bash
export TEST_ADMIN_EMAIL="admin@test.com"
export TEST_ADMIN_PASSWORD="tu_password_segura_aqui"
export TEST_USER_EMAIL="test@test.com"
export TEST_USER_PASSWORD="tu_password_segura_aqui"
```

### ⚠️ IMPORTANTE

1. **NO uses contraseñas reales** en los tests
2. **NO commitees archivos .env** con credenciales de test
3. **En CI/CD**, usa GitHub Secrets o similar para las variables de test
4. Las contraseñas de test **NO deben** ser las mismas que producción

### Configuración en GitHub Actions

```yaml
- name: Run tests
  env:
    TEST_ADMIN_PASSWORD: ${{ secrets.TEST_ADMIN_PASSWORD }}
    TEST_USER_PASSWORD: ${{ secrets.TEST_USER_PASSWORD }}
  run: pytest tests/
```

## 📊 Base de Datos de Testing

Los tests usan una base de datos temporal en memoria que:
- Se crea antes de cada test (`db.create_all()`)
- Se destruye después de cada test (`db.drop_all()`)
- NO afecta la base de datos de producción
- NO persiste datos entre ejecuciones

## 🏗️ Fixtures Disponibles

- **`app`**: Instancia de la aplicación configurada para testing
- **`client`**: Cliente HTTP para hacer requests a la API
- **`auth_headers`**: Headers con token JWT de admin para requests autenticados

## 📝 Ejemplo de Test

```python
def test_crear_producto(client, auth_headers):
    """Test de creación de producto con autenticación"""
    response = client.post('/api/productos', 
        headers=auth_headers,
        json={'nombre': 'Martillo', 'precio': 15.50}
    )
    assert response.status_code == 201
```
