import React, { useState, useMemo } from 'react';
import { 
  PlusIcon, 
  EyeIcon,
  MagnifyingGlassIcon,
  ArrowDownTrayIcon,
  TruckIcon,
  CurrencyDollarIcon,
  ShoppingCartIcon,
  ChartBarIcon,
  PencilIcon,
  TrashIcon,
} from '@heroicons/react/24/outline';
import { Compra } from '../types';
import CompraModal from '../components/CompraModal';
import ExportModal from '../components/ExportModal';
import { useCompras } from '../hooks/useCompras';
import { useProductos } from '../hooks/useProductos';
import { useProveedores } from '../hooks/useProveedores';
import { format, startOfMonth, endOfMonth, subMonths } from 'date-fns';
import { es } from 'date-fns/locale';

const Compras: React.FC = () => {
  const { compras, loading: loadingCompras, createCompra, updateCompra, deleteCompra } = useCompras();
  const { productos, loading: loadingProductos } = useProductos();
  const { proveedores, loading: loadingProveedores } = useProveedores();
  
  const loading = loadingCompras || loadingProductos || loadingProveedores;
  const [modalOpen, setModalOpen] = useState(false);
  const [exportModalOpen, setExportModalOpen] = useState(false);
  const [selectedCompra, setSelectedCompra] = useState<Compra | null>(null);
  const [editingCompra, setEditingCompra] = useState<Compra | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedProveedor, setSelectedProveedor] = useState<string>('');
  const [dateFilter, setDateFilter] = useState({
    desde: '',
    hasta: '',
  });

  // Primero filtrar las compras
  const filteredCompras = useMemo(() => {
    return compras.filter(compra => {
      // Filtro de búsqueda
      if (searchTerm) {
        const searchLower = searchTerm.toLowerCase();
        const matchProducto = compra.producto?.nombre?.toLowerCase().includes(searchLower);
        const matchProveedor = compra.proveedor?.nombre?.toLowerCase().includes(searchLower);
        if (!matchProducto && !matchProveedor) return false;
      }
      
      // Filtro de proveedor
      if (selectedProveedor && compra.proveedor_id?.toString() !== selectedProveedor) {
        return false;
      }
      
      // Filtro de fecha
      if (dateFilter.desde && compra.fecha_compra) {
        if (new Date(compra.fecha_compra) < new Date(dateFilter.desde)) return false;
      }
      if (dateFilter.hasta && compra.fecha_compra) {
        if (new Date(compra.fecha_compra) > new Date(dateFilter.hasta)) return false;
      }
      
      return true;
    });
  }, [compras, searchTerm, selectedProveedor, dateFilter]);

  // Calcular estadísticas basadas en filteredCompras
  const stats = useMemo(() => {
    const totalCompras = filteredCompras.reduce((sum, c) => sum + c.total, 0);
    const numCompras = filteredCompras.length;
    const promedioCompra = numCompras > 0 ? totalCompras / numCompras : 0;
    
    // Comparar con mes anterior
    const now = new Date();
    const mesActualStart = startOfMonth(now);
    const mesActualEnd = endOfMonth(now);
    const mesAnteriorStart = startOfMonth(subMonths(now, 1));
    const mesAnteriorEnd = endOfMonth(subMonths(now, 1));
    
    const comprasMesActual = compras.filter(c => {
      const fecha = c.fecha_compra ? new Date(c.fecha_compra) : null;
      return fecha && fecha >= mesActualStart && fecha <= mesActualEnd;
    });
    
    const comprasMesAnterior = compras.filter(c => {
      const fecha = c.fecha_compra ? new Date(c.fecha_compra) : null;
      return fecha && fecha >= mesAnteriorStart && fecha <= mesAnteriorEnd;
    });
    
    const totalMesActual = comprasMesActual.reduce((sum, c) => sum + c.total, 0);
    const totalMesAnterior = comprasMesAnterior.reduce((sum, c) => sum + c.total, 0);
    const cambio = totalMesAnterior > 0 
      ? ((totalMesActual - totalMesAnterior) / totalMesAnterior) * 100 
      : 0;
    
    return {
      totalCompras,
      numCompras,
      promedioCompra,
      cambio,
      totalMesActual,
      totalMesAnterior,
    };
  }, [filteredCompras, compras]);

  const handleNuevaCompra = async (compraData: { producto_id: number; cantidad: number; precio_unitario: number; proveedor_id?: number }) => {
    try {
      await createCompra(compraData as any);
      setModalOpen(false);
    } catch (error) {
      console.error('Error al crear compra:', error);
    }
  };

  const handleEditarCompra = async (compraData: { producto_id: number; cantidad: number; precio_unitario: number; proveedor_id?: number }) => {
    if (!editingCompra) return;
    try {
      await updateCompra(editingCompra.id!, compraData);
      setEditingCompra(null);
      setModalOpen(false);
    } catch (error) {
      console.error('Error al editar compra:', error);
    }
  };

  const handleEliminarCompra = async (id: number) => {
    if (globalThis.confirm('¿Estás seguro de eliminar esta compra? El stock del producto será ajustado.')) {
      try {
        await deleteCompra(id);
      } catch (error) {
        console.error('Error al eliminar compra:', error);
      }
    }
  };

  const handleVerDetalle = (compra: Compra) => {
    setSelectedCompra(compra);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 text-lg">Cargando compras...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestión de Compras</h1>
          <p className="mt-2 text-sm text-gray-700">
            Registro de compras a proveedores y actualización de inventario
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setExportModalOpen(true)}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
            Exportar
          </button>
          <button
            onClick={() => setModalOpen(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Nueva Compra
          </button>
        </div>
      </div>

      {/* Estadísticas */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white overflow-hidden shadow-lg rounded-xl hover:shadow-xl transition-shadow">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-blue-500 rounded-xl p-3">
                <CurrencyDollarIcon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Compras</dt>
                  <dd className="text-2xl font-bold text-gray-900">
                    ${stats.totalCompras.toFixed(2)}
                  </dd>
                  <dd className="text-xs text-gray-500 mt-1">
                    {stats.numCompras} compras
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow-lg rounded-xl hover:shadow-xl transition-shadow">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-green-500 rounded-xl p-3">
                <ShoppingCartIcon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Compra Promedio</dt>
                  <dd className="text-2xl font-bold text-gray-900">
                    ${stats.promedioCompra.toFixed(2)}
                  </dd>
                  <dd className="text-xs text-gray-500 mt-1">
                    Por compra
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow-lg rounded-xl hover:shadow-xl transition-shadow">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-purple-500 rounded-xl p-3">
                <TruckIcon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Este Mes</dt>
                  <dd className="text-2xl font-bold text-gray-900">
                    ${stats.totalMesActual.toFixed(2)}
                  </dd>
                  <dd className="text-xs text-gray-500 mt-1">
                    {compras.filter(c => {
                      const fecha = c.fecha_compra ? new Date(c.fecha_compra) : null;
                      return fecha && fecha >= startOfMonth(new Date());
                    }).length} compras
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow-lg rounded-xl hover:shadow-xl transition-shadow">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-orange-500 rounded-xl p-3">
                <ChartBarIcon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Cambio vs Anterior</dt>
                  <dd className={`text-2xl font-bold ${stats.cambio >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {stats.cambio >= 0 ? '↑' : '↓'} {Math.abs(stats.cambio).toFixed(1)}%
                  </dd>
                  <dd className="text-xs text-gray-500 mt-1">
                    ${stats.totalMesAnterior.toFixed(2)} anterior
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filtros */}
      <div className="bg-white shadow-lg rounded-xl p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="md:col-span-1">
            <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-2">
              Buscar
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                id="search"
                placeholder="Producto o proveedor..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>
          </div>

          <div className="md:col-span-1">
            <label htmlFor="proveedor" className="block text-sm font-medium text-gray-700 mb-2">
              Proveedor
            </label>
            <select
              id="proveedor"
              value={selectedProveedor}
              onChange={(e) => setSelectedProveedor(e.target.value)}
              className="block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="">Todos los proveedores</option>
              {proveedores.filter(p => p.id_proveedor).map(p => (
                <option key={p.id_proveedor} value={String(p.id_proveedor)}>
                  {p.nombre}
                </option>
              ))}
            </select>
          </div>

          <div className="md:col-span-1">
            <label htmlFor="desde" className="block text-sm font-medium text-gray-700 mb-2">
              Desde
            </label>
            <input
              type="date"
              id="desde"
              value={dateFilter.desde}
              onChange={(e) => setDateFilter({ ...dateFilter, desde: e.target.value })}
              className="block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>

          <div className="md:col-span-1">
            <label htmlFor="hasta" className="block text-sm font-medium text-gray-700 mb-2">
              Hasta
            </label>
            <input
              type="date"
              id="hasta"
              value={dateFilter.hasta}
              onChange={(e) => setDateFilter({ ...dateFilter, hasta: e.target.value })}
              className="block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="mt-4 flex items-center justify-between">
          <div className="text-sm text-gray-600">
            Mostrando <span className="font-semibold text-gray-900">{filteredCompras.length}</span> de{' '}
            <span className="font-semibold text-gray-900">{compras.length}</span> compras
          </div>
          {(searchTerm || selectedProveedor || dateFilter.desde || dateFilter.hasta) && (
            <button
              onClick={() => {
                setSearchTerm('');
                setSelectedProveedor('');
                setDateFilter({ desde: '', hasta: '' });
              }}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Limpiar filtros
            </button>
          )}
        </div>
      </div>

      {/* Lista de compras */}
      <div className="bg-white shadow-lg rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gradient-to-r from-gray-50 to-gray-100">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  ID
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Fecha
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Proveedor
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Producto
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Cantidad
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Precio Unit.
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Total
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Usuario
                </th>
                <th className="px-6 py-4 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredCompras.map((compra) => {
                console.log('🔍 Compra:', {
                  id: compra.id,
                  producto_id: compra.producto_id,
                  proveedor_id: compra.proveedor_id,
                  usuario_id: compra.usuario_id,
                  compra_completa: compra
                });
                
                const producto = productos.find(p => p.id === compra.producto_id);
                const proveedor = proveedores.find(p => p.id_proveedor === compra.proveedor_id);
                
                return (
                  <tr key={compra.id} className="hover:bg-blue-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                      #{compra.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      {compra.fecha_compra ? format(new Date(compra.fecha_compra), 'dd/MM/yyyy', { locale: es }) : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-8 w-8 bg-gradient-to-br from-purple-400 to-purple-600 rounded-full flex items-center justify-center">
                          <TruckIcon className="h-4 w-4 text-white" />
                        </div>
                        <div className="ml-3">
                          <div className="text-sm font-medium text-gray-900">
                            {proveedor?.nombre || 'Sin proveedor'}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {producto?.nombre || `Producto ID: ${compra.producto_id}`}
                      </div>
                      {producto?.categoria?.nombre && (
                        <div className="text-xs text-gray-500">{producto.categoria.nombre}</div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {compra.cantidad} unidades
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      ${compra.precio_unitario.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">
                      ${compra.total.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      {compra.usuario?.nombre || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleVerDetalle(compra)}
                          className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-lg text-white bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200 shadow-sm hover:shadow-md"
                          title="Ver detalle"
                        >
                          <EyeIcon className="h-4 w-4 mr-1" />
                          Ver
                        </button>
                        <button
                          onClick={() => {
                            setEditingCompra(compra);
                            setModalOpen(true);
                          }}
                          className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-lg text-white bg-gradient-to-r from-yellow-500 to-yellow-600 hover:from-yellow-600 hover:to-yellow-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500 transition-all duration-200 shadow-sm hover:shadow-md"
                          title="Editar compra"
                        >
                          <PencilIcon className="h-4 w-4 mr-1" />
                          Editar
                        </button>
                        <button
                          onClick={() => handleEliminarCompra(compra.id!)}
                          className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-lg text-white bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-all duration-200 shadow-sm hover:shadow-md"
                          title="Eliminar compra"
                        >
                          <TrashIcon className="h-4 w-4 mr-1" />
                          Eliminar
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {filteredCompras.length === 0 && (
        <div className="bg-white shadow-lg rounded-xl p-12 text-center">
          <div className="mx-auto h-24 w-24 bg-gray-100 rounded-full flex items-center justify-center mb-4">
            <ShoppingCartIcon className="h-12 w-12 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No se encontraron compras</h3>
          <p className="text-sm text-gray-500">
            {searchTerm || selectedProveedor || dateFilter.desde || dateFilter.hasta
              ? 'Intenta ajustar los filtros de búsqueda'
              : 'Comienza registrando tu primera compra'}
          </p>
        </div>
      )}

      {/* Modal Nueva/Editar Compra */}
      <CompraModal
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setEditingCompra(null);
        }}
        onSave={editingCompra ? handleEditarCompra : handleNuevaCompra}
        productos={productos}
        proveedores={proveedores}
        compra={editingCompra || undefined}
      />

      {/* Modal Detalle Compra */}
      {selectedCompra && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setSelectedCompra(null)} />
            <span className="hidden sm:inline-block sm:align-middle sm:h-screen">&#8203;</span>
            <div className="inline-block align-bottom bg-white rounded-xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
              <div className="bg-gradient-to-r from-blue-500 to-blue-600 px-6 py-4">
                <h3 className="text-xl font-bold text-white flex items-center">
                  <ShoppingCartIcon className="h-6 w-6 mr-2" />
                  Detalle de Compra #{selectedCompra.id}
                </h3>
              </div>
              <div className="bg-white px-6 py-5">
                <div className="space-y-4">
                  <div className="flex items-center justify-between py-3 border-b border-gray-200">
                    <span className="text-sm font-medium text-gray-500">Fecha:</span>
                    <span className="text-sm font-semibold text-gray-900">
                      {selectedCompra.fecha_compra ? format(new Date(selectedCompra.fecha_compra), 'dd/MM/yyyy HH:mm', { locale: es }) : 'N/A'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between py-3 border-b border-gray-200">
                    <span className="text-sm font-medium text-gray-500">Proveedor:</span>
                    <span className="text-sm font-semibold text-gray-900">
                      {proveedores.find(p => p.id_proveedor === selectedCompra.proveedor_id)?.nombre || 'Sin proveedor'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between py-3 border-b border-gray-200">
                    <span className="text-sm font-medium text-gray-500">Producto:</span>
                    <span className="text-sm font-semibold text-gray-900">
                      {productos.find(p => p.id === selectedCompra.producto_id)?.nombre || `Producto ID: ${selectedCompra.producto_id}`}
                    </span>
                  </div>
                  <div className="flex items-center justify-between py-3 border-b border-gray-200">
                    <span className="text-sm font-medium text-gray-500">Cantidad:</span>
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold bg-blue-100 text-blue-800">
                      {selectedCompra.cantidad} unidades
                    </span>
                  </div>
                  <div className="flex items-center justify-between py-3 border-b border-gray-200">
                    <span className="text-sm font-medium text-gray-500">Precio Unitario:</span>
                    <span className="text-sm font-semibold text-gray-900">
                      ${selectedCompra.precio_unitario.toFixed(2)}
                    </span>
                  </div>
                  <div className="flex items-center justify-between py-3 border-b border-gray-200">
                    <span className="text-sm font-medium text-gray-500">Total:</span>
                    <span className="text-lg font-bold text-gray-900">
                      ${selectedCompra.total.toFixed(2)}
                    </span>
                  </div>
                  <div className="flex items-center justify-between py-3">
                    <span className="text-sm font-medium text-gray-500">Usuario:</span>
                    <span className="text-sm font-semibold text-gray-900">
                      {selectedCompra.usuario?.nombre || 'N/A'}
                    </span>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 px-6 py-4 sm:flex sm:flex-row-reverse">
                <button
                  type="button"
                  onClick={() => setSelectedCompra(null)}
                  className="w-full inline-flex justify-center rounded-lg border border-transparent shadow-sm px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 text-base font-medium text-white hover:from-blue-600 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm transition-all"
                >
                  Cerrar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Exportación */}
      <ExportModal
        isOpen={exportModalOpen}
        onClose={() => setExportModalOpen(false)}
        title="Compras"
        data={filteredCompras.map(c => ({
          ID: c.id,
          Fecha: c.fecha_compra ? format(new Date(c.fecha_compra), "dd/MM/yyyy HH:mm", { locale: es }) : '—',
          Proveedor: c.proveedor?.nombre || 'N/A',
          Cantidad: c.cantidad,
          Total: `$${c.total.toFixed(2)}`,
          Usuario: c.usuario?.nombre || 'N/A'
        }))}
        filename="compras"
      />
    </div>
  );
};

export default Compras;