import React, { useState, useMemo } from 'react';
import { 
  PlusIcon, 
  PencilIcon, 
  TrashIcon,
  TagIcon,
  CubeIcon,
  ArchiveBoxXMarkIcon
} from '@heroicons/react/24/outline';
import { Categoria } from '../types';
import CategoriaModal from '../components/CategoriaModal';
import ExportModal from '../components/ExportModal';
import toast from 'react-hot-toast';
import { useCategorias } from '../hooks/useCategorias';
import { useProductos } from '../hooks/useProductos';
import { useAuth } from '../contexts/AuthContext';

const Categorias: React.FC = () => {
  const { categorias, loading, createCategoria, updateCategoria, deleteCategoria } = useCategorias();
  const { productos } = useProductos();
  const { isAdmin } = useAuth();
  const [modalOpen, setModalOpen] = useState(false);
  const [exportModalOpen, setExportModalOpen] = useState(false);
  const [editingCategoria, setEditingCategoria] = useState<Categoria | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  // Calcular estadísticas
  const stats = useMemo(() => {
    const totalCategorias = categorias.length;
    
    // Contar productos por categoría
    const productosPorCategoria = new Map<number, number>();
    productos.forEach(producto => {
      const count = productosPorCategoria.get(producto.categoria_id) || 0;
      productosPorCategoria.set(producto.categoria_id, count + 1);
    });
    
    const categoriasConProductos = Array.from(productosPorCategoria.entries())
      .filter(([_, count]) => count > 0).length;
    
    const categoriasSinProductos = totalCategorias - categoriasConProductos;
    
    return {
      totalCategorias,
      categoriasConProductos,
      categoriasSinProductos,
      productosPorCategoria
    };
  }, [categorias, productos]);

  // Filtrar categorías
  const filteredCategorias = useMemo(() => {
    return categorias.filter(categoria =>
      categoria.nombre.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [categorias, searchTerm]);

  // Handlers
  const handleSaveCategoria = async (categoriaData: { nombre: string }) => {
    try {
      if (editingCategoria) {
        await updateCategoria(editingCategoria.id, categoriaData);
      } else {
        await createCategoria(categoriaData);
      }
      setModalOpen(false);
      setEditingCategoria(null);
    } catch (error) {
      console.error('Error al guardar categoría:', error);
    }
  };

  const handleEditCategoria = (categoria: Categoria) => {
    setEditingCategoria(categoria);
    setModalOpen(true);
  };

  const handleDeleteCategoria = async (id: number) => {
    const productosAsociados = stats.productosPorCategoria.get(id) || 0;
    
    if (productosAsociados > 0) {
      toast.error(`No se puede eliminar. Hay ${productosAsociados} producto(s) asociado(s) a esta categoría.`);
      return;
    }
    
    if (window.confirm('¿Está seguro de que desea eliminar esta categoría?')) {
      try {
        await deleteCategoria(id);
      } catch (error) {
        console.error('Error al eliminar categoría:', error);
      }
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Categorías</h1>
          <p className="mt-1 text-sm text-gray-500">Organiza tus productos por categorías</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setExportModalOpen(true)}
            className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-lg shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <ArchiveBoxXMarkIcon className="h-5 w-5 mr-2" />
            Exportar
          </button>
          <button
            onClick={() => {
              setEditingCategoria(null);
              setModalOpen(true);
            }}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg shadow-lg text-white bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all duration-200"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Nueva Categoría
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Total Categorías */}
        <div className="bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-indigo-100 text-sm font-medium">Total Categorías</p>
              <p className="text-3xl font-bold mt-2">{stats.totalCategorias}</p>
            </div>
            <TagIcon className="h-12 w-12 text-indigo-200 opacity-80" />
          </div>
        </div>

        {/* Categorías con Productos */}
        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm font-medium">Con Productos</p>
              <p className="text-3xl font-bold mt-2">{stats.categoriasConProductos}</p>
              <p className="text-green-100 text-xs mt-1">
                {stats.totalCategorias > 0 
                  ? ((stats.categoriasConProductos / stats.totalCategorias) * 100).toFixed(0) 
                  : 0}% del total
              </p>
            </div>
            <CubeIcon className="h-12 w-12 text-green-200 opacity-80" />
          </div>
        </div>

        {/* Categorías Vacías */}
        <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-100 text-sm font-medium">Sin Productos</p>
              <p className="text-3xl font-bold mt-2">{stats.categoriasSinProductos}</p>
              <p className="text-orange-100 text-xs mt-1">
                Categorías vacías
              </p>
            </div>
            <ArchiveBoxXMarkIcon className="h-12 w-12 text-orange-200 opacity-80" />
          </div>
        </div>
      </div>

      {/* Búsqueda */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="max-w-md">
          <input
            type="text"
            placeholder="Buscar categorías..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="block w-full px-4 py-2 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>
        <div className="mt-3">
          <p className="text-sm text-gray-600">
            Mostrando <span className="font-bold text-indigo-600">{filteredCategorias.length}</span> de {categorias.length} categorías
          </p>
        </div>
      </div>

      {/* Grid de categorías */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {filteredCategorias.map((categoria) => {
          const numProductos = stats.productosPorCategoria.get(categoria.id) || 0;
          return (
            <div 
              key={categoria.id} 
              className="bg-white overflow-hidden shadow-lg rounded-xl hover:shadow-xl transition-all duration-200 border border-gray-100"
            >
              <div className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-bold text-gray-900 truncate mb-2">
                      {categoria.nombre}
                    </h3>
                    
                    {/* Badge de productos */}
                    <div className="flex items-center gap-2 mb-3">
                      <span className={`inline-flex items-center px-3 py-1 rounded-lg text-sm font-medium ${
                        numProductos > 0 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-gray-100 text-gray-600'
                      }`}>
                        <CubeIcon className="h-4 w-4 mr-1" />
                        {numProductos} {numProductos === 1 ? 'producto' : 'productos'}
                      </span>
                    </div>

                    {categoria.created_at && (
                      <p className="text-xs text-gray-500">
                        Creada: {new Date(categoria.created_at).toLocaleDateString('es', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric'
                        })}
                      </p>
                    )}
                  </div>
                </div>

                {/* Botones de acción */}
                <div className="mt-4 flex gap-2">
                  <button
                    onClick={() => handleEditCategoria(categoria)}
                    className="flex-1 inline-flex items-center justify-center px-3 py-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white text-sm font-medium rounded-lg hover:from-blue-600 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
                  >
                    <PencilIcon className="h-4 w-4 mr-1" />
                    Editar
                  </button>
                  {isAdmin && (
                    <button
                      onClick={() => handleDeleteCategoria(categoria.id)}
                      className={`flex-1 inline-flex items-center justify-center px-3 py-2 text-sm font-medium rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 transition-all duration-200 ${
                        numProductos > 0
                          ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                          : 'bg-gradient-to-r from-red-500 to-red-600 text-white hover:from-red-600 hover:to-red-700 focus:ring-red-500'
                      }`}
                      disabled={numProductos > 0}
                      title={numProductos > 0 ? 'No se puede eliminar categorías con productos' : 'Eliminar categoría'}
                    >
                      <TrashIcon className="h-4 w-4 mr-1" />
                      Eliminar
                    </button>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Mensaje cuando no hay categorías */}
      {filteredCategorias.length === 0 && (
        <div className="bg-white rounded-xl shadow-lg py-12">
          <div className="text-center">
            <TagIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">
              {searchTerm ? 'No se encontraron categorías' : 'No hay categorías registradas'}
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              {searchTerm 
                ? 'Intenta ajustar tu búsqueda' 
                : 'Comienza creando tu primera categoría para organizar tus productos'}
            </p>
            {!searchTerm && (
              <div className="mt-6">
                <button
                  onClick={() => {
                    setEditingCategoria(null);
                    setModalOpen(true);
                  }}
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-lg text-white bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  <PlusIcon className="h-5 w-5 mr-2" />
                  Crear Primera Categoría
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Modal */}
      <CategoriaModal
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setEditingCategoria(null);
        }}
        onSave={handleSaveCategoria}
        categoria={editingCategoria}
      />

      {/* Modal de Exportación */}
      <ExportModal
        isOpen={exportModalOpen}
        onClose={() => setExportModalOpen(false)}
        title="Categorías"
        data={filteredCategorias.map(c => {
          const productoCount = productos.filter(p => p.categoria_id === c.id).length;
          return {
            ID: c.id,
            Nombre: c.nombre,
            Descripción: c.descripcion || 'N/A',
            'Productos': productoCount
          };
        })}
        filename="categorias"
      />
    </div>
  );
};

export default Categorias;