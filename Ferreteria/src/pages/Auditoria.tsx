import React, { useState, useEffect } from 'react';
import { 
  DocumentTextIcon, 
  UserIcon, 
  CalendarIcon,
  FilterIcon,
  DownloadIcon,
  EyeIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import { format, startOfMonth, endOfMonth } from 'date-fns';
import { es } from 'date-fns/locale';
import toast from 'react-hot-toast';

interface AuditoriaLog {
  id: number;
  usuario_id: number;
  accion: string;
  tabla_afectada: string;
  registro_id?: string;
  datos_anteriores?: any;
  datos_nuevos?: any;
  ip_address?: string;
  user_agent?: string;
  detalles_adicionales?: string;
  created_at: string;
  usuario?: {
    id: number;
    nombre: string;
    email: string;
  };
}

const Auditoria: React.FC = () => {
  const [logs, setLogs] = useState<AuditoriaLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    fecha_inicio: format(startOfMonth(new Date()), 'yyyy-MM-dd'),
    fecha_fin: format(endOfMonth(new Date()), 'yyyy-MM-dd'),
    usuario_id: '',
    accion: '',
    tabla: ''
  });
  const [selectedLog, setSelectedLog] = useState<AuditoriaLog | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [estadisticas, setEstadisticas] = useState({
    total_acciones: 0,
    acciones_por_tipo: {},
    usuarios_activos: 0,
    tablas_afectadas: 0
  });

  useEffect(() => {
    cargarLogs();
    cargarEstadisticas();
  }, [filters]);

  const cargarLogs = async () => {
    try {
      setLoading(true);
      // Simular datos de auditoría
      const logsSimulados: AuditoriaLog[] = [
        {
          id: 1,
          usuario_id: 1,
          accion: 'crear_producto',
          tabla_afectada: 'productos',
          registro_id: '15',
          datos_nuevos: { nombre: 'Martillo Nuevo', precio: 25.99 },
          ip_address: '192.168.1.100',
          created_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
          usuario: { id: 1, nombre: 'Admin', email: 'admin@ferreteria.com' }
        },
        {
          id: 2,
          usuario_id: 2,
          accion: 'actualizar_precio',
          tabla_afectada: 'productos',
          registro_id: '12',
          datos_anteriores: { precio: 20.99 },
          datos_nuevos: { precio: 22.99 },
          ip_address: '192.168.1.101',
          created_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
          usuario: { id: 2, nombre: 'Juan Pérez', email: 'vendedor@ferreteria.com' }
        },
        {
          id: 3,
          usuario_id: 1,
          accion: 'eliminar_usuario',
          tabla_afectada: 'usuarios',
          registro_id: '5',
          datos_anteriores: { nombre: 'Usuario Eliminado', email: 'test@test.com' },
          ip_address: '192.168.1.100',
          created_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
          usuario: { id: 1, nombre: 'Admin', email: 'admin@ferreteria.com' }
        },
        {
          id: 4,
          usuario_id: 2,
          accion: 'crear_venta',
          tabla_afectada: 'ventas',
          registro_id: '25',
          datos_nuevos: { total: 156.75, items: 3 },
          ip_address: '192.168.1.101',
          created_at: new Date(Date.now() - 1000 * 60 * 60 * 48).toISOString(),
          usuario: { id: 2, nombre: 'Juan Pérez', email: 'vendedor@ferreteria.com' }
        }
      ];

      // Filtrar logs según los filtros
      let logsFiltrados = logsSimulados;
      
      if (filters.usuario_id) {
        logsFiltrados = logsFiltrados.filter(log => log.usuario_id.toString() === filters.usuario_id);
      }
      if (filters.accion) {
        logsFiltrados = logsFiltrados.filter(log => log.accion.includes(filters.accion));
      }
      if (filters.tabla) {
        logsFiltrados = logsFiltrados.filter(log => log.tabla_afectada.includes(filters.tabla));
      }

      setLogs(logsFiltrados);
    } catch (error) {
      toast.error('Error al cargar logs de auditoría');
    } finally {
      setLoading(false);
    }
  };

  const cargarEstadisticas = async () => {
    try {
      // Simular estadísticas
      setEstadisticas({
        total_acciones: 156,
        acciones_por_tipo: {
          'crear_producto': 45,
          'actualizar_precio': 32,
          'crear_venta': 28,
          'eliminar_usuario': 12,
          'actualizar_stock': 39
        },
        usuarios_activos: 5,
        tablas_afectadas: 8
      });
    } catch (error) {
      toast.error('Error al cargar estadísticas');
    }
  };

  const handleFilterChange = (field: string, value: string) => {
    setFilters(prev => ({ ...prev, [field]: value }));
  };

  const handleVerDetalle = (log: AuditoriaLog) => {
    setSelectedLog(log);
    setModalOpen(true);
  };

  const exportarLogs = () => {
    try {
      const csvContent = [
        ['ID', 'Usuario', 'Acción', 'Tabla', 'Registro ID', 'IP', 'Fecha'],
        ...logs.map(log => [
          log.id,
          log.usuario?.nombre || 'N/A',
          log.accion,
          log.tabla_afectada,
          log.registro_id || 'N/A',
          log.ip_address || 'N/A',
          format(new Date(log.created_at), 'dd/MM/yyyy HH:mm')
        ])
      ].map(row => row.join(',')).join('\n');

      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `auditoria_${format(new Date(), 'yyyy-MM-dd')}.csv`;
      link.click();
      
      toast.success('Logs exportados exitosamente');
    } catch (error) {
      toast.error('Error al exportar logs');
    }
  };

  const getAccionColor = (accion: string) => {
    if (accion.includes('crear')) return 'bg-green-100 text-green-800';
    if (accion.includes('actualizar')) return 'bg-blue-100 text-blue-800';
    if (accion.includes('eliminar')) return 'bg-red-100 text-red-800';
    return 'bg-gray-100 text-gray-800';
  };

  const getAccionLabel = (accion: string) => {
    const labels: { [key: string]: string } = {
      'crear_producto': 'Crear Producto',
      'actualizar_precio': 'Actualizar Precio',
      'eliminar_usuario': 'Eliminar Usuario',
      'crear_venta': 'Crear Venta',
      'actualizar_stock': 'Actualizar Stock',
      'crear_categoria': 'Crear Categoría',
      'actualizar_categoria': 'Actualizar Categoría'
    };
    return labels[accion] || accion.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

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
      <div className="sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Auditoría del Sistema</h1>
          <p className="mt-2 text-sm text-gray-700">
            Registro de todas las acciones realizadas en el sistema
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <button
            onClick={exportarLogs}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <DownloadIcon className="h-4 w-4 mr-2" />
            Exportar Logs
          </button>
        </div>
      </div>

      {/* Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <DocumentTextIcon className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total de Acciones
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {estadisticas.total_acciones}
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
                <UserIcon className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Usuarios Activos
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {estadisticas.usuarios_activos}
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
                <DocumentTextIcon className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Tablas Afectadas
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {estadisticas.tablas_afectadas}
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
                <ClockIcon className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Última Actividad
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {logs.length > 0 ? format(new Date(logs[0].created_at), 'HH:mm') : 'N/A'}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filtros */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center mb-4">
          <FilterIcon className="h-5 w-5 text-gray-400 mr-2" />
          <h3 className="text-lg font-medium text-gray-900">Filtros</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Fecha Inicio</label>
            <input
              type="date"
              value={filters.fecha_inicio}
              onChange={(e) => handleFilterChange('fecha_inicio', e.target.value)}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">Fecha Fin</label>
            <input
              type="date"
              value={filters.fecha_fin}
              onChange={(e) => handleFilterChange('fecha_fin', e.target.value)}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">Acción</label>
            <input
              type="text"
              value={filters.accion}
              onChange={(e) => handleFilterChange('accion', e.target.value)}
              placeholder="Buscar por acción..."
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">Tabla</label>
            <input
              type="text"
              value={filters.tabla}
              onChange={(e) => handleFilterChange('tabla', e.target.value)}
              placeholder="Buscar por tabla..."
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Tabla de logs */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Logs de Auditoría ({logs.length})
          </h3>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                    Usuario
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                    Acción
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                    Tabla
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                    Registro ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                    IP
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                    Fecha
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {logs.map((log) => (
                  <tr key={log.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {log.usuario?.nombre || 'N/A'}
                      </div>
                      <div className="text-sm text-gray-500">
                        {log.usuario?.email || 'N/A'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getAccionColor(log.accion)}`}>
                        {getAccionLabel(log.accion)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {log.tabla_afectada}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {log.registro_id || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {log.ip_address || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {format(new Date(log.created_at), 'dd/MM/yyyy HH:mm', { locale: es })}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => handleVerDetalle(log)}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        <EyeIcon className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Modal de detalle */}
      {modalOpen && selectedLog && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-900 bg-opacity-75 transition-opacity" onClick={() => setModalOpen(false)} />

            <span className="hidden sm:inline-block sm:align-middle sm:h-screen">&#8203;</span>

            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg leading-6 font-medium text-gray-900">
                    Detalle del Log de Auditoría
                  </h3>
                  <button
                    onClick={() => setModalOpen(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">ID</label>
                      <p className="mt-1 text-sm text-gray-900">{selectedLog.id}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Usuario</label>
                      <p className="mt-1 text-sm text-gray-900">{selectedLog.usuario?.nombre || 'N/A'}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Acción</label>
                      <p className="mt-1 text-sm text-gray-900">{getAccionLabel(selectedLog.accion)}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Tabla</label>
                      <p className="mt-1 text-sm text-gray-900">{selectedLog.tabla_afectada}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Registro ID</label>
                      <p className="mt-1 text-sm text-gray-900">{selectedLog.registro_id || 'N/A'}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">IP Address</label>
                      <p className="mt-1 text-sm text-gray-900">{selectedLog.ip_address || 'N/A'}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Fecha</label>
                      <p className="mt-1 text-sm text-gray-900">
                        {format(new Date(selectedLog.created_at), 'dd/MM/yyyy HH:mm:ss', { locale: es })}
                      </p>
                    </div>
                  </div>

                  {selectedLog.datos_anteriores && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Datos Anteriores</label>
                      <pre className="mt-1 text-sm text-gray-900 bg-gray-100 p-2 rounded overflow-auto">
                        {JSON.stringify(selectedLog.datos_anteriores, null, 2)}
                      </pre>
                    </div>
                  )}

                  {selectedLog.datos_nuevos && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Datos Nuevos</label>
                      <pre className="mt-1 text-sm text-gray-900 bg-gray-100 p-2 rounded overflow-auto">
                        {JSON.stringify(selectedLog.datos_nuevos, null, 2)}
                      </pre>
                    </div>
                  )}

                  {selectedLog.detalles_adicionales && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Detalles Adicionales</label>
                      <p className="mt-1 text-sm text-gray-900">{selectedLog.detalles_adicionales}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Auditoria;
