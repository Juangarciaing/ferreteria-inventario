import React, { useState, useEffect, memo } from 'react';
import { CheckCircleIcon, XCircleIcon, ExclamationCircleIcon } from '@heroicons/react/24/outline';

interface FormInputProps {
  label: string;
  name: string;
  type?: 'text' | 'number' | 'email' | 'password' | 'tel';
  value: string | number;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onBlur?: (e: React.FocusEvent<HTMLInputElement>) => void;
  error?: string;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  autoFocus?: boolean;
  min?: number;
  max?: number;
  step?: number;
  pattern?: string;
  tooltip?: string;
  prefix?: string; // Para mostrar $ antes del input
  suffix?: string; // Para mostrar texto después
  validation?: (value: string) => string | null; // Validación custom
  formatValue?: (value: string) => string; // Formateo automático
  icon?: React.ReactNode;
}

const FormInput: React.FC<FormInputProps> = ({
  label,
  name,
  type = 'text',
  value,
  onChange,
  onBlur,
  error,
  placeholder,
  required = false,
  disabled = false,
  autoFocus = false,
  min,
  max,
  step,
  pattern,
  tooltip,
  prefix,
  suffix,
  validation,
  formatValue,
  icon,
}) => {
  const [touched, setTouched] = useState(false);
  const [isValid, setIsValid] = useState<boolean | null>(null);
  const [localError, setLocalError] = useState<string>('');

  // Validación en tiempo real
  useEffect(() => {
    if (touched && value !== '') {
      if (validation) {
        const validationError = validation(value.toString());
        setLocalError(validationError || '');
        setIsValid(validationError === null);
      } else if (required && !value) {
        setLocalError(`${label} es requerido`);
        setIsValid(false);
      } else {
        setLocalError('');
        setIsValid(value !== '');
      }
    }
  }, [value, touched, validation, required, label]);

  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    setTouched(true);
    if (onBlur) {
      onBlur(e);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let newValue = e.target.value;

    // Aplicar formato si existe
    if (formatValue) {
      newValue = formatValue(newValue);
      e.target.value = newValue;
    }

    onChange(e);
  };

  const displayError = error || (touched ? localError : '');
  const showValidIcon = touched && isValid && !error;
  const showErrorIcon = touched && (error || localError);

  return (
    <div className="mb-4">
      {/* Label */}
      <label htmlFor={name} className="block text-sm font-medium text-gray-700 mb-2">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
        {tooltip && (
          <span className="ml-2 group relative">
            <ExclamationCircleIcon className="h-4 w-4 inline text-gray-400 hover:text-gray-600 cursor-help" />
            <span className="absolute left-0 bottom-full mb-2 hidden group-hover:block w-64 p-2 bg-gray-800 text-white text-xs rounded shadow-lg z-10">
              {tooltip}
            </span>
          </span>
        )}
      </label>

      {/* Input Container */}
      <div className="relative">
        {/* Prefix (ej: $) */}
        {prefix && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <span className="text-gray-500 sm:text-sm">{prefix}</span>
          </div>
        )}

        {/* Icon */}
        {icon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            {icon}
          </div>
        )}

        {/* Input */}
        <input
          type={type}
          id={name}
          name={name}
          value={value}
          onChange={handleChange}
          onBlur={handleBlur}
          placeholder={placeholder}
          required={required}
          disabled={disabled}
          autoFocus={autoFocus}
          min={min}
          max={max}
          step={step}
          pattern={pattern}
          className={`
            block w-full rounded-lg border px-4 py-2.5 text-gray-900
            ${prefix ? 'pl-8' : ''}
            ${icon ? 'pl-10' : ''}
            ${suffix ? 'pr-12' : ''}
            ${showValidIcon || showErrorIcon ? 'pr-10' : ''}
            ${displayError
              ? 'border-red-300 focus:border-red-500 focus:ring-red-500'
              : showValidIcon
              ? 'border-green-300 focus:border-green-500 focus:ring-green-500'
              : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'
            }
            ${disabled ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}
            focus:outline-none focus:ring-2 focus:ring-opacity-50
            transition-colors duration-200
          `}
        />

        {/* Suffix */}
        {suffix && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <span className="text-gray-500 sm:text-sm">{suffix}</span>
          </div>
        )}

        {/* Validation Icons */}
        {showValidIcon && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <CheckCircleIcon className="h-5 w-5 text-green-500" />
          </div>
        )}

        {showErrorIcon && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <XCircleIcon className="h-5 w-5 text-red-500" />
          </div>
        )}
      </div>

      {/* Error Message */}
      {displayError && (
        <p className="mt-2 text-sm text-red-600 flex items-center">
          <XCircleIcon className="h-4 w-4 mr-1" />
          {displayError}
        </p>
      )}

      {/* Success Message (opcional) */}
      {showValidIcon && !displayError && (
        <p className="mt-2 text-sm text-green-600 flex items-center">
          <CheckCircleIcon className="h-4 w-4 mr-1" />
          Válido
        </p>
      )}
    </div>
  );
};

// Optimización: Memoizar componente para evitar re-renders innecesarios
export default memo(FormInput);
