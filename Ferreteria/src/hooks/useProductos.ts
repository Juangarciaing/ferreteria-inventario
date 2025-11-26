/**
 * Hook para gestión de productos
 */
import { useState, useEffect } from 'react';
import { Producto } from '../types';
import toast from 'react-hot-toast';
import { apiClient } from '../lib/api';

// Sin datos simulados: usamos API real

export const useProductos = () => {
  const [productos, setProductos] = useState<Producto[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Cargar productos desde API (requiere login)
  const loadProductos = async (silent = false) => {
    try {
      if (!silent) {
        setLoading(true);
      }
      setError(null);
      const data = await apiClient.getProductos();
      setProductos(data as Producto[]);
      console.log('✅ Productos cargados (API):', Array.isArray(data) ? data.length : 0);
      return data as Producto[]; // Devolver los productos cargados
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error desconocido';
      setError(message);
      toast.error(message);
      return []; // Devolver array vacío en caso de error
    } finally {
      if (!silent) {
        setLoading(false);
      }
    }
  };

  // Crear producto (requiere rol admin)
  const createProducto = async (producto: Omit<Producto, 'id' | 'created_at' | 'updated_at'>) => {
    try {
      const created = await apiClient.createProducto(producto);
      await loadProductos();
      toast.success('Producto creado exitosamente');
      return created as Producto;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al crear producto';
      toast.error(message);
      throw err;
    }
  };

  // Actualizar producto
  const updateProducto = async (id: number, updates: Partial<Producto>) => {
    try {
      console.log('🔍 useProductos - Producto ID:', id);
      console.log('🔍 useProductos - Datos recibidos:', updates);
      console.log('🔍 useProductos - Productos en estado:', productos.length);
      
      // CRÍTICO: Asegurar que enviamos TODOS los campos obligatorios
      // Si falta algún campo obligatorio, obtenerlo del producto actual
      const productoActual = productos.find(p => p.id === id);
      
      if (!productoActual) {
        console.error('❌ useProductos - Producto no encontrado en estado local');
        console.log('📋 IDs disponibles:', productos.map(p => p.id));
        throw new Error('Producto no encontrado en el estado local');
      }

      console.log('📦 useProductos - Producto actual:', productoActual);

      // Construir objeto con TODOS los campos obligatorios
      const datosCompletos = {
        nombre: updates.nombre ?? productoActual.nombre,
        categoria_id: updates.categoria_id ?? productoActual.categoria_id,
        precio: updates.precio ?? productoActual.precio,
        stock: updates.stock ?? productoActual.stock,
        stock_minimo: updates.stock_minimo ?? productoActual.stock_minimo,
        descripcion: updates.descripcion ?? productoActual.descripcion,
        proveedor_id: updates.proveedor_id ?? productoActual.proveedor_id,
        codigo_barras: updates.codigo_barras ?? productoActual.codigo_barras,
      };

      console.log('✅ useProductos - Datos completos a enviar:', datosCompletos);
      
      const resultado = await apiClient.updateProducto(id, datosCompletos);
      console.log('🎯 useProductos - Respuesta del servidor:', resultado);
      
      // Actualizar el estado local inmediatamente con la respuesta del servidor
      const productoActualizado = resultado.data || resultado;
      
      setProductos(prev => prev.map(p => 
        p.id === id ? { ...p, ...productoActualizado } : p
      ));
      
      console.log('✅ useProductos - Producto actualizado en estado local');
      
      toast.success('Producto actualizado exitosamente');
      return productoActualizado as Producto;
    } catch (err) {
      console.error('❌ useProductos - Error completo:', err);
      const message = err instanceof Error ? err.message : 'Error al actualizar producto';
      toast.error(message);
      throw err;
    }
  };

  // Eliminar producto
  const deleteProducto = async (id: number) => {
    try {
      await apiClient.deleteProducto(id);
      setProductos(prev => prev.filter(p => p.id !== id));
      toast.success('Producto eliminado exitosamente');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al eliminar producto';
      toast.error(message);
      throw err;
    }
  };

  // Buscar productos
  const searchProductos = async (searchTerm: string) => {
    try {
      if (!searchTerm.trim()) {
        await loadProductos();
        return productos;
      }
      const data = await apiClient.searchProductos(searchTerm);
      setProductos(data as Producto[]);
      return data as Producto[];
    } catch (err) {
      console.error('Error al buscar productos:', err);
      toast.error('Error al buscar productos');
      return productos;
    }
  };

  // Cargar al montar el componente
  useEffect(() => {
    loadProductos();
  }, []);

  return {
    productos,
    loading,
    error,
    loadProductos,
    createProducto,
    updateProducto,
    deleteProducto,
    searchProductos
  };
};