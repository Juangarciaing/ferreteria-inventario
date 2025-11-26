export interface User {
  id: string;
  email: string;
  nombre: string;
  rol: 'admin' | 'vendedor' | 'usuario';
  estado?: boolean; // Campo activo/inactivo
  created_at?: string;
  updated_at?: string;
}

export interface Categoria {
  id: number;
  nombre: string;
  descripcion?: string;
  created_at?: string;
}

export interface Producto {
  id: number;
  nombre: string;
  categoria_id: number;
  categoria?: Categoria;
  precio: number;
  stock: number;
  stock_minimo: number;
  descripcion?: string;
  proveedor_id?: number;
  codigo_barras?: string;
  created_at?: string;
  updated_at?: string;
}

export interface Venta {
  id: number;
  usuario_id: string;
  usuario?: User;
  total: number;
  fecha?: string;
  cliente_nombre?: string;
  cliente_documento?: string;
  cliente_telefono?: string;
  detalles?: DetalleVenta[];
  created_at?: string;
}

export interface DetalleVenta {
  id: number;
  venta_id: number;
  producto_id: number;
  producto?: Producto;
  cantidad: number;
  precio_unitario: number;
  subtotal: number;
}

export interface Compra {
  id?: number;
  producto_id?: number;
  producto?: Producto;
  proveedor_id?: number;
  proveedor?: Proveedor;
  cantidad: number;
  precio_unitario: number;
  total: number;
  usuario_id?: number;
  usuario?: User;
  fecha?: string;
  fecha_compra?: string;
  created_at?: string;
}

export interface Proveedor {
  id_proveedor: number;
  id?: number; // Alias para compatibilidad con backend
  nombre: string;
  contacto?: string;
  telefono?: string;
  email?: string;
  direccion?: string;
  rut_ruc?: string;
  condiciones_pago?: 'contado' | 'credito_30' | 'credito_60';
  descuento_default?: number;
  estado?: 'activo' | 'inactivo';
  rating?: number;
  notas?: string;
  created_at?: string;
  updated_at?: string;
}

export interface DashboardStats {
  total_productos: number;
  productos_stock_bajo: number;
  ventas_mes: number;
  ingresos_mes: number;
}

export interface ReporteVentas {
  fecha: string;
  total: number;
  cantidad_ventas: number;
}

export interface ProductoMasVendido {
  producto_id: number;
  nombre: string;
  total_vendido: number;
  ingresos_totales: number;
}