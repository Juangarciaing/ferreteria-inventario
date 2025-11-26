import React, { useState, useEffect } from 'react';
import { XMarkIcon, TagIcon } from '@heroicons/react/24/outline';
import { Categoria } from '../types';
import FormInput from './FormInput';
import FormButton from './FormButton';
import { validateRequired } from '../utils/formHelpers';

interface CategoriaModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (categoria: { nombre: string }) => void;
  categoria: Categoria | null;
}

const CategoriaModal: React.FC<CategoriaModalProps> = ({
  isOpen,
  onClose,
  onSave,
  categoria,
}) => {
  const [nombre, setNombre] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    if (categoria) {
      setNombre(categoria.nombre);
    } else {
      setNombre('');
    }
    setError('');
  }, [categoria, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!nombre.trim()) {
      setError('El nombre es requerido');
      return;
    }

    setLoading(true);
    try {
      await onSave({ nombre: nombre.trim() });
      setHasChanges(false);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (hasChanges) {
      if (window.confirm('Hay cambios sin guardar. ¿Deseas cerrar sin guardar?')) {
        onClose();
      }
    } else {
      onClose();
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setNombre(e.target.value);
    setHasChanges(true);
    if (error) {
      setError('');
    }
  };

  // Manejo de tecla ESC para cerrar
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        handleClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, hasChanges]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={onClose} />

        <span className="hidden sm:inline-block sm:align-middle sm:h-screen">&#8203;</span>

        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          {/* Header con gradiente */}
          <div className="bg-gradient-to-r from-purple-600 to-purple-700 px-6 py-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <TagIcon className="h-7 w-7 text-white" />
              <h3 className="text-xl font-semibold text-white">
                {categoria ? 'Editar Categoría' : 'Nueva Categoría'}
              </h3>
            </div>
            <button
              onClick={handleClose}
              className="text-white hover:text-purple-100 transition-colors"
              disabled={loading}
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="px-6 py-6">
            <FormInput
              label="Nombre de la Categoría"
              name="nombre"
              value={nombre}
              onChange={handleChange}
              error={error}
              placeholder="Ej: Herramientas, Materiales, Pinturas"
              required
              autoFocus
              icon={<TagIcon className="h-5 w-5" />}
              tooltip="Nombre descriptivo para agrupar productos relacionados"
              validation={(value) => validateRequired(value, 'El nombre')}
            />

            {/* Botones */}
            <div className="flex items-center justify-end space-x-3 mt-6 pt-6 border-t border-gray-200">
              <FormButton
                type="button"
                variant="secondary"
                onClick={handleClose}
                disabled={loading}
              >
                Cancelar
              </FormButton>

              <FormButton
                type="submit"
                variant="primary"
                loading={loading}
                disabled={loading}
              >
                {categoria ? 'Actualizar' : 'Crear'} Categoría
              </FormButton>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default CategoriaModal;