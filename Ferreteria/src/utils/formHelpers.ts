/**
 * Utilidades para formateo y validación de formularios
 */

import { formatCurrency, convertFromUSD } from '../config/currency';

// ===== VALIDACIONES =====

/**
 * Valida que un email sea válido
 */
export const validateEmail = (email: string): string | null => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!email) return 'El email es requerido';
  if (!emailRegex.test(email)) return 'Email inválido';
  return null;
};

/**
 * Valida que un teléfono sea válido (formato flexible)
 */
export const validatePhone = (phone: string): string | null => {
  const phoneRegex = /^[\d\s\-\+\(\)]{7,}$/;
  if (!phone) return null; // Opcional
  if (!phoneRegex.test(phone)) return 'Teléfono inválido';
  return null;
};

/**
 * Valida que un número sea positivo
 */
export const validatePositiveNumber = (value: string, fieldName: string = 'El valor'): string | null => {
  const num = parseFloat(value);
  if (isNaN(num)) return `${fieldName} debe ser un número`;
  if (num < 0) return `${fieldName} debe ser positivo`;
  return null;
};

/**
 * Valida que un número esté en un rango
 */
export const validateNumberRange = (
  value: string,
  min: number,
  max: number,
  fieldName: string = 'El valor'
): string | null => {
  const num = parseFloat(value);
  if (isNaN(num)) return `${fieldName} debe ser un número`;
  if (num < min) return `${fieldName} debe ser mayor o igual a ${min}`;
  if (num > max) return `${fieldName} debe ser menor o igual a ${max}`;
  return null;
};

/**
 * Valida longitud mínima de texto
 */
export const validateMinLength = (value: string, minLength: number, fieldName: string = 'El campo'): string | null => {
  if (value.length < minLength) {
    return `${fieldName} debe tener al menos ${minLength} caracteres`;
  }
  return null;
};

/**
 * Valida longitud máxima de texto
 */
export const validateMaxLength = (value: string, maxLength: number, fieldName: string = 'El campo'): string | null => {
  if (value.length > maxLength) {
    return `${fieldName} no puede exceder ${maxLength} caracteres`;
  }
  return null;
};

/**
 * Valida que un campo no esté vacío
 */
export const validateRequired = (value: string | number, fieldName: string = 'El campo'): string | null => {
  if (!value || value.toString().trim() === '') {
    return `${fieldName} es requerido`;
  }
  return null;
};

// ===== FORMATEADORES =====

/**
 * Formatea un número como precio ($1,234.56)
 */
export const formatPrice = (value: string): string => {
  // Remover todo excepto dígitos y punto decimal
  let cleaned = value.replace(/[^\d.]/g, '');
  
  // Permitir solo un punto decimal
  const parts = cleaned.split('.');
  if (parts.length > 2) {
    cleaned = parts[0] + '.' + parts.slice(1).join('');
  }
  
  // Limitar a 2 decimales
  if (parts[1] && parts[1].length > 2) {
    cleaned = parts[0] + '.' + parts[1].substring(0, 2);
  }
  
  return cleaned;
};

/**
 * Formatea un número como entero (solo dígitos)
 */
export const formatInteger = (value: string): string => {
  return value.replace(/\D/g, '');
};

/**
 * Formatea un teléfono (permite dígitos, espacios, guiones, paréntesis)
 */
export const formatPhone = (value: string): string => {
  return value.replace(/[^\d\s\-\+\(\)]/g, '');
};

/**
 * Formatea texto eliminando espacios extra
 */
export const formatText = (value: string): string => {
  return value.replace(/\s+/g, ' ');
};

/**
 * Convierte a mayúsculas
 */
export const formatUpperCase = (value: string): string => {
  return value.toUpperCase();
};

/**
 * Convierte a minúsculas
 */
export const formatLowerCase = (value: string): string => {
  return value.toLowerCase();
};

/**
 * Capitaliza primera letra de cada palabra
 */
export const formatCapitalize = (value: string): string => {
  return value
    .toLowerCase()
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

/**
 * Formatea un precio para mostrar con la moneda actual del sistema
 * Convierte automáticamente de USD (base de datos) a la moneda seleccionada
 */
export const displayPrice = (valueInUSD: number): string => {
  // Convertir de USD a la moneda actual
  const convertedValue = convertFromUSD(valueInUSD);
  // Formatear con el símbolo y formato de la moneda actual
  return formatCurrency(convertedValue);
};

/**
 * Formatea un número con separadores de miles
 */
export const displayNumber = (value: number): string => {
  return new Intl.NumberFormat('es-CO').format(value);
};

// ===== VALIDADORES COMPUESTOS =====

/**
 * Validador para precios (positivo, máximo 2 decimales)
 */
export const validatePrice = (value: string): string | null => {
  const num = parseFloat(value);
  if (isNaN(num)) return 'El precio debe ser un número';
  if (num < 0) return 'El precio debe ser positivo';
  if (num > 999999.99) return 'El precio es demasiado alto';
  
  // Validar máximo 2 decimales
  const parts = value.split('.');
  if (parts[1] && parts[1].length > 2) {
    return 'El precio no puede tener más de 2 decimales';
  }
  
  return null;
};

/**
 * Validador para stock (entero positivo)
 */
export const validateStock = (value: string): string | null => {
  const num = parseInt(value);
  if (isNaN(num)) return 'El stock debe ser un número entero';
  if (num < 0) return 'El stock no puede ser negativo';
  if (num > 999999) return 'El stock es demasiado alto';
  return null;
};

/**
 * Validador para nombres (mínimo 2 caracteres, sin números)
 */
export const validateName = (value: string): string | null => {
  if (!value || value.trim().length < 2) {
    return 'El nombre debe tener al menos 2 caracteres';
  }
  if (/\d/.test(value)) {
    return 'El nombre no puede contener números';
  }
  if (value.length > 100) {
    return 'El nombre es demasiado largo';
  }
  return null;
};

// ===== UTILIDADES =====

/**
 * Limpia un formulario de errores
 */
export const cleanErrors = <T extends Record<string, any>>(errors: T): T => {
  const cleaned = {} as T;
  Object.keys(errors).forEach(key => {
    cleaned[key as keyof T] = '' as T[keyof T];
  });
  return cleaned;
};

/**
 * Verifica si hay errores en un objeto de errores
 */
export const hasErrors = (errors: Record<string, string>): boolean => {
  return Object.values(errors).some(error => error !== '');
};

/**
 * Cuenta los errores en un objeto de errores
 */
export const countErrors = (errors: Record<string, string>): number => {
  return Object.values(errors).filter(error => error !== '').length;
};
