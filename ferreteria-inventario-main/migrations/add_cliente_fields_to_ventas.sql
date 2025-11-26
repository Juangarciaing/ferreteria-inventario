-- Agregar campos de cliente a la tabla ventas
-- Fecha: 2025-11-10
-- Descripción: Permite almacenar información opcional del cliente en cada venta

USE ferreteria_db;

-- Verificar si las columnas ya existen antes de agregarlas
ALTER TABLE ventas 
ADD COLUMN IF NOT EXISTS cliente_nombre VARCHAR(200) NULL AFTER usuario_id,
ADD COLUMN IF NOT EXISTS cliente_documento VARCHAR(50) NULL AFTER cliente_nombre,
ADD COLUMN IF NOT EXISTS cliente_telefono VARCHAR(20) NULL AFTER cliente_documento;

-- Verificar que las columnas se agregaron correctamente
DESCRIBE ventas;

SELECT 'Migración completada exitosamente' AS resultado;
