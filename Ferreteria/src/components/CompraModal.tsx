import React, { useState, useEffect, useCallback } from 'react';
import { XMarkIcon, ShoppingCartIcon } from '@heroicons/react/24/outline';
import { Producto, Proveedor, Compra } from '../types';
import FormInput from './FormInput';
import FormSelect from './FormSelect';
import FormButton from './FormButton';
import { validateStock, validatePrice, formatInteger, formatPrice, displayPrice } from '../utils/formHelpers';

interface CompraModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (compraData: { producto_id: number; cantidad: number; precio_unitario: number; proveedor_id?: number }) => void;
  productos: Producto[];
  proveedores?: Proveedor[];
  compra?: Compra;
}

const CompraModal: React.FC<CompraModalProps> = ({
  isOpen,
  onClose,
  onSave,
  productos,
  proveedores = [],
  compra,
}) => {
  const [formData, setFormData] = useState({
    producto_id: '',
    proveedor_id: '',
    cantidad: '',
    precio_unitario: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    if (isOpen) {
      if (compra) {
        // Modo edición
        console.log('🔧 Editando compra:', compra);
        console.log('📦 producto_id:', compra.producto_id);
        console.log('🏪 proveedor_id:', compra.proveedor_id);
        
        setFormData({
          producto_id: compra.producto_id ? String(compra.producto_id) : '',
          proveedor_id: compra.proveedor_id ? String(compra.proveedor_id) : '',
          cantidad: compra.cantidad ? String(compra.cantidad) : '',
          precio_unitario: compra.precio_unitario ? String(compra.precio_unitario) : '',
        });
        
        console.log('✅ FormData establecido:', {
          producto_id: compra.producto_id ? String(compra.producto_id) : '',
          proveedor_id: compra.proveedor_id ? String(compra.proveedor_id) : '',
        });
      } else {
        // Modo creación
        setFormData({
          producto_id: '',
          proveedor_id: '',
          cantidad: '',
          precio_unitario: '',
        });
      }
      setErrors({});
      setHasChanges(false);
    }
  }, [isOpen, compra]);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.producto_id) {
      newErrors.producto_id = 'El producto es requerido';
    }

    if (!formData.cantidad || Number.parseInt(formData.cantidad, 10) <= 0) {
      newErrors.cantidad = 'La cantidad debe ser mayor a 0';
    }

    if (!formData.precio_unitario || Number.parseFloat(formData.precio_unitario) <= 0) {
      newErrors.precio_unitario = 'El precio unitario debe ser mayor a 0';
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
      const compraData = {
        producto_id: Number.parseInt(formData.producto_id, 10),
        cantidad: Number.parseInt(formData.cantidad, 10),
        precio_unitario: Number.parseFloat(formData.precio_unitario),
        proveedor_id: formData.proveedor_id ? Number.parseInt(formData.proveedor_id, 10) : undefined,
      };

      await onSave(compraData);
      setHasChanges(false);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = useCallback(() => {
    if (hasChanges) {
      if (globalThis.confirm('Hay cambios sin guardar. ¿Deseas cerrar sin guardar?')) {
        onClose();
      }
    } else {
      onClose();
    }
  }, [hasChanges, onClose]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setHasChanges(true);
    
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
  }, [isOpen, hasChanges, handleClose]);

  const selectedProducto = productos.find(p => p.id.toString() === formData.producto_id);
  const total = formData.cantidad && formData.precio_unitario
    ? (Number.parseInt(formData.cantidad, 10) * Number.parseFloat(formData.precio_unitario)).toFixed(2)
    : '0.00';  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        {/* Overlay con soporte para teclado */}
        <div 
          className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" 
          onClick={onClose}
          onKeyDown={(e) => e.key === 'Escape' && onClose()}
          tabIndex={-1}
          aria-label="Cerrar modal"
        />

        <span className="hidden sm:inline-block sm:align-middle sm:h-screen">&#8203;</span>

        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          {/* Header con gradiente */}
          <div className="bg-gradient-to-r from-emerald-600 to-emerald-700 px-6 py-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <ShoppingCartIcon className="h-7 w-7 text-white" />
              <h3 className="text-xl font-semibold text-white">
                {compra ? 'Editar Compra' : 'Nueva Compra'}
              </h3>
            </div>
            <button
              onClick={handleClose}
              className="text-white hover:text-emerald-100 transition-colors"
              disabled={loading}
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="px-6 py-6 space-y-5">
            {/* Selección de Producto */}
            <FormSelect
              label="Producto"
              name="producto_id"
              value={formData.producto_id}
              onChange={(value) => handleChange({ target: { name: 'producto_id', value } } as React.ChangeEvent<HTMLSelectElement>)}
              options={productos.map(p => ({
                value: String(p.id),
                label: `${p.nombre} (Stock: ${p.stock})`
              }))}
              error={errors.producto_id}
              required
              searchable
              tooltip="Selecciona el producto que estás comprando"
            />

            {selectedProducto && (
              <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
                <p className="text-sm text-blue-800">
                  💰 Precio actual de venta: <span className="font-semibold">{displayPrice(selectedProducto.precio)}</span>
                </p>
              </div>
            )}

            {/* Proveedor (opcional) */}
            {proveedores.length > 0 && (
              <FormSelect
                label="Proveedor"
                name="proveedor_id"
                value={formData.proveedor_id}
                onChange={(value) => handleChange({ target: { name: 'proveedor_id', value } } as React.ChangeEvent<HTMLSelectElement>)}
                options={[
                  { value: '', label: 'Sin proveedor (opcional)' },
                  ...proveedores.map(p => ({
                    value: String(p.id_proveedor),
                    label: p.nombre
                  }))
                ]}
                searchable
                tooltip="Proveedor que suministra el producto (opcional)"
              />
            )}

            {/* Cantidad y Precio */}
            <div className="grid grid-cols-2 gap-4">
              <FormInput
                label="Cantidad"
                name="cantidad"
                type="number"
                value={formData.cantidad}
                onChange={handleChange}
                error={errors.cantidad}
                placeholder="0"
                suffix="unid."
                required
                validation={validateStock}
                formatValue={formatInteger}
                tooltip="Cantidad de unidades a comprar"
              />

              <FormInput
                label="Precio Unitario"
                name="precio_unitario"
                type="number"
                value={formData.precio_unitario}
                onChange={handleChange}
                error={errors.precio_unitario}
                placeholder="0.00"
                prefix="$"
                required
                validation={validatePrice}
                formatValue={formatPrice}
                tooltip="Precio de compra por unidad"
              />
            </div>

            {/* Total calculado */}
            {(formData.cantidad && formData.precio_unitario) && (
              <div className="bg-gradient-to-r from-emerald-50 to-green-50 border-2 border-emerald-300 p-4 rounded-lg">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-emerald-800">💵 Total de la compra:</span>
                  <span className="text-2xl font-bold text-emerald-900">{displayPrice(Number.parseFloat(total))}</span>
                </div>
              </div>
            )}

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
                variant="success"
                loading={loading}
                disabled={loading}
              >
                {compra ? 'Actualizar Compra' : 'Registrar Compra'}
              </FormButton>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default CompraModal;