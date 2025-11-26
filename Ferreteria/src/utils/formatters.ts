/**
 * Utilidades para formateo y validación
 */

import { convertFromUSD, formatCurrency } from '../config/currency';

/**
 * Formatear precio en formato de moneda
 * Convierte automáticamente de USD (base de datos) a la moneda seleccionada
 */
export const formatPrice = (priceInUSD: number): string => {
  // Convertir de USD a la moneda actual
  const convertedPrice = convertFromUSD(priceInUSD);
  // Formatear con el símbolo y formato de la moneda actual
  return formatCurrency(convertedPrice);
};

/**
 * Formatear fecha en formato legible
 */
export const formatDate = (date: string | Date): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return new Intl.DateTimeFormat('es-CO', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(dateObj);
};

/**
 * Formatear fecha y hora
 */
export const formatDateTime = (date: string | Date): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return new Intl.DateTimeFormat('es-CO', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(dateObj);
};

/**
 * Validar email
 */
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Validar cédula (formato básico)
 */
export const isValidCedula = (cedula: string): boolean => {
  // Validación básica: solo números y longitud entre 6-12 dígitos
  const cedulaRegex = /^\d{6,12}$/;
  return cedulaRegex.test(cedula);
};

/**
 * Generar ID temporal para elementos que no tienen ID de servidor
 */
export const generateTempId = (): string => {
  return `temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Debounce para búsquedas
 */
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

/**
 * Capitalizar primera letra
 */
export const capitalize = (str: string): string => {
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
};

/**
 * Truncar texto
 */
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.substr(0, maxLength) + '...';
};

/**
 * Validar rango de fechas
 */
export const isValidDateRange = (startDate: string, endDate: string): boolean => {
  if (!startDate || !endDate) return false;
  return new Date(startDate) <= new Date(endDate);
};

/**
 * Obtener estado del stock
 */
export const getStockStatus = (stock: number, stockMinimo: number): 'bajo' | 'medio' | 'alto' => {
  if (stock <= stockMinimo) return 'bajo';
  if (stock <= stockMinimo * 2) return 'medio';
  return 'alto';
};

/**
 * Obtener color del estado del stock
 */
export const getStockStatusColor = (status: 'bajo' | 'medio' | 'alto'): string => {
  switch (status) {
    case 'bajo':
      return 'text-red-600 bg-red-100';
    case 'medio':
      return 'text-yellow-600 bg-yellow-100';
    case 'alto':
      return 'text-green-600 bg-green-100';
    default:
      return 'text-gray-600 bg-gray-100';
  }
};