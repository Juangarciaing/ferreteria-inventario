import React, { useState, useEffect } from 'react';
import { XMarkIcon, CubeIcon, QrCodeIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import { Producto, Categoria } from '../types';
import FormInput from './FormInput';
import FormSelect from './FormSelect';
import FormTextArea from './FormTextArea';
import FormButton from './FormButton';
import BarcodeGenerator from './BarcodeGenerator';
import {
  validateRequired,
  validatePrice,
  validateStock,
  formatPrice,
  formatInteger,
} from '../utils/formHelpers';
import { generateUniqueBarcode, validateEAN13 } from '../utils/barcodeUtils';
import toast from 'react-hot-toast';

interface ProductoModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (producto: Partial<Producto>) => void;
  producto: Producto | null;
  categorias: Categoria[];
}

const ProductoModal: React.FC<ProductoModalProps> = ({
  isOpen,
  onClose,
  onSave,
  producto,
  categorias,
}) => {
  const [formData, setFormData] = useState({
    nombre: '',
    categoria_id: '',
    proveedor_id: '',
    precio: '',
    stock: '',
    stock_minimo: '',
    descripcion: '',
    codigo_barras: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [showBarcodeGenerator, setShowBarcodeGenerator] = useState(false);

  useEffect(() => {
    if (producto) {
      console.log('🔧 Editando producto:', producto);
      setFormData({
        nombre: producto.nombre,
        categoria_id: producto.categoria_id.toString(),
        proveedor_id: (producto as any).proveedor_id?.toString() || '',
        precio: producto.precio.toString(),
        stock: producto.stock.toString(),
        stock_minimo: producto.stock_minimo.toString(),
        descripcion: producto.descripcion || '',
        codigo_barras: (producto as any).codigo_barras || '',
      });
    } else {
      setFormData({
        nombre: '',
        categoria_id: '',
        proveedor_id: '',
        precio: '',
        stock: '',
        stock_minimo: '',
        descripcion: '',
        codigo_barras: '',
      });
    }
    setErrors({});
    setShowBarcodeGenerator(false);
  }, [producto, isOpen]);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.nombre.trim()) {
      newErrors.nombre = 'El nombre es requerido';
    }

    if (!formData.categoria_id) {
      newErrors.categoria_id = 'La categoría es requerida';
    }

    if (!formData.precio || Number.parseFloat(formData.precio) < 0) {
      newErrors.precio = 'El precio debe ser mayor o igual a 0';
    }

    if (!formData.stock || Number.parseInt(formData.stock, 10) < 0) {
      newErrors.stock = 'El stock debe ser mayor o igual a 0';
    }

    if (!formData.stock_minimo || Number.parseInt(formData.stock_minimo, 10) < 0) {
      newErrors.stock_minimo = 'El stock mínimo debe ser mayor o igual a 0';
    }

    // Validar código de barras si está presente
    if (formData.codigo_barras?.length === 13) {
      if (!validateEAN13(formData.codigo_barras)) {
        newErrors.codigo_barras = 'Código de barras EAN-13 inválido';
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
      console.log('📝 Enviando datos del producto:', formData);
      
      const productoData: any = {
        nombre: formData.nombre.trim(),
        categoria_id: Number.parseInt(formData.categoria_id, 10),
        precio: Number.parseFloat(formData.precio),
        stock: Number.parseInt(formData.stock, 10),
        stock_minimo: Number.parseInt(formData.stock_minimo, 10),
        descripcion: formData.descripcion.trim() || undefined,
      };

      // Agregar proveedor si está presente
      if (formData.proveedor_id) {
        productoData.proveedor_id = Number.parseInt(formData.proveedor_id, 10);
      }

      // Agregar código de barras si está presente
      if (formData.codigo_barras) {
        productoData.codigo_barras = formData.codigo_barras;
      }

      console.log('✅ Datos procesados para enviar:', productoData);
      await onSave(productoData);
      setHasChanges(false);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (hasChanges) {
      const confirmClose = globalThis.confirm(
        '¿Estás seguro de cerrar? Los cambios no guardados se perderán.'
      );
      if (!confirmClose) return;
    }
    onClose();
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setHasChanges(true);
    
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleGenerateBarcode = () => {
    const newBarcode = generateUniqueBarcode();
    setFormData(prev => ({ ...prev, codigo_barras: newBarcode }));
    setHasChanges(true);
    toast.success('Código de barras generado');
  };

  // Manejo de teclas (ESC para cerrar)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        handleClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, hasChanges]);

  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={onClose} />

        <span className="hidden sm:inline-block sm:align-middle sm:h-screen">&#8203;</span>

        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4">
            <div className="flex justify-between items-center">
              <h3 className="text-xl font-bold text-white flex items-center">
                <CubeIcon className="h-6 w-6 mr-2" />
                {producto ? 'Editar Producto' : 'Nuevo Producto'}
              </h3>
              <button
                onClick={handleClose}
                className="text-white hover:text-gray-200 transition-colors"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="px-6 py-6">
            {/* Nombre */}
            <FormInput
              label="Nombre del Producto"
              name="nombre"
              value={formData.nombre}
              onChange={handleChange}
              error={errors.nombre}
              placeholder="Ej: Martillo de Carpintero"
              required
              autoFocus
              tooltip="Nombre descriptivo del producto"
              validation={(value) => validateRequired(value, 'El nombre')}
            />

            {/* Categoría */}
            <FormSelect
              label="Categoría"
              name="categoria_id"
              value={formData.categoria_id}
              onChange={(value) => {
                handleChange({
                  target: { name: 'categoria_id', value }
                } as any);
              }}
              options={categorias.map(cat => ({
                value: cat.id,
                label: cat.nombre
              }))}
              error={errors.categoria_id}
              placeholder="Seleccionar categoría"
              required
              searchable
              tooltip="Categoría a la que pertenece el producto"
            />

            {/* Precio y Stock en Grid */}
            <div className="grid grid-cols-2 gap-4">
              {/* Precio */}
              <FormInput
                label="Precio"
                name="precio"
                type="number"
                value={formData.precio}
                onChange={handleChange}
                error={errors.precio}
                placeholder="0.00"
                required
                min={0}
                step={0.01}
                prefix="$"
                tooltip="Precio de venta al público"
                validation={validatePrice}
                formatValue={formatPrice}
              />

              {/* Stock */}
              <FormInput
                label="Stock Actual"
                name="stock"
                type="number"
                value={formData.stock}
                onChange={handleChange}
                error={errors.stock}
                placeholder="0"
                required
                min={0}
                suffix="unid."
                tooltip="Cantidad disponible en inventario"
                validation={validateStock}
                formatValue={formatInteger}
              />
            </div>

            {/* Stock Mínimo */}
            <FormInput
              label="Stock Mínimo"
              name="stock_minimo"
              type="number"
              value={formData.stock_minimo}
              onChange={handleChange}
              error={errors.stock_minimo}
              placeholder="0"
              required
              min={0}
              suffix="unid."
              tooltip="Alerta cuando el stock llegue a este nivel"
              validation={validateStock}
              formatValue={formatInteger}
            />

            {/* Descripción */}
            <FormTextArea
              label="Descripción"
              name="descripcion"
              value={formData.descripcion}
              onChange={handleChange}
              placeholder="Descripción detallada del producto (opcional)"
              rows={3}
              maxLength={500}
              showCharCount
              tooltip="Información adicional sobre el producto"
            />

            {/* Código de Barras */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Código de Barras (Opcional)
              </label>
              
              <div className="flex gap-2 mb-3">
                <input
                  type="text"
                  name="codigo_barras"
                  value={formData.codigo_barras}
                  onChange={handleChange}
                  maxLength={13}
                  placeholder="EAN-13 (13 dígitos)"
                  className="block w-full px-3 py-2 border border-gray-300 rounded-lg text-sm
                           focus:outline-none focus:ring-2 focus:ring-blue-500
                           bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white"
                />
                {errors.codigo_barras && (
                  <p className="text-sm text-red-600 mt-1">{errors.codigo_barras}</p>
                )}
                
                <button
                  type="button"
                  onClick={handleGenerateBarcode}
                  className="px-4 py-2 bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-lg hover:from-purple-700 hover:to-purple-800 transition-all duration-200 flex items-center gap-2 whitespace-nowrap shadow-lg"
                  title="Generar código automáticamente"
                >
                  <QrCodeIcon className="h-5 w-5" />
                  Generar
                </button>
              </div>

              {/* Vista Previa del Código de Barras */}
              {formData.codigo_barras && formData.codigo_barras.length >= 8 && (
                <div className="mt-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">
                      Vista Previa
                    </span>
                    <button
                      type="button"
                      onClick={() => setShowBarcodeGenerator(!showBarcodeGenerator)}
                      className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
                    >
                      {showBarcodeGenerator ? 'Ocultar' : 'Ver más opciones'}
                      <ArrowPathIcon className="h-4 w-4" />
                    </button>
                  </div>
                  
                  {showBarcodeGenerator && (
                    <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                      <BarcodeGenerator
                        value={formData.codigo_barras}
                        productName={formData.nombre || 'Producto'}
                        price={formData.precio ? Number.parseFloat(formData.precio) : undefined}
                        showLabel={true}
                        format={formData.codigo_barras.length === 13 ? 'EAN13' : 'CODE128'}
                        width={2}
                        height={80}
                      />
                    </div>
                  )}
                </div>
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
                {producto ? 'Actualizar' : 'Crear'} Producto
              </FormButton>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ProductoModal;