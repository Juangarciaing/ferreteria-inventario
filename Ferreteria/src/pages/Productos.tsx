import React, { useState, useMemo, useEffect } from 'react';
import { 
  PlusIcon, 
  PencilIcon, 
  TrashIcon, 
  Squares2X2Icon,
  TableCellsIcon,
  ArrowDownTrayIcon,
  CubeIcon,
  CurrencyDollarIcon,
  ExclamationTriangleIcon,
  ChartBarIcon,
  PlusCircleIcon,
  MinusCircleIcon,
} from '@heroicons/react/24/outline';
import { Producto } from '../types';
import ProductoModal from '../components/ProductoModal';
import ExportModal from '../components/ExportModal';
import SearchBar from '../components/SearchBar';
import FilterPanel, { FilterConfig } from '../components/FilterPanel';
import Pagination from '../components/Pagination';
import { useProductos } from '../hooks/useProductos';
import { useCategorias } from '../hooks/useCategorias';
import { useAuth } from '../contexts/AuthContext';
import { formatPrice, getStockStatus, getStockStatusColor } from '../utils/formatters';

type ViewMode = 'table' | 'grid';
type SortField = 'nombre' | 'precio' | 'stock' | 'categoria';
type SortOrder = 'asc' | 'desc';

const Productos: React.FC = () => {
  // Helper para obtener etiqueta de estado de stock
  const getStockStatusLabel = (status: string): string => {
    switch (status) {
      case 'bajo': return '⚠️ Stock Bajo';
      case 'medio': return '📊 Stock Medio';
      case 'alto': return '✅ Stock Alto';
      default: return '❌ Sin Stock';
    }
  };

  // Helper para obtener emoji de estado de stock
  const getStockStatusEmoji = (status: string): string => {
    switch (status) {
      case 'bajo': return '⚠️';
      case 'medio': return '📊';
      case 'alto': return '✅';
      default: return '❌';
    }
  };

  // Helper para obtener estado de producto para exportación
  const getProductoEstado = (producto: Producto): string => {
    if (producto.stock === 0) return 'Agotado';
    if (producto.stock <= producto.stock_minimo) return 'Stock Bajo';
    return 'Normal';
  };

  const { productos, loading: loadingProductos, createProducto, updateProducto, deleteProducto } = useProductos();
  const { categorias, loading: loadingCategorias } = useCategorias();
  const { isAdmin } = useAuth();
  
  const loading = loadingProductos || loadingCategorias;
  const [modalOpen, setModalOpen] = useState(false);
  const [editingProducto, setEditingProducto] = useState<Producto | null>(null);
  const [exportModalOpen, setExportModalOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState<ViewMode>('table');
  const [sortField, setSortField] = useState<SortField>('nombre');
  const [sortOrder, setSortOrder] = useState<SortOrder>('asc');
  
  // Estados para FilterPanel
  const [filterPanelOpen, setFilterPanelOpen] = useState(false);
  const [filterValues, setFilterValues] = useState<Record<string, any>>({
    categorias: [],
    precioRange: [0, 1000],
    stockStatus: '',
  });

  // Estados para Paginación
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(20);

  // Calcular estadísticas del inventario
  const stats = useMemo(() => {
    const total = productos.length;
    const valorTotal = productos.reduce((sum, p) => sum + (p.precio * p.stock), 0);
    const stockBajo = productos.filter(p => p.stock <= p.stock_minimo && p.stock > 0).length;
    const sinStock = productos.filter(p => p.stock === 0).length;
    
    return {
      total,
      valorTotal,
      stockBajo,
      sinStock,
    };
  }, [productos]);

  // Configuración de filtros para FilterPanel
  const filterConfigs: FilterConfig[] = useMemo(() => [
    {
      name: 'categorias',
      label: 'Categorías',
      type: 'multiselect',
      options: categorias.map(cat => ({
        value: cat.id,
        label: cat.nombre
      }))
    },
    {
      name: 'precioRange',
      label: 'Rango de Precio',
      type: 'range',
      min: 0,
      max: Math.max(...productos.map(p => p.precio), 1000),
      step: 10
    },
    {
      name: 'stockStatus',
      label: 'Estado del Stock',
      type: 'select',
      placeholder: 'Todos los estados',
      options: [
        { value: 'sin', label: 'Sin Stock (0)' },
        { value: 'bajo', label: 'Stock Bajo' },
        { value: 'normal', label: 'Stock Normal' },
        { value: 'alto', label: 'Stock Alto' },
      ]
    },
  ], [categorias, productos]);

  // Manejadores de filtros
  const handleFilterChange = (name: string, value: unknown) => {
    setFilterValues(prev => ({ ...prev, [name]: value }));
  };

  const handleResetFilters = () => {
    setFilterValues({
      categorias: [],
      precioRange: [0, 1000],
      stockStatus: '',
    });
    setFilterPanelOpen(false);
  };

  const handleApplyFilters = () => {
    setFilterPanelOpen(false);
  };

  // Contar filtros activos
  const activeFiltersCount = useMemo(() => {
    let count = 0;
    if (filterValues.categorias && filterValues.categorias.length > 0) count++;
    if (filterValues.precioRange && (filterValues.precioRange[0] > 0 || filterValues.precioRange[1] < 1000)) count++;
    if (filterValues.stockStatus) count++;
    return count;
  }, [filterValues]);

  // Función de ordenamiento
  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('asc');
    }
  };

  const handleEditProducto = (producto: Producto) => {
    setEditingProducto(producto);
    setModalOpen(true);
  };

  const handleSaveProducto = async (productoData: Partial<Producto>) => {
    console.log('🔥 Guardando producto:', productoData);
    try {
      // Validar que los campos requeridos estén presentes
      if (!productoData.nombre || !productoData.categoria_id || productoData.precio === undefined || productoData.stock === undefined || productoData.stock_minimo === undefined) {
        console.error('❌ Faltan campos requeridos');
        return;
      }

      const productoCompleto = {
        nombre: productoData.nombre,
        categoria_id: productoData.categoria_id,
        precio: productoData.precio,
        stock: productoData.stock,
        stock_minimo: productoData.stock_minimo,
        descripcion: productoData.descripcion || ''
      };

      console.log('🔥 Producto completo a guardar:', productoCompleto);

      if (editingProducto) {
        console.log('🔥 Actualizando producto existente');
        await updateProducto(editingProducto.id, productoCompleto);
      } else {
        console.log('🔥 Creando nuevo producto');
        await createProducto(productoCompleto);
      }
      console.log('✅ Producto guardado exitosamente');
      setModalOpen(false);
      setEditingProducto(null);
    } catch (error) {
      console.error('❌ Error al guardar producto:', error);
    }
  };

  const handleDeleteProducto = async (id: number) => {
    if (globalThis.confirm('¿Está seguro de que desea eliminar este producto?')) {
      try {
        await deleteProducto(id);
      } catch (error) {
        console.error('Error al eliminar producto:', error);
      }
    }
  };

  const filteredProductos = useMemo(() => {
    let filtered = [...productos];
    
    // Filtro de búsqueda
    if (searchTerm) {
      filtered = filtered.filter(producto =>
        producto.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
        producto.descripcion?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    // Filtro de categorías (multiselect)
    if (filterValues.categorias && filterValues.categorias.length > 0) {
      filtered = filtered.filter(producto => 
        filterValues.categorias.includes(producto.categoria_id.toString())
      );
    }
    
    // Filtro de rango de precio
    if (filterValues.precioRange) {
      const [min, max] = filterValues.precioRange;
      filtered = filtered.filter(producto => 
        producto.precio >= min && producto.precio <= max
      );
    }
    
    // Filtro de estado del stock
    if (filterValues.stockStatus) {
      filtered = filtered.filter(producto => {
        const status = getStockStatus(producto.stock, producto.stock_minimo);
        if (filterValues.stockStatus === 'sin') return producto.stock === 0;
        return status === filterValues.stockStatus;
      });
    }
    
    // Ordenamiento
    filtered.sort((a, b) => {
      let aValue: any;
      let bValue: any;
      
      switch (sortField) {
        case 'nombre':
          aValue = a.nombre.toLowerCase();
          bValue = b.nombre.toLowerCase();
          break;
        case 'precio':
          aValue = a.precio;
          bValue = b.precio;
          break;
        case 'stock':
          aValue = a.stock;
          bValue = b.stock;
          break;
        case 'categoria':
          aValue = a.categoria?.nombre?.toLowerCase() || '';
          bValue = b.categoria?.nombre?.toLowerCase() || '';
          break;
        default:
          return 0;
      }
      
      if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });
    
    return filtered;
  }, [productos, searchTerm, filterValues, sortField, sortOrder]);

  // Paginación: calcular productos para la página actual
  const paginatedProductos = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return filteredProductos.slice(startIndex, endIndex);
  }, [filteredProductos, currentPage, itemsPerPage]);

  const totalPages = Math.ceil(filteredProductos.length / itemsPerPage);

  // Resetear a página 1 cuando cambian los filtros
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, filterValues]);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleItemsPerPageChange = (newItemsPerPage: number) => {
    setItemsPerPage(newItemsPerPage);
    setCurrentPage(1);
  };

  // Ajuste rápido de stock
  const handleQuickStockAdjust = async (producto: Producto, delta: number) => {
    const newStock = Math.max(0, producto.stock + delta);
    console.log(`📊 Ajuste rápido de stock - Producto ${producto.id}: ${producto.stock} → ${newStock}`);
    
    try {
      await updateProducto(producto.id, { stock: newStock });
      console.log('✅ Stock ajustado exitosamente');
    } catch (error) {
      console.error('❌ Error al ajustar stock:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 text-lg">Cargando productos...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="sm:flex sm:items-center sm:justify-between">
        <div className="sm:flex-auto">
          <h1 className="text-3xl font-bold text-gray-900">Inventario de Productos</h1>
          <p className="mt-2 text-sm text-gray-700">
            Gestiona el inventario completo de productos de la ferretería
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex items-center space-x-3">
          {/* Toggle Vista */}
          <div className="inline-flex rounded-lg border border-gray-200 bg-white p-1">
            <button
              onClick={() => setViewMode('table')}
              className={`inline-flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                viewMode === 'table'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <TableCellsIcon className="h-4 w-4 mr-2" />
              Tabla
            </button>
            <button
              onClick={() => setViewMode('grid')}
              className={`inline-flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                viewMode === 'grid'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <Squares2X2Icon className="h-4 w-4 mr-2" />
              Tarjetas
            </button>
          </div>
          
          {/* Exportar - Modal mejorado */}
          <button
            onClick={() => setExportModalOpen(true)}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
            Exportar
          </button>
          
          {/* Agregar Producto */}
          <button
            type="button"
            onClick={() => {
              setEditingProducto(null);
              setModalOpen(true);
            }}
            className="inline-flex items-center justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Agregar Producto
          </button>
        </div>
      </div>

      {/* Estadísticas */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white overflow-hidden shadow-lg rounded-xl hover:shadow-xl transition-shadow">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-blue-500 rounded-xl p-3">
                <CubeIcon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Productos</dt>
                  <dd className="text-2xl font-bold text-gray-900">{stats.total}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
        
        <div className="bg-white overflow-hidden shadow-lg rounded-xl hover:shadow-xl transition-shadow">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-green-500 rounded-xl p-3">
                <CurrencyDollarIcon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Valor Inventario</dt>
                  <dd className="text-2xl font-bold text-gray-900">{formatPrice(stats.valorTotal)}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
        
        <div className="bg-white overflow-hidden shadow-lg rounded-xl hover:shadow-xl transition-shadow">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-orange-500 rounded-xl p-3">
                <ExclamationTriangleIcon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Stock Bajo</dt>
                  <dd className="text-2xl font-bold text-gray-900">{stats.stockBajo}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
        
        <div className="bg-white overflow-hidden shadow-lg rounded-xl hover:shadow-xl transition-shadow">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-red-500 rounded-xl p-3">
                <ChartBarIcon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Sin Stock</dt>
                  <dd className="text-2xl font-bold text-gray-900">{stats.sinStock}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Barra de Búsqueda y Filtros */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
          {/* Barra de Búsqueda */}
          <div className="flex-1 max-w-2xl">
            <SearchBar
              value={searchTerm}
              onChange={setSearchTerm}
              placeholder="Buscar productos por nombre o descripción..."
              autoFocus
            />
          </div>

          {/* Panel de Filtros */}
          <FilterPanel
            filters={filterConfigs}
            values={filterValues}
            onChange={handleFilterChange}
            onReset={handleResetFilters}
            onApply={handleApplyFilters}
            isOpen={filterPanelOpen}
            onToggle={() => setFilterPanelOpen(!filterPanelOpen)}
            activeFiltersCount={activeFiltersCount}
          />
        </div>

        {/* Info de resultados */}
        <div className="mt-4 flex items-center justify-between border-t border-gray-200 pt-4">
          <p className="text-sm text-gray-700">
            Mostrando <span className="font-medium">{filteredProductos.length}</span> de{' '}
            <span className="font-medium">{productos.length}</span> productos
            {activeFiltersCount > 0 && (
              <span className="ml-2 text-blue-600">
                (con {activeFiltersCount} {activeFiltersCount === 1 ? 'filtro activo' : 'filtros activos'})
              </span>
            )}
          </p>
          {(searchTerm || activeFiltersCount > 0) && (
            <button
              onClick={() => {
                setSearchTerm('');
                handleResetFilters();
              }}
              className="text-sm text-blue-600 hover:text-blue-800 font-medium transition-colors"
            >
              Limpiar todo
            </button>
          )}
        </div>
      </div>

      {/* Tabla */}
      {viewMode === 'table' ? (
        <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
          <table className="min-w-full divide-y divide-gray-300">
            <thead className="bg-gray-50">
              <tr>
                <th 
                  onClick={() => handleSort('nombre')}
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide cursor-pointer hover:bg-gray-100"
                >
                  <div className="flex items-center">
                    Producto
                    {sortField === 'nombre' && (
                      <span className="ml-2">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </div>
                </th>
                <th 
                  onClick={() => handleSort('categoria')}
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide cursor-pointer hover:bg-gray-100"
                >
                  <div className="flex items-center">
                    Categoría
                    {sortField === 'categoria' && (
                      <span className="ml-2">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </div>
                </th>
                <th 
                  onClick={() => handleSort('precio')}
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide cursor-pointer hover:bg-gray-100"
                >
                  <div className="flex items-center">
                    Precio
                    {sortField === 'precio' && (
                      <span className="ml-2">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </div>
                </th>
                <th 
                  onClick={() => handleSort('stock')}
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide cursor-pointer hover:bg-gray-100"
                >
                  <div className="flex items-center">
                    Stock
                    {sortField === 'stock' && (
                      <span className="ml-2">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </div>
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                  Estado
                </th>
                <th className="relative px-6 py-3">
                  <span className="sr-only">Acciones</span>
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {paginatedProductos.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-sm text-gray-500">
                    {filteredProductos.length === 0 
                      ? 'No se encontraron productos que coincidan con los filtros'
                      : 'No hay productos en esta página'}
                  </td>
                </tr>
              ) : (
                paginatedProductos.map((producto) => {
                  const stockStatus = getStockStatus(producto.stock, producto.stock_minimo);
                  const statusColor = getStockStatusColor(stockStatus);
                  
                  return (
                    <tr key={producto.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {producto.nombre}
                          </div>
                          {producto.descripcion && (
                            <div className="text-xs text-gray-500 mt-1">
                              {producto.descripcion}
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                          {producto.categoria?.nombre}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                        {formatPrice(producto.precio)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => handleQuickStockAdjust(producto, -1)}
                            className="text-red-600 hover:text-red-800 hover:bg-red-50 rounded p-1"
                            title="Disminuir stock"
                          >
                            <MinusCircleIcon className="h-5 w-5" />
                          </button>
                          <span className="text-sm font-medium text-gray-900 min-w-[60px] text-center">
                            {producto.stock} uds
                          </span>
                          <button
                            onClick={() => handleQuickStockAdjust(producto, 1)}
                            className="text-green-600 hover:text-green-800 hover:bg-green-50 rounded p-1"
                            title="Aumentar stock"
                          >
                            <PlusCircleIcon className="h-5 w-5" />
                          </button>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2.5 py-1 text-xs font-semibold rounded-full ${statusColor}`}>
                          {getStockStatusLabel(stockStatus)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex items-center justify-end space-x-2">
                          <button
                            onClick={() => handleEditProducto(producto)}
                            className="text-blue-600 hover:text-blue-900 hover:bg-blue-50 rounded p-2"
                            title="Editar"
                          >
                            <PencilIcon className="h-5 w-5" />
                          </button>
                          {isAdmin && (
                            <button
                              onClick={() => handleDeleteProducto(producto.id)}
                              className="text-red-600 hover:text-red-900 hover:bg-red-50 rounded p-2"
                              title="Eliminar"
                            >
                              <TrashIcon className="h-5 w-5" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      ) : (
        /* Vista de Tarjetas */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {paginatedProductos.length === 0 ? (
            <div className="col-span-full text-center py-12 text-gray-500">
              {filteredProductos.length === 0 
                ? 'No se encontraron productos que coincidan con los filtros'
                : 'No hay productos en esta página'}
            </div>
          ) : (
            paginatedProductos.map((producto) => {
              const stockStatus = getStockStatus(producto.stock, producto.stock_minimo);
              const statusColor = getStockStatusColor(stockStatus);
              
              return (
                <div
                  key={producto.id}
                  className="bg-white rounded-xl shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 overflow-hidden"
                >
                  <div className="p-6">
                    {/* Header */}
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <h3 className="text-lg font-bold text-gray-900 mb-1">
                          {producto.nombre}
                        </h3>
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
                          {producto.categoria?.nombre}
                        </span>
                      </div>
                      <span className={`inline-flex px-2.5 py-1 text-xs font-semibold rounded-full ${statusColor}`}>
                        {getStockStatusEmoji(stockStatus)}
                      </span>
                    </div>

                    {/* Descripción */}
                    {producto.descripcion && (
                      <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                        {producto.descripcion}
                      </p>
                    )}

                    {/* Precio */}
                    <div className="mb-4">
                      <p className="text-2xl font-bold text-gray-900">
                        {formatPrice(producto.precio)}
                      </p>
                    </div>

                    {/* Stock */}
                    <div className="flex items-center justify-between mb-4 p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => handleQuickStockAdjust(producto, -1)}
                          className="text-red-600 hover:text-red-800 hover:bg-red-100 rounded p-1.5"
                        >
                          <MinusCircleIcon className="h-6 w-6" />
                        </button>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-gray-900">{producto.stock}</p>
                          <p className="text-xs text-gray-500">unidades</p>
                        </div>
                        <button
                          onClick={() => handleQuickStockAdjust(producto, 1)}
                          className="text-green-600 hover:text-green-800 hover:bg-green-100 rounded p-1.5"
                        >
                          <PlusCircleIcon className="h-6 w-6" />
                        </button>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-gray-500">Mínimo</p>
                        <p className="text-sm font-medium text-gray-700">{producto.stock_minimo}</p>
                      </div>
                    </div>

                    {/* Acciones */}
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleEditProducto(producto)}
                        className="flex-1 inline-flex items-center justify-center px-4 py-2 border border-blue-600 rounded-lg text-sm font-medium text-blue-600 bg-white hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                      >
                        <PencilIcon className="h-4 w-4 mr-2" />
                        Editar
                      </button>
                      {isAdmin && (
                        <button
                          onClick={() => handleDeleteProducto(producto.id)}
                          className="px-4 py-2 border border-red-600 rounded-lg text-sm font-medium text-red-600 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                        >
                          <TrashIcon className="h-5 w-5" />
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      )}

      {/* Paginación */}
      {filteredProductos.length > 0 && (
        <div className="bg-white rounded-lg shadow mt-6">
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            totalItems={filteredProductos.length}
            itemsPerPage={itemsPerPage}
            onPageChange={handlePageChange}
            onItemsPerPageChange={handleItemsPerPageChange}
            showItemsPerPage={true}
            itemsPerPageOptions={[10, 20, 50, 100]}
          />
        </div>
      )}

      {/* Modal */}
      <ProductoModal
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setEditingProducto(null);
        }}
        onSave={handleSaveProducto}
        producto={editingProducto}
        categorias={categorias}
      />

      {/* Modal de Exportación */}
      <ExportModal
        isOpen={exportModalOpen}
        onClose={() => setExportModalOpen(false)}
        title="Productos"
        data={filteredProductos.map(p => ({
          Código: p.id,
          Nombre: p.nombre,
          Categoría: p.categoria?.nombre || 'Sin categoría',
          Precio: `$${p.precio.toFixed(2)}`,
          Stock: p.stock,
          'Stock Mínimo': p.stock_minimo,
          Estado: getProductoEstado(p)
        }))}
        filename="productos"
      />
    </div>
  );
};

export default Productos;