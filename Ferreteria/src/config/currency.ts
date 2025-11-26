// Configuración de monedas y tasas de cambio
// APIs para obtener tasas actualizadas
const EXCHANGE_RATE_API = 'https://api.frankfurter.app/latest?from=USD';
const BACKUP_API = 'https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/usd.json';

export interface Currency {
  code: string;
  symbol: string;
  name: string;
  exchangeRate: number; // Tasa con respecto al USD
}

export const currencies: Record<string, Currency> = {
  USD: {
    code: 'USD',
    symbol: '$',
    name: 'Dólar Estadounidense',
    exchangeRate: 1,
  },
  COP: {
    code: 'COP',
    symbol: '$',
    name: 'Peso Colombiano',
    exchangeRate: 3746.83, // Valor actualizado 12 nov 2025
  },
  EUR: {
    code: 'EUR',
    symbol: '€',
    name: 'Euro',
    exchangeRate: 0.92, // Valor inicial, se actualiza desde API
  },
  MXN: {
    code: 'MXN',
    symbol: '$',
    name: 'Peso Mexicano',
    exchangeRate: 17, // Valor inicial, se actualiza desde API
  },
};

// Moneda por defecto del sistema
export const DEFAULT_CURRENCY = 'COP'; // Cambiado a COP (Peso Colombiano)

// Estado de última actualización
let lastUpdate: Date | null = null;
let isUpdating = false;

/**
 * Actualiza las tasas de cambio desde la API
 * Se ejecuta automáticamente al cargar y cada 24 horas
 */
export const updateExchangeRates = async (): Promise<boolean> => {
  // Evitar múltiples actualizaciones simultáneas
  if (isUpdating) {
    return false;
  }

  try {
    isUpdating = true;
    console.log('🔄 Actualizando tasas de cambio...');

    let rates: any = null;

    // Intentar con la API principal (Frankfurter)
    try {
      const response = await fetch(EXCHANGE_RATE_API);
      if (response.ok) {
        const data = await response.json();
        rates = data.rates;
      }
    } catch (error) {
      console.warn('⚠️ API principal falló, intentando con respaldo...');
    }

    // Si falla, intentar con API de respaldo
    if (!rates) {
      try {
        const response = await fetch(BACKUP_API);
        if (response.ok) {
          const data = await response.json();
          // Esta API tiene estructura diferente: { usd: { cop: value, eur: value, ... } }
          rates = data.usd;
        }
      } catch (error) {
        console.error('API de respaldo también falló');
      }
    }

    if (!rates) {
      throw new Error('No se pudieron obtener las tasas de cambio de ninguna API');
    }

    // Actualizar tasas de cambio (intentar ambos formatos de keys)
    if (rates.COP || rates.cop) {
      currencies.COP.exchangeRate = rates.COP || rates.cop;
    }
    if (rates.EUR || rates.eur) {
      currencies.EUR.exchangeRate = rates.EUR || rates.eur;
    }
    if (rates.MXN || rates.mxn) {
      currencies.MXN.exchangeRate = rates.MXN || rates.mxn;
    }

    lastUpdate = new Date();
    
    // Guardar en localStorage para uso offline
    localStorage.setItem('exchangeRates', JSON.stringify({
      rates: {
        COP: currencies.COP.exchangeRate,
        EUR: currencies.EUR.exchangeRate,
        MXN: currencies.MXN.exchangeRate,
      },
      lastUpdate: lastUpdate.toISOString(),
    }));

    console.log('✅ Tasas de cambio actualizadas:', {
      COP: currencies.COP.exchangeRate.toFixed(2),
      EUR: currencies.EUR.exchangeRate.toFixed(4),
      MXN: currencies.MXN.exchangeRate.toFixed(2),
      lastUpdate: lastUpdate.toLocaleString('es-CO'),
    });

    return true;
  } catch (error) {
    console.error('❌ Error actualizando tasas de cambio:', error);
    
    // Intentar cargar tasas guardadas en localStorage
    try {
      const saved = localStorage.getItem('exchangeRates');
      if (saved) {
        const data = JSON.parse(saved);
        if (data.rates) {
          currencies.COP.exchangeRate = data.rates.COP || 3746.83;
          currencies.EUR.exchangeRate = data.rates.EUR || 0.92;
          currencies.MXN.exchangeRate = data.rates.MXN || 17;
          lastUpdate = new Date(data.lastUpdate);
          console.log('📦 Usando tasas guardadas (offline)');
          return true;
        }
      }
    } catch (e) {
      console.error('Error cargando tasas guardadas:', e);
    }
    
    return false;
  } finally {
    isUpdating = false;
  }
};

/**
 * Obtiene la fecha de última actualización
 */
export const getLastUpdateTime = (): Date | null => {
  return lastUpdate;
};

/**
 * Verifica si las tasas necesitan actualizarse (más de 24 horas)
 */
const shouldUpdate = (): boolean => {
  if (!lastUpdate) return true;
  const hoursSinceUpdate = (Date.now() - lastUpdate.getTime()) / (1000 * 60 * 60);
  return hoursSinceUpdate >= 24;
};

// Función para obtener la moneda actual (puedes cambiarla dinámicamente)
let currentCurrency = DEFAULT_CURRENCY;

export const getCurrentCurrency = (): Currency => {
  return currencies[currentCurrency] || currencies.USD;
};

export const setCurrentCurrency = (code: string): void => {
  if (currencies[code]) {
    currentCurrency = code;
    // Guardar en localStorage para persistencia
    localStorage.setItem('currency', code);
  }
};

// Cargar moneda desde localStorage al iniciar
export const loadCurrencyFromStorage = (): void => {
  try {
    const saved = localStorage.getItem('currency');
    if (saved && currencies[saved]) {
      currentCurrency = saved;
    }
    
    // Cargar tasas guardadas
    const savedRates = localStorage.getItem('exchangeRates');
    if (savedRates) {
      const data = JSON.parse(savedRates);
      if (data.rates) {
        currencies.COP.exchangeRate = data.rates.COP || 3746.83;
        currencies.EUR.exchangeRate = data.rates.EUR || 0.92;
        currencies.MXN.exchangeRate = data.rates.MXN || 17;
        currencies.MXN.exchangeRate = data.rates.MXN || 17;
        lastUpdate = new Date(data.lastUpdate);
      }
    }
    
    // Actualizar tasas si es necesario (de forma asíncrona, sin bloquear)
    if (shouldUpdate()) {
      updateExchangeRates().catch(err => {
        console.error('Error al actualizar tasas:', err);
      });
    }
  } catch (e) {
    console.error('Error cargando configuración de moneda:', e);
  }
};

// Convertir de USD a la moneda actual
export const convertFromUSD = (amountUSD: number): number => {
  const currency = getCurrentCurrency();
  return amountUSD * currency.exchangeRate;
};

// Convertir de la moneda actual a USD
export const convertToUSD = (amount: number): number => {
  const currency = getCurrentCurrency();
  return amount / currency.exchangeRate;
};

// Formatear precio en la moneda actual
export const formatCurrency = (amount: number): string => {
  const currency = getCurrentCurrency();
  
  // Formato específico para pesos colombianos (sin decimales)
  if (currency.code === 'COP') {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  }
  
  // Formato para otras monedas (con decimales)
  return new Intl.NumberFormat('es-ES', {
    style: 'currency',
    currency: currency.code,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
};

// Obtener símbolo de la moneda actual
export const getCurrencySymbol = (): string => {
  return getCurrentCurrency().symbol;
};

// Obtener nombre de la moneda actual
export const getCurrencyName = (): string => {
  return getCurrentCurrency().name;
};

// Obtener código de la moneda actual
export const getCurrencyCode = (): string => {
  return getCurrentCurrency().code;
};
