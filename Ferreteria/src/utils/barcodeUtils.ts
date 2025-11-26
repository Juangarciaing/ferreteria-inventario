/**
 * Genera un código de barras EAN-13 válido
 * @returns Código de barras de 13 dígitos
 */
export const generateEAN13 = (): string => {
  // Generar 12 dígitos aleatorios
  let code = '';
  for (let i = 0; i < 12; i++) {
    code += Math.floor(Math.random() * 10);
  }
  
  // Calcular dígito de control
  const checkDigit = calculateEAN13CheckDigit(code);
  
  return code + checkDigit;
};

/**
 * Calcula el dígito de control para un código EAN-13
 * @param code Código de 12 dígitos
 * @returns Dígito de control (0-9)
 */
export const calculateEAN13CheckDigit = (code: string): number => {
  if (code.length !== 12) {
    throw new Error('El código debe tener exactamente 12 dígitos');
  }
  
  let sum = 0;
  
  // Sumar dígitos en posiciones impares (multiplicados por 1)
  // y dígitos en posiciones pares (multiplicados por 3)
  for (let i = 0; i < 12; i++) {
    const digit = parseInt(code[i]);
    sum += (i % 2 === 0) ? digit : digit * 3;
  }
  
  // El dígito de control es el número que hace que la suma sea múltiplo de 10
  const checkDigit = (10 - (sum % 10)) % 10;
  
  return checkDigit;
};

/**
 * Valida un código de barras EAN-13
 * @param code Código de barras completo (13 dígitos)
 * @returns true si el código es válido
 */
export const validateEAN13 = (code: string): boolean => {
  if (!/^\d{13}$/.test(code)) {
    return false;
  }
  
  const checkDigit = calculateEAN13CheckDigit(code.substring(0, 12));
  return checkDigit === parseInt(code[12]);
};

/**
 * Genera un código CODE128 basado en un prefijo y un número secuencial
 * @param prefix Prefijo (ej: "PROD")
 * @param sequence Número secuencial
 * @returns Código formateado
 */
export const generateCODE128 = (prefix: string = 'PROD', sequence: number): string => {
  return `${prefix}${String(sequence).padStart(6, '0')}`;
};

/**
 * Formatea un código de barras para mostrar con guiones
 * @param code Código de barras
 * @returns Código formateado
 */
export const formatBarcode = (code: string): string => {
  if (code.length === 13) {
    // EAN-13: XXX-XXXX-XXXX-X
    return `${code.substring(0, 3)}-${code.substring(3, 7)}-${code.substring(7, 12)}-${code[12]}`;
  }
  return code;
};

/**
 * Genera un código de barras único basado en timestamp y random
 * @returns Código único de 12 dígitos + check digit
 */
export const generateUniqueBarcode = (): string => {
  const timestamp = Date.now().toString().slice(-8); // Últimos 8 dígitos del timestamp
  const random = Math.floor(Math.random() * 10000).toString().padStart(4, '0'); // 4 dígitos aleatorios
  
  const code = timestamp + random;
  const checkDigit = calculateEAN13CheckDigit(code);
  
  return code + checkDigit;
};
