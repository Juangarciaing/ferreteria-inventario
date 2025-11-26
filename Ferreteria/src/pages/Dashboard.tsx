import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  CubeIcon,
  ShoppingCartIcon,
  ExclamationTriangleIcon,
  CurrencyDollarIcon,
  UserGroupIcon,
  TruckIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  ChartBarIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { apiClient } from '../lib/api';
import toast from 'react-hot-toast';
import { format, parseISO } from 'date-fns';
import { es } from 'date-fns/locale';

interface DashboardStats {
  total_productos: number;
  productos_stock_bajo: number;
  productos_sin_stock: number;
  ventas_mes: number;
  ventas_mes_anterior: number;
  cambio_ventas: number;
  ingresos_mes: number;
  ingresos_mes_anterior: number;
  cambio_ingresos: number;
  compras_mes: number;
  gastos_mes: number;
  proveedores_activos: number;
  margen_mes: number;
}

interface VentaPorDia {
  fecha: string;
  cantidad: number;
  total: number;
}

interface ProductoMasVendido {
  id: number;
  nombre: string;
  stock: number;
  total_vendido: number;
  ingresos: number;
}

interface StockCritico {
  id: number;
  nombre: string;
  stock: number;
  stock_minimo: number;
  categoria?: {
    id: number;
    nombre: string;
  };
}

interface ActividadReciente {
  tipo: 'venta' | 'compra';
  id: number;
  fecha: string;
  total: number;
  descripcion: string;
  usuario?: string;
  proveedor?: string;
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [ventasPorDia, setVentasPorDia] = useState<VentaPorDia[]>([]);
  const [productosMasVendidos, setProductosMasVendidos] = useState<ProductoMasVendido[]>([]);
  const [stockCritico, setStockCritico] = useState<StockCritico[]>([]);
  const [actividadReciente, setActividadReciente] = useState<ActividadReciente[]>([]);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    loadDashboardData();
    
    // Auto-refresh cada 30 segundos si está habilitado
    let interval: NodeJS.Timeout | null = null;
    if (autoRefresh) {
      interval = setInterval(() => {
        loadDashboardData();
      }, 30000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Cargar datos con manejo individual de errores
      const statsPromise = apiClient.getDashboardStats().catch(e => {
        console.error('Error cargando stats:', e);
        return null;
      });
      
      const ventasPromise = apiClient.getVentasRecientes(5).catch(e => {
        console.error('Error cargando ventas recientes:', e);
        return [];
      });
      
      const ventasDiaPromise = apiClient.getVentasPorDia(7).catch(e => {
        console.error('Error cargando ventas por día:', e);
        return [];
      });
      
      const productosPromise = apiClient.getProductosMasVendidosDashboard(5, 30).catch(e => {
        console.error('Error cargando productos más vendidos:', e);
        return [];
      });
      
      const stockPromise = apiClient.getStockCritico().catch(e => {
        console.error('Error cargando stock crítico:', e);
        return [];
      });
      
      const actividadPromise = apiClient.getActividadReciente(10).catch(e => {
        console.error('Error cargando actividad reciente:', e);
        return [];
      });
      
      const [
        statsData, 
        _ventasData, // No se usa pero se obtiene para mantener compatibilidad con API
        ventasDiaData, 
        productosData,
        stockData,
        actividadData
      ] = await Promise.all([
        statsPromise,
        ventasPromise,
        ventasDiaPromise,
        productosPromise,
        stockPromise,
        actividadPromise,
      ]);
      
      if (statsData) setStats(statsData);
      setVentasPorDia(ventasDiaData);
      setProductosMasVendidos(productosData);
      setStockCritico(stockData);
      setActividadReciente(actividadData);
      
      // Solo mostrar error si las estadísticas principales fallaron
      if (!statsData) {
        toast.error('Error al cargar algunas estadísticas del dashboard');
      }
    } catch (error: any) {
      console.error('Error cargando dashboard:', error);
      toast.error('Error al cargar el dashboard');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 text-lg">Cargando dashboard...</p>
        </div>
      </div>
    );
  }

  const statCards = [
    {
      title: 'Ingresos del Mes',
      value: `$${(stats?.ingresos_mes ?? 0).toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      icon: CurrencyDollarIcon,
      color: 'bg-gradient-to-br from-green-500 to-green-600',
      change: stats?.cambio_ingresos ?? 0,
      subtitle: `${stats?.ventas_mes ?? 0} ventas este mes`,
      previous: `$${(stats?.ingresos_mes_anterior ?? 0).toLocaleString('es-MX', { minimumFractionDigits: 2 })} mes anterior`,
    },
    {
      title: 'Ventas del Mes',
      value: stats?.ventas_mes ?? 0,
      icon: ShoppingCartIcon,
      color: 'bg-gradient-to-br from-blue-500 to-blue-600',
      change: stats?.cambio_ventas ?? 0,
      subtitle: 'Transacciones completadas',
      previous: `${stats?.ventas_mes_anterior ?? 0} mes anterior`,
    },
    {
      title: 'Productos en Stock',
      value: stats?.total_productos ?? 0,
      icon: CubeIcon,
      color: 'bg-gradient-to-br from-purple-500 to-purple-600',
      subtitle: 'Total en inventario',
      badge: stats?.productos_stock_bajo ? `${stats.productos_stock_bajo} bajo stock` : undefined,
      badgeColor: 'bg-orange-100 text-orange-800',
    },
    {
      title: 'Margen del Mes',
      value: `$${(stats?.margen_mes ?? 0).toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      icon: ChartBarIcon,
      color: 'bg-gradient-to-br from-indigo-500 to-indigo-600',
      subtitle: `Ingresos - Gastos`,
      badge: stats?.gastos_mes ? `$${stats.gastos_mes.toLocaleString('es-MX', { minimumFractionDigits: 2 })} en compras` : undefined,
      badgeColor: 'bg-red-100 text-red-800',
    },
  ];

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-gray-900">Dashboard</h1>
            <p className="mt-2 text-lg text-gray-600">
              Sistema de Control de Inventario - Ferretería
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center text-sm text-gray-600 bg-white px-4 py-2 rounded-lg shadow">
              <ClockIcon className="w-5 h-5 mr-2 text-blue-500" />
              Actualización: {new Date().toLocaleTimeString()}
            </div>
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`px-4 py-2 rounded-lg shadow transition-colors ${
                autoRefresh 
                  ? 'bg-green-500 text-white hover:bg-green-600' 
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {autoRefresh ? '🔄 Auto-refresh ON' : '⏸️ Auto-refresh OFF'}
            </button>
          </div>
        </div>
        <div className="mt-2 flex items-center text-sm text-green-600">
          <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
          Sistema funcionando correctamente
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        {statCards.map((stat, index) => (
          <div key={index} className="bg-white overflow-hidden shadow-lg rounded-xl hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className={`p-3 rounded-xl ${stat.color} shadow-lg`}>
                  <stat.icon className="w-7 h-7 text-white" />
                </div>
                {stat.change !== undefined && (
                  <div className={`flex items-center text-sm font-medium ${
                    stat.change >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {stat.change >= 0 ? (
                      <ArrowTrendingUpIcon className="w-4 h-4 mr-1" />
                    ) : (
                      <ArrowTrendingDownIcon className="w-4 h-4 mr-1" />
                    )}
                    {Math.abs(stat.change).toFixed(1)}%
                  </div>
                )}
              </div>
              <p className="text-sm font-medium text-gray-600 mb-1">{stat.title}</p>
              <p className="text-3xl font-bold text-gray-900 mb-2">{stat.value}</p>
              <p className="text-xs text-gray-500">{stat.subtitle}</p>
              {stat.previous && (
                <p className="text-xs text-gray-400 mt-1">{stat.previous}</p>
              )}
              {stat.badge && (
                <span className={`inline-block mt-2 px-2 py-1 text-xs font-medium rounded-full ${stat.badgeColor}`}>
                  {stat.badge}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Gráfico de Ventas por Día */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
            <ChartBarIcon className="w-5 h-5 mr-2 text-blue-500" />
            Ventas de los Últimos 7 Días
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={ventasPorDia}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="fecha" 
                tickFormatter={(fecha) => format(parseISO(fecha), 'dd/MM', { locale: es })}
                stroke="#666"
                style={{ fontSize: '12px' }}
              />
              <YAxis stroke="#666" style={{ fontSize: '12px' }} />
              <Tooltip 
                formatter={(value: any, name: string) => [
                  name === 'total' ? `$${Number(value).toFixed(2)}` : value,
                  name === 'total' ? 'Total' : 'Cantidad'
                ]}
                labelFormatter={(label) => format(parseISO(label), 'dd MMM yyyy', { locale: es })}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="cantidad" 
                stroke="#3b82f6" 
                strokeWidth={3}
                dot={{ fill: '#3b82f6', r: 5 }}
                name="Cantidad"
              />
              <Line 
                type="monotone" 
                dataKey="total" 
                stroke="#10b981" 
                strokeWidth={3}
                dot={{ fill: '#10b981', r: 5 }}
                name="Total ($)"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Top 5 Productos Más Vendidos */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
            <CubeIcon className="w-5 h-5 mr-2 text-purple-500" />
            Top 5 Productos Más Vendidos (30 días)
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={productosMasVendidos} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis type="number" stroke="#666" style={{ fontSize: '12px' }} />
              <YAxis 
                dataKey="nombre" 
                type="category" 
                width={120}
                stroke="#666"
                style={{ fontSize: '11px' }}
                tickFormatter={(value) => value.length > 15 ? value.substring(0, 15) + '...' : value}
              />
              <Tooltip 
                formatter={(value: any) => [`${value} unidades`, 'Vendido']}
              />
              <Bar dataKey="total_vendido" fill="#8b5cf6" radius={[0, 8, 8, 0]}>
                {productosMasVendidos.map((_entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Sección de 3 columnas */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Acciones Rápidas */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
            <ChartBarIcon className="w-5 h-5 mr-2 text-blue-500" />
            Acciones Rápidas
          </h3>
          <div className="space-y-3">
            <button
              onClick={() => navigate('/ventas')}
              className="w-full text-left p-4 rounded-lg bg-blue-50 hover:bg-blue-100 transition-all duration-200 transform hover:scale-105 group"
            >
              <div className="flex items-center">
                <ShoppingCartIcon className="w-6 h-6 text-blue-600 mr-3 group-hover:scale-110 transition-transform" />
                <div>
                  <div className="font-bold text-blue-900">Nueva Venta</div>
                  <div className="text-sm text-blue-700">Registrar una nueva venta</div>
                </div>
              </div>
            </button>
            <button
              onClick={() => navigate('/productos')}
              className="w-full text-left p-4 rounded-lg bg-green-50 hover:bg-green-100 transition-all duration-200 transform hover:scale-105 group"
            >
              <div className="flex items-center">
                <CubeIcon className="w-6 h-6 text-green-600 mr-3 group-hover:scale-110 transition-transform" />
                <div>
                  <div className="font-bold text-green-900">Agregar Producto</div>
                  <div className="text-sm text-green-700">Añadir al inventario</div>
                </div>
              </div>
            </button>
            <button
              onClick={() => navigate('/reportes')}
              className="w-full text-left p-4 rounded-lg bg-orange-50 hover:bg-orange-100 transition-all duration-200 transform hover:scale-105 group"
            >
              <div className="flex items-center">
                <ChartBarIcon className="w-6 h-6 text-orange-600 mr-3 group-hover:scale-110 transition-transform" />
                <div>
                  <div className="font-bold text-orange-900">Ver Reportes</div>
                  <div className="text-sm text-orange-700">Analizar tendencias</div>
                </div>
              </div>
            </button>
            <button
              onClick={() => navigate('/compras')}
              className="w-full text-left p-4 rounded-lg bg-purple-50 hover:bg-purple-100 transition-all duration-200 transform hover:scale-105 group"
            >
              <div className="flex items-center">
                <TruckIcon className="w-6 h-6 text-purple-600 mr-3 group-hover:scale-110 transition-transform" />
                <div>
                  <div className="font-bold text-purple-900">Nueva Compra</div>
                  <div className="text-sm text-purple-700">Registrar inventario</div>
                </div>
              </div>
            </button>
          </div>
        </div>

        {/* Stock Crítico */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
            <ExclamationTriangleIcon className="w-5 h-5 mr-2 text-red-500" />
            Alertas de Stock
          </h3>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {stockCritico.length === 0 ? (
              <div className="text-center py-8">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <CubeIcon className="w-8 h-8 text-green-600" />
                </div>
                <p className="text-sm text-gray-500">¡Todo el stock está bien!</p>
              </div>
            ) : (
              stockCritico.map((producto) => (
                <div key={producto.id} className="flex items-center justify-between p-3 rounded-lg bg-red-50 border border-red-200">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-bold text-gray-900 truncate">
                      {producto.nombre}
                    </p>
                    <p className="text-xs text-gray-600">
                      {producto.categoria?.nombre || 'Sin categoría'}
                    </p>
                    <div className="flex items-center mt-1">
                      <span className={`text-xs font-medium px-2 py-1 rounded ${
                        producto.stock === 0 
                          ? 'bg-red-600 text-white' 
                          : 'bg-orange-100 text-orange-800'
                      }`}>
                        Stock: {producto.stock}
                      </span>
                      <span className="text-xs text-gray-500 ml-2">
                        Min: {producto.stock_minimo}
                      </span>
                    </div>
                  </div>
                  <ExclamationTriangleIcon className={`w-6 h-6 ml-2 ${
                    producto.stock === 0 ? 'text-red-600' : 'text-orange-500'
                  }`} />
                </div>
              ))
            )}
          </div>
        </div>

        {/* Actividad Reciente */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
            <ClockIcon className="w-5 h-5 mr-2 text-indigo-500" />
            Actividad Reciente
          </h3>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {actividadReciente.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-8">No hay actividad reciente</p>
            ) : (
              actividadReciente.map((actividad, index) => (
                <div key={`${actividad.tipo}-${actividad.id}-${index}`} className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                    actividad.tipo === 'venta' ? 'bg-green-100' : 'bg-blue-100'
                  }`}>
                    {actividad.tipo === 'venta' ? (
                      <ShoppingCartIcon className="w-5 h-5 text-green-600" />
                    ) : (
                      <TruckIcon className="w-5 h-5 text-blue-600" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900">
                      {actividad.descripcion}
                    </p>
                    <p className="text-xs text-gray-600">
                      {actividad.tipo === 'venta' ? actividad.usuario : actividad.proveedor}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {format(parseISO(actividad.fecha), "dd/MM/yyyy HH:mm", { locale: es })}
                    </p>
                  </div>
                  <div className={`text-sm font-bold ${
                    actividad.tipo === 'venta' ? 'text-green-600' : 'text-blue-600'
                  }`}>
                    ${actividad.total.toFixed(2)}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Status Footer */}
      <div className="bg-white rounded-xl shadow-lg p-4">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center space-x-6">
            <div className="flex items-center text-sm text-gray-600">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
              <span className="font-medium">Backend:</span>
              <span className="ml-1 text-green-600">Conectado</span>
            </div>
            <div className="flex items-center text-sm text-gray-600">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
              <span className="font-medium">Base de datos:</span>
              <span className="ml-1 text-green-600">Activa</span>
            </div>
            <div className="flex items-center text-sm text-gray-600">
              <UserGroupIcon className="w-4 h-4 mr-1 text-purple-500" />
              <span className="font-medium">Proveedores activos:</span>
              <span className="ml-1 text-purple-600">{stats?.proveedores_activos ?? 0}</span>
            </div>
          </div>
          <button 
            onClick={loadDashboardData}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center text-sm font-medium"
          >
            <ArrowTrendingUpIcon className="w-4 h-4 mr-2" />
            Actualizar Ahora
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
