import React, { useState } from 'react';
import { FunnelIcon, XMarkIcon, CheckIcon } from '@heroicons/react/24/outline';
import FormButton from './FormButton';

export interface FilterOption {
  label: string;
  value: string | number;
}

export interface FilterConfig {
  name: string;
  label: string;
  type: 'select' | 'multiselect' | 'range' | 'date' | 'daterange';
  options?: FilterOption[];
  min?: number;
  max?: number;
  step?: number;
  placeholder?: string;
}

interface FilterPanelProps {
  filters: FilterConfig[];
  values: Record<string, any>;
  onChange: (name: string, value: any) => void;
  onReset: () => void;
  onApply: () => void;
  isOpen: boolean;
  onToggle: () => void;
  activeFiltersCount?: number;
}

const FilterPanel: React.FC<FilterPanelProps> = ({
  filters,
  values,
  onChange,
  onReset,
  onApply,
  isOpen,
  onToggle,
  activeFiltersCount = 0,
}) => {
  const [localValues, setLocalValues] = useState<Record<string, any>>(values);

  const handleLocalChange = (name: string, value: any) => {
    setLocalValues(prev => ({ ...prev, [name]: value }));
  };

  const handleApply = () => {
    Object.keys(localValues).forEach(key => {
      onChange(key, localValues[key]);
    });
    onApply();
  };

  const handleReset = () => {
    setLocalValues({});
    onReset();
  };

  const renderFilter = (filter: FilterConfig) => {
    const value = localValues[filter.name] || '';

    switch (filter.type) {
      case 'select':
        return (
          <div key={filter.name} className="mb-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {filter.label}
            </label>
            <select
              value={value}
              onChange={(e) => handleLocalChange(filter.name, e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm
                       focus:outline-none focus:ring-2 focus:ring-blue-500
                       bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white"
            >
              <option value="">{filter.placeholder || 'Todos'}</option>
              {filter.options?.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        );

      case 'multiselect':
        const selectedValues = (value as string[]) || [];
        return (
          <div key={filter.name} className="mb-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {filter.label}
            </label>
            <div className="space-y-2 max-h-48 overflow-y-auto border border-gray-300 rounded-lg p-2
                          bg-white dark:bg-gray-800 dark:border-gray-600">
              {filter.options?.map(option => (
                <label
                  key={option.value}
                  className="flex items-center space-x-2 cursor-pointer hover:bg-gray-50 
                           dark:hover:bg-gray-700 p-2 rounded transition-colors"
                >
                  <input
                    type="checkbox"
                    checked={selectedValues.includes(String(option.value))}
                    onChange={(e) => {
                      const newValues = e.target.checked
                        ? [...selectedValues, String(option.value)]
                        : selectedValues.filter(v => v !== String(option.value));
                      handleLocalChange(filter.name, newValues);
                    }}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    {option.label}
                  </span>
                </label>
              ))}
            </div>
          </div>
        );

      case 'range':
        const [min, max] = (value as [number, number]) || [filter.min || 0, filter.max || 100];
        return (
          <div key={filter.name} className="mb-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {filter.label}
            </label>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <input
                  type="number"
                  placeholder="Mín"
                  value={min}
                  onChange={(e) => handleLocalChange(filter.name, [Number(e.target.value), max])}
                  min={filter.min}
                  max={max}
                  step={filter.step || 1}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm
                           focus:outline-none focus:ring-2 focus:ring-blue-500
                           bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                />
              </div>
              <div>
                <input
                  type="number"
                  placeholder="Máx"
                  value={max}
                  onChange={(e) => handleLocalChange(filter.name, [min, Number(e.target.value)])}
                  min={min}
                  max={filter.max}
                  step={filter.step || 1}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm
                           focus:outline-none focus:ring-2 focus:ring-blue-500
                           bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                />
              </div>
            </div>
            <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
              Rango: ${min.toFixed(2)} - ${max.toFixed(2)}
            </div>
          </div>
        );

      case 'date':
        return (
          <div key={filter.name} className="mb-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {filter.label}
            </label>
            <input
              type="date"
              value={value}
              onChange={(e) => handleLocalChange(filter.name, e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm
                       focus:outline-none focus:ring-2 focus:ring-blue-500
                       bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white"
            />
          </div>
        );

      case 'daterange':
        const [startDate, endDate] = (value as [string, string]) || ['', ''];
        return (
          <div key={filter.name} className="mb-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {filter.label}
            </label>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <input
                  type="date"
                  placeholder="Desde"
                  value={startDate}
                  onChange={(e) => handleLocalChange(filter.name, [e.target.value, endDate])}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm
                           focus:outline-none focus:ring-2 focus:ring-blue-500
                           bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                />
                <span className="text-xs text-gray-500 dark:text-gray-400">Desde</span>
              </div>
              <div>
                <input
                  type="date"
                  placeholder="Hasta"
                  value={endDate}
                  onChange={(e) => handleLocalChange(filter.name, [startDate, e.target.value])}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm
                           focus:outline-none focus:ring-2 focus:ring-blue-500
                           bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                />
                <span className="text-xs text-gray-500 dark:text-gray-400">Hasta</span>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="relative">
      {/* Botón de Toggle */}
      <button
        onClick={onToggle}
        className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg
                 text-sm font-medium text-gray-700 bg-white hover:bg-gray-50
                 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
                 transition-all duration-200 shadow-sm
                 dark:bg-gray-800 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
      >
        <FunnelIcon className="h-5 w-5 mr-2" />
        Filtros
        {activeFiltersCount > 0 && (
          <span className="ml-2 inline-flex items-center justify-center px-2 py-0.5 
                         rounded-full text-xs font-bold bg-blue-600 text-white">
            {activeFiltersCount}
          </span>
        )}
      </button>

      {/* Panel de Filtros */}
      {isOpen && (
        <>
          {/* Overlay */}
          <div
            className="fixed inset-0 z-40"
            onClick={onToggle}
          />

          {/* Panel */}
          <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-gray-800 rounded-lg 
                        shadow-xl border border-gray-200 dark:border-gray-700 z-50
                        max-h-[80vh] overflow-y-auto">
            {/* Header */}
            <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 
                          dark:border-gray-700 px-4 py-3 flex justify-between items-center">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Filtros
              </h3>
              <button
                onClick={onToggle}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <XMarkIcon className="h-5 w-5" />
              </button>
            </div>

            {/* Contenido */}
            <div className="px-4 py-4">
              {filters.map(filter => renderFilter(filter))}
            </div>

            {/* Footer con botones */}
            <div className="sticky bottom-0 bg-gray-50 dark:bg-gray-900 border-t border-gray-200 
                          dark:border-gray-700 px-4 py-3 grid grid-cols-2 gap-2">
              <FormButton
                type="button"
                variant="secondary"
                onClick={handleReset}
              >
                Limpiar
              </FormButton>
              <FormButton
                type="button"
                variant="primary"
                onClick={handleApply}
              >
                <CheckIcon className="h-4 w-4 mr-1 inline" />
                Aplicar
              </FormButton>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default FilterPanel;
