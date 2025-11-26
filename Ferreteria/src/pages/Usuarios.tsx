import React, { useState, useMemo } from 'react';
import { 
  PlusIcon, 
  PencilIcon, 
  TrashIcon, 
  MagnifyingGlassIcon,
  UserGroupIcon,
  ShieldCheckIcon,
  UserIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';
import { User } from '../types';
import { useUsuarios } from '../hooks/useUsuarios';
import UsuarioModal from '../components/UsuarioModal';
import ExportModal from '../components/ExportModal';

const Usuarios: React.FC = () => {
  const {
    usuarios,
    loading,
    createUsuario,
    updateUsuario,
    deleteUsuario,
  } = useUsuarios();
  
  const [modalOpen, setModalOpen] = useState(false);
  const [exportModalOpen, setExportModalOpen] = useState(false);
  const [editingUsuario, setEditingUsuario] = useState<User | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRol, setSelectedRol] = useState<string>('');

  // Calcular estadísticas
  const stats = useMemo(() => {
    const totalUsuarios = usuarios.length;
    const administradores = usuarios.filter(u => u.rol === 'admin').length;
    const vendedores = usuarios.filter(u => u.rol === 'vendedor').length;
    const activos = usuarios.filter(u => u.estado !== false).length;
    const inactivos = usuarios.filter(u => u.estado === false).length;
    
    return {
      totalUsuarios,
      administradores,
      vendedores,
      activos,
      inactivos
    };
  }, [usuarios]);

  // Filtrar usuarios
  const filteredUsuarios = useMemo(() => {
    return usuarios.filter(usuario => {
      const matchesSearch = usuario.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           usuario.email.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesRol = selectedRol === '' || usuario.rol === selectedRol;
      return matchesSearch && matchesRol;
    });
  }, [usuarios, searchTerm, selectedRol]);

  // Handlers
  const handleSaveUsuario = async (usuarioData: Partial<User>) => {
    try {
      if (editingUsuario) {
        await updateUsuario(editingUsuario.id, usuarioData);
      } else {
        await createUsuario(usuarioData as Omit<User, 'id' | 'created_at' | 'updated_at'>);
      }
      setModalOpen(false);
      setEditingUsuario(null);
    } catch (error) {
      console.error('Error al guardar usuario:', error);
    }
  };

  const handleEditUsuario = (usuario: User) => {
    setEditingUsuario(usuario);
    setModalOpen(true);
  };

  const handleDeleteUsuario = async (id: string) => {
    if (window.confirm('¿Está seguro de que desea eliminar este usuario?')) {
      try {
        await deleteUsuario(id);
      } catch (error) {
        console.error('Error al eliminar usuario:', error);
      }
    }
  };

  const handleToggleEstado = async (usuario: User) => {
    // Determinar el estado actual (si es undefined, considerarlo como true/activo)
    const estadoActual = usuario.estado !== false; // undefined o true = activo
    const nuevoEstado = !estadoActual;
    const accion = nuevoEstado ? 'activar' : 'desactivar';
    
    console.log('🔍 Toggle Estado:', {
      usuario: usuario.nombre,
      estadoOriginal: usuario.estado,
      estadoActual,
      nuevoEstado,
      accion
    });
    
    if (window.confirm(`¿Está seguro de que desea ${accion} al usuario ${usuario.nombre}?`)) {
      try {
        await updateUsuario(usuario.id, { estado: nuevoEstado });
      } catch (error) {
        console.error('Error al cambiar estado:', error);
      }
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Usuarios</h1>
          <p className="mt-1 text-sm text-gray-500">Gestiona los usuarios del sistema</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setExportModalOpen(true)}
            className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-lg shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-cyan-500"
          >
            <UserGroupIcon className="h-5 w-5 mr-2" />
            Exportar
          </button>
          <button
            onClick={() => {
              setEditingUsuario(null);
              setModalOpen(true);
            }}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg shadow-lg text-white bg-gradient-to-r from-cyan-600 to-cyan-700 hover:from-cyan-700 hover:to-cyan-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-cyan-500 transition-all duration-200"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Nuevo Usuario
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        {/* Total Usuarios */}
        <div className="bg-gradient-to-br from-cyan-500 to-cyan-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-cyan-100 text-sm font-medium">Total Usuarios</p>
              <p className="text-3xl font-bold mt-2">{stats.totalUsuarios}</p>
            </div>
            <UserGroupIcon className="h-12 w-12 text-cyan-200 opacity-80" />
          </div>
        </div>

        {/* Administradores */}
        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm font-medium">Administradores</p>
              <p className="text-3xl font-bold mt-2">{stats.administradores}</p>
            </div>
            <ShieldCheckIcon className="h-12 w-12 text-purple-200 opacity-80" />
          </div>
        </div>

        {/* Vendedores */}
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm font-medium">Vendedores</p>
              <p className="text-3xl font-bold mt-2">{stats.vendedores}</p>
            </div>
            <UserIcon className="h-12 w-12 text-blue-200 opacity-80" />
          </div>
        </div>

        {/* Activos */}
        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm font-medium">Activos</p>
              <p className="text-3xl font-bold mt-2">{stats.activos}</p>
            </div>
            <CheckCircleIcon className="h-12 w-12 text-green-200 opacity-80" />
          </div>
        </div>

        {/* Inactivos */}
        <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-red-100 text-sm font-medium">Inactivos</p>
              <p className="text-3xl font-bold mt-2">{stats.inactivos}</p>
            </div>
            <XCircleIcon className="h-12 w-12 text-red-200 opacity-80" />
          </div>
        </div>
      </div>

      {/* Filtros */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Buscar por nombre o email..."
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <select
            className="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500"
            value={selectedRol}
            onChange={(e) => setSelectedRol(e.target.value)}
          >
            <option value="">Todos los roles</option>
            <option value="admin">Administrador</option>
            <option value="vendedor">Vendedor</option>
          </select>
        </div>
        
        <div className="mt-4 flex items-center justify-between">
          <p className="text-sm text-gray-600">
            Mostrando <span className="font-bold text-cyan-600">{filteredUsuarios.length}</span> de {usuarios.length} usuarios
          </p>
          {(searchTerm || selectedRol) && (
            <button
              onClick={() => {
                setSearchTerm('');
                setSelectedRol('');
              }}
              className="text-sm text-cyan-600 hover:text-cyan-800 font-medium"
            >
              Limpiar filtros
            </button>
          )}
        </div>
      </div>

      {/* Tabla de usuarios */}
      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gradient-to-r from-cyan-50 to-cyan-100">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-medium text-cyan-900 uppercase tracking-wider">
                  Usuario
                </th>
                <th className="px-6 py-4 text-left text-xs font-medium text-cyan-900 uppercase tracking-wider">
                  Rol
                </th>
                <th className="px-6 py-4 text-left text-xs font-medium text-cyan-900 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-4 text-left text-xs font-medium text-cyan-900 uppercase tracking-wider">
                  Fecha Creación
                </th>
                <th className="px-6 py-4 text-right text-xs font-medium text-cyan-900 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredUsuarios.map((usuario) => (
                <tr key={usuario.id} className="hover:bg-cyan-50 transition-colors duration-150">
                  <td className="px-6 py-4">
                    <div className="flex items-center">
                      <div className={`flex-shrink-0 h-10 w-10 rounded-full flex items-center justify-center ${
                        usuario.rol === 'admin' 
                          ? 'bg-purple-100 text-purple-700' 
                          : 'bg-blue-100 text-blue-700'
                      }`}>
                        <span className="text-lg font-bold">
                          {usuario.nombre.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
                          {usuario.nombre}
                        </div>
                        <div className="text-sm text-gray-600 flex items-center">
                          ✉️ {usuario.email}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-3 py-1 rounded-lg text-xs font-medium ${
                      usuario.rol === 'admin'
                        ? 'bg-purple-100 text-purple-800'
                        : 'bg-blue-100 text-blue-800'
                    }`}>
                      {usuario.rol === 'admin' ? '👑 Administrador' : '👤 Vendedor'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-3 py-1 rounded-lg text-xs font-medium ${
                      usuario.estado !== false
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {usuario.estado !== false ? '✅ Activo' : '❌ Inactivo'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {usuario.created_at 
                      ? new Date(usuario.created_at).toLocaleDateString('es', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric'
                        })
                      : '-'
                    }
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <div className="flex justify-end gap-2">
                      <button
                        onClick={() => handleToggleEstado(usuario)}
                        className={`inline-flex items-center px-3 py-1.5 text-white text-xs font-medium rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 transition-all duration-200 ${
                          usuario.estado !== false
                            ? 'bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 focus:ring-orange-500'
                            : 'bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 focus:ring-green-500'
                        }`}
                        title={usuario.estado !== false ? 'Desactivar usuario' : 'Activar usuario'}
                      >
                        {usuario.estado !== false ? (
                          <>
                            <XCircleIcon className="h-4 w-4 mr-1" />
                            Desactivar
                          </>
                        ) : (
                          <>
                            <CheckCircleIcon className="h-4 w-4 mr-1" />
                            Activar
                          </>
                        )}
                      </button>
                      <button
                        onClick={() => handleEditUsuario(usuario)}
                        className="inline-flex items-center px-3 py-1.5 bg-gradient-to-r from-blue-500 to-blue-600 text-white text-xs font-medium rounded-lg hover:from-blue-600 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
                        title="Editar usuario"
                      >
                        <PencilIcon className="h-4 w-4 mr-1" />
                        Editar
                      </button>
                      <button
                        onClick={() => handleDeleteUsuario(usuario.id)}
                        className="inline-flex items-center px-3 py-1.5 bg-gradient-to-r from-red-500 to-red-600 text-white text-xs font-medium rounded-lg hover:from-red-600 hover:to-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-all duration-200"
                        title="Eliminar usuario"
                      >
                        <TrashIcon className="h-4 w-4 mr-1" />
                        Eliminar
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Mensaje cuando no hay resultados */}
      {filteredUsuarios.length === 0 && (
        <div className="bg-white rounded-xl shadow-lg py-12">
          <div className="text-center">
            <UserGroupIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">
              {searchTerm || selectedRol ? 'No se encontraron usuarios' : 'No hay usuarios registrados'}
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              {searchTerm || selectedRol
                ? 'Intenta ajustar los filtros de búsqueda'
                : 'Comienza agregando un nuevo usuario al sistema'}
            </p>
            {!(searchTerm || selectedRol) && (
              <div className="mt-6">
                <button
                  onClick={() => {
                    setEditingUsuario(null);
                    setModalOpen(true);
                  }}
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-lg text-white bg-gradient-to-r from-cyan-600 to-cyan-700 hover:from-cyan-700 hover:to-cyan-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-cyan-500"
                >
                  <PlusIcon className="h-5 w-5 mr-2" />
                  Crear Primer Usuario
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Modal */}
      <UsuarioModal
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setEditingUsuario(null);
        }}
        onSave={handleSaveUsuario}
        usuario={editingUsuario}
      />

      {/* Modal de Exportación */}
      <ExportModal
        isOpen={exportModalOpen}
        onClose={() => setExportModalOpen(false)}
        title="Usuarios"
        data={filteredUsuarios.map(u => ({
          ID: u.id,
          Nombre: u.nombre,
          Email: u.email,
          Rol: u.rol,
          Estado: u.estado ? 'Activo' : 'Inactivo'
        }))}
        filename="usuarios"
      />
    </div>
  );
};

export default Usuarios;