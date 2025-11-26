import { useState, useEffect, useCallback } from 'react';
import { Venta, Producto } from '../types';
import { apiClient } from '../lib/api';
import toast from 'react-hot-toast';
import { generateInvoicePdf } from '../utils/pdfGenerator';

interface UseVentasReturn {
  ventas: Venta[];
  productos: Producto[];
  loading: boolean;
  refreshing: boolean;
  loadData: () => Promise<void>;
  createVenta: (ventaData: { items: Array<{ producto_id: number; cantidad: number; precio_unitario: number }>; total: number }) => Promise<void>;
  deleteVenta: (venta: Venta) => Promise<void>;
  exportarPDF: (venta: Venta) => void;
}

export const useVentas = (): UseVentasReturn => {
  const [ventas, setVentas] = useState<Venta[]>([]);
  const [productos, setProductos] = useState<Producto[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = useCallback(async () => {
    try {
      const isInitialLoad = loading;
      if (isInitialLoad) {
        setLoading(true);
      } else {
        setRefreshing(true);
      }

      const [productosData, ventasData] = await Promise.all([
        apiClient.getProductos(),
        apiClient.getVentas(),
      ]);
      
      setProductos(productosData as Producto[]);
      setVentas(ventasData as Venta[]);
    } catch (error: any) {
      console.error('Error cargando datos:', error);
      toast.error(error?.message || 'Error al cargar los datos');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [loading]);

  useEffect(() => {
    loadData();
  }, []);

  const createVenta = useCallback(async (ventaData: { 
    items: Array<{ producto_id: number; cantidad: number; precio_unitario: number }>; 
    total: number;
    cliente_nombre?: string;
    cliente_documento?: string;
    cliente_telefono?: string;
  }) => {
    try {
      const payload: any = {
        detalles: ventaData.items.map(item => ({
          producto_id: item.producto_id,
          cantidad: item.cantidad
        }))
      };

      // Agregar información del cliente si está presente
      if (ventaData.cliente_nombre) payload.cliente_nombre = ventaData.cliente_nombre;
      if (ventaData.cliente_documento) payload.cliente_documento = ventaData.cliente_documento;
      if (ventaData.cliente_telefono) payload.cliente_telefono = ventaData.cliente_telefono;
      
      await apiClient.createVenta(payload);
      toast.success('Venta registrada correctamente');
      
      // Recargar los datos
      await loadData();
    } catch (error: any) {
      console.error('Error al registrar venta:', error);
      toast.error(error?.message || 'Error al registrar la venta');
      throw error; // Re-throw para que el componente pueda manejarlo
    }
  }, [loadData]);

  const deleteVenta = useCallback(async (venta: Venta) => {
    try {
      await apiClient.deleteVenta(venta.id);
      toast.success(`Venta #${venta.id} anulada exitosamente`);
      
      // Recargar los datos
      await loadData();
    } catch (error: any) {
      console.error('Error anulando venta:', error);
      toast.error(error?.message || 'Error al anular la venta');
      throw error;
    }
  }, [loadData]);

  const exportarPDF = useCallback((venta: Venta) => {
    try {
      if (!venta.detalles || venta.detalles.length === 0) {
        toast.error('La venta no tiene detalles para generar factura');
        return;
      }
      
      generateInvoicePdf(venta);
      toast.success('Factura generada y descargada correctamente');
    } catch (error: any) {
      console.error('Error generando factura:', error);
      toast.error(error?.message || 'Error al generar la factura');
    }
  }, []);

  return {
    ventas,
    productos,
    loading,
    refreshing,
    loadData,
    createVenta,
    deleteVenta,
    exportarPDF,
  };
};
