import React, { useState } from 'react';
import { XCircleIcon } from '@heroicons/react/24/outline';

interface FormTextAreaProps {
  label: string;
  name: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  error?: string;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  rows?: number;
  maxLength?: number;
  showCharCount?: boolean;
  tooltip?: string;
}

const FormTextArea: React.FC<FormTextAreaProps> = ({
  label,
  name,
  value,
  onChange,
  error,
  placeholder,
  required = false,
  disabled = false,
  rows = 3,
  maxLength,
  showCharCount = false,
  tooltip,
}) => {
  const [touched, setTouched] = useState(false);

  const displayError = touched && error;
  const charCount = value.length;
  const isNearLimit = maxLength && charCount > maxLength * 0.8;

  return (
    <div className="mb-4">
      {/* Label */}
      <div className="flex items-center justify-between mb-2">
        <label htmlFor={name} className="block text-sm font-medium text-gray-700">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
          {tooltip && (
            <span className="ml-2 text-gray-400 text-xs">ℹ️ {tooltip}</span>
          )}
        </label>

        {/* Character Count */}
        {(showCharCount || maxLength) && (
          <span
            className={`text-xs ${
              isNearLimit ? 'text-orange-500 font-medium' : 'text-gray-500'
            }`}
          >
            {charCount}
            {maxLength && ` / ${maxLength}`}
          </span>
        )}
      </div>

      {/* TextArea */}
      <textarea
        id={name}
        name={name}
        value={value}
        onChange={onChange}
        onBlur={() => setTouched(true)}
        placeholder={placeholder}
        required={required}
        disabled={disabled}
        rows={rows}
        maxLength={maxLength}
        className={`
          block w-full rounded-lg border px-4 py-2.5 text-gray-900
          ${displayError
            ? 'border-red-300 focus:border-red-500 focus:ring-red-500'
            : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'
          }
          ${disabled ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}
          focus:outline-none focus:ring-2 focus:ring-opacity-50
          transition-colors duration-200
          resize-none
        `}
      />

      {/* Error Message */}
      {displayError && (
        <p className="mt-2 text-sm text-red-600 flex items-center">
          <XCircleIcon className="h-4 w-4 mr-1" />
          {error}
        </p>
      )}

      {/* Max Length Warning */}
      {isNearLimit && !displayError && (
        <p className="mt-2 text-sm text-orange-500">
          Te quedan {maxLength! - charCount} caracteres
        </p>
      )}
    </div>
  );
};

export default FormTextArea;
