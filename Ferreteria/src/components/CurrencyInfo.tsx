import { useState, useEffect } from 'react';
import { 
  updateExchangeRates, 
  getLastUpdateTime, 
  currencies, 
  setCurrentCurrency,
  getCurrencyCode
} from '../config/currency';
import { ArrowPathIcon, CheckCircleIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';

/**
 * Componente que muestra información sobre las tasas de cambio
 * y permite cambiar la moneda del sistema
 */
export default function CurrencyInfo() {
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [isUpdating, setIsUpdating] = useState(false);
  const [updateStatus, setUpdateStatus] = useState<'success' | 'error' | null>(null);
  const [currentCurrency, setCurrentCurrencyState] = useState('COP');

  useEffect(() => {
    try {
      setLastUpdate(getLastUpdateTime());
      setCurrentCurrencyState(getCurrencyCode());
    } catch (error) {
      console.error('Error inicializando CurrencyInfo:', error);
    }
  }, []);

  const handleUpdateRates = async () => {
    try {
      setIsUpdating(true);
      setUpdateStatus(null);

      const success = await updateExchangeRates();
      
      setIsUpdating(false);
      setUpdateStatus(success ? 'success' : 'error');
      setLastUpdate(getLastUpdateTime());

      // Limpiar mensaje después de 3 segundos
      setTimeout(() => setUpdateStatus(null), 3000);
    } catch (error) {
      console.error('Error al actualizar tasas:', error);
      setIsUpdating(false);
      setUpdateStatus('error');
    }
  };

  const handleCurrencyChange = (code: string) => {
    try {
      setCurrentCurrency(code);
      setCurrentCurrencyState(code);
      window.location.reload(); // Recargar para aplicar cambios
    } catch (error) {
      console.error('Error al cambiar moneda:', error);
    }
  };

  const formatLastUpdate = () => {
    try {
      if (!lastUpdate) return 'Nunca';
      
      const now = new Date();
      const diffMs = now.getTime() - lastUpdate.getTime();
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
      const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));

      if (diffHours < 1) {
        return `Hace ${diffMinutes} minutos`;
      } else if (diffHours < 24) {
        return `Hace ${diffHours} horas`;
      } else {
        return lastUpdate.toLocaleDateString('es-CO', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
      }
    } catch (error) {
      console.error('Error formateando fecha:', error);
      return 'Desconocido';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Configuración de Moneda</h3>
        <button
          onClick={handleUpdateRates}
          disabled={isUpdating}
          className={`
            flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium
            transition-colors
            ${isUpdating 
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
              : 'bg-blue-50 text-blue-600 hover:bg-blue-100'
            }
          `}
        >
          <ArrowPathIcon className={`h-4 w-4 ${isUpdating ? 'animate-spin' : ''}`} />
          {isUpdating ? 'Actualizando...' : 'Actualizar Tasas'}
        </button>
      </div>

      {/* Selector de Moneda */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Moneda del Sistema
        </label>
        <select
          value={currentCurrency}
          onChange={(e) => handleCurrencyChange(e.target.value)}
          className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          {Object.values(currencies).map((currency) => (
            <option key={currency.code} value={currency.code}>
              {currency.symbol} {currency.name} ({currency.code})
            </option>
          ))}
        </select>
        <p className="mt-1 text-xs text-gray-500">
          Todos los precios se mostrarán en esta moneda
        </p>
      </div>

      {/* Estado de Actualización */}
      {updateStatus && (
        <div className={`
          mb-4 p-3 rounded-md flex items-center gap-2
          ${updateStatus === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}
        `}>
          {updateStatus === 'success' ? (
            <>
              <CheckCircleIcon className="h-5 w-5" />
              <span className="text-sm">Tasas actualizadas correctamente</span>
            </>
          ) : (
            <>
              <ExclamationTriangleIcon className="h-5 w-5" />
              <span className="text-sm">Error al actualizar tasas (usando valores guardados)</span>
            </>
          )}
        </div>
      )}

      {/* Información de Tasas Actuales */}
      <div className="space-y-2">
        <p className="text-sm text-gray-600 mb-3">
          Tasas de cambio actuales (base: 1 USD):
        </p>
        
        <div className="grid grid-cols-2 gap-3">
          {Object.entries(currencies)
            .filter(([code]) => code !== 'USD')
            .map(([code, currency]) => (
              <div 
                key={code}
                className={`
                  p-3 rounded-md border
                  ${currentCurrency === code 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-200 bg-gray-50'
                  }
                `}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700">
                    {currency.symbol} {code}
                  </span>
                  <span className="text-sm font-semibold text-gray-900">
                    {currency.exchangeRate.toLocaleString('es-CO', {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2
                    })}
                  </span>
                </div>
              </div>
            ))}
        </div>

        <p className="text-xs text-gray-500 mt-3">
          Última actualización: {formatLastUpdate()}
        </p>
        <p className="text-xs text-gray-400">
          Las tasas se actualizan automáticamente cada 24 horas
        </p>
      </div>
    </div>
  );
}
