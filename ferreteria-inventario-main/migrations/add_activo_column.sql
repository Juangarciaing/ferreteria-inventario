-- Agregar columna activo a la tabla usuarios
ALTER TABLE usuarios 
ADD COLUMN activo TINYINT(1) NOT NULL DEFAULT 1
AFTER direccion;
