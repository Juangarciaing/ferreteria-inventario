import { useState, useEffect } from 'react';
import { XMarkIcon, PlusIcon, MinusIcon, ShoppingBagIcon, UserIcon, IdentificationIcon, PhoneIcon } from '@heroicons/react/24/outline';
import { Producto } from '../types';
import FormInput from './FormInput';
import FormButton from './FormButton';
import { validatePhone, formatPhone, displayPrice } from '../utils/formHelpers';

interface VentaItem {
  producto_id: number;
  nombre: string;
  precio_unitario: number;
  cantidad: number;
  subtotal: number;
  stock_disponible: number;
}

interface VentaModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (ventaData: { 
    items: VentaItem[]; 
    total: number;
    cliente_nombre?: string;
    cliente_documento?: string;
    cliente_telefono?: string;
  }) => void;
  productos: Producto[];
}

const VentaModal: React.FC<VentaModalProps> = ({
  isOpen,
  onClose,
  onSave,
  productos,
}) => {
  const [items, setItems] = useState<VentaItem[]>([]);
  const [selectedProducto, setSelectedProducto] = useState<string>('');
  const [clienteNombre, setClienteNombre] = useState('');
  const [clienteDocumento, setClienteDocumento] = useState('');
  const [clienteTelefono, setClienteTelefono] = useState('');
  const [loading, setLoading] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setItems([]);
      setSelectedProducto('');
      setClienteNombre('');
      setClienteDocumento('');
      setClienteTelefono('');
    }
  }, [isOpen]);

  const agregarProducto = () => {
    if (!selectedProducto) return;

    const producto = productos.find(p => p.id.toString() === selectedProducto);
    if (!producto) return;

    setHasChanges(true);

    // Verificar si el producto ya está en la lista
    const existingItem = items.find(item => item.producto_id === producto.id);
    if (existingItem) {
      // Incrementar cantidad si hay stock disponible
      if (existingItem.cantidad < producto.stock) {
        actualizarCantidad(producto.id, existingItem.cantidad + 1);
      }
    } else {
      // Agregar nuevo producto
      const newItem: VentaItem = {
        producto_id: producto.id,
        nombre: producto.nombre,
        precio_unitario: producto.precio,
        cantidad: 1,
        subtotal: producto.precio,
        stock_disponible: producto.stock,
      };
      setItems([...items, newItem]);
    }
    setSelectedProducto('');
  };

  const actualizarCantidad = (producto_id: number, nuevaCantidad: number) => {
    if (nuevaCantidad <= 0) {
      eliminarItem(producto_id);
      return;
    }

    setHasChanges(true);
    setItems(items.map(item => {
      if (item.producto_id === producto_id) {
        const cantidad = Math.min(nuevaCantidad, item.stock_disponible);
        return {
          ...item,
          cantidad,
          subtotal: item.precio_unitario * cantidad,
        };
      }
      return item;
    }));
  };

  const eliminarItem = (producto_id: number) => {
    setHasChanges(true);
    setItems(items.filter(item => item.producto_id !== producto_id));
  };

  const calcularTotal = () => {
    return items.reduce((total, item) => total + item.subtotal, 0);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (items.length === 0) {
      alert('Debe agregar al menos un producto');
      return;
    }

    setLoading(true);
    try {
      await onSave({
        items,
        total: calcularTotal(),
        cliente_nombre: clienteNombre || undefined,
        cliente_documento: clienteDocumento || undefined,
        cliente_telefono: clienteTelefono || undefined,
      });
      setHasChanges(false);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (hasChanges && items.length > 0) {
      if (window.confirm('Hay productos agregados sin guardar. ¿Deseas cerrar sin guardar?')) {
        onClose();
      }
    } else {
      onClose();
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
  }, [isOpen, hasChanges, items]);

  const productosDisponibles = productos.filter(p => 
    p.stock > 0 && !items.some(item => item.producto_id === p.id)
  );

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={onClose} />

        <span className="hidden sm:inline-block sm:align-middle sm:h-screen">&#8203;</span>

        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
          {/* Header con gradiente */}
          <div className="bg-gradient-to-r from-green-600 to-green-700 px-6 py-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <ShoppingBagIcon className="h-7 w-7 text-white" />
              <h3 className="text-xl font-semibold text-white">
                Nueva Venta
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

          <form onSubmit={handleSubmit} className="px-6 py-6 space-y-6">
            {/* Información del Cliente (Opcional) */}
            <div className="border-b border-gray-200 pb-4">
              <h4 className="text-sm font-semibold text-gray-700 mb-4 flex items-center">
                <UserIcon className="h-5 w-5 mr-2" />
                Información del Cliente (Opcional)
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <FormInput
                  label="Nombre"
                  name="cliente_nombre"
                  value={clienteNombre}
                  onChange={(e) => {
                    setClienteNombre(e.target.value);
                    setHasChanges(true);
                  }}
                  placeholder="Nombre del cliente"
                  icon={<UserIcon className="h-5 w-5" />}
                  tooltip="Nombre del cliente (opcional)"
                />

                <FormInput
                  label="Documento"
                  name="cliente_documento"
                  value={clienteDocumento}
                  onChange={(e) => {
                    setClienteDocumento(e.target.value);
                    setHasChanges(true);
                  }}
                  placeholder="CI/RUC"
                  icon={<IdentificationIcon className="h-5 w-5" />}
                  tooltip="Cédula o RUC del cliente (opcional)"
                />

                <FormInput
                  label="Teléfono"
                  name="cliente_telefono"
                  type="tel"
                  value={clienteTelefono}
                  onChange={(e) => {
                    setClienteTelefono(e.target.value);
                    setHasChanges(true);
                  }}
                  placeholder="Teléfono"
                  icon={<PhoneIcon className="h-5 w-5" />}
                  formatValue={formatPhone}
                  validation={validatePhone}
                  tooltip="Número de teléfono del cliente (opcional)"
                />
              </div>
            </div>

            {/* Selector de productos */}
            <div>
              <h4 className="text-sm font-semibold text-gray-700 mb-3">Agregar Productos</h4>
              <div className="flex gap-2">
                <select
                  value={selectedProducto}
                  onChange={(e) => setSelectedProducto(e.target.value)}
                  className="flex-1 border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Seleccionar producto...</option>
                  {productosDisponibles.map(producto => (
                    <option key={producto.id} value={producto.id}>
                      {producto.nombre} - {displayPrice(producto.precio)} (Stock: {producto.stock})
                    </option>
                  ))}
                </select>
                <button
                  type="button"
                  onClick={agregarProducto}
                  disabled={!selectedProducto}
                  className="h-10 w-10 flex items-center justify-center rounded-md border border-transparent text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  title="Agregar producto"
                >
                  <PlusIcon className="h-5 w-5" />
                </button>
              </div>
            </div>

            {/* Lista de productos seleccionados */}
            {items.length > 0 && (
              <div className="border-2 border-gray-200 rounded-lg overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gradient-to-r from-gray-50 to-gray-100">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                        Producto
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                        Precio
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                        Cantidad
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                        Subtotal
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">
                        Acciones
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {items.map((item) => (
                      <tr key={item.producto_id} className="hover:bg-gray-50 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">{item.nombre}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 font-medium">
                          {displayPrice(item.precio_unitario)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center space-x-2">
                            <button
                              type="button"
                              onClick={() => actualizarCantidad(item.producto_id, item.cantidad - 1)}
                              className="p-1 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                            >
                              <MinusIcon className="h-4 w-4" />
                            </button>
                            <span className="w-10 text-center font-semibold text-gray-900">{item.cantidad}</span>
                            <button
                              type="button"
                              onClick={() => actualizarCantidad(item.producto_id, item.cantidad + 1)}
                              disabled={item.cantidad >= item.stock_disponible}
                              className="p-1 text-gray-500 hover:text-green-600 hover:bg-green-50 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                              <PlusIcon className="h-4 w-4" />
                            </button>
                          </div>
                          <div className="text-xs text-gray-500 mt-1">
                            📦 Stock: {item.stock_disponible}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">
                          {displayPrice(item.subtotal)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <button
                            type="button"
                            onClick={() => eliminarItem(item.producto_id)}
                            className="text-red-600 hover:text-red-900 hover:underline transition-colors"
                          >
                            Eliminar
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {items.length === 0 && (
              <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                <ShoppingBagIcon className="mx-auto h-12 w-12 text-gray-400" />
                <p className="mt-2 text-sm text-gray-500">
                  No hay productos agregados. Selecciona un producto para comenzar.
                </p>
              </div>
            )}

            {/* Total */}
            {items.length > 0 && (
              <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-300 p-6 rounded-lg">
                <div className="flex justify-between items-center">
                  <span className="text-lg font-semibold text-green-800">💰 Total de la Venta:</span>
                  <span className="text-3xl font-bold text-green-900">
                    {displayPrice(calcularTotal())}
                  </span>
                </div>
                <div className="mt-2 text-sm text-green-700">
                  {items.length} {items.length === 1 ? 'producto' : 'productos'} • {items.reduce((sum, item) => sum + item.cantidad, 0)} unidades
                </div>
              </div>
            )}

            {/* Botones */}
            <div className="flex items-center justify-end space-x-3 pt-4 border-t border-gray-200">
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
                disabled={items.length === 0 || loading}
              >
                Registrar Venta
              </FormButton>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default VentaModal;