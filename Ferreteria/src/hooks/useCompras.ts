/**
 * Hook para gestión de compras
 */
import { useState, useEffect } from 'react';
import { Compra } from '../types';
import { apiClient } from '../lib/api';
import toast from 'react-hot-toast';

export const useCompras = () => {
  const [compras, setCompras] = useState<Compra[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Cargar compras
  const loadCompras = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.getCompras();
      
      console.log('📦 Compras recibidas del backend:', data);
      
      // Asegurar que los campos estén correctamente mapeados
      const transformedData = data.map((c: Compra) => {
        const compra = {
          ...c,
          producto_id: c.producto_id || c.producto?.id,
          proveedor_id: c.proveedor_id || c.proveedor?.id,
          usuario_id: c.usuario_id || c.usuario?.id
        };
        
        console.log('🔄 Compra transformada:', {
          id: compra.id,
          producto_id: compra.producto_id,
          proveedor_id: compra.proveedor_id,
          usuario_id: compra.usuario_id
        });
        
        return compra;
      });
      
      setCompras(transformedData);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error desconocido';
      setError(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  // Crear compra
  const createCompra = async (compra: Omit<Compra, 'id' | 'created_at'>) => {
    try {
      const newCompra = await apiClient.createCompra(compra);
      setCompras(prev => [...prev, newCompra]);
      toast.success('Compra registrada exitosamente, stock actualizado');
      return newCompra;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al registrar compra';
      toast.error(message);
      throw err;
    }
  };

  // Actualizar compra
  const updateCompra = async (id: number, compra: Partial<Omit<Compra, 'id' | 'created_at'>>) => {
    try {
      const response = await apiClient.updateCompra(id, compra);
      const updatedCompra = response.data;
      setCompras(prev => prev.map(c => c.id === id ? { ...c, ...updatedCompra } : c));
      toast.success('Compra actualizada exitosamente');
      await loadCompras(); // Recargar para obtener datos actualizados
      return updatedCompra;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al actualizar compra';
      toast.error(message);
      throw err;
    }
  };

  // Eliminar compra
  const deleteCompra = async (id: number) => {
    try {
      await apiClient.deleteCompra(id);
      setCompras(prev => prev.filter(c => c.id !== id));
      toast.success('Compra eliminada exitosamente, stock ajustado');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al eliminar compra';
      toast.error(message);
      throw err;
    }
  };

  // Cargar al montar el componente
  useEffect(() => {
    loadCompras();
  }, []);

  return {
    compras,
    loading,
    error,
    loadCompras,
    createCompra,
    updateCompra,
    deleteCompra,
  };
};