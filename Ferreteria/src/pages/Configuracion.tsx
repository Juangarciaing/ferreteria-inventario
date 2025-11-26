import React, { useState, useEffect } from 'react';
import { 
  CogIcon, 
  BuildingStorefrontIcon, 
  CurrencyDollarIcon, 
  BellIcon,
  ShieldCheckIcon,
  DocumentTextIcon,
  CloudArrowUpIcon,
  UserCircleIcon,
  KeyIcon,
  CheckCircleIcon,
  ExclamationCircleIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';
import CurrencyInfo from '../components/CurrencyInfo';

const Configuracion: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('perfil');
  const [saving, setSaving] = useState(false);
  const [passwordModal, setPasswordModal] = useState(false);
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [config, setConfig] = useState({
    // Configuración general
    nombreEmpresa: 'Ferretería El Martillo',
    direccion: 'Av. Principal 123',
    telefono: '+1234567890',
    email: 'info@ferreteria.com',
    rut: '12345678-9',
    
    // Configuración de inventario
    alertaStockBajo: true,
    nivelStockCritico: 5,
    actualizacionAutomaticaPrecios: false,
    
    // Configuración de ventas
    iva: 19,
    descuentoMaximo: 50,
    permitirVentaSinStock: false,
    
    // Configuración de notificaciones
    notificacionesEmail: true,
    notificacionesVentas: true,
    notificacionesStock: true,
    
    // Configuración de backup
    backupAutomatico: true,
    frecuenciaBackup: 'diario',
  });

  // Cargar configuración guardada al montar el componente
  useEffect(() => {
    const configGuardada = localStorage.getItem('ferreteria_config');
    if (configGuardada) {
      try {
        const configParsed = JSON.parse(configGuardada);
        setConfig(prev => ({ ...prev, ...configParsed }));
      } catch (error) {
        console.error('Error al cargar configuración guardada:', error);
      }
    }
  }, []);

  const tabs = [
    { id: 'perfil', name: 'Mi Perfil', icon: UserCircleIcon },
    { id: 'empresa', name: 'Empresa', icon: BuildingStorefrontIcon },
    { id: 'moneda', name: 'Moneda', icon: CurrencyDollarIcon },
    { id: 'inventario', name: 'Inventario', icon: DocumentTextIcon },
    { id: 'ventas', name: 'Ventas', icon: CurrencyDollarIcon },
    { id: 'notificaciones', name: 'Notificaciones', icon: BellIcon },
    { id: 'seguridad', name: 'Seguridad', icon: ShieldCheckIcon },
    { id: 'backup', name: 'Backup', icon: CloudArrowUpIcon },
  ];

  const handleChangePassword = async () => {
    if (!passwordData.currentPassword || !passwordData.newPassword || !passwordData.confirmPassword) {
      toast.error('Por favor complete todos los campos');
      return;
    }

    if (passwordData.newPassword !== passwordData.confirmPassword) {
      toast.error('Las contraseñas no coinciden');
      return;
    }

    if (passwordData.newPassword.length < 6) {
      toast.error('La contraseña debe tener al menos 6 caracteres');
      return;
    }

    if (passwordData.newPassword === passwordData.currentPassword) {
      toast.error('La nueva contraseña debe ser diferente a la actual');
      return;
    }

    setSaving(true);
    try {
      // Llamada al backend para cambiar la contraseña
      if (user?.id) {
        const { apiClient } = await import('../lib/api');
        await apiClient.authFetch(`/usuarios/${user.id}/change-password`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            current_password: passwordData.currentPassword,
            new_password: passwordData.newPassword
          })
        });
        
        toast.success('✅ Contraseña actualizada correctamente');
        setPasswordModal(false);
        setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
      } else {
        toast.error('No se pudo obtener la información del usuario');
      }
    } catch (error: any) {
      console.error('Error al cambiar contraseña:', error);
      const mensaje = error?.response?.data?.message || error?.message || 'Error al cambiar la contraseña';
      toast.error(mensaje);
    } finally {
      setSaving(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      // Guardar configuración en localStorage
      localStorage.setItem('ferreteria_config', JSON.stringify(config));
      
      // Aquí podrías guardar configuración específica del usuario en el backend si es necesario
      // Por ahora solo guardamos en localStorage
      
      await new Promise(resolve => setTimeout(resolve, 500));
      toast.success('✅ Configuración guardada correctamente');
    } catch (error: any) {
      console.error('Error al guardar configuración:', error);
      toast.error('Error al guardar la configuración');
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (field: string, value: string | number | boolean) => {
    setConfig(prev => ({ ...prev, [field]: value }));
  };

  const renderPerfilTab = () => (
    <div className="space-y-6">
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100">
        <div className="flex items-center space-x-4">
          <div className="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full p-4">
            <UserCircleIcon className="h-16 w-16 text-white" />
          </div>
          <div>
            <h3 className="text-2xl font-bold text-gray-900">{user?.nombre || 'Usuario'}</h3>
            <p className="text-gray-600">{user?.email}</p>
            <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium mt-2 ${
              user?.rol === 'admin' 
                ? 'bg-purple-100 text-purple-800' 
                : 'bg-blue-100 text-blue-800'
            }`}>
              {user?.rol === 'admin' ? '👑 Administrador' : '👤 Usuario'}
            </span>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <CogIcon className="h-5 w-5 mr-2 text-blue-500" />
          Información Personal
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nombre Completo
            </label>
            <input
              type="text"
              value={user?.nombre || ''}
              readOnly
              className="block w-full border border-gray-300 rounded-lg shadow-sm py-2.5 px-4 bg-gray-50 text-gray-700 cursor-not-allowed"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <input
              type="email"
              value={user?.email || ''}
              readOnly
              className="block w-full border border-gray-300 rounded-lg shadow-sm py-2.5 px-4 bg-gray-50 text-gray-700 cursor-not-allowed"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Rol en el Sistema
            </label>
            <input
              type="text"
              value={user?.rol === 'admin' ? 'Administrador' : 'Usuario'}
              readOnly
              className="block w-full border border-gray-300 rounded-lg shadow-sm py-2.5 px-4 bg-gray-50 text-gray-700 cursor-not-allowed"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Estado de la Cuenta
            </label>
            <div className="flex items-center space-x-2">
              <CheckCircleIcon className="h-5 w-5 text-green-500" />
              <span className="text-green-700 font-medium">Activa</span>
            </div>
          </div>
        </div>

        <div className="mt-6 pt-6 border-t border-gray-200">
          <button
            onClick={() => setPasswordModal(true)}
            className="inline-flex items-center px-4 py-2.5 border border-transparent text-sm font-medium rounded-lg text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 shadow-lg transition-all"
          >
            <KeyIcon className="h-5 w-5 mr-2" />
            Cambiar Contraseña
          </button>
        </div>
      </div>
    </div>
  );

  const renderEmpresaTab = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
          <BuildingStorefrontIcon className="h-6 w-6 mr-2 text-purple-500" />
          Información de la Empresa
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nombre de la Empresa *
            </label>
            <input
              type="text"
              value={config.nombreEmpresa}
              onChange={(e) => handleChange('nombreEmpresa', e.target.value)}
              className="block w-full border border-gray-300 rounded-lg shadow-sm py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              placeholder="Ej: Ferretería El Martillo"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              RUT/NIT *
            </label>
            <input
              type="text"
              value={config.rut}
              onChange={(e) => handleChange('rut', e.target.value)}
              className="block w-full border border-gray-300 rounded-lg shadow-sm py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              placeholder="12345678-9"
            />
          </div>
          
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Dirección *
            </label>
            <input
              type="text"
              value={config.direccion}
              onChange={(e) => handleChange('direccion', e.target.value)}
              className="block w-full border border-gray-300 rounded-lg shadow-sm py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              placeholder="Av. Principal 123, Ciudad"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Teléfono *
            </label>
            <input
              type="tel"
              value={config.telefono}
              onChange={(e) => handleChange('telefono', e.target.value)}
              className="block w-full border border-gray-300 rounded-lg shadow-sm py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              placeholder="+1234567890"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email de Contacto *
            </label>
            <input
              type="email"
              value={config.email}
              onChange={(e) => handleChange('email', e.target.value)}
              className="block w-full border border-gray-300 rounded-lg shadow-sm py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              placeholder="contacto@empresa.com"
            />
          </div>
        </div>
        <p className="text-xs text-gray-500 mt-4">* Campos requeridos</p>
      </div>
    </div>
  );

  const renderMonedaTab = () => {
    return (
      <div className="space-y-6">
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-2 flex items-center">
            <CurrencyDollarIcon className="h-6 w-6 mr-2 text-blue-600" />
            Sistema de Monedas
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            Las tasas de cambio se actualizan automáticamente cada 24 horas desde APIs externas.
            Todos los precios en el sistema se mostrarán en la moneda seleccionada.
          </p>
        </div>
        
        <CurrencyInfo />
        
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start">
            <ExclamationCircleIcon className="h-5 w-5 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" />
            <div className="text-sm text-yellow-800">
              <p className="font-medium mb-1">Información importante:</p>
              <ul className="list-disc list-inside space-y-1 text-xs">
                <li>Las tasas de cambio son referenciales y pueden variar</li>
                <li>Se utilizan APIs públicas gratuitas para obtener las tasas</li>
                <li>Si no hay conexión a internet, se usan las últimas tasas guardadas</li>
                <li>Cambiar la moneda recargará la aplicación para aplicar los cambios</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderInventarioTab = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
          <DocumentTextIcon className="h-6 w-6 mr-2 text-green-500" />
          Configuración de Inventario
        </h3>
        <div className="space-y-6">
          {/* Alertas de Stock */}
          <div className="flex items-start justify-between p-4 bg-green-50 rounded-lg border border-green-100">
            <div className="flex-1">
              <label className="text-sm font-semibold text-gray-900 flex items-center">
                <BellIcon className="h-5 w-5 mr-2 text-green-600" />
                Alertas de Stock Bajo
              </label>
              <p className="text-sm text-gray-600 mt-1">
                Recibir notificaciones cuando el stock esté por debajo del mínimo configurado
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer ml-4">
              <input
                type="checkbox"
                checked={config.alertaStockBajo}
                onChange={(e) => handleChange('alertaStockBajo', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-green-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
            </label>
          </div>
          
          {/* Nivel Stock Crítico */}
          <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-100">
            <label className="block text-sm font-semibold text-gray-900 mb-3 flex items-center">
              <ExclamationCircleIcon className="h-5 w-5 mr-2 text-yellow-600" />
              Nivel de Stock Crítico
            </label>
            <div className="flex items-center space-x-4">
              <input
                type="number"
                min="0"
                max="100"
                value={config.nivelStockCritico}
                onChange={(e) => handleChange('nivelStockCritico', parseInt(e.target.value))}
                className="block w-32 border border-gray-300 rounded-lg shadow-sm py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent transition-all"
              />
              <span className="text-sm text-gray-600">
                unidades (los productos con stock igual o menor a este valor mostrarán alerta)
              </span>
            </div>
          </div>
          
          {/* Actualización Automática */}
          <div className="flex items-start justify-between p-4 bg-blue-50 rounded-lg border border-blue-100">
            <div className="flex-1">
              <label className="text-sm font-semibold text-gray-900 flex items-center">
                <CogIcon className="h-5 w-5 mr-2 text-blue-600" />
                Actualización Automática de Precios
              </label>
              <p className="text-sm text-gray-600 mt-1">
                Actualizar precios de productos automáticamente según información de proveedores
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer ml-4">
              <input
                type="checkbox"
                checked={config.actualizacionAutomaticaPrecios}
                onChange={(e) => handleChange('actualizacionAutomaticaPrecios', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
        </div>
      </div>
    </div>
  );

  const renderVentasTab = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Configuración de Ventas</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              IVA (%)
            </label>
            <input
              type="number"
              min="0"
              max="100"
              step="0.1"
              value={config.iva}
              onChange={(e) => handleChange('iva', parseFloat(e.target.value))}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Descuento Máximo (%)
            </label>
            <input
              type="number"
              min="0"
              max="100"
              value={config.descuentoMaximo}
              onChange={(e) => handleChange('descuentoMaximo', parseInt(e.target.value))}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
        
        <div className="flex items-center justify-between">
          <div>
            <label className="text-sm font-medium text-gray-700">
              Permitir Ventas sin Stock
            </label>
            <p className="text-sm text-gray-500">
              Permitir registrar ventas aunque no haya stock disponible
            </p>
          </div>
          <input
            type="checkbox"
            checked={config.permitirVentaSinStock}
            onChange={(e) => handleChange('permitirVentaSinStock', e.target.checked)}
            className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
          />
        </div>
      </div>
    </div>
  );

  const renderNotificacionesTab = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Configuración de Notificaciones</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">
                Notificaciones por Email
              </label>
              <p className="text-sm text-gray-500">
                Recibir notificaciones importantes por correo electrónico
              </p>
            </div>
            <input
              type="checkbox"
              checked={config.notificacionesEmail}
              onChange={(e) => handleChange('notificacionesEmail', e.target.checked)}
              className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
            />
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">
                Notificaciones de Ventas
              </label>
              <p className="text-sm text-gray-500">
                Notificar cuando se registren ventas importantes
              </p>
            </div>
            <input
              type="checkbox"
              checked={config.notificacionesVentas}
              onChange={(e) => handleChange('notificacionesVentas', e.target.checked)}
              className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
            />
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">
                Notificaciones de Stock
              </label>
              <p className="text-sm text-gray-500">
                Notificar cuando productos tengan stock bajo
              </p>
            </div>
            <input
              type="checkbox"
              checked={config.notificacionesStock}
              onChange={(e) => handleChange('notificacionesStock', e.target.checked)}
              className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
            />
          </div>
        </div>
      </div>
    </div>
  );

  const renderSeguridadTab = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Configuración de Seguridad</h3>
        <div className="space-y-4">
          <div>
            <button className="w-full md:w-auto px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
              Cambiar Contraseña
            </button>
          </div>
          
          <div>
            <button className="w-full md:w-auto px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
              Ver Sesiones Activas
            </button>
          </div>
          
          <div>
            <button className="w-full md:w-auto px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
              Descargar Logs de Auditoría
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderBackupTab = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Configuración de Backup</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">
                Backup Automático
              </label>
              <p className="text-sm text-gray-500">
                Realizar copias de seguridad automáticamente
              </p>
            </div>
            <input
              type="checkbox"
              checked={config.backupAutomatico}
              onChange={(e) => handleChange('backupAutomatico', e.target.checked)}
              className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Frecuencia de Backup
            </label>
            <select 
              value={config.frecuenciaBackup}
              onChange={(e) => handleChange('frecuenciaBackup', e.target.value)}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="diario">Diario</option>
              <option value="semanal">Semanal</option>
              <option value="mensual">Mensual</option>
            </select>
          </div>
          
          <div className="flex space-x-4">
            <button className="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500">
              Crear Backup Ahora
            </button>
            
            <button className="px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
              Ver Backups Existentes
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'perfil':
        return renderPerfilTab();
      case 'empresa':
        return renderEmpresaTab();
      case 'moneda':
        return renderMonedaTab();
      case 'inventario':
        return renderInventarioTab();
      case 'ventas':
        return renderVentasTab();
      case 'notificaciones':
        return renderNotificacionesTab();
      case 'seguridad':
        return renderSeguridadTab();
      case 'backup':
        return renderBackupTab();
      default:
        return renderPerfilTab();
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">⚙️ Configuración</h1>
          <p className="text-gray-600 mt-1">Administra las preferencias y ajustes del sistema</p>
        </div>
        <button
          onClick={handleSave}
          disabled={saving}
          className={`inline-flex items-center px-5 py-2.5 border border-transparent text-sm font-medium rounded-lg shadow-lg text-white transition-all ${
            saving
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'
          }`}
        >
          {saving ? (
            <>
              <CogIcon className="animate-spin h-5 w-5 mr-2" />
              Guardando...
            </>
          ) : (
            <>
              <CheckCircleIcon className="h-5 w-5 mr-2" />
              Guardar Cambios
            </>
          )}
        </button>
      </div>

      {/* Tabs Container */}
      <div className="bg-white shadow-xl rounded-xl border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-4 px-6 overflow-x-auto" aria-label="Tabs">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-3 border-b-2 font-medium text-sm whitespace-nowrap flex items-center space-x-2 transition-all ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="h-5 w-5" />
                <span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {renderTabContent()}
        </div>
      </div>

      {/* Modal de Cambio de Contraseña */}
      {passwordModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setPasswordModal(false)} />
            <span className="hidden sm:inline-block sm:align-middle sm:h-screen">&#8203;</span>
            <div className="inline-block align-bottom bg-white rounded-xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
              {/* Header */}
              <div className="bg-gradient-to-r from-blue-500 to-indigo-600 px-6 py-5">
                <div className="flex items-center">
                  <KeyIcon className="h-8 w-8 text-white mr-3" />
                  <h3 className="text-2xl font-bold text-white">
                    Cambiar Contraseña
                  </h3>
                </div>
              </div>

              {/* Body */}
              <div className="bg-white px-6 py-5">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Contraseña Actual *
                    </label>
                    <input
                      type="password"
                      value={passwordData.currentPassword}
                      onChange={(e) => setPasswordData({ ...passwordData, currentPassword: e.target.value })}
                      className="block w-full border border-gray-300 rounded-lg shadow-sm py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Ingrese su contraseña actual"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Nueva Contraseña *
                    </label>
                    <input
                      type="password"
                      value={passwordData.newPassword}
                      onChange={(e) => setPasswordData({ ...passwordData, newPassword: e.target.value })}
                      className="block w-full border border-gray-300 rounded-lg shadow-sm py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Mínimo 6 caracteres"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Confirmar Nueva Contraseña *
                    </label>
                    <input
                      type="password"
                      value={passwordData.confirmPassword}
                      onChange={(e) => setPasswordData({ ...passwordData, confirmPassword: e.target.value })}
                      className="block w-full border border-gray-300 rounded-lg shadow-sm py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Repita la nueva contraseña"
                    />
                  </div>

                  {passwordData.newPassword && passwordData.confirmPassword && passwordData.newPassword !== passwordData.confirmPassword && (
                    <div className="flex items-center text-red-600 text-sm">
                      <ExclamationCircleIcon className="h-5 w-5 mr-2" />
                      Las contraseñas no coinciden
                    </div>
                  )}
                </div>
              </div>

              {/* Footer */}
              <div className="bg-gray-50 px-6 py-4 flex flex-col sm:flex-row-reverse gap-3">
                <button
                  type="button"
                  onClick={handleChangePassword}
                  disabled={saving}
                  className={`w-full sm:w-auto inline-flex justify-center items-center rounded-lg border border-transparent shadow-sm px-5 py-2.5 text-base font-medium text-white transition-all ${
                    saving
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'
                  }`}
                >
                  {saving ? 'Cambiando...' : 'Cambiar Contraseña'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setPasswordModal(false);
                    setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
                  }}
                  disabled={saving}
                  className="w-full sm:w-auto inline-flex justify-center rounded-lg border border-gray-300 shadow-sm px-5 py-2.5 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Configuracion;