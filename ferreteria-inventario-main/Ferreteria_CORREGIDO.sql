-- MySQL dump corregido para sistema de inventario ferretería
-- Estructura actualizada para coincidir con modelos Python

-- Usar la base de datos
USE ferreteria_db;# Ejecuta backend y frontend en ventanas separadas (incluye pre-chequeo de MySQL)
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\Juanc\Videos\Modelo y simulacion\S2\run_all.ps1"

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

-- Crear base de datos si no existe
CREATE DATABASE IF NOT EXISTS `ferreteria_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `ferreteria_db`;

--
-- Tabla: usuarios (debe ir primero por las FK)
--
DROP TABLE IF EXISTS `usuarios`;
CREATE TABLE `usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `email` varchar(120) NOT NULL,
  `password` varchar(256) NOT NULL,
  `rol` enum('admin','vendedor') NOT NULL DEFAULT 'vendedor',
  `telefono` varchar(20) DEFAULT NULL,
  `direccion` varchar(200) DEFAULT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT '1',
  `fecha_creacion` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email_unique` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Tabla: categorias
--
DROP TABLE IF EXISTS `categorias`;
CREATE TABLE `categorias` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text,
  `fecha_creacion` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre_unique` (`nombre`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Tabla: proveedores
--
DROP TABLE IF EXISTS `proveedores`;
CREATE TABLE `proveedores` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(150) NOT NULL,
  `contacto` varchar(100) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `email` varchar(120) DEFAULT NULL,
  `direccion` varchar(200) DEFAULT NULL,
  `condiciones_pago` varchar(100) DEFAULT NULL,
  `rating` decimal(2,1) DEFAULT '0.0',
  `activo` tinyint(1) NOT NULL DEFAULT '1',
  `fecha_creacion` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Tabla: productos
--
DROP TABLE IF EXISTS `productos`;
CREATE TABLE `productos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(150) NOT NULL,
  `descripcion` text,
  `precio` decimal(10,2) NOT NULL,
  `stock` int NOT NULL DEFAULT '0',
  `stock_minimo` int NOT NULL DEFAULT '5',
  `categoria_id` int DEFAULT NULL,
  `proveedor_id` int DEFAULT NULL,
  `codigo_barras` varchar(50) DEFAULT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT '1',
  `fecha_creacion` datetime DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_categoria` (`categoria_id`),
  KEY `idx_proveedor` (`proveedor_id`),
  KEY `idx_codigo_barras` (`codigo_barras`),
  CONSTRAINT `fk_productos_categoria` FOREIGN KEY (`categoria_id`) REFERENCES `categorias` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_productos_proveedor` FOREIGN KEY (`proveedor_id`) REFERENCES `proveedores` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Tabla: compras
--
DROP TABLE IF EXISTS `compras`;
CREATE TABLE `compras` (
  `id` int NOT NULL AUTO_INCREMENT,
  `fecha` datetime DEFAULT CURRENT_TIMESTAMP,
  `proveedor_id` int NOT NULL,
  `producto_id` int NOT NULL,
  `cantidad` int NOT NULL,
  `precio_unitario` decimal(10,2) NOT NULL,
  `total` decimal(10,2) NOT NULL,
  `usuario_id` int NOT NULL,
  `observaciones` text,
  PRIMARY KEY (`id`),
  KEY `idx_proveedor` (`proveedor_id`),
  KEY `idx_producto` (`producto_id`),
  KEY `idx_usuario` (`usuario_id`),
  KEY `idx_fecha` (`fecha`),
  CONSTRAINT `fk_compras_proveedor` FOREIGN KEY (`proveedor_id`) REFERENCES `proveedores` (`id`),
  CONSTRAINT `fk_compras_producto` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id`),
  CONSTRAINT `fk_compras_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Tabla: ventas
--
DROP TABLE IF EXISTS `ventas`;
CREATE TABLE `ventas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `fecha` datetime DEFAULT CURRENT_TIMESTAMP,
  `total` decimal(10,2) NOT NULL,
  `usuario_id` int NOT NULL,
  `cliente_nombre` varchar(100) DEFAULT NULL,
  `cliente_telefono` varchar(20) DEFAULT NULL,
  `observaciones` text,
  PRIMARY KEY (`id`),
  KEY `idx_usuario` (`usuario_id`),
  KEY `idx_fecha` (`fecha`),
  CONSTRAINT `fk_ventas_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Tabla: detalle_venta
--
DROP TABLE IF EXISTS `detalle_venta`;
CREATE TABLE `detalle_venta` (
  `id` int NOT NULL AUTO_INCREMENT,
  `venta_id` int NOT NULL,
  `producto_id` int NOT NULL,
  `cantidad` int NOT NULL,
  `precio_unitario` decimal(10,2) NOT NULL,
  `subtotal` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_venta` (`venta_id`),
  KEY `idx_producto` (`producto_id`),
  CONSTRAINT `fk_detalle_venta_venta` FOREIGN KEY (`venta_id`) REFERENCES `ventas` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_detalle_venta_producto` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id`),
  CONSTRAINT `chk_cantidad_positiva` CHECK ((`cantidad` > 0)),
  CONSTRAINT `chk_precio_positivo` CHECK ((`precio_unitario` > 0)),
  CONSTRAINT `chk_subtotal_positivo` CHECK ((`subtotal` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Datos iniciales: usuarios
--
INSERT INTO `usuarios` (`nombre`, `email`, `password`, `rol`, `telefono`, `direccion`) VALUES
('Administrador', 'admin@ferreteria.com', 'scrypt:32768:8:1$8fZR3QXiV$8d3f9c2e5a1b6c4d8e7f9a2b3c4e5f6d7a8b9c0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e', 'admin', '555-0001', 'Oficina Principal'),
('Juan Pérez', 'vendedor@ferreteria.com', 'scrypt:32768:8:1$7eYQ2PWhU$7c2e8d1f4a5b6c3d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f', 'vendedor', '555-0002', 'Sucursal Norte'),
('María González', 'maria@ferreteria.com', 'scrypt:32768:8:1$6dXP1OVgT$6b1d7c0e3f4a5b2c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e', 'vendedor', '555-0003', 'Sucursal Sur');

--
-- Datos iniciales: categorias
--
INSERT INTO `categorias` (`nombre`, `descripcion`) VALUES
('Herramientas Manuales', 'Martillos, destornilladores, llaves, alicates'),
('Herramientas Eléctricas', 'Taladros, amoladoras, sierras eléctricas'),
('Tornillería y Fijación', 'Tornillos, tuercas, arandelas, clavos'),
('Electricidad', 'Cables, interruptores, enchufes, bombillas'),
('Fontanería', 'Tuberías, grifos, conexiones, válvulas'),
('Pintura y Acabados', 'Pinturas, brochas, rodillos, barnices'),
('Adhesivos y Selladores', 'Silicona, pegamentos, cintas'),
('Ferretería General', 'Candados, bisagras, cerraduras'),
('Seguridad Industrial', 'Cascos, guantes, mascarillas'),
('Material de Construcción', 'Cemento, ladrillos, bloques'),
('Jardinería', 'Herramientas de jardín, semillas, macetas'),
('Iluminación', 'Bombillas LED, lámparas, reflectores');

--
-- Datos iniciales: proveedores
--
INSERT INTO `proveedores` (`nombre`, `contacto`, `telefono`, `email`, `direccion`, `condiciones_pago`, `rating`) VALUES
('Distribuidora Central', 'Carlos Ramírez', '555-1001', 'ventas@distcentral.com', 'Av. Principal 123, Industrial', '30 días', 4.5),
('Herramientas del Norte', 'Ana López', '555-1002', 'pedidos@herranorte.com', 'Zona Industrial Norte', '15 días', 4.8),
('Suministros Técnicos', 'Miguel Torres', '555-1003', 'info@sumtecnicos.com', 'Calle Comercio 456', '45 días', 4.2),
('Eléctricos Modernos', 'Laura Jiménez', '555-1004', 'contacto@elecmodernos.com', 'Centro Comercial', '30 días', 4.7),
('Pinturas y Más', 'Roberto Silva', '555-1005', 'ventas@pinturasymas.com', 'Av. Colores 789', '20 días', 4.4);

--
-- Datos iniciales: productos
--
INSERT INTO `productos` (`nombre`, `descripcion`, `precio`, `stock`, `stock_minimo`, `categoria_id`, `proveedor_id`) VALUES
('Martillo de Acero 16 oz', 'Martillo de acero con mango de madera', 12.50, 25, 5, 1, 1),
('Destornillador Phillips #2', 'Destornillador con punta Phillips número 2', 3.75, 50, 10, 1, 1),
('Taladro Percutor 1/2"', 'Taladro percutor de 1/2 pulgada, 600W', 85.00, 8, 2, 2, 2),
('Amoladora Angular 4.5"', 'Amoladora angular 4.5 pulgadas, 850W', 65.00, 12, 3, 2, 2),
('Tornillo Acero 1/4" x 1"', 'Tornillo de acero galvanizado', 0.15, 500, 100, 3, 3),
('Cable THHN 12 AWG', 'Cable eléctrico THHN calibre 12', 1.25, 200, 50, 4, 4),
('Interruptor Sencillo', 'Interruptor sencillo 15A, 120V', 2.80, 30, 10, 4, 4),
('Tubo PVC 1/2" x 3m', 'Tubo PVC presión 1/2 pulgada', 4.50, 40, 15, 5, 1),
('Llave de Paso 1/2"', 'Llave de paso de bronce 1/2 pulgada', 8.75, 20, 5, 5, 1),
('Pintura Látex Blanca 1 Gal', 'Pintura látex interior blanca 1 galón', 18.50, 15, 5, 6, 5),
('Brocha 2 pulgadas', 'Brocha para pintura de 2 pulgadas', 5.25, 25, 8, 6, 5),
('Silicona Transparente', 'Silicona selladora transparente 300ml', 3.80, 35, 10, 7, 3),
('Candado de Latón 40mm', 'Candado de latón macizo 40mm', 12.00, 18, 5, 8, 1),
('Casco de Seguridad Blanco', 'Casco de seguridad industrial blanco', 15.50, 10, 3, 9, 2),
('Guantes de Trabajo', 'Guantes de trabajo de cuero', 8.25, 30, 10, 9, 2),
('Bombilla LED 9W', 'Bombilla LED 9W luz blanca', 4.50, 60, 20, 12, 4),
('Reflector LED 50W', 'Reflector LED 50W uso exterior', 35.00, 8, 3, 12, 4),
('Tijera de Podar 8"', 'Tijera de podar acero inoxidable 8 pulgadas', 22.50, 15, 5, 11, 2),
('Maceta Plástico 6"', 'Maceta de plástico 6 pulgadas', 2.25, 50, 15, 11, 1),
('Cemento Gris 50kg', 'Cemento Portland gris saco 50kg', 8.75, 100, 25, 10, 3);

--
-- Datos iniciales: algunas ventas de ejemplo
--
INSERT INTO `ventas` (`fecha`, `total`, `usuario_id`, `cliente_nombre`) VALUES
('2024-01-15 10:30:00', 28.25, 2, 'Roberto Martínez'),
('2024-01-15 14:15:00', 95.50, 3, 'Carmen López'),
('2024-01-16 09:45:00', 156.75, 2, 'José Hernández');

INSERT INTO `detalle_venta` (`venta_id`, `producto_id`, `cantidad`, `precio_unitario`, `subtotal`) VALUES
(1, 1, 2, 12.50, 25.00),
(1, 5, 20, 0.15, 3.00),
(2, 3, 1, 85.00, 85.00),
(2, 16, 2, 4.50, 9.00),
(2, 12, 1, 3.80, 3.80),
(3, 2, 5, 3.75, 18.75),
(3, 6, 10, 1.25, 12.50),
(3, 20, 15, 8.75, 131.25);

--
-- Datos iniciales: algunas compras de ejemplo
--
INSERT INTO `compras` (`fecha`, `proveedor_id`, `producto_id`, `cantidad`, `precio_unitario`, `total`, `usuario_id`, `observaciones`) VALUES
('2024-01-10 08:00:00', 1, 1, 50, 8.00, 400.00, 1, 'Restock mensual'),
('2024-01-10 08:00:00', 2, 3, 10, 60.00, 600.00, 1, 'Pedido especial'),
('2024-01-12 14:30:00', 4, 16, 100, 3.20, 320.00, 1, 'Stock bajo');

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;