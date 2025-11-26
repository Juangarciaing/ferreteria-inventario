import React, { useState, useRef, useEffect } from 'react';
import { ChevronDownIcon, XCircleIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline';

interface Option {
  value: string | number;
  label: string;
  disabled?: boolean;
}

interface FormSelectProps {
  label: string;
  name: string;
  value: string | number;
  onChange: (value: string) => void;
  options: Option[];
  error?: string;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  searchable?: boolean; // Nueva feature: búsqueda
  tooltip?: string;
}

const FormSelect: React.FC<FormSelectProps> = ({
  label,
  name,
  value,
  onChange,
  options,
  error,
  placeholder = 'Seleccionar...',
  required = false,
  disabled = false,
  searchable = false,
  tooltip,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [touched, setTouched] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Cerrar dropdown al hacer click fuera
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setSearchTerm('');
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Enfocar input de búsqueda cuando se abre
  useEffect(() => {
    if (isOpen && searchable && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [isOpen, searchable]);

  // Filtrar opciones según búsqueda
  const filteredOptions = searchable && searchTerm
    ? options.filter(option =>
        option.label.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : options;

  const selectedOption = options.find(opt => opt.value.toString() === value.toString());

  const handleSelect = (optionValue: string | number) => {
    onChange(optionValue.toString());
    setIsOpen(false);
    setSearchTerm('');
    setTouched(true);
  };

  const displayError = touched && error;

  return (
    <div className="mb-4" ref={containerRef}>
      {/* Label */}
      <label htmlFor={name} className="block text-sm font-medium text-gray-700 mb-2">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
        {tooltip && (
          <span className="ml-2 text-gray-400 text-xs">ℹ️ {tooltip}</span>
        )}
      </label>

      {/* Select Button */}
      <div className="relative">
        <button
          type="button"
          onClick={() => !disabled && setIsOpen(!isOpen)}
          onBlur={() => setTouched(true)}
          disabled={disabled}
          className={`
            relative w-full rounded-lg border px-4 py-2.5 text-left cursor-pointer
            ${displayError
              ? 'border-red-300 focus:border-red-500 focus:ring-red-500'
              : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'
            }
            ${disabled ? 'bg-gray-100 cursor-not-allowed' : 'bg-white hover:bg-gray-50'}
            focus:outline-none focus:ring-2 focus:ring-opacity-50
            transition-all duration-200
          `}
        >
          <span className={selectedOption ? 'text-gray-900' : 'text-gray-400'}>
            {selectedOption ? selectedOption.label : placeholder}
          </span>
          <span className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
            <ChevronDownIcon
              className={`h-5 w-5 text-gray-400 transition-transform duration-200 ${
                isOpen ? 'transform rotate-180' : ''
              }`}
            />
          </span>
        </button>

        {/* Dropdown */}
        {isOpen && (
          <div className="absolute z-10 mt-1 w-full bg-white shadow-lg max-h-60 rounded-lg py-1 text-base ring-1 ring-black ring-opacity-5 overflow-auto focus:outline-none sm:text-sm">
            {/* Search Input */}
            {searchable && (
              <div className="sticky top-0 z-10 bg-white px-3 py-2 border-b border-gray-200">
                <div className="relative">
                  <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    ref={searchInputRef}
                    type="text"
                    placeholder="Buscar..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
            )}

            {/* Options List */}
            {filteredOptions.length > 0 ? (
              filteredOptions.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => !option.disabled && handleSelect(option.value)}
                  disabled={option.disabled}
                  className={`
                    w-full text-left px-4 py-2 cursor-pointer
                    ${option.value.toString() === value.toString()
                      ? 'bg-blue-600 text-white'
                      : option.disabled
                      ? 'text-gray-400 cursor-not-allowed'
                      : 'text-gray-900 hover:bg-blue-50'
                    }
                    transition-colors duration-150
                  `}
                >
                  {option.label}
                </button>
              ))
            ) : (
              <div className="px-4 py-2 text-gray-500 text-sm">
                No se encontraron resultados
              </div>
            )}
          </div>
        )}
      </div>

      {/* Error Message */}
      {displayError && (
        <p className="mt-2 text-sm text-red-600 flex items-center">
          <XCircleIcon className="h-4 w-4 mr-1" />
          {error}
        </p>
      )}
    </div>
  );
};

export default FormSelect;
