import React, { useState, useEffect } from 'react';
import { XMarkIcon, UserIcon, EnvelopeIcon, IdentificationIcon, ShieldCheckIcon, EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline';
import { User } from '../types';
import FormInput from './FormInput';
import FormSelect from './FormSelect';
import FormButton from './FormButton';
import { validateRequired, validateEmail } from '../utils/formHelpers';

interface UsuarioModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (usuario: Partial<User>) => void;
  usuario: User | null;
}

const UsuarioModal: React.FC<UsuarioModalProps> = ({
  isOpen,
  onClose,
  onSave,
  usuario,
}) => {
  const [formData, setFormData] = useState({
    nombre: '',
    email: '',
    cedula: '',
    rol: 'vendedor' as 'admin' | 'vendedor',
    estado: true, // Boolean en lugar de string
    password: '',
    confirmPassword: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    if (usuario) {
      setFormData({
        nombre: usuario.nombre,
        email: usuario.email,
        cedula: '',
        rol: (usuario.rol === 'admin' ? 'admin' : 'vendedor'),
        estado: usuario.estado !== false, // Convertir a boolean
        password: '',
        confirmPassword: '',
      });
    } else {
      setFormData({
        nombre: '',
        email: '',
        cedula: '',
        rol: 'vendedor',
        estado: true, // Por defecto activo
        password: '',
        confirmPassword: '',
      });
    }
    setErrors({});
  }, [usuario, isOpen]);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.nombre.trim()) {
      newErrors.nombre = 'El nombre es requerido';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'El email es requerido';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'El email no es válido';
    }

    // Cédula opcional en esta versión (el backend no requiere este campo)
    if (formData.cedula && !/^\d{6,12}$/.test(formData.cedula)) {
      newErrors.cedula = 'La cédula debe ser numérica (6 a 12 dígitos)';
    }

    // Validar contraseña solo si es un usuario nuevo o si se está cambiando
    if (!usuario || formData.password) {
      if (!formData.password) {
        newErrors.password = 'La contraseña es requerida';
      } else if (formData.password.length < 6) {
        newErrors.password = 'La contraseña debe tener al menos 6 caracteres';
      }

      if (formData.password !== formData.confirmPassword) {
        newErrors.confirmPassword = 'Las contraseñas no coinciden';
      }
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
      // Si es admin, forzar estado a true
      const estadoFinal = formData.rol === 'admin' ? true : formData.estado;

      const usuarioData: Partial<User> = {
        nombre: formData.nombre.trim(),
        email: formData.email.trim(),
        rol: formData.rol,
        estado: estadoFinal, // SIEMPRE incluir estado
      };

      // Solo incluir la contraseña si se está creando un usuario nuevo o si se cambió
      if (!usuario || formData.password) {
        // En producción, aquí enviarías la contraseña al backend para que la hashee
        (usuarioData as Record<string, unknown>).password = formData.password;
      }

      console.log('📤 Enviando al backend:', usuarioData);
      await onSave(usuarioData);
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

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    
    setHasChanges(true);
    
    // Si se cambia el rol a admin, forzar estado a true
    if (name === 'rol' && value === 'admin') {
      setFormData(prev => ({ ...prev, [name]: value, estado: true }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
    
    // Limpiar error del campo cuando el usuario empiece a escribir
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

        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          {/* Header con gradiente */}
          <div className="bg-gradient-to-r from-indigo-600 to-indigo-700 px-6 py-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <UserIcon className="h-7 w-7 text-white" />
              <h3 className="text-xl font-semibold text-white">
                {usuario ? 'Editar Usuario' : 'Nuevo Usuario'}
              </h3>
            </div>
            <button
              onClick={handleClose}
              className="text-white hover:text-indigo-100 transition-colors"
              disabled={loading}
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="px-6 py-6 space-y-5">
            {/* Información básica */}
            <FormInput
              label="Nombre Completo"
              name="nombre"
              value={formData.nombre}
              onChange={handleChange}
              error={errors.nombre}
              placeholder="Ej: Juan Pérez"
              required
              autoFocus
              icon={<UserIcon className="h-5 w-5" />}
              tooltip="Nombre completo del usuario"
              validation={(value) => validateRequired(value, 'El nombre')}
            />

            <FormInput
              label="Email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              error={errors.email}
              placeholder="Ej: usuario@empresa.com"
              required
              icon={<EnvelopeIcon className="h-5 w-5" />}
              validation={validateEmail}
              tooltip="Correo electrónico para acceso al sistema"
            />

            <FormInput
              label="Cédula"
              name="cedula"
              value={formData.cedula}
              onChange={handleChange}
              error={errors.cedula}
              placeholder="Ej: 12345678"
              icon={<IdentificationIcon className="h-5 w-5" />}
              tooltip="Número de identificación personal (6-12 dígitos)"
              validation={(value) => {
                if (!value) return null;
                if (!/^\d{6,12}$/.test(value)) {
                  return 'La cédula debe ser numérica (6 a 12 dígitos)';
                }
                return null;
              }}
            />

            {/* Rol y Estado */}
            <div className="grid grid-cols-2 gap-4">
              <FormSelect
                label="Rol"
                name="rol"
                value={formData.rol}
                onChange={(value) => handleChange({ target: { name: 'rol', value } } as any)}
                options={[
                  { value: 'vendedor', label: 'Vendedor' },
                  { value: 'admin', label: '🔒 Administrador' },
                ]}
                required
                tooltip="Nivel de acceso en el sistema"
              />

              <FormSelect
                label="Estado"
                name="estado"
                value={formData.estado ? 'true' : 'false'}
                onChange={(value) => setFormData(prev => ({ ...prev, estado: value === 'true' }))}
                options={[
                  { value: 'true', label: '✓ Activo' },
                  { value: 'false', label: '✗ Inactivo', disabled: formData.rol === 'admin' },
                ]}
                required
                tooltip={formData.rol === 'admin' ? 'Los administradores siempre están activos' : 'Estado del usuario en el sistema'}
              />
            </div>

            {formData.rol === 'admin' && (
              <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
                <p className="text-sm text-blue-800 flex items-center">
                  <ShieldCheckIcon className="h-5 w-5 mr-2" />
                  ℹ️ Los administradores siempre están activos
                </p>
              </div>
            )}

            {/* Contraseñas con toggle visibility */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                Contraseña {!usuario && <span className="text-red-500">*</span>}
                {usuario && <span className="text-sm text-gray-500 ml-1">(dejar vacío para no cambiar)</span>}
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className={`block w-full border rounded-md shadow-sm py-2 px-3 pr-10 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors ${
                    errors.password ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 transition-colors"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeSlashIcon className="h-5 w-5" />
                  ) : (
                    <EyeIcon className="h-5 w-5" />
                  )}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password}</p>
              )}
              {!errors.password && !usuario && (
                <p className="mt-1 text-xs text-gray-500">Mínimo 6 caracteres</p>
              )}
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
                Confirmar Contraseña {!usuario && <span className="text-red-500">*</span>}
              </label>
              <div className="relative">
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  id="confirmPassword"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  className={`block w-full border rounded-md shadow-sm py-2 px-3 pr-10 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors ${
                    errors.confirmPassword ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 transition-colors"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                >
                  {showConfirmPassword ? (
                    <EyeSlashIcon className="h-5 w-5" />
                  ) : (
                    <EyeIcon className="h-5 w-5" />
                  )}
                </button>
              </div>
              {errors.confirmPassword && (
                <p className="mt-1 text-sm text-red-600">{errors.confirmPassword}</p>
              )}
            </div>

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
                {usuario ? 'Actualizar' : 'Crear'} Usuario
              </FormButton>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default UsuarioModal;