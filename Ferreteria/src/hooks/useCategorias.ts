/**
 * Hook para gestión de categorías
 */
import { useState, useEffect } from 'react';
import { Categoria } from '../types';
// import { CategoriaService } from '../services/ProductoService';
import toast from 'react-hot-toast';

// Removed unused simulated categories
import { apiClient } from '../lib/api';

export const useCategorias = () => {
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Cargar categorías simuladas
  const loadCategorias = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.getCategorias();
      setCategorias(data as Categoria[]);
      console.log('✅ Categorías cargadas (API):', Array.isArray(data) ? data.length : 0);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error desconocido';
      setError(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  // Crear categoría
  const createCategoria = async (categoria: Omit<Categoria, 'id' | 'created_at'>) => {
    try {
      setLoading(true);
      await apiClient.createCategoria(categoria);
      await loadCategorias();
      toast.success('Categoría creada exitosamente');
      return true;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al crear categoría';
      setError(message);
      toast.error(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Actualizar categoría
  const updateCategoria = async (id: number, updates: Partial<Categoria>) => {
    try {
      setLoading(true);
      await apiClient.updateCategoria(id, updates);
      await loadCategorias();
      toast.success('Categoría actualizada exitosamente');
      return true;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al actualizar categoría';
      setError(message);
      toast.error(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Eliminar categoría
  const deleteCategoria = async (id: number) => {
    try {
      setLoading(true);
      await apiClient.deleteCategoria(id);
      setCategorias(prev => prev.filter(c => c.id !== id));
      toast.success('Categoría eliminada exitosamente');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al eliminar categoría';
      setError(message);
      toast.error(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Cargar al montar el componente
  useEffect(() => {
    loadCategorias();
  }, []);

  return {
    categorias,
    loading,
    error,
    loadCategorias,
    createCategoria,
    updateCategoria,
    deleteCategoria
  };
};