import React, { useState, useEffect, useCallback } from 'react';
import { MagnifyingGlassIcon, XMarkIcon } from '@heroicons/react/24/outline';

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
  onClear?: () => void;
  autoFocus?: boolean;
  showClearButton?: boolean;
  debounceMs?: number; // Tiempo de debounce en milisegundos (optimización)
}

const SearchBar: React.FC<SearchBarProps> = ({
  value,
  onChange,
  placeholder = 'Buscar...',
  className = '',
  onClear,
  autoFocus = false,
  showClearButton = true,
  debounceMs = 300, // 300ms por defecto para optimizar búsquedas
}) => {
  const [localValue, setLocalValue] = useState(value);

  // Debounce: esperar a que el usuario deje de escribir antes de actualizar
  useEffect(() => {
    const timer = setTimeout(() => {
      if (localValue !== value) {
        onChange(localValue);
      }
    }, debounceMs);

    return () => clearTimeout(timer);
  }, [localValue, debounceMs]);

  // Sincronizar cuando cambia el valor externo
  useEffect(() => {
    setLocalValue(value);
  }, [value]);

  const handleClear = useCallback(() => {
    setLocalValue('');
    onChange('');
    if (onClear) {
      onClear();
    }
  }, [onChange, onClear]);

  return (
    <div className={`relative ${className}`}>
      {/* Ícono de búsqueda */}
      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
      </div>

      {/* Input */}
      <input
        type="text"
        value={localValue}
        onChange={(e) => setLocalValue(e.target.value)}
        placeholder={placeholder}
        autoFocus={autoFocus}
        className="block w-full pl-10 pr-10 py-2.5 border border-gray-300 rounded-lg text-sm 
                   placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 
                   focus:border-transparent transition-all duration-200
                   bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white
                   dark:placeholder-gray-500"
      />

      {/* Botón limpiar */}
      {showClearButton && localValue && (
        <button
          type="button"
          onClick={handleClear}
          className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 
                     hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
        >
          <XMarkIcon className="h-5 w-5" />
        </button>
      )}
    </div>
  );
};

export default SearchBar;
