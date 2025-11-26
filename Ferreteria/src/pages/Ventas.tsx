import React, { useState, useMemo } from 'react';
import { 
  PlusIcon, 
  EyeIcon, 
  DocumentArrowDownIcon, 
  TrashIcon, 
  ArrowDownTrayIcon,
  MagnifyingGlassIcon,
  CurrencyDollarIcon,
  ShoppingBagIcon,
  ChartBarIcon,
  UserGroupIcon,
} from '@heroicons/react/24/outline';
import { Venta } from '../types';
import VentaModal from '../components/VentaModal';
import ExportModal from '../components/ExportModal';
import toast from 'react-hot-toast';
import { format, startOfMonth, endOfMonth, subMonths } from 'date-fns';
import { es } from 'date-fns/locale';
import { useVentas } from '../hooks/useVentas';

const Ventas: React.FC = () => {
  const { ventas, productos, loading, createVenta, deleteVenta, exportarPDF } = useVentas();
  const [modalOpen, setModalOpen] = useState(false);
  const [exportModalOpen, setExportModalOpen] = useState(false);
  const [selectedVenta, setSelectedVenta] = useState<Venta | null>(null);
  const [ventaToDelete, setVentaToDelete] = useState<Venta | null>(null);
  const [ventaForPDF, setVentaForPDF] = useState<Venta | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<'fecha' | 'total' | 'id'>('fecha');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(10);
  const [dateFilter, setDateFilter] = useState({
    desde: '',
    hasta: '',
  });

  const handleNuevaVenta = async (ventaData: { items: Array<{ producto_id: number; cantidad: number; precio_unitario: number }>; total: number }) => {
    try {
      await createVenta(ventaData);
      setModalOpen(false);
    } catch (error) {
      // Error ya manejado en el hook
    }
  };

  const handleVerDetalle = (venta: Venta) => {
    setSelectedVenta(venta);
  };

  const handleAnularVenta = async () => {
    if (!ventaToDelete) return;

    try {
      await deleteVenta(ventaToDelete);
      setVentaToDelete(null);
    } catch (error) {
      // Error ya manejado en el hook
    }
  };

  const formatCurrency = (value: unknown) => {
    const n = Number(value ?? 0);
    if (Number.isNaN(n)) return '0.00';
    return n.toFixed(2);
  };

  const toggleSort = (column: 'fecha' | 'total' | 'id') => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('desc');
    }
  };

  const filteredVentas = ventas.filter(venta => {
    const ventaDate = venta.fecha ? new Date(venta.fecha) : null;
    
    // Filtro por fecha
    if (dateFilter.desde && ventaDate) {
      const desdeDate = new Date(dateFilter.desde);
      if (ventaDate < desdeDate) return false;
    }
    
    if (dateFilter.hasta && ventaDate) {
      const hastaDate = new Date(dateFilter.hasta);
      if (ventaDate > hastaDate) return false;
    }

    // Filtro por búsqueda (ID, cliente, vendedor, total)
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      const matchesId = venta.id.toString().includes(term);
      const matchesVendedor = venta.usuario?.nombre.toLowerCase().includes(term);
      const matchesCliente = venta.cliente_nombre?.toLowerCase().includes(term);
      const matchesDocumento = venta.cliente_documento?.toLowerCase().includes(term);
      const matchesTotal = venta.total.toString().includes(term);
      
      if (!matchesId && !matchesVendedor && !matchesCliente && !matchesDocumento && !matchesTotal) {
        return false;
      }
    }
    
    return true;
  }).sort((a, b) => {
    let comparison = 0;

    switch (sortBy) {
      case 'id':
        comparison = a.id - b.id;
        break;
      case 'total':
        comparison = a.total - b.total;
        break;
      case 'fecha':
      default:
        const dateA = a.fecha ? new Date(a.fecha).getTime() : 0;
        const dateB = b.fecha ? new Date(b.fecha).getTime() : 0;
        comparison = dateA - dateB;
        break;
    }

    return sortOrder === 'asc' ? comparison : -comparison;
  });

  // Calcular estadísticas basadas en filteredVentas
  const stats = useMemo(() => {
    const totalVentas = filteredVentas.reduce((sum, v) => sum + v.total, 0);
    const numVentas = filteredVentas.length;
    const promedioVenta = numVentas > 0 ? totalVentas / numVentas : 0;
    
    // Comparar con mes anterior
    const now = new Date();
    const mesActualStart = startOfMonth(now);
    const mesActualEnd = endOfMonth(now);
    const mesAnteriorStart = startOfMonth(subMonths(now, 1));
    const mesAnteriorEnd = endOfMonth(subMonths(now, 1));
    
    const ventasMesActual = ventas.filter(v => {
      const fecha = v.fecha ? new Date(v.fecha) : null;
      return fecha && fecha >= mesActualStart && fecha <= mesActualEnd;
    });
    
    const ventasMesAnterior = ventas.filter(v => {
      const fecha = v.fecha ? new Date(v.fecha) : null;
      return fecha && fecha >= mesAnteriorStart && fecha <= mesAnteriorEnd;
    });
    
    const totalMesActual = ventasMesActual.reduce((sum, v) => sum + v.total, 0);
    const totalMesAnterior = ventasMesAnterior.reduce((sum, v) => sum + v.total, 0);
    const cambio = totalMesAnterior > 0 
      ? ((totalMesActual - totalMesAnterior) / totalMesAnterior) * 100 
      : 0;
    
    // Contar clientes únicos (si tienen nombre)
    const clientesUnicos = new Set(
      ventas.filter(v => v.cliente_nombre).map(v => v.cliente_nombre)
    ).size;
    
    return {
      totalVentas,
      numVentas,
      promedioVenta,
      cambio,
      totalMesActual,
      totalMesAnterior,
      clientesUnicos,
    };
  }, [filteredVentas, ventas]);

  // Paginación
  const totalPages = Math.ceil(filteredVentas.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedVentas = filteredVentas.slice(startIndex, endIndex);

  // Resetear página cuando cambien los filtros
  React.useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, dateFilter.desde, dateFilter.hasta]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Ventas</h1>
          <p className="text-gray-600 mt-1">Gestiona las ventas y genera facturas</p>
        </div>
        <div className="flex space-x-3">
          {/* Botón de exportación mejorado */}
          <button
            onClick={() => setExportModalOpen(true)}
            className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50"
          >
            <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
            Exportar
          </button>
          
          <button
            onClick={() => setModalOpen(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            Nueva Venta
          </button>
        </div>
      </div>

      {/* Estadísticas */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white overflow-hidden shadow-lg rounded-xl hover:shadow-xl transition-shadow">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-green-500 rounded-xl p-3">
                <CurrencyDollarIcon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Ventas</dt>
                  <dd className="text-2xl font-bold text-gray-900">
                    ${stats.totalVentas.toFixed(2)}
                  </dd>
                  <dd className="text-xs text-gray-500 mt-1">
                    {stats.numVentas} ventas
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow-lg rounded-xl hover:shadow-xl transition-shadow">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-blue-500 rounded-xl p-3">
                <ShoppingBagIcon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Venta Promedio</dt>
                  <dd className="text-2xl font-bold text-gray-900">
                    ${stats.promedioVenta.toFixed(2)}
                  </dd>
                  <dd className="text-xs text-gray-500 mt-1">
                    Por venta
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
                <UserGroupIcon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Este Mes</dt>
                  <dd className="text-2xl font-bold text-gray-900">
                    ${stats.totalMesActual.toFixed(2)}
                  </dd>
                  <dd className="text-xs text-gray-500 mt-1">
                    {ventas.filter(v => {
                      const fecha = v.fecha ? new Date(v.fecha) : null;
                      return fecha && fecha >= startOfMonth(new Date());
                    }).length} ventas
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

      {/* Filtros por fecha y búsqueda */}
      <div className="bg-white p-6 rounded-xl shadow-lg space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">Buscar</label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                placeholder="Buscar por ID, cliente, vendedor o monto..."
                className="pl-10 block w-full border border-gray-300 rounded-lg shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Desde</label>
            <input
              type="date"
              className="block w-full border border-gray-300 rounded-lg shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              value={dateFilter.desde}
              onChange={(e) => setDateFilter(prev => ({ ...prev, desde: e.target.value }))}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Hasta</label>
            <input
              type="date"
              className="block w-full border border-gray-300 rounded-lg shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              value={dateFilter.hasta}
              onChange={(e) => setDateFilter(prev => ({ ...prev, hasta: e.target.value }))}
            />
          </div>
        </div>
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-600">
            Mostrando <span className="font-semibold text-gray-900">{filteredVentas.length}</span> de{' '}
            <span className="font-semibold text-gray-900">{ventas.length}</span> ventas
          </div>
          {(searchTerm || dateFilter.desde || dateFilter.hasta) && (
            <button
              onClick={() => {
                setDateFilter({ desde: '', hasta: '' });
                setSearchTerm('');
              }}
              className="px-4 py-2 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Limpiar filtros
            </button>
          )}
        </div>
      </div>

      {/* Resumen */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                  <span className="text-white font-bold">$</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total Ventas
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    ${filteredVentas.reduce((sum, venta) => sum + venta.total, 0).toFixed(2)}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                  <span className="text-white font-bold">#</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Número de Ventas
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {filteredVentas.length}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                  <span className="text-white font-bold">Ø</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Venta Promedio
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    ${filteredVentas.length > 0 
                      ? (filteredVentas.reduce((sum, venta) => sum + venta.total, 0) / filteredVentas.length).toFixed(2)
                      : '0.00'
                    }
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Lista de ventas */}
      <div className="bg-white shadow-lg rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gradient-to-r from-gray-50 to-gray-100">
              <tr>
                <th 
                  className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => toggleSort('id')}
                >
                  <div className="flex items-center space-x-1">
                    <span>ID</span>
                    {sortBy === 'id' && (
                      <span>{sortOrder === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </div>
                </th>
                <th 
                  className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => toggleSort('fecha')}
                >
                  <div className="flex items-center space-x-1">
                    <span>Fecha</span>
                    {sortBy === 'fecha' && (
                      <span>{sortOrder === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </div>
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Cliente
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Vendedor
                </th>
                <th 
                  className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => toggleSort('total')}
                >
                  <div className="flex items-center space-x-1">
                    <span>Total</span>
                    {sortBy === 'total' && (
                      <span>{sortOrder === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </div>
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Items
                </th>
                <th className="px-6 py-4 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {paginatedVentas.map((venta) => (
                <tr key={venta.id} className="hover:bg-green-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                    #{venta.id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                    {venta.fecha ? format(new Date(venta.fecha), 'dd/MM/yyyy HH:mm', { locale: es }) : '—'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {venta.cliente_nombre ? (
                      <div>
                        <div className="text-sm font-medium text-gray-900">{venta.cliente_nombre}</div>
                        {venta.cliente_documento && (
                          <div className="text-xs text-gray-500">{venta.cliente_documento}</div>
                        )}
                        {venta.cliente_telefono && (
                          <div className="text-xs text-gray-500">{venta.cliente_telefono}</div>
                        )}
                      </div>
                    ) : (
                      <span className="text-sm text-gray-400 italic">Sin cliente</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                    {venta.usuario?.nombre || 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-green-600">
                    ${formatCurrency(venta.total)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {venta.detalles?.length || 0} productos
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex justify-end space-x-2">
                      <button
                        onClick={() => handleVerDetalle(venta)}
                        className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs leading-4 font-medium rounded-lg text-white bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200 shadow-sm hover:shadow-md"
                        title="Ver detalle"
                      >
                        <EyeIcon className="h-4 w-4 mr-1" />
                        Ver
                      </button>
                      <button
                        onClick={() => setVentaForPDF(venta)}
                        className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs leading-4 font-medium rounded-lg text-white bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-all duration-200 shadow-sm hover:shadow-md"
                        title="Generar PDF"
                      >
                        <DocumentArrowDownIcon className="h-4 w-4 mr-1" />
                        PDF
                      </button>
                      <button
                        onClick={() => setVentaToDelete(venta)}
                        className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs leading-4 font-medium rounded-lg text-white bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-all duration-200 shadow-sm hover:shadow-md"
                        title="Anular venta"
                      >
                        <TrashIcon className="h-4 w-4 mr-1" />
                        Anular
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Paginación */}
        {filteredVentas.length > itemsPerPage && (
          <div className="bg-gray-50 px-4 py-3 flex items-center justify-between border-t border-gray-200">
            <div className="flex-1 flex justify-between sm:hidden">
              <button
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
                className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Anterior
              </button>
              <button
                onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                disabled={currentPage === totalPages}
                className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Siguiente
              </button>
            </div>
            <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-gray-700">
                  Mostrando <span className="font-medium">{startIndex + 1}</span> a{' '}
                  <span className="font-medium">{Math.min(endIndex, filteredVentas.length)}</span> de{' '}
                  <span className="font-medium">{filteredVentas.length}</span> resultados
                </p>
              </div>
              <div>
                <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                  <button
                    onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                    disabled={currentPage === 1}
                    className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    ‹
                  </button>
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    let pageNum;
                    if (totalPages <= 5) {
                      pageNum = i + 1;
                    } else if (currentPage <= 3) {
                      pageNum = i + 1;
                    } else if (currentPage >= totalPages - 2) {
                      pageNum = totalPages - 4 + i;
                    } else {
                      pageNum = currentPage - 2 + i;
                    }
                    
                    return (
                      <button
                        key={pageNum}
                        onClick={() => setCurrentPage(pageNum)}
                        className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                          currentPage === pageNum
                            ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                            : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                        }`}
                      >
                        {pageNum}
                      </button>
                    );
                  })}
                  <button
                    onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                    disabled={currentPage === totalPages}
                    className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    ›
                  </button>
                </nav>
              </div>
            </div>
          </div>
        )}
      </div>

      {filteredVentas.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-500">No se encontraron ventas</div>
        </div>
      )}

      {/* Modal Nueva Venta */}
      <VentaModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onSave={handleNuevaVenta}
        productos={productos}
      />

      {/* Modal Detalle Venta */}
      {selectedVenta && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setSelectedVenta(null)} />
            <span className="hidden sm:inline-block sm:align-middle sm:h-screen">&#8203;</span>
            <div className="inline-block align-bottom bg-white rounded-xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-3xl sm:w-full">
              {/* Header con gradiente */}
              <div className="bg-gradient-to-r from-green-500 to-green-600 px-6 py-5">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-2xl font-bold text-white flex items-center">
                      <ShoppingBagIcon className="h-7 w-7 mr-3" />
                      Venta #{selectedVenta.id}
                    </h3>
                    <p className="text-green-100 text-sm mt-1">
                      {selectedVenta.fecha ? format(new Date(selectedVenta.fecha), "dd 'de' MMMM 'de' yyyy, HH:mm", { locale: es }) : '—'}
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="text-green-100 text-xs font-medium">TOTAL</div>
                    <div className="text-3xl font-bold text-white">${formatCurrency(selectedVenta.total)}</div>
                  </div>
                </div>
              </div>

              <div className="bg-white px-6 py-5">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                  {/* Información del Vendedor */}
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                      <UserGroupIcon className="h-5 w-5 mr-2 text-blue-500" />
                      Vendedor
                    </h4>
                    <div className="space-y-2">
                      <div className="flex items-center">
                        <span className="text-sm text-gray-600">Nombre:</span>
                        <span className="text-sm font-semibold text-gray-900 ml-2">
                          {selectedVenta.usuario?.nombre || 'N/A'}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Información del Cliente */}
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                      <UserGroupIcon className="h-5 w-5 mr-2 text-purple-500" />
                      Cliente
                    </h4>
                    {selectedVenta.cliente_nombre || selectedVenta.cliente_documento ? (
                      <div className="space-y-2">
                        {selectedVenta.cliente_nombre && (
                          <div className="flex items-center">
                            <span className="text-sm text-gray-600">Nombre:</span>
                            <span className="text-sm font-semibold text-gray-900 ml-2">
                              {selectedVenta.cliente_nombre}
                            </span>
                          </div>
                        )}
                        {selectedVenta.cliente_documento && (
                          <div className="flex items-center">
                            <span className="text-sm text-gray-600">Documento:</span>
                            <span className="text-sm font-semibold text-gray-900 ml-2">
                              {selectedVenta.cliente_documento}
                            </span>
                          </div>
                        )}
                        {selectedVenta.cliente_telefono && (
                          <div className="flex items-center">
                            <span className="text-sm text-gray-600">Teléfono:</span>
                            <span className="text-sm font-semibold text-gray-900 ml-2">
                              {selectedVenta.cliente_telefono}
                            </span>
                          </div>
                        )}
                      </div>
                    ) : (
                      <p className="text-sm text-gray-400 italic">Sin información del cliente</p>
                    )}
                  </div>
                </div>

                {/* Productos Vendidos */}
                <div className="border-t border-gray-200 pt-5">
                  <h4 className="text-base font-semibold text-gray-900 mb-4 flex items-center">
                    <ShoppingBagIcon className="h-5 w-5 mr-2 text-green-500" />
                    Productos Vendidos ({selectedVenta.detalles?.length || 0})
                  </h4>
                  
                  <div className="bg-gray-50 rounded-lg overflow-hidden">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-100">
                        <tr>
                          <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                            Producto
                          </th>
                          <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">
                            Cantidad
                          </th>
                          <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">
                            Precio Unit.
                          </th>
                          <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">
                            Subtotal
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {selectedVenta.detalles?.map((detalle) => (
                          <tr key={detalle.id} className="hover:bg-gray-50">
                            <td className="px-4 py-3 text-sm font-medium text-gray-900">
                              {detalle.producto?.nombre || `Producto ID: ${detalle.producto_id}`}
                            </td>
                            <td className="px-4 py-3 text-center">
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                {detalle.cantidad}
                              </span>
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-700 text-right">
                              ${formatCurrency(detalle.precio_unitario)}
                            </td>
                            <td className="px-4 py-3 text-sm font-semibold text-gray-900 text-right">
                              ${formatCurrency(detalle.subtotal)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                      <tfoot className="bg-gray-50">
                        <tr>
                          <td colSpan={3} className="px-4 py-4 text-sm font-bold text-gray-900 text-right">
                            TOTAL:
                          </td>
                          <td className="px-4 py-4 text-base font-bold text-green-600 text-right">
                            ${formatCurrency(selectedVenta.total)}
                          </td>
                        </tr>
                      </tfoot>
                    </table>
                  </div>
                </div>
              </div>

              {/* Footer con botones */}
              <div className="bg-gray-50 px-6 py-4 sm:flex sm:flex-row-reverse gap-3">
                <button
                  type="button"
                  onClick={() => setSelectedVenta(null)}
                  className="w-full sm:w-auto inline-flex justify-center rounded-lg border border-transparent shadow-sm px-6 py-2.5 bg-gradient-to-r from-green-500 to-green-600 text-base font-medium text-white hover:from-green-600 hover:to-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-all"
                >
                  Cerrar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal Confirmación Anular Venta */}
      {ventaToDelete && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setVentaToDelete(null)} />
            <span className="hidden sm:inline-block sm:align-middle sm:h-screen">&#8203;</span>
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="sm:flex sm:items-start">
                  <div className="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">
                    <TrashIcon className="h-6 w-6 text-red-600" />
                  </div>
                  <div className="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">
                      Anular Venta #{ventaToDelete.id}
                    </h3>
                    <div className="mt-2">
                      <p className="text-sm text-gray-500">
                        ¿Está seguro que desea anular esta venta? Esta acción:
                      </p>
                      <ul className="mt-2 text-sm text-gray-500 list-disc list-inside space-y-1">
                        <li>Restaurará el stock de todos los productos</li>
                        <li>Eliminará permanentemente el registro de la venta</li>
                        <li>Se registrará en auditoría</li>
                      </ul>
                      <div className="mt-3 p-3 bg-gray-50 rounded-md">
                        <p className="text-sm font-medium text-gray-900">
                          Total de la venta: ${formatCurrency(ventaToDelete.total)}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          {ventaToDelete.detalles?.length || 0} productos
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <button
                  type="button"
                  className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:ml-3 sm:w-auto sm:text-sm"
                  onClick={handleAnularVenta}
                >
                  Sí, anular venta
                </button>
                <button
                  type="button"
                  className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
                  onClick={() => setVentaToDelete(null)}
                >
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal Vista Previa PDF */}
      {ventaForPDF && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setVentaForPDF(null)} />
            <span className="hidden sm:inline-block sm:align-middle sm:h-screen">&#8203;</span>
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg leading-6 font-medium text-gray-900">
                    Vista Previa - Factura #{ventaForPDF.id}
                  </h3>
                  <button
                    onClick={() => setVentaForPDF(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <span className="text-2xl">&times;</span>
                  </button>
                </div>

                {/* Preview del contenido del PDF */}
                <div className="border border-gray-200 rounded-lg p-6 bg-gray-50 space-y-4">
                  {/* Header */}
                  <div className="text-center border-b border-gray-300 pb-4">
                    <h2 className="text-2xl font-bold text-gray-900">FACTURA DE VENTA</h2>
                    <p className="text-sm text-gray-600 mt-1">Sistema de Inventario Ferretería</p>
                  </div>

                  {/* Información */}
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="font-medium text-gray-700">Factura No:</span>
                      <span className="text-gray-900">{ventaForPDF.id}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium text-gray-700">Fecha:</span>
                      <span className="text-gray-900">
                        {ventaForPDF.fecha ? format(new Date(ventaForPDF.fecha), 'dd/MM/yyyy HH:mm', { locale: es }) : '—'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium text-gray-700">Vendedor:</span>
                      <span className="text-gray-900">{ventaForPDF.usuario?.nombre || 'N/A'}</span>
                    </div>
                  </div>

                  {/* Tabla de productos */}
                  <div className="border-t border-gray-300 pt-4">
                    <table className="min-w-full text-sm">
                      <thead className="bg-gray-100">
                        <tr>
                          <th className="px-3 py-2 text-left font-medium text-gray-700">Producto</th>
                          <th className="px-3 py-2 text-center font-medium text-gray-700">Cant.</th>
                          <th className="px-3 py-2 text-right font-medium text-gray-700">P. Unit.</th>
                          <th className="px-3 py-2 text-right font-medium text-gray-700">Subtotal</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {ventaForPDF.detalles?.map((detalle, idx) => (
                          <tr key={idx}>
                            <td className="px-3 py-2 text-gray-900">
                              {detalle.producto?.nombre || `Producto ID: ${detalle.producto_id}`}
                            </td>
                            <td className="px-3 py-2 text-center text-gray-900">{detalle.cantidad}</td>
                            <td className="px-3 py-2 text-right text-gray-900">
                              ${formatCurrency(detalle.precio_unitario)}
                            </td>
                            <td className="px-3 py-2 text-right font-medium text-gray-900">
                              ${formatCurrency(detalle.subtotal)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* Total */}
                  <div className="border-t-2 border-gray-400 pt-4">
                    <div className="flex justify-end">
                      <div className="text-right">
                        <p className="text-lg font-bold text-gray-900">
                          TOTAL: ${formatCurrency(ventaForPDF.total)}
                        </p>
                      </div>
                    </div>
                  </div>

                  <p className="text-center text-sm italic text-gray-500 mt-4">
                    Gracias por su compra
                  </p>
                </div>

                {/* Botones de acción */}
                <div className="mt-6 flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => setVentaForPDF(null)}
                    className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                  >
                    Cerrar
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      exportarPDF(ventaForPDF);
                      setVentaForPDF(null);
                    }}
                    className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
                  >
                    Descargar PDF
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      exportarPDF(ventaForPDF);
                      toast.success('Abriendo en nueva pestaña para imprimir...');
                      setVentaForPDF(null);
                    }}
                    className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700"
                  >
                    Imprimir
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Exportación */}
      <ExportModal
        isOpen={exportModalOpen}
        onClose={() => setExportModalOpen(false)}
        title="Ventas"
        data={filteredVentas.map(v => ({
          ID: v.id,
          Fecha: v.fecha ? format(new Date(v.fecha), "dd/MM/yyyy HH:mm", { locale: es }) : '—',
          Cliente: v.cliente_nombre || 'Cliente General',
          Total: `$${v.total.toFixed(2)}`
        }))}
        filename="ventas"
      />
    </div>
  );
};

export default Ventas;