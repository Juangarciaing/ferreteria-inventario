import React, { useState, useEffect } from 'react';
import { 
  CloudArrowDownIcon, 
  CloudArrowUpIcon, 
  DocumentArrowDownIcon,
  TrashIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import toast from 'react-hot-toast';

interface Backup {
  filename: string;
  path: string;
  size: number;
  created: string;
  type: 'database' | 'full';
}

interface BackupStats {
  total_backups: number;
  total_size: number;
  total_size_mb: number;
  database_backups: number;
  full_backups: number;
  oldest_backup: string | null;
  newest_backup: string | null;
}

const Backup: React.FC = () => {
  const [backups, setBackups] = useState<Backup[]>([]);
  const [stats, setStats] = useState<BackupStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [creatingBackup, setCreatingBackup] = useState(false);
  const [selectedBackup, setSelectedBackup] = useState<Backup | null>(null);
  const [showRestoreModal, setShowRestoreModal] = useState(false);

  useEffect(() => {
    loadBackups();
  }, []);

  const loadBackups = async () => {
    try {
      setLoading(true);
      
      // Simular datos de backup
      const mockBackups: Backup[] = [
        {
          filename: 'database_backup_20241201_143022.json',
          path: '/backups/database_backup_20241201_143022.json',
          size: 1024000,
          created: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
          type: 'database'
        },
        {
          filename: 'full_backup_20241201_120000.zip',
          path: '/backups/full_backup_20241201_120000.zip',
          size: 5120000,
          created: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
          type: 'full'
        },
        {
          filename: 'database_backup_20241130_143022.json',
          path: '/backups/database_backup_20241130_143022.json',
          size: 980000,
          created: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
          type: 'database'
        }
      ];

      const mockStats: BackupStats = {
        total_backups: 3,
        total_size: 7124000,
        total_size_mb: 6.8,
        database_backups: 2,
        full_backups: 1,
        oldest_backup: mockBackups[2].created,
        newest_backup: mockBackups[0].created
      };

      setBackups(mockBackups);
      setStats(mockStats);
      
    } catch (error) {
      toast.error('Error al cargar backups');
    } finally {
      setLoading(false);
    }
  };

  const createBackup = async (type: 'database' | 'full') => {
    try {
      setCreatingBackup(true);
      
      // Simular creación de backup
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      toast.success(`Backup ${type === 'database' ? 'de base de datos' : 'completo'} creado exitosamente`);
      loadBackups();
      
    } catch (error) {
      toast.error('Error al crear backup');
    } finally {
      setCreatingBackup(false);
    }
  };

  const downloadBackup = (backup: Backup) => {
    try {
      // Simular descarga
      const link = document.createElement('a');
      link.href = '#';
      link.download = backup.filename;
      link.click();
      
      toast.success('Descarga iniciada');
    } catch (error) {
      toast.error('Error al descargar backup');
    }
  };

  const restoreBackup = async (backup: Backup) => {
    try {
      // Simular restauración
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      toast.success('Backup restaurado exitosamente');
      setShowRestoreModal(false);
      setSelectedBackup(null);
      
    } catch (error) {
      toast.error('Error al restaurar backup');
    }
  };

  const deleteBackup = async (backup: Backup) => {
    if (!confirm(`¿Estás seguro de que quieres eliminar el backup ${backup.filename}?`)) {
      return;
    }

    try {
      // Simular eliminación
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      toast.success('Backup eliminado exitosamente');
      loadBackups();
      
    } catch (error) {
      toast.error('Error al eliminar backup');
    }
  };

  const cleanupOldBackups = async () => {
    try {
      // Simular limpieza
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      toast.success('Backups antiguos eliminados exitosamente');
      loadBackups();
      
    } catch (error) {
      toast.error('Error al limpiar backups antiguos');
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getBackupTypeColor = (type: string) => {
    return type === 'full' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800';
  };

  const getBackupTypeLabel = (type: string) => {
    return type === 'full' ? 'Completo' : 'Base de Datos';
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
          <h1 className="text-2xl font-semibold text-gray-900">Gestión de Backups</h1>
          <p className="mt-2 text-sm text-gray-700">
            Crear, restaurar y gestionar backups del sistema
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex space-x-3">
          <button
            onClick={() => createBackup('database')}
            disabled={creatingBackup}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
          >
            <CloudArrowDownIcon className="h-4 w-4 mr-2" />
            {creatingBackup ? 'Creando...' : 'Backup BD'}
          </button>
          <button
            onClick={() => createBackup('full')}
            disabled={creatingBackup}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <CloudArrowDownIcon className="h-4 w-4 mr-2" />
            {creatingBackup ? 'Creando...' : 'Backup Completo'}
          </button>
        </div>
      </div>

      {/* Estadísticas */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <DocumentArrowDownIcon className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Total de Backups
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {stats.total_backups}
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
                      Tamaño Total
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {stats.total_size_mb} MB
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
                  <CheckCircleIcon className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Backups BD
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {stats.database_backups}
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
                  <InformationCircleIcon className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Backups Completos
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {stats.full_backups}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Acciones rápidas */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Acciones Rápidas</h3>
        <div className="flex space-x-4">
          <button
            onClick={cleanupOldBackups}
            className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <TrashIcon className="h-4 w-4 mr-2" />
            Limpiar Antiguos
          </button>
        </div>
      </div>

      {/* Lista de backups */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Backups Disponibles ({backups.length})
          </h3>
          
          {backups.length > 0 ? (
            <div className="space-y-3">
              {backups.map((backup, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="flex-shrink-0">
                        <DocumentArrowDownIcon className="h-8 w-8 text-gray-400" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {backup.filename}
                          </p>
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getBackupTypeColor(backup.type)}`}>
                            {getBackupTypeLabel(backup.type)}
                          </span>
                        </div>
                        <div className="mt-1 flex items-center space-x-4 text-sm text-gray-500">
                          <span>{formatFileSize(backup.size)}</span>
                          <span>{format(new Date(backup.created), 'dd/MM/yyyy HH:mm', { locale: es })}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => downloadBackup(backup)}
                        className="text-blue-600 hover:text-blue-900 text-sm font-medium"
                      >
                        Descargar
                      </button>
                      <button
                        onClick={() => {
                          setSelectedBackup(backup);
                          setShowRestoreModal(true);
                        }}
                        className="text-green-600 hover:text-green-900 text-sm font-medium"
                      >
                        Restaurar
                      </button>
                      <button
                        onClick={() => deleteBackup(backup)}
                        className="text-red-600 hover:text-red-900 text-sm font-medium"
                      >
                        Eliminar
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <DocumentArrowDownIcon className="mx-auto h-12 w-12 text-gray-400" />
              <p className="mt-2">No hay backups disponibles</p>
            </div>
          )}
        </div>
      </div>

      {/* Modal de restauración */}
      {showRestoreModal && selectedBackup && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-900 bg-opacity-75 transition-opacity" onClick={() => setShowRestoreModal(false)} />

            <span className="hidden sm:inline-block sm:align-middle sm:h-screen">&#8203;</span>

            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg leading-6 font-medium text-gray-900">
                    Restaurar Backup
                  </h3>
                  <button
                    onClick={() => setShowRestoreModal(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                <div className="mb-4">
                  <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
                    <div className="flex">
                      <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400" />
                      <div className="ml-3">
                        <h3 className="text-sm font-medium text-yellow-800">
                          Advertencia
                        </h3>
                        <div className="mt-2 text-sm text-yellow-700">
                          <p>
                            Restaurar este backup reemplazará todos los datos actuales del sistema. 
                            Esta acción no se puede deshacer.
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="mb-4">
                  <p className="text-sm text-gray-600">
                    <strong>Archivo:</strong> {selectedBackup.filename}
                  </p>
                  <p className="text-sm text-gray-600">
                    <strong>Tipo:</strong> {getBackupTypeLabel(selectedBackup.type)}
                  </p>
                  <p className="text-sm text-gray-600">
                    <strong>Tamaño:</strong> {formatFileSize(selectedBackup.size)}
                  </p>
                  <p className="text-sm text-gray-600">
                    <strong>Fecha:</strong> {format(new Date(selectedBackup.created), 'dd/MM/yyyy HH:mm', { locale: es })}
                  </p>
                </div>

                <div className="flex justify-end space-x-3">
                  <button
                    onClick={() => setShowRestoreModal(false)}
                    className="px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    Cancelar
                  </button>
                  <button
                    onClick={() => restoreBackup(selectedBackup)}
                    className="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                  >
                    Restaurar
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Backup;
