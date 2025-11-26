/**
 * Hook para gestión de proveedores
 */
import { useState, useEffect } from 'react';
import { apiClient } from '../lib/api';
import { Proveedor } from '../types';
import toast from 'react-hot-toast';

export const useProveedores = () => {
  const [proveedores, setProveedores] = useState<Proveedor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Cargar proveedores
  const loadProveedores = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.getProveedores();
      // Transformar id a id_proveedor para compatibilidad
      const transformedData = data.map((p: any) => ({
        ...p,
        id_proveedor: p.id || p.id_proveedor
      }));
      setProveedores(transformedData);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error desconocido';
      setError(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  // Crear proveedor
  const createProveedor = async (proveedor: Omit<Proveedor, 'id_proveedor' | 'created_at'>) => {
    try {
      const newProveedor = await apiClient.createProveedor(proveedor);
      setProveedores(prev => [...prev, newProveedor]);
      toast.success('Proveedor creado exitosamente');
      return newProveedor;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al crear proveedor';
      toast.error(message);
      throw err;
    }
  };

  // Actualizar proveedor
  const updateProveedor = async (id: number, updates: Partial<Proveedor>) => {
    try {
      const updatedProveedor = await apiClient.updateProveedor(id, updates);
      setProveedores(prev => 
        prev.map(p => p.id_proveedor === id ? updatedProveedor : p)
      );
      toast.success('Proveedor actualizado exitosamente');
      return updatedProveedor;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al actualizar proveedor';
      toast.error(message);
      throw err;
    }
  };

  // Eliminar proveedor
  const deleteProveedor = async (id: number) => {
    try {
      await apiClient.deleteProveedor(id);
      setProveedores(prev => prev.filter(p => p.id_proveedor !== id));
      toast.success('Proveedor eliminado exitosamente');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al eliminar proveedor';
      toast.error(message);
      throw err;
    }
  };

  // Cargar al montar el componente
  useEffect(() => {
    loadProveedores();
  }, []);

  return {
    proveedores,
    loading,
    error,
    loadProveedores,
    createProveedor,
    updateProveedor,
    deleteProveedor,
  };
};