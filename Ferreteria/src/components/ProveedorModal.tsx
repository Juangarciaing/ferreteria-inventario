import React, { useState, useEffect } from 'react';
import { XMarkIcon, BuildingOfficeIcon, UserIcon, PhoneIcon, EnvelopeIcon } from '@heroicons/react/24/outline';
import { Proveedor } from '../types';
import FormInput from './FormInput';
import FormSelect from './FormSelect';
import FormTextArea from './FormTextArea';
import FormButton from './FormButton';
import {
  validateRequired,
  validateEmail,
  validatePhone,
  formatPhone,
} from '../utils/formHelpers';

interface ProveedorModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (proveedor: Partial<Proveedor>) => void;
  proveedor: Proveedor | null;
}

const ProveedorModal: React.FC<ProveedorModalProps> = ({
  isOpen,
  onClose,
  onSave,
  proveedor,
}) => {
  const [formData, setFormData] = useState({
    nombre: '',
    contacto: '',
    telefono: '',
    email: '',
    direccion: '',
    rut_ruc: '',
    condiciones_pago: 'contado' as 'contado' | 'credito_30' | 'credito_60',
    descuento_default: '',
    estado: 'activo' as 'activo' | 'inactivo',
    rating: '',
    notas: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    if (proveedor) {
      setFormData({
        nombre: proveedor.nombre,
        contacto: proveedor.contacto || '',
        telefono: proveedor.telefono || '',
        email: proveedor.email || '',
        direccion: proveedor.direccion || '',
        rut_ruc: proveedor.rut_ruc || '',
        condiciones_pago: proveedor.condiciones_pago || 'contado',
        descuento_default: proveedor.descuento_default?.toString() || '',
        estado: proveedor.estado || 'activo',
        rating: proveedor.rating?.toString() || '',
        notas: proveedor.notas || '',
      });
    } else {
      setFormData({
        nombre: '',
        contacto: '',
        telefono: '',
        email: '',
        direccion: '',
        rut_ruc: '',
        condiciones_pago: 'contado',
        descuento_default: '',
        estado: 'activo',
        rating: '',
        notas: '',
      });
    }
    setErrors({});
  }, [proveedor, isOpen]);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.nombre.trim()) {
      newErrors.nombre = 'El nombre es requerido';
    }

    if (!formData.contacto.trim()) {
      newErrors.contacto = 'El contacto es requerido';
    }

    if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'El email no es válido';
    }

    if (formData.descuento_default && (parseFloat(formData.descuento_default) < 0 || parseFloat(formData.descuento_default) > 100)) {
      newErrors.descuento_default = 'El descuento debe estar entre 0 y 100';
    }

    if (formData.rating && (parseInt(formData.rating) < 1 || parseInt(formData.rating) > 5)) {
      newErrors.rating = 'El rating debe estar entre 1 y 5';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      const proveedorData: Partial<Proveedor> = {
        nombre: formData.nombre.trim(),
        contacto: formData.contacto.trim(),
        telefono: formData.telefono.trim() || undefined,
        email: formData.email.trim() || undefined,
        direccion: formData.direccion.trim() || undefined,
        rut_ruc: formData.rut_ruc.trim() || undefined,
        condiciones_pago: formData.condiciones_pago,
        descuento_default: formData.descuento_default ? parseFloat(formData.descuento_default) : undefined,
        estado: formData.estado,
        rating: formData.rating ? parseInt(formData.rating) : undefined,
        notas: formData.notas.trim() || undefined,
      };

      await onSave(proveedorData);
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

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setHasChanges(true);
    
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
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

        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
          {/* Header con gradiente */}
          <div className="bg-gradient-to-r from-green-600 to-green-700 px-6 py-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <BuildingOfficeIcon className="h-7 w-7 text-white" />
              <h3 className="text-xl font-semibold text-white">
                {proveedor ? 'Editar Proveedor' : 'Nuevo Proveedor'}
              </h3>
            </div>
            <button
              onClick={handleClose}
              className="text-white hover:text-green-100 transition-colors"
              disabled={loading}
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="px-6 py-6 space-y-5">
            {/* Información básica */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormInput
                label="Nombre de la Empresa"
                name="nombre"
                value={formData.nombre}
                onChange={handleChange}
                error={errors.nombre}
                placeholder="Ej: Distribuidora ABC S.A."
                required
                autoFocus
                icon={<BuildingOfficeIcon className="h-5 w-5" />}
                tooltip="Nombre legal o comercial de la empresa proveedora"
                validation={(value) => validateRequired(value, 'El nombre')}
              />

              <FormInput
                label="Persona de Contacto"
                name="contacto"
                value={formData.contacto}
                onChange={handleChange}
                error={errors.contacto}
                placeholder="Ej: Juan Pérez"
                required
                icon={<UserIcon className="h-5 w-5" />}
                tooltip="Persona responsable de atención comercial"
                validation={(value) => validateRequired(value, 'El contacto')}
              />
            </div>

            {/* Información de contacto */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormInput
                label="Teléfono"
                name="telefono"
                type="tel"
                value={formData.telefono}
                onChange={handleChange}
                error={errors.telefono}
                placeholder="Ej: +1 234 567 8900"
                icon={<PhoneIcon className="h-5 w-5" />}
                formatValue={formatPhone}
                validation={validatePhone}
                tooltip="Número de teléfono principal"
              />

              <FormInput
                label="Email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                error={errors.email}
                placeholder="Ej: ventas@proveedor.com"
                icon={<EnvelopeIcon className="h-5 w-5" />}
                validation={validateEmail}
                tooltip="Correo electrónico de contacto"
              />
            </div>

            {/* Dirección */}
            <FormInput
              label="Dirección"
              name="direccion"
              value={formData.direccion}
              onChange={handleChange}
              placeholder="Ej: Av. Principal 123, Ciudad"
              tooltip="Dirección física de la empresa"
            />

            {/* RUT/RUC y Condiciones de Pago */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormInput
                label="RUT/RUC"
                name="rut_ruc"
                value={formData.rut_ruc}
                onChange={handleChange}
                placeholder="Ej: 12.345.678-9"
                tooltip="Número de identificación tributaria"
              />

              <FormSelect
                label="Condiciones de Pago"
                name="condiciones_pago"
                value={formData.condiciones_pago}
                onChange={(value) => handleChange({ target: { name: 'condiciones_pago', value } } as any)}
                options={[
                  { value: 'contado', label: 'Contado' },
                  { value: 'credito_30', label: 'Crédito 30 días' },
                  { value: 'credito_60', label: 'Crédito 60 días' },
                ]}
                tooltip="Términos de pago acordados con el proveedor"
              />
            </div>

            {/* Descuento, Rating y Estado */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <FormInput
                label="Descuento por Defecto (%)"
                name="descuento_default"
                type="number"
                value={formData.descuento_default}
                onChange={handleChange}
                error={errors.descuento_default}
                placeholder="0.0"
                suffix="%"
                validation={(value) => {
                  if (!value) return null;
                  const num = parseFloat(value);
                  if (isNaN(num) || num < 0 || num > 100) {
                    return 'El descuento debe estar entre 0 y 100';
                  }
                  return null;
                }}
                tooltip="Descuento estándar ofrecido por el proveedor"
              />

              <FormSelect
                label="Rating"
                name="rating"
                value={formData.rating}
                onChange={(value) => handleChange({ target: { name: 'rating', value } } as any)}
                options={[
                  { value: '', label: 'Sin rating' },
                  { value: '1', label: '⭐ 1 estrella' },
                  { value: '2', label: '⭐⭐ 2 estrellas' },
                  { value: '3', label: '⭐⭐⭐ 3 estrellas' },
                  { value: '4', label: '⭐⭐⭐⭐ 4 estrellas' },
                  { value: '5', label: '⭐⭐⭐⭐⭐ 5 estrellas' },
                ]}
                tooltip="Calificación de calidad y servicio del proveedor"
              />

              <FormSelect
                label="Estado"
                name="estado"
                value={formData.estado}
                onChange={(value) => handleChange({ target: { name: 'estado', value } } as any)}
                options={[
                  { value: 'activo', label: '✓ Activo' },
                  { value: 'inactivo', label: '✗ Inactivo' },
                ]}
                tooltip="Estado actual del proveedor en el sistema"
              />
            </div>

            {/* Notas */}
            <FormTextArea
              label="Notas"
              name="notas"
              value={formData.notas}
              onChange={handleChange}
              placeholder="Notas adicionales sobre el proveedor..."
              rows={3}
              maxLength={500}
              showCharCount
              tooltip="Información adicional o comentarios sobre el proveedor"
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
                {proveedor ? 'Actualizar' : 'Crear'} Proveedor
              </FormButton>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ProveedorModal;