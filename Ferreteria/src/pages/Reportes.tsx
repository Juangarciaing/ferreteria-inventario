import React, { useState, useEffect } from 'react';
import { 
  DocumentArrowDownIcon, 
  ChartBarIcon
} from '@heroicons/react/24/outline';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  PieChart, 
  Pie, 
  Cell,
  Legend
} from 'recharts';
import { ReporteVentas, ProductoMasVendido } from '../types';
import { apiClient } from '../lib/api';
import ExportModal from '../components/ExportModal';
import toast from 'react-hot-toast';
import { format, startOfMonth, endOfMonth } from 'date-fns';
import { es } from 'date-fns/locale';

const Reportes: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState({
    desde: format(startOfMonth(new Date()), 'yyyy-MM-dd'),
    hasta: format(endOfMonth(new Date()), 'yyyy-MM-dd'),
  });

  const [ventasPorDia, setVentasPorDia] = useState<ReporteVentas[]>([]);
  const [ventasPorCategoria, setVentasPorCategoria] = useState<Array<{nombre: string, valor: number, color: string}>>([]);
  const [productosMasVendidos, setProductosMasVendidos] = useState<ProductoMasVendido[]>([]);
  const [exportModalOpen, setExportModalOpen] = useState(false);
  const [exportTitle, setExportTitle] = useState('');
  const [exportData, setExportData] = useState<Record<string, unknown>[]>([]);
  const [resumenGeneral, setResumenGeneral] = useState({
    totalVentas: 0,
    totalProductosVendidos: 0,
    ventaPromedio: 0,
    mejorDia: '',
  });

  useEffect(() => {
    cargarDatos();
  }, [dateRange]);

  const cargarDatos = async () => {
    setLoading(true);
    try {
      // Obtener datos reales del API
      const [ventasResponse, productosData] = await Promise.all([
        apiClient.getVentasPorFecha(dateRange.desde, dateRange.hasta),
        apiClient.getProductosMasVendidos(5),
      ]);

      console.log('Datos de ventas:', ventasResponse);
      console.log('Productos más vendidos:', productosData);

      // ventasResponse es un objeto con { ventas: [], total_ventas, cantidad_ventas }
      const ventasData = ventasResponse as any;
      
      // Procesar ventas por día
      const ventasMap = new Map<string, { total: number; cantidad: number }>();
      
      if (ventasData.ventas && Array.isArray(ventasData.ventas)) {
        ventasData.ventas.forEach((venta: any) => {
          try {
            const fecha = format(new Date(venta.fecha), 'yyyy-MM-dd');
            const existing = ventasMap.get(fecha) || { total: 0, cantidad: 0 };
            ventasMap.set(fecha, {
              total: existing.total + (parseFloat(venta.total) || 0),
              cantidad: existing.cantidad + 1,
            });
          } catch (err) {
            console.warn('Error procesando venta:', venta, err);
          }
        });
      }

      const ventasPorDiaData = Array.from(ventasMap.entries())
        .map(([fecha, datos]) => ({
          fecha,
          total: datos.total,
          cantidad_ventas: datos.cantidad,
        }))
        .sort((a, b) => a.fecha.localeCompare(b.fecha));

      setVentasPorDia(ventasPorDiaData);

      // Productos más vendidos
      const productosFormateados = (productosData as any[]).map((p: any) => ({
        producto_id: p.id,
        nombre: p.nombre,
        total_vendido: p.total_vendido || 0,
        ingresos_totales: p.total_ingresos || 0,
      }));
      setProductosMasVendidos(productosFormateados);

      // Calcular resumen
      const totalVentas = ventasData.total_ventas || 0;
      const cantidadVentas = ventasData.cantidad_ventas || 0;
      const ventaPromedio = cantidadVentas > 0 ? totalVentas / cantidadVentas : 0;
      
      // Encontrar mejor día
      let mejorDia = '';
      if (ventasPorDiaData.length > 0) {
        const mejorVenta = ventasPorDiaData.reduce((max, venta) => 
          venta.total > max.total ? venta : max
        );
        mejorDia = mejorVenta.fecha;
      }

      setResumenGeneral({
        totalVentas,
        totalProductosVendidos: (productosData as any[]).reduce((sum: number, p: any) => sum + (p.total_vendido || 0), 0),
        ventaPromedio,
        mejorDia,
      });

      // Por ahora, ventas por categoría simuladas (falta endpoint)
      setVentasPorCategoria([
        { nombre: 'Herramientas', valor: totalVentas * 0.35, color: '#3B82F6' },
        { nombre: 'Materiales', valor: totalVentas * 0.25, color: '#10B981' },
        { nombre: 'Electricidad', valor: totalVentas * 0.20, color: '#F59E0B' },
        { nombre: 'Plomería', valor: totalVentas * 0.12, color: '#EF4444' },
        { nombre: 'Pintura', valor: totalVentas * 0.08, color: '#8B5CF6' },
      ]);

    } catch (error: any) {
      console.error('Error detallado al cargar reportes:', error);
      const mensajeError = error?.response?.data?.message || error?.message || 'Error al generar reporte';
      toast.error(mensajeError);
      
      // En caso de error, establecer datos vacíos para evitar crashes
      setVentasPorDia([]);
      setProductosMasVendidos([]);
      setVentasPorCategoria([]);
      setResumenGeneral({
        totalVentas: 0,
        totalProductosVendidos: 0,
        ventaPromedio: 0,
        mejorDia: '',
      });
    } finally {
      setLoading(false);
    }
  };

  const exportarExcel = (titulo: string, data: unknown[]) => {
    setExportTitle(titulo);
    setExportData(data as Record<string, unknown>[]);
    setExportModalOpen(true);
  };

  if (loading) {
    return (
      <div className="flex flex-col justify-center items-center h-96 bg-white rounded-lg shadow">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-indigo-600 mb-4"></div>
        <p className="text-gray-600 font-medium">Generando reportes...</p>
        <p className="text-gray-400 text-sm mt-1">Esto puede tomar unos segundos</p>
      </div>
    );
  }

  const sinDatos = ventasPorDia.length === 0 && productosMasVendidos.length === 0;

  return (
    <div className="space-y-6">
      {/* Header mejorado */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">📊 Reportes y Análisis</h1>
            <p className="text-gray-500 mt-1">Visualiza el rendimiento de tu ferretería</p>
          </div>
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="flex flex-col">
              <label className="text-xs font-medium text-gray-600 mb-1">Fecha Inicio</label>
              <input
                type="date"
                value={dateRange.desde}
                onChange={(e) => setDateRange({...dateRange, desde: e.target.value})}
                className="border-2 border-gray-300 rounded-lg px-4 py-2 focus:border-indigo-500 focus:outline-none transition-colors"
              />
            </div>
            <div className="flex flex-col">
              <label className="text-xs font-medium text-gray-600 mb-1">Fecha Fin</label>
              <input
                type="date"
                value={dateRange.hasta}
                onChange={(e) => setDateRange({...dateRange, hasta: e.target.value})}
                className="border-2 border-gray-300 rounded-lg px-4 py-2 focus:border-indigo-500 focus:outline-none transition-colors"
              />
            </div>
          </div>
        </div>
      </div>

      {sinDatos ? (
        <div className="bg-white rounded-lg shadow-lg p-12 text-center">
          <div className="max-w-md mx-auto">
            <ChartBarIcon className="h-20 w-20 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No hay datos disponibles</h3>
            <p className="text-gray-500 mb-6">
              No se encontraron ventas en el período seleccionado.
              <br />
              Intenta cambiar el rango de fechas o registra algunas ventas.
            </p>
            <button
              onClick={() => setDateRange({
                desde: format(startOfMonth(new Date()), 'yyyy-MM-dd'),
                hasta: format(endOfMonth(new Date()), 'yyyy-MM-dd'),
              })}
              className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium"
            >
              Ver mes actual
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-6">

      {/* Tarjetas de resumen mejoradas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-blue-100">Ventas Totales</p>
              <p className="text-3xl font-bold mt-2">${resumenGeneral.totalVentas.toLocaleString('es-ES', { minimumFractionDigits: 2 })}</p>
              <p className="text-xs text-blue-100 mt-1">En el período seleccionado</p>
            </div>
            <div className="bg-blue-400 bg-opacity-30 rounded-full p-3">
              <ChartBarIcon className="h-8 w-8" />
            </div>
          </div>
        </div>
        
        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-green-100">Productos Vendidos</p>
              <p className="text-3xl font-bold mt-2">{resumenGeneral.totalProductosVendidos}</p>
              <p className="text-xs text-green-100 mt-1">Unidades totales</p>
            </div>
            <div className="bg-green-400 bg-opacity-30 rounded-full p-3">
              <DocumentArrowDownIcon className="h-8 w-8" />
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-yellow-500 to-yellow-600 rounded-lg shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-yellow-100">Venta Promedio</p>
              <p className="text-3xl font-bold mt-2">${resumenGeneral.ventaPromedio.toFixed(2)}</p>
              <p className="text-xs text-yellow-100 mt-1">Por transacción</p>
            </div>
            <div className="bg-yellow-400 bg-opacity-30 rounded-full p-3">
              <ChartBarIcon className="h-8 w-8" />
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-purple-100">Mejor Día</p>
              <p className="text-3xl font-bold mt-2">
                {resumenGeneral.mejorDia ? format(new Date(resumenGeneral.mejorDia), 'dd', { locale: es }) : '-'}
              </p>
              <p className="text-xs text-purple-100 mt-1">
                {resumenGeneral.mejorDia ? format(new Date(resumenGeneral.mejorDia), 'MMMM', { locale: es }) : 'Sin datos'}
              </p>
            </div>
            <div className="bg-purple-400 bg-opacity-30 rounded-full p-3">
              <ChartBarIcon className="h-8 w-8" />
            </div>
          </div>
        </div>
      </div>

      {/* Gráficos mejorados - MISMO TAMAÑO */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Ventas por día - GRÁFICO DE LÍNEA */}
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Evolución de Ventas</h3>
              <p className="text-sm text-gray-500 mt-1">Tendencia de ventas por día</p>
            </div>
            <button
              onClick={() => exportarExcel('Ventas por Día', ventasPorDia)}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors"
            >
              <DocumentArrowDownIcon className="h-4 w-4" />
              Exportar
            </button>
          </div>
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={ventasPorDia} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <defs>
                <linearGradient id="colorVentas" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis 
                dataKey="fecha" 
                tickFormatter={(value) => format(new Date(value), 'dd MMM', { locale: es })}
                tick={{ fill: '#6B7280', fontSize: 12 }}
                stroke="#9CA3AF"
              />
              <YAxis 
                tick={{ fill: '#6B7280', fontSize: 12 }}
                stroke="#9CA3AF"
                tickFormatter={(value) => `$${value}`}
              />
              <Tooltip
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: 'none', 
                  borderRadius: '8px',
                  boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
                }}
                labelStyle={{ color: '#F9FAFB', fontWeight: 'bold' }}
                itemStyle={{ color: '#F3F4F6' }}
                labelFormatter={(value) => format(new Date(value), "dd 'de' MMMM, yyyy", { locale: es })}
                formatter={(value: number, name: string) => {
                  if (name === 'total') return [`$${value.toFixed(2)}`, 'Total Ventas'];
                  return [`${value}`, 'Cantidad'];
                }}
              />
              <Line 
                type="monotone" 
                dataKey="total" 
                stroke="#3B82F6" 
                strokeWidth={3}
                dot={{ fill: '#3B82F6', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, fill: '#2563EB' }}
                fill="url(#colorVentas)"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Ventas por categoría - GRÁFICO CIRCULAR MEJORADO */}
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Ventas por Categoría</h3>
            <p className="text-sm text-gray-500 mt-1">Distribución de ventas</p>
          </div>
          <ResponsiveContainer width="100%" height={350}>
            <PieChart>
              <Pie
                data={ventasPorCategoria}
                cx="50%"
                cy="45%"
                labelLine={{
                  stroke: '#9CA3AF',
                  strokeWidth: 1
                }}
                label={({ nombre, percent, cx, cy, midAngle, outerRadius }: any) => {
                  const RADIAN = Math.PI / 180;
                  const radius = outerRadius + 25;
                  const x = cx + radius * Math.cos(-midAngle * RADIAN);
                  const y = cy + radius * Math.sin(-midAngle * RADIAN);
                  
                  return (
                    <text 
                      x={x} 
                      y={y} 
                      fill="#374151"
                      textAnchor={x > cx ? 'start' : 'end'} 
                      dominantBaseline="central"
                      className="text-xs font-medium"
                    >
                      {`${nombre}: ${(percent * 100).toFixed(0)}%`}
                    </text>
                  );
                }}
                outerRadius={85}
                innerRadius={0}
                fill="#8884d8"
                dataKey="valor"
                animationDuration={800}
              >
                {ventasPorCategoria.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={entry.color}
                    stroke="#fff"
                    strokeWidth={2}
                  />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: 'none', 
                  borderRadius: '8px',
                  padding: '12px'
                }}
                itemStyle={{ color: '#F3F4F6', fontSize: '14px' }}
                formatter={(value: number) => [`$${value.toLocaleString('es-ES', { minimumFractionDigits: 2 })}`, 'Ventas']} 
              />
              <Legend 
                verticalAlign="bottom" 
                height={36}
                iconType="circle"
                iconSize={8}
                wrapperStyle={{
                  paddingTop: '20px',
                  fontSize: '12px'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Segunda fila de gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Productos más vendidos - GRÁFICO DE BARRAS HORIZONTAL */}
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Top 5 Productos</h3>
              <p className="text-sm text-gray-500 mt-1">Productos más vendidos</p>
            </div>
            <button
              onClick={() => exportarExcel('Productos Más Vendidos', productosMasVendidos)}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-green-600 bg-green-50 rounded-lg hover:bg-green-100 transition-colors"
            >
              <DocumentArrowDownIcon className="h-4 w-4" />
              Exportar
            </button>
          </div>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart 
              data={productosMasVendidos} 
              layout="vertical"
              margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" horizontal={false} />
              <XAxis 
                type="number" 
                tick={{ fill: '#6B7280', fontSize: 12 }}
                stroke="#9CA3AF"
              />
              <YAxis 
                type="category" 
                dataKey="nombre"
                tick={{ fill: '#374151', fontSize: 12 }}
                stroke="#9CA3AF"
                width={90}
              />
              <Tooltip
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: 'none', 
                  borderRadius: '8px' 
                }}
                itemStyle={{ color: '#F3F4F6' }}
                cursor={{ fill: 'rgba(16, 185, 129, 0.1)' }}
                formatter={(value: number) => [`${value} unidades`, 'Vendidas']} 
              />
              <Bar 
                dataKey="total_vendido" 
                fill="#10B981"
                radius={[0, 8, 8, 0]}
                animationDuration={800}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Tabla de productos más vendidos - MEJORADA */}
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Detalle de Ventas por Producto</h3>
            <p className="text-sm text-gray-500 mt-1">Ranking de productos</p>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="border-b-2 border-gray-200">
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Ranking
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Producto
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Unidades
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Ingresos
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {productosMasVendidos.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="px-4 py-8 text-center text-gray-500">
                      No hay datos de productos vendidos en este período
                    </td>
                  </tr>
                ) : (
                  productosMasVendidos.map((producto, index) => (
                    <tr key={producto.producto_id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-4 py-4 whitespace-nowrap">
                        <div className={`
                          inline-flex items-center justify-center w-8 h-8 rounded-full font-bold text-sm
                          ${index === 0 ? 'bg-yellow-100 text-yellow-700' : 
                            index === 1 ? 'bg-gray-100 text-gray-700' : 
                            index === 2 ? 'bg-orange-100 text-orange-700' : 
                            'bg-blue-50 text-blue-600'}
                        `}>
                          {index + 1}
                        </div>
                      </td>
                      <td className="px-4 py-4">
                        <div className="text-sm font-medium text-gray-900">{producto.nombre}</div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-right">
                        <div className="text-sm font-semibold text-gray-900">{producto.total_vendido}</div>
                        <div className="text-xs text-gray-500">unidades</div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-right">
                        <div className="text-sm font-bold text-green-600">
                          ${producto.ingresos_totales.toLocaleString('es-ES', { minimumFractionDigits: 2 })}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
        </div>
      )}

      {/* Modal de Exportación */}
      <ExportModal
        isOpen={exportModalOpen}
        onClose={() => setExportModalOpen(false)}
        title={exportTitle}
        data={exportData}
        filename="reporte_ventas"
      />
    </div>
  );
};

export default Reportes;