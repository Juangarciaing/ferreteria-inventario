"""
Pruebas de Carga con Locust
Sistema de Inventario para Ferretería
"""

from locust import HttpUser, task, between, events
import random
import json

class InventarioUser(HttpUser):
    """Usuario simulado para pruebas de carga"""
    
    wait_time = between(1, 3)  # Espera entre 1-3 segundos entre tareas
    
    def on_start(self):
        """Se ejecuta al inicio de cada usuario simulado"""
        # Login
        response = self.client.post("/api/auth/login", json={
            "email": "admin@ferreteria.com",
            "password": "admin123"
        }, catch_response=True)
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("data", {}).get("token") or data.get("token")
            response.success()
        else:
            response.failure(f"Login failed: {response.status_code}")
            self.token = None
    
    def _get_headers(self):
        """Retorna headers con token de autenticación"""
        headers = {"Content-Type": "application/json"}
        if getattr(self, "token", None):
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    @task(5)
    def listar_productos(self):
        """Tarea más común: listar productos"""
        with self.client.get(
            "/api/productos",
            headers=self._get_headers(),
            catch_response=True,
            name="/api/productos [GET]"
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    # Aceptar tanto lista simple como objeto paginado o envuelto en data
                    productos = data.get("data", data) if isinstance(data, dict) else data
                    if not isinstance(productos, (list, dict)):
                        response.failure("Formato de respuesta inesperado en /api/productos")
                    else:
                        response.success()
                except Exception as e:
                    response.failure(f"Error parseando JSON en /api/productos: {e}")
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(3)
    def buscar_producto(self):
        """Buscar productos por término"""
        terminos = ["tornillo", "martillo", "cemento", "pintura", "cable"]
        termino = random.choice(terminos)
        
        with self.client.get(
            f"/api/productos/search?q={termino}",
            headers=self._get_headers(),
            catch_response=True,
            name="/api/productos/search [GET]"
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    resultados = data.get("data", data) if isinstance(data, dict) else data
                    if not isinstance(resultados, (list, dict)):
                        response.failure("Formato de respuesta inesperado en /api/productos/search")
                    else:
                        response.success()
                except Exception as e:
                    response.failure(f"Error parseando JSON en /api/productos/search: {e}")
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(2)
    def listar_categorias(self):
        """Listar categorías"""
        with self.client.get(
            "/api/categorias",
            headers=self._get_headers(),
            catch_response=True,
            name="/api/categorias [GET]"
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    categorias = data.get("data", data) if isinstance(data, dict) else data
                    if not isinstance(categorias, (list, dict)):
                        response.failure("Formato de respuesta inesperado en /api/categorias")
                    else:
                        response.success()
                except Exception as e:
                    response.failure(f"Error parseando JSON en /api/categorias: {e}")
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(2)
    def productos_stock_bajo(self):
        """Ver productos con stock bajo"""
        with self.client.get(
            "/api/productos/stock-bajo",
            headers=self._get_headers(),
            catch_response=True,
            name="/api/productos/stock-bajo [GET]"
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    productos = data.get("data", data) if isinstance(data, dict) else data
                    if not isinstance(productos, (list, dict)):
                        response.failure("Formato de respuesta inesperado en /api/productos/stock-bajo")
                    else:
                        response.success()
                except Exception as e:
                    response.failure(f"Error parseando JSON en /api/productos/stock-bajo: {e}")
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(1)
    def obtener_producto_detalle(self):
        """Obtener detalle de un producto específico"""
        # IDs de productos existentes (ajustar según tu DB)
        producto_id = random.randint(1, 20)
        
        with self.client.get(
            f"/api/productos/{producto_id}",
            headers=self._get_headers(),
            catch_response=True,
            name="/api/productos/{id} [GET]"
        ) as response:
            if response.status_code in [200, 404]:
                # 200: producto encontrado, 404: no existe el ID; ambos son válidos
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(1)
    def crear_venta(self):
        """Simular creación de venta (operación pesada)"""
        venta_data = {
            "detalles": [
                {
                    "producto_id": random.randint(1, 10),
                    "cantidad": random.randint(1, 5),
                    "precio_unitario": random.uniform(10, 100)
                }
            ],
            "cliente_nombre": f"Cliente Test {random.randint(1, 1000)}",
            "cliente_rfc": f"RFC{random.randint(10000, 99999)}"
        }
        
        with self.client.post(
            "/api/ventas",
            json=venta_data,
            headers=self._get_headers(),
            catch_response=True,
            name="/api/ventas [POST]"
        ) as response:
            if response.status_code in [200, 201]:
                try:
                    _ = response.json()
                    response.success()
                except Exception as e:
                    response.failure(f"Error parseando JSON en /api/ventas: {e}")
            elif response.status_code == 400:
                # Stock insuficiente u otras validaciones de negocio son aceptables en pruebas
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(1)
    def dashboard_stats(self):
        """Obtener estadísticas del dashboard"""
        with self.client.get(
            "/api/dashboard/stats",
            headers=self._get_headers(),
            catch_response=True,
            name="/api/dashboard/stats [GET]"
        ) as response:
            if response.status_code == 200:
                try:
                    _ = response.json()
                    response.success()
                except Exception as e:
                    response.failure(f"Error parseando JSON en /api/dashboard/stats: {e}")
            else:
                response.failure(f"Status: {response.status_code}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Se ejecuta al inicio de las pruebas"""
    print("🚀 Iniciando pruebas de carga...")
    print(f"   Host: {environment.host}")
    print(f"   Usuarios: {environment.runner.user_count if hasattr(environment.runner, 'user_count') else 'N/A'}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Se ejecuta al finalizar las pruebas"""
    print("\n✅ Pruebas de carga completadas")
    stats = environment.stats
    print(f"   Total requests: {stats.total.num_requests}")
    print(f"   Failures: {stats.total.num_failures}")
    print(f"   Average response time: {stats.total.avg_response_time:.2f}ms")
    print(f"   RPS: {stats.total.total_rps:.2f}")
