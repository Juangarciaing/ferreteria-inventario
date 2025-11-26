import React, { useState, useEffect } from 'react';
import { ExclamationTriangleIcon, ShoppingCartIcon, EyeIcon } from '@heroicons/react/24/outline';
import { Producto } from '../types';
import { apiClient } from '../lib/api';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';

const AlertasStock: React.FC = () => {
  const [productosStockBajo, setProductosStockBajo] = useState<Producto[]>([]);
  const [productosAgotados, setProductosAgotados] = useState<Producto[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadAlertas();
  }, []);

  const loadAlertas = async () => {
    try {
      setLoading(true);
      // Obtener productos con stock bajo desde el API
      const response = await apiClient.getProductosStockBajo();
      const productos = response as Producto[];

      // Filtrar productos con stock bajo (stock <= stock_minimo pero > 0)
      const stockBajo = productos.filter(p => p.stock > 0 && p.stock <= p.stock_minimo);
      
      // Filtrar productos agotados (stock = 0)
      const agotados = productos.filter(p => p.stock === 0);

      setProductosStockBajo(stockBajo);
      setProductosAgotados(agotados);
    } catch (error) {
      console.error('Error al cargar alertas:', error);
      toast.error('Error al cargar los productos con stock bajo');
    } finally {
      setLoading(false);
    }
  };

  const handleComprarProducto = (producto: Producto) => {
    // Redirigir a la página de compras
    toast.success(`Redirigiendo a Compras para reponer: ${producto.nombre}`);
    setTimeout(() => navigate('/compras'), 500);
  };

  const handleVerDetalles = (producto: Producto) => {
    // Redirigir a la página de productos
    toast.success(`Redirigiendo a Productos: ${producto.nombre}`);
    setTimeout(() => navigate('/productos'), 500);
  };

  const getStockStatus = (producto: Producto) => {
    if (producto.stock === 0) {
      return { text: 'Agotado', color: 'bg-red-100 text-red-800' };
    } else if (producto.stock <= producto.stock_minimo) {
      return { text: 'Stock Bajo', color: 'bg-yellow-100 text-yellow-800' };
    }
    return { text: 'Normal', color: 'bg-green-100 text-green-800' };
  };

  const getUrgencyLevel = (producto: Producto) => {
    if (producto.stock === 0) return 'Crítico';
    const porcentaje = (producto.stock / producto.stock_minimo) * 100;
    if (porcentaje <= 50) return 'Alto';
    if (porcentaje <= 80) return 'Medio';
    return 'Bajo';
  };

  const getUrgencyColor = (nivel: string) => {
    switch (nivel) {
      case 'Crítico': return 'text-red-600';
      case 'Alto': return 'text-orange-600';
      case 'Medio': return 'text-yellow-600';
      default: return 'text-green-600';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const totalAlertas = productosStockBajo.length + productosAgotados.length;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Alertas de Stock</h1>
        <div className="flex items-center space-x-2">
          <ExclamationTriangleIcon className="h-6 w-6 text-red-500" />
          <span className="text-lg font-medium text-gray-900">
            {totalAlertas} alertas activas
          </span>
        </div>
      </div>

      {/* Resumen de alertas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-red-500 rounded-md flex items-center justify-center">
                  <ExclamationTriangleIcon className="h-5 w-5 text-white" />
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Productos Agotados
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {productosAgotados.length}
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
                <div className="w-8 h-8 bg-yellow-500 rounded-md flex items-center justify-center">
                  <ExclamationTriangleIcon className="h-5 w-5 text-white" />
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Stock Bajo
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {productosStockBajo.length}
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
                  <span className="text-white font-bold">%</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Nivel de Alerta
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {productosAgotados.length > 0 ? 'Crítico' : 
                     productosStockBajo.length > 5 ? 'Alto' : 
                     productosStockBajo.length > 0 ? 'Medio' : 'Normal'}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {totalAlertas === 0 ? (
        <div className="bg-white shadow rounded-lg p-6">
          <div className="text-center">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
              <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h3 className="mt-2 text-sm font-medium text-gray-900">¡Todo en orden!</h3>
            <p className="mt-1 text-sm text-gray-500">
              No hay productos con stock bajo o agotados en este momento.
            </p>
          </div>
        </div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Productos que Requieren Atención
            </h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Producto
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Categoría
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Stock Actual
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Stock Mínimo
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Estado
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Urgencia
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Acciones
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {[...productosAgotados, ...productosStockBajo].map((producto) => {
                    const status = getStockStatus(producto);
                    const urgencia = getUrgencyLevel(producto);
                    
                    return (
                      <tr key={producto.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {producto.nombre}
                            </div>
                            {producto.descripcion && (
                              <div className="text-sm text-gray-500">
                                {producto.descripcion}
                              </div>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {producto.categoria?.nombre}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          <span className={`font-medium ${producto.stock === 0 ? 'text-red-600' : 'text-gray-900'}`}>
                            {producto.stock}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {producto.stock_minimo}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${status.color}`}>
                            {status.text}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`text-sm font-medium ${getUrgencyColor(urgencia)}`}>
                            {urgencia}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <div className="flex justify-end space-x-2">
                            <button
                              onClick={() => handleComprarProducto(producto)}
                              className="text-blue-600 hover:text-blue-900 transition-colors"
                              title="Registrar compra"
                            >
                              <ShoppingCartIcon className="h-5 w-5" />
                            </button>
                            <button
                              onClick={() => handleVerDetalles(producto)}
                              className="text-gray-600 hover:text-gray-900 transition-colors"
                              title="Ver detalles"
                            >
                              <EyeIcon className="h-5 w-5" />
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
        </div>
      )}
    </div>
  );
};

export default AlertasStock;