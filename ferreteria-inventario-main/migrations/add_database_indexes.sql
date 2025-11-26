-- ================================================
-- ÍNDICES PARA OPTIMIZACIÓN DE RENDIMIENTO
-- ================================================
-- Ejecutar después de crear las tablas principales
-- Estos índices mejoran significativamente las consultas

USE ferreteria_db;

-- Índices para tabla PRODUCTOS
-- Mejora búsquedas por nombre (filtros y búsqueda)
CREATE INDEX IF NOT EXISTS idx_producto_nombre ON productos(nombre);

-- Mejora filtrado por categoría (muy usado en la UI)
CREATE INDEX IF NOT EXISTS idx_producto_categoria ON productos(categoria_id);

-- Mejora búsquedas por código de barras
CREATE INDEX IF NOT EXISTS idx_producto_codigo_barras ON productos(codigo_barras);

-- Mejora filtrado de productos activos
CREATE INDEX IF NOT EXISTS idx_producto_activo ON productos(activo);

-- Índice compuesto para alertas de stock bajo
CREATE INDEX IF NOT EXISTS idx_producto_stock_alert ON productos(stock, stock_minimo, activo);

-- Índices para tabla VENTAS
-- Mejora ordenamiento y filtrado por fecha (reportes)
CREATE INDEX IF NOT EXISTS idx_venta_fecha ON ventas(fecha DESC);

-- Mejora búsqueda por usuario (historial de vendedor)
CREATE INDEX IF NOT EXISTS idx_venta_usuario ON ventas(usuario_id);

-- Mejora filtrado de ventas anuladas
CREATE INDEX IF NOT EXISTS idx_venta_anulada ON ventas(anulada);

-- Índice compuesto para reportes de ventas por período
CREATE INDEX IF NOT EXISTS idx_venta_fecha_usuario ON ventas(fecha DESC, usuario_id);

-- Índices para tabla COMPRAS
-- Mejora ordenamiento por fecha
CREATE INDEX IF NOT EXISTS idx_compra_fecha ON compras(fecha DESC);

-- Mejora filtrado por proveedor
CREATE INDEX IF NOT EXISTS idx_compra_proveedor ON compras(proveedor_id);

-- Índices para tabla USUARIOS
-- Mejora autenticación (login)
CREATE INDEX IF NOT EXISTS idx_usuario_email ON usuarios(email);

-- Mejora filtrado por rol
CREATE INDEX IF NOT EXISTS idx_usuario_rol ON usuarios(rol);

-- Mejora filtrado de usuarios activos
CREATE INDEX IF NOT EXISTS idx_usuario_activo ON usuarios(activo);

-- Índices para tabla PROVEEDORES
-- Mejora búsqueda por nombre
CREATE INDEX IF NOT EXISTS idx_proveedor_nombre ON proveedores(nombre);

-- Mejora filtrado de proveedores activos
CREATE INDEX IF NOT EXISTS idx_proveedor_activo ON proveedores(activo);

-- Índices para tabla CATEGORIAS
-- Mejora búsqueda por nombre
CREATE INDEX IF NOT EXISTS idx_categoria_nombre ON categorias(nombre);

-- Mejora filtrado de categorías activas
CREATE INDEX IF NOT EXISTS idx_categoria_activo ON categorias(activo);

-- Índices para tabla DETALLE_VENTA
-- Mejora consultas de detalles por venta
CREATE INDEX IF NOT EXISTS idx_detalle_venta_venta_id ON detalle_venta(venta_id);

-- Mejora análisis de productos vendidos
CREATE INDEX IF NOT EXISTS idx_detalle_venta_producto ON detalle_venta(producto_id);

-- Índice compuesto para reportes de ventas por producto
CREATE INDEX IF NOT EXISTS idx_detalle_venta_producto_cantidad ON detalle_venta(producto_id, cantidad);

-- Índices para tabla DETALLE_COMPRA
-- Mejora consultas de detalles por compra
CREATE INDEX IF NOT EXISTS idx_detalle_compra_compra_id ON detalle_compra(compra_id);

-- Mejora análisis de productos comprados
CREATE INDEX IF NOT EXISTS idx_detalle_compra_producto ON detalle_compra(producto_id);

-- Índices para tabla AUDITORIA (si existe)
CREATE INDEX IF NOT EXISTS idx_auditoria_fecha ON auditoria(fecha DESC);
CREATE INDEX IF NOT EXISTS idx_auditoria_usuario ON auditoria(usuario_id);
CREATE INDEX IF NOT EXISTS idx_auditoria_tabla ON auditoria(tabla_afectada);
CREATE INDEX IF NOT EXISTS idx_auditoria_accion ON auditoria(accion);

-- ================================================
-- VERIFICAR ÍNDICES CREADOS
-- ================================================
SELECT 
    TABLE_NAME,
    INDEX_NAME,
    COLUMN_NAME,
    SEQ_IN_INDEX,
    INDEX_TYPE
FROM 
    information_schema.STATISTICS 
WHERE 
    TABLE_SCHEMA = 'ferreteria_db'
    AND INDEX_NAME LIKE 'idx_%'
ORDER BY 
    TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX;

-- ================================================
-- ANÁLISIS DE RENDIMIENTO
-- ================================================
-- Ejecutar EXPLAIN antes y después de crear índices para comparar

-- Ejemplo de consulta optimizada con índices:
-- EXPLAIN SELECT * FROM productos WHERE nombre LIKE '%martillo%' AND activo = 1;
-- EXPLAIN SELECT * FROM ventas WHERE fecha >= '2025-01-01' ORDER BY fecha DESC;
-- EXPLAIN SELECT * FROM usuarios WHERE email = 'admin@ferreteria.com';
