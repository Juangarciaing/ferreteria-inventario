import { useState, useEffect } from 'react';
import { User } from '../types';
import { apiClient } from '../lib/api';
import toast from 'react-hot-toast';

export const useUsuarios = () => {
  const [usuarios, setUsuarios] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadUsuarios();
  }, []);

  const loadUsuarios = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.getUsuarios();
      setUsuarios(data as User[]);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al cargar usuarios';
      setError(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  const createUsuario = async (usuario: Omit<User, 'id' | 'created_at' | 'updated_at'>) => {
    try {
      // Mapear payload al backend
      const payload = {
        nombre: usuario.nombre,
        email: usuario.email,
        password: (usuario as any).password || 'temporal123',
        rol: usuario.rol || 'vendedor',
        estado: usuario.estado !== undefined ? usuario.estado : true, // ✅ Incluir estado
      };
      console.log('📤 Creando usuario con payload:', payload)
      await apiClient.createUsuario(payload);
      await loadUsuarios();
      toast.success('Usuario creado exitosamente');
      return true;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al crear usuario';
      toast.error(message);
      throw err;
    }
  };

  const updateUsuario = async (id: string, updates: Partial<User>) => {
    try {
      const payload: any = {}
      if (updates.nombre) payload.nombre = updates.nombre
      if (updates.email) payload.email = updates.email
      if ((updates as any).password) payload.password = (updates as any).password
      if (updates.rol) payload.rol = updates.rol
      // ✅ IMPORTANTE: Incluir el campo estado si está presente
      if (updates.estado !== undefined) payload.estado = updates.estado

      console.log('📤 Enviando actualización al API:', payload)
      await apiClient.updateUsuario(id, payload)
      await loadUsuarios()
      toast.success('Usuario actualizado exitosamente')
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al actualizar usuario';
      toast.error(message);
      throw err;
    }
  };

  const deleteUsuario = async (id: string) => {
    try {
      await apiClient.deleteUsuario(id)
      setUsuarios(prev => prev.filter(user => user.id !== id));
      toast.success('Usuario eliminado');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al eliminar usuario';
      toast.error(message);
      throw err;
    }
  };

  const toggleUsuarioEstado = async (_id: string) => {
    try {
      // No hay endpoint de estado; omitir o implementar si se agrega al backend
      toast.success('Esta operación no está disponible (sin endpoint)');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al cambiar estado';
      toast.error(message);
      throw err;
    }
  };

  return {
    usuarios,
    loading,
    error,
    refetch: loadUsuarios,
    createUsuario,
    updateUsuario,
    deleteUsuario,
    toggleUsuarioEstado,
  };
};