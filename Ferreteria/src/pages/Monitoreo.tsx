import React, { useState, useEffect } from 'react';
import { 
  ChartBarIcon, 
  CpuChipIcon, 
  ServerIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  UserGroupIcon
} from '@heroicons/react/24/outline';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import toast from 'react-hot-toast';

interface SystemMetrics {
  memory: {
    used_percent: number;
    used_gb: number;
    available_gb: number;
  };
  cpu: {
    percent: number;
  };
  disk: {
    used_percent: number;
    used_gb: number;
    total_gb: number;
  };
}

interface PerformanceMetrics {
  avg_response_time: number;
  min_response_time: number;
  max_response_time: number;
  total_requests: number;
  error_rate: number;
}

interface HealthStatus {
  status: 'healthy' | 'warning' | 'critical' | 'error';
  issues: string[];
  system_metrics: SystemMetrics;
  performance_metrics: PerformanceMetrics;
  active_users: number;
  timestamp: string;
}

interface Alert {
  type: 'warning' | 'error' | 'info';
  category: string;
  message: string;
  value: string;
  timestamp: string;
}

const Monitoreo: React.FC = () => {
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null);
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null);
  const [performanceMetrics, setPerformanceMetrics] = useState<PerformanceMetrics | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    loadMonitoringData();
    
    if (autoRefresh) {
      const interval = setInterval(loadMonitoringData, 30000); // Actualizar cada 30 segundos
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const loadMonitoringData = async () => {
    try {
      setLoading(true);
      
      // Simular datos de monitoreo
      const mockHealthStatus: HealthStatus = {
        status: 'healthy',
        issues: [],
        system_metrics: {
          memory: {
            used_percent: 65.2,
            used_gb: 8.1,
            available_gb: 4.3
          },
          cpu: {
            percent: 45.8
          },
          disk: {
            used_percent: 72.5,
            used_gb: 145.2,
            total_gb: 200.0
          }
        },
        performance_metrics: {
          avg_response_time: 0.245,
          min_response_time: 0.089,
          max_response_time: 1.234,
          total_requests: 1547,
          error_rate: 2.1
        },
        active_users: 8,
        timestamp: new Date().toISOString()
      };

      const mockAlerts: Alert[] = [
        {
          type: 'warning',
          category: 'memory',
          message: 'Uso de memoria moderado',
          value: '65.2%',
          timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString()
        },
        {
          type: 'info',
          category: 'performance',
          message: 'Tiempo de respuesta normal',
          value: '0.245s',
          timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString()
        }
      ];

      setHealthStatus(mockHealthStatus);
      setSystemMetrics(mockHealthStatus.system_metrics);
      setPerformanceMetrics(mockHealthStatus.performance_metrics);
      setAlerts(mockAlerts);
      
    } catch (error) {
      toast.error('Error al cargar datos de monitoreo');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-600 bg-green-100';
      case 'warning': return 'text-yellow-600 bg-yellow-100';
      case 'critical': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return <CheckCircleIcon className="h-5 w-5" />;
      case 'warning': return <ExclamationTriangleIcon className="h-5 w-5" />;
      case 'critical': return <XCircleIcon className="h-5 w-5" />;
      default: return <ClockIcon className="h-5 w-5" />;
    }
  };

  const getAlertColor = (type: string) => {
    switch (type) {
      case 'error': return 'border-red-200 bg-red-50';
      case 'warning': return 'border-yellow-200 bg-yellow-50';
      case 'info': return 'border-blue-200 bg-blue-50';
      default: return 'border-gray-200 bg-gray-50';
    }
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
          <h1 className="text-2xl font-semibold text-gray-900">Monitoreo del Sistema</h1>
          <p className="mt-2 text-sm text-gray-700">
            Estado de salud y rendimiento del sistema
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
            />
            <span className="ml-2 text-sm text-gray-700">Actualización automática</span>
          </label>
        </div>
      </div>

      {/* Estado de salud general */}
      {healthStatus && (
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">Estado de Salud</h3>
            <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(healthStatus.status)}`}>
              {getStatusIcon(healthStatus.status)}
              <span className="ml-2 capitalize">{healthStatus.status}</span>
            </div>
          </div>
          
          <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{healthStatus.active_users}</div>
              <div className="text-sm text-gray-500">Usuarios Activos</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{healthStatus.performance_metrics.total_requests}</div>
              <div className="text-sm text-gray-500">Total de Peticiones</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{healthStatus.performance_metrics.error_rate}%</div>
              <div className="text-sm text-gray-500">Tasa de Errores</div>
            </div>
          </div>
        </div>
      )}

      {/* Métricas del sistema */}
      {systemMetrics && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Memoria */}
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center">
              <ServerIcon className="h-8 w-8 text-blue-600" />
              <h3 className="ml-3 text-lg font-medium text-gray-900">Memoria</h3>
            </div>
            <div className="mt-4">
              <div className="flex justify-between text-sm text-gray-600">
                <span>Usado: {systemMetrics.memory.used_gb} GB</span>
                <span>{systemMetrics.memory.used_percent.toFixed(1)}%</span>
              </div>
              <div className="mt-2 bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${systemMetrics.memory.used_percent > 80 ? 'bg-red-500' : systemMetrics.memory.used_percent > 60 ? 'bg-yellow-500' : 'bg-green-500'}`}
                  style={{ width: `${systemMetrics.memory.used_percent}%` }}
                ></div>
              </div>
              <div className="mt-2 text-sm text-gray-500">
                Disponible: {systemMetrics.memory.available_gb} GB
              </div>
            </div>
          </div>

          {/* CPU */}
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center">
              <CpuChipIcon className="h-8 w-8 text-green-600" />
              <h3 className="ml-3 text-lg font-medium text-gray-900">CPU</h3>
            </div>
            <div className="mt-4">
              <div className="flex justify-between text-sm text-gray-600">
                <span>Uso</span>
                <span>{systemMetrics.cpu.percent.toFixed(1)}%</span>
              </div>
              <div className="mt-2 bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${systemMetrics.cpu.percent > 80 ? 'bg-red-500' : systemMetrics.cpu.percent > 60 ? 'bg-yellow-500' : 'bg-green-500'}`}
                  style={{ width: `${systemMetrics.cpu.percent}%` }}
                ></div>
              </div>
            </div>
          </div>

          {/* Disco */}
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center">
              <ChartBarIcon className="h-8 w-8 text-purple-600" />
              <h3 className="ml-3 text-lg font-medium text-gray-900">Disco</h3>
            </div>
            <div className="mt-4">
              <div className="flex justify-between text-sm text-gray-600">
                <span>Usado: {systemMetrics.disk.used_gb} GB</span>
                <span>{systemMetrics.disk.used_percent.toFixed(1)}%</span>
              </div>
              <div className="mt-2 bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${systemMetrics.disk.used_percent > 80 ? 'bg-red-500' : systemMetrics.disk.used_percent > 60 ? 'bg-yellow-500' : 'bg-green-500'}`}
                  style={{ width: `${systemMetrics.disk.used_percent}%` }}
                ></div>
              </div>
              <div className="mt-2 text-sm text-gray-500">
                Total: {systemMetrics.disk.total_gb} GB
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Métricas de rendimiento */}
      {performanceMetrics && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Rendimiento</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{performanceMetrics.avg_response_time}s</div>
              <div className="text-sm text-gray-500">Tiempo Promedio</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{performanceMetrics.min_response_time}s</div>
              <div className="text-sm text-gray-500">Tiempo Mínimo</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">{performanceMetrics.max_response_time}s</div>
              <div className="text-sm text-gray-500">Tiempo Máximo</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{performanceMetrics.total_requests}</div>
              <div className="text-sm text-gray-500">Total Peticiones</div>
            </div>
          </div>
        </div>
      )}

      {/* Alertas */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Alertas del Sistema</h3>
        {alerts.length > 0 ? (
          <div className="space-y-3">
            {alerts.map((alert, index) => (
              <div key={index} className={`border rounded-lg p-4 ${getAlertColor(alert.type)}`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      alert.type === 'error' ? 'text-red-800 bg-red-200' :
                      alert.type === 'warning' ? 'text-yellow-800 bg-yellow-200' :
                      'text-blue-800 bg-blue-200'
                    }`}>
                      {alert.type}
                    </div>
                    <span className="ml-3 text-sm font-medium text-gray-900">{alert.message}</span>
                  </div>
                  <div className="text-sm text-gray-500">
                    {format(new Date(alert.timestamp), 'HH:mm')}
                  </div>
                </div>
                <div className="mt-2 text-sm text-gray-600">
                  Valor: {alert.value} | Categoría: {alert.category}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <CheckCircleIcon className="mx-auto h-12 w-12 text-green-400" />
            <p className="mt-2">No hay alertas activas</p>
          </div>
        )}
      </div>

      {/* Información de actualización */}
      <div className="text-center text-sm text-gray-500">
        Última actualización: {healthStatus ? format(new Date(healthStatus.timestamp), 'dd/MM/yyyy HH:mm:ss', { locale: es }) : 'N/A'}
      </div>
    </div>
  );
};

export default Monitoreo;
