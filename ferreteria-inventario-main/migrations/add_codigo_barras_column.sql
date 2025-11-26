-- Agregar columna codigo_barras a la tabla productos
-- Fecha: 2024
-- Descripción: Permite almacenar códigos de barras EAN-13 para los productos

ALTER TABLE productos 
ADD COLUMN codigo_barras VARCHAR(13) NULL
COMMENT 'Código de barras EAN-13 del producto'
AFTER descripcion;

-- Crear índice único para codigo_barras (permitiendo NULL)
ALTER TABLE productos 
ADD UNIQUE INDEX idx_codigo_barras (codigo_barras);

-- Comentario explicativo
-- Este campo es opcional y permite:
-- 1. Almacenar códigos EAN-13 de 13 dígitos
-- 2. Búsqueda rápida por código de barras
-- 3. Integración con sistemas de punto de venta
-- 4. Generación automática desde el frontend
