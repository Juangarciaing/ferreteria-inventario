import React, { useState, useMemo } from 'react';
import { 
  PlusIcon, 
  PencilIcon, 
  TrashIcon, 
  MagnifyingGlassIcon,
  BuildingStorefrontIcon,
  CheckBadgeIcon,
  StarIcon,
  ShoppingCartIcon,
  DocumentArrowDownIcon
} from '@heroicons/react/24/outline';
import ProveedorModal from '../components/ProveedorModal';
import ExportModal from '../components/ExportModal';
import { useProveedores } from '../hooks/useProveedores';
import { useCompras } from '../hooks/useCompras';
import { useAuth } from '../contexts/AuthContext';
import { Proveedor } from '../types';

const Proveedores: React.FC = () => {
  const { proveedores, loading, createProveedor, updateProveedor, deleteProveedor } = useProveedores();
  const { compras } = useCompras();
  const { isAdmin } = useAuth();
  const [modalOpen, setModalOpen] = useState(false);
  const [exportModalOpen, setExportModalOpen] = useState(false);
  const [editingProveedor, setEditingProveedor] = useState<Proveedor | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedEstado, setSelectedEstado] = useState<string>('');
  const [selectedCondiciones, setSelectedCondiciones] = useState<string>('');
  const [selectedRating, setSelectedRating] = useState<string>('');

  // Calcular estadísticas
  const stats = useMemo(() => {
    const totalProveedores = proveedores.length;
    const proveedoresActivos = proveedores.filter(p => p.estado === 'activo').length;
    
    // Rating promedio
    const proveedoresConRating = proveedores.filter(p => p.rating && p.rating > 0);
    const ratingPromedio = proveedoresConRating.length > 0
      ? proveedoresConRating.reduce((sum, p) => sum + (p.rating || 0), 0) / proveedoresConRating.length
      : 0;
    
    // Total de compras
    const totalCompras = compras.length;
    const comprasPorProveedor = new Map<number, number>();
    compras.forEach(compra => {
      // Usar proveedor_id o proveedor.id_proveedor si está poblado
      const proveedorId = compra.proveedor_id || compra.proveedor?.id_proveedor;
      if (proveedorId) {
        const count = comprasPorProveedor.get(proveedorId) || 0;
        comprasPorProveedor.set(proveedorId, count + 1);
      }
    });

    return {
      totalProveedores,
      proveedoresActivos,
      ratingPromedio,
      totalCompras,
      comprasPorProveedor
    };
  }, [proveedores, compras]);

  // Handlers
  const handleSaveProveedor = async (proveedorData: Partial<Proveedor>) => {
    try {
      if (editingProveedor) {
        await updateProveedor(editingProveedor.id_proveedor, proveedorData);
      } else {
        await createProveedor(proveedorData as Omit<Proveedor, 'id_proveedor' | 'created_at'>);
      }
      setModalOpen(false);
      setEditingProveedor(null);
    } catch (error) {
      console.error('Error al guardar proveedor:', error);
    }
  };

  const handleEditProveedor = (proveedor: Proveedor) => {
    setEditingProveedor(proveedor);
    setModalOpen(true);
  };

  const handleDeleteProveedor = async (id_proveedor: number) => {
    if (window.confirm('¿Está seguro de que desea eliminar este proveedor?')) {
      try {
        await deleteProveedor(id_proveedor);
      } catch (error) {
        console.error('Error al eliminar proveedor:', error);
      }
    }
  };

  // Filtrar proveedores
  const filteredProveedores = useMemo(() => {
    return proveedores.filter(proveedor => {
      const matchesSearch = proveedor.nombre?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           proveedor.contacto?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           proveedor.telefono?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           proveedor.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           proveedor.rut_ruc?.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesEstado = selectedEstado === '' || proveedor.estado === selectedEstado;
      
      const matchesCondiciones = selectedCondiciones === '' || proveedor.condiciones_pago === selectedCondiciones;
      
      const matchesRating = selectedRating === '' || 
        (proveedor.rating && proveedor.rating >= parseInt(selectedRating));
      
      return matchesSearch && matchesEstado && matchesCondiciones && matchesRating;
    });
  }, [proveedores, searchTerm, selectedEstado, selectedCondiciones, selectedRating]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Proveedores</h1>
          <p className="mt-1 text-sm text-gray-500">Gestiona tu red de proveedores</p>
        </div>
        <button
          onClick={() => {
            setEditingProveedor(null);
            setModalOpen(true);
          }}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg shadow-lg text-white bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 transition-all duration-200"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Nuevo Proveedor
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Proveedores */}
        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm font-medium">Total Proveedores</p>
              <p className="text-3xl font-bold mt-2">{stats.totalProveedores}</p>
            </div>
            <BuildingStorefrontIcon className="h-12 w-12 text-purple-200 opacity-80" />
          </div>
        </div>

        {/* Proveedores Activos */}
        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm font-medium">Proveedores Activos</p>
              <p className="text-3xl font-bold mt-2">{stats.proveedoresActivos}</p>
              <p className="text-green-100 text-xs mt-1">
                {((stats.proveedoresActivos / stats.totalProveedores) * 100).toFixed(0)}% del total
              </p>
            </div>
            <CheckBadgeIcon className="h-12 w-12 text-green-200 opacity-80" />
          </div>
        </div>

        {/* Rating Promedio */}
        <div className="bg-gradient-to-br from-yellow-500 to-yellow-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-yellow-100 text-sm font-medium">Rating Promedio</p>
              <p className="text-3xl font-bold mt-2">{stats.ratingPromedio.toFixed(1)}</p>
              <div className="flex mt-1">
                {[1, 2, 3, 4, 5].map((star) => (
                  <StarIcon
                    key={star}
                    className={`h-4 w-4 ${star <= Math.round(stats.ratingPromedio) ? 'fill-yellow-200 text-yellow-200' : 'text-yellow-300'}`}
                  />
                ))}
              </div>
            </div>
            <StarIcon className="h-12 w-12 text-yellow-200 opacity-80" />
          </div>
        </div>

        {/* Total Compras */}
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm font-medium">Total Compras</p>
              <p className="text-3xl font-bold mt-2">{stats.totalCompras}</p>
              <p className="text-blue-100 text-xs mt-1">
                Promedio: {(stats.totalCompras / stats.totalProveedores).toFixed(1)} por proveedor
              </p>
            </div>
            <ShoppingCartIcon className="h-12 w-12 text-blue-200 opacity-80" />
          </div>
        </div>
      </div>

      {/* Filtros */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Buscar por nombre, contacto, email, teléfono..."
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <select
            className="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
            value={selectedEstado}
            onChange={(e) => setSelectedEstado(e.target.value)}
          >
            <option value="">Todos los estados</option>
            <option value="activo">Activo</option>
            <option value="inactivo">Inactivo</option>
          </select>
          <select
            className="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
            value={selectedCondiciones}
            onChange={(e) => setSelectedCondiciones(e.target.value)}
          >
            <option value="">Todas las condiciones</option>
            <option value="contado">Contado</option>
            <option value="credito_30">Crédito 30 días</option>
            <option value="credito_60">Crédito 60 días</option>
          </select>
          <select
            className="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
            value={selectedRating}
            onChange={(e) => setSelectedRating(e.target.value)}
          >
            <option value="">Todos los ratings</option>
            <option value="5">5 estrellas</option>
            <option value="4">4+ estrellas</option>
            <option value="3">3+ estrellas</option>
            <option value="2">2+ estrellas</option>
            <option value="1">1+ estrellas</option>
          </select>
        </div>
        
        {/* Contador y botón limpiar filtros */}
        <div className="mt-4 flex items-center justify-between">
          <p className="text-sm text-gray-600">
            Mostrando <span className="font-bold text-purple-600">{filteredProveedores.length}</span> de {proveedores.length} proveedores
          </p>
          {(searchTerm || selectedEstado || selectedCondiciones || selectedRating) && (
            <button
              onClick={() => {
                setSearchTerm('');
                setSelectedEstado('');
                setSelectedCondiciones('');
                setSelectedRating('');
              }}
              className="text-sm text-purple-600 hover:text-purple-800 font-medium"
            >
              Limpiar filtros
            </button>
          )}
          <button
            onClick={() => setExportModalOpen(true)}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
          >
            <DocumentArrowDownIcon className="h-4 w-4 mr-2" />
            Exportar
          </button>
        </div>
      </div>

      {/* Tabla de proveedores */}
      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gradient-to-r from-purple-50 to-purple-100">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-medium text-purple-900 uppercase tracking-wider">
                  Proveedor
                </th>
                <th className="px-6 py-4 text-left text-xs font-medium text-purple-900 uppercase tracking-wider">
                  Contacto
                </th>
                <th className="px-6 py-4 text-left text-xs font-medium text-purple-900 uppercase tracking-wider">
                  Condiciones
                </th>
                <th className="px-6 py-4 text-left text-xs font-medium text-purple-900 uppercase tracking-wider">
                  Rating
                </th>
                <th className="px-6 py-4 text-left text-xs font-medium text-purple-900 uppercase tracking-wider">
                  Compras
                </th>
                <th className="px-6 py-4 text-left text-xs font-medium text-purple-900 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-4 text-right text-xs font-medium text-purple-900 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredProveedores.map((proveedor) => (
                <tr key={proveedor.id_proveedor} className="hover:bg-purple-50 transition-colors duration-150">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {proveedor.nombre}
                      </div>
                      {proveedor.rut_ruc && (
                        <div className="text-sm text-gray-500">
                          RUT/RUC: {proveedor.rut_ruc}
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm font-medium text-gray-900">{proveedor.contacto}</div>
                    {proveedor.telefono && (
                      <div className="text-sm text-gray-600 flex items-center">
                        📞 {proveedor.telefono}
                      </div>
                    )}
                    {proveedor.email && (
                      <div className="text-sm text-gray-600 flex items-center">
                        ✉️ {proveedor.email}
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <span className={`inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium ${
                        proveedor.condiciones_pago === 'contado' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-blue-100 text-blue-800'
                      }`}>
                        {proveedor.condiciones_pago === 'contado' && '💵 Contado'}
                        {proveedor.condiciones_pago === 'credito_30' && '📅 Crédito 30 días'}
                        {proveedor.condiciones_pago === 'credito_60' && '📅 Crédito 60 días'}
                      </span>
                    </div>
                    {proveedor.descuento_default && proveedor.descuento_default > 0 && (
                      <div className="mt-1">
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                          🏷️ Desc: {proveedor.descuento_default}%
                        </span>
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {proveedor.rating && proveedor.rating > 0 ? (
                        <>
                          {[1, 2, 3, 4, 5].map((star) => (
                            <StarIcon
                              key={star}
                              className={`h-4 w-4 ${star <= proveedor.rating! ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}`}
                            />
                          ))}
                          <span className="ml-2 text-sm font-medium text-gray-700">
                            {proveedor.rating.toFixed(1)}
                          </span>
                        </>
                      ) : (
                        <span className="text-sm text-gray-400">Sin rating</span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center">
                    <span className="inline-flex items-center px-3 py-1 rounded-lg text-sm font-medium bg-blue-100 text-blue-800">
                      {stats.comprasPorProveedor.get(proveedor.id_proveedor) || 0}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-3 py-1 rounded-lg text-xs font-medium ${
                      proveedor.estado === 'activo'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {proveedor.estado === 'activo' ? '✅ Activo' : '❌ Inactivo'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <div className="flex justify-end gap-2">
                      <button
                        onClick={() => handleEditProveedor(proveedor)}
                        className="inline-flex items-center px-3 py-1.5 bg-gradient-to-r from-blue-500 to-blue-600 text-white text-xs font-medium rounded-lg hover:from-blue-600 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
                      >
                        <PencilIcon className="h-4 w-4 mr-1" />
                        Editar
                      </button>
                      {isAdmin && (
                        <button
                          onClick={() => handleDeleteProveedor(proveedor.id_proveedor)}
                          className="inline-flex items-center px-3 py-1.5 bg-gradient-to-r from-red-500 to-red-600 text-white text-xs font-medium rounded-lg hover:from-red-600 hover:to-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-all duration-200"
                        >
                          <TrashIcon className="h-4 w-4 mr-1" />
                          Eliminar
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Mensaje cuando no hay resultados */}
      {filteredProveedores.length === 0 && (
        <div className="bg-white rounded-xl shadow-lg py-12">
          <div className="text-center">
            <BuildingStorefrontIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No se encontraron proveedores</h3>
            <p className="mt-1 text-sm text-gray-500">
              {searchTerm || selectedEstado || selectedCondiciones || selectedRating
                ? 'Intenta ajustar los filtros de búsqueda'
                : 'Comienza agregando un nuevo proveedor'}
            </p>
            {!(searchTerm || selectedEstado || selectedCondiciones || selectedRating) && (
              <div className="mt-6">
                <button
                  onClick={() => {
                    setEditingProveedor(null);
                    setModalOpen(true);
                  }}
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-lg text-white bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
                >
                  <PlusIcon className="h-5 w-5 mr-2" />
                  Nuevo Proveedor
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Modal */}
      <ProveedorModal
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setEditingProveedor(null);
        }}
        onSave={handleSaveProveedor}
        proveedor={editingProveedor}
      />

      {/* Modal de Exportación */}
      <ExportModal
        isOpen={exportModalOpen}
        onClose={() => setExportModalOpen(false)}
        title="Proveedores"
        data={filteredProveedores.map(p => ({
          ID: p.id,
          Nombre: p.nombre,
          Contacto: p.contacto || 'N/A',
          Teléfono: p.telefono || 'N/A',
          Email: p.email || 'N/A',
          Dirección: p.direccion || 'N/A',
          Estado: p.estado || 'N/A'
        }))}
        filename="proveedores"
      />
    </div>
  );
};

export default Proveedores;