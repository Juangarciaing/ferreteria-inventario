import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../lib/api';
import { Producto } from '../types';
import toast from 'react-hot-toast';

export interface Notification {
  id: string;
  type: 'stock_bajo' | 'sin_stock' | 'venta' | 'compra' | 'sistema';
  title: string;
  message: string;
  producto_id?: number;
  producto_nombre?: string;
  stock?: number;
  stock_minimo?: number;
  timestamp: Date;
  read: boolean;
}

interface UseNotificationsReturn {
  notifications: Notification[];
  unreadCount: number;
  loading: boolean;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  clearNotification: (id: string) => void;
  clearAll: () => void;
  refreshNotifications: () => Promise<void>;
}

const POLLING_INTERVAL = 30000; // 30 segundos
const MAX_NOTIFICATIONS = 50;

export const useNotifications = (): UseNotificationsReturn => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);

  // Generar notificaciones basadas en productos con stock bajo
  const checkStockAlerts = useCallback(async () => {
    try {
      const productos = await apiClient.getProductos();
      const newNotifications: Notification[] = [];

      productos.forEach((producto: Producto) => {
        // Producto sin stock
        if (producto.stock === 0) {
          const existingNotification = notifications.find(
            n => n.type === 'sin_stock' && n.producto_id === producto.id
          );

          if (!existingNotification) {
            newNotifications.push({
              id: `sin_stock_${producto.id}_${Date.now()}`,
              type: 'sin_stock',
              title: '⚠️ Producto Sin Stock',
              message: `${producto.nombre} no tiene unidades disponibles`,
              producto_id: producto.id,
              producto_nombre: producto.nombre,
              stock: producto.stock,
              stock_minimo: producto.stock_minimo,
              timestamp: new Date(),
              read: false,
            });
          }
        }
        // Producto con stock bajo
        else if (producto.stock <= producto.stock_minimo) {
          const existingNotification = notifications.find(
            n => n.type === 'stock_bajo' && n.producto_id === producto.id
          );

          if (!existingNotification) {
            newNotifications.push({
              id: `stock_bajo_${producto.id}_${Date.now()}`,
              type: 'stock_bajo',
              title: '📉 Stock Bajo',
              message: `${producto.nombre} tiene solo ${producto.stock} unidades (mínimo: ${producto.stock_minimo})`,
              producto_id: producto.id,
              producto_nombre: producto.nombre,
              stock: producto.stock,
              stock_minimo: producto.stock_minimo,
              timestamp: new Date(),
              read: false,
            });
          }
        }
      });

      if (newNotifications.length > 0) {
        setNotifications(prev => {
          const combined = [...newNotifications, ...prev];
          // Limitar a MAX_NOTIFICATIONS
          return combined.slice(0, MAX_NOTIFICATIONS);
        });

        // Mostrar toast solo para la primera nueva notificación
        const firstNotif = newNotifications[0];
        if (firstNotif.type === 'sin_stock') {
          toast.error(firstNotif.message, {
            icon: '⚠️',
            duration: 4000,
          });
        } else if (firstNotif.type === 'stock_bajo') {
          toast(firstNotif.message, {
            icon: '📉',
            duration: 4000,
            style: {
              background: '#f59e0b',
              color: '#fff',
            },
          });
        }
      }
    } catch (error) {
      console.error('Error al verificar alertas de stock:', error);
    }
  }, [notifications]);

  // Refrescar notificaciones
  const refreshNotifications = useCallback(async () => {
    setLoading(true);
    await checkStockAlerts();
    setLoading(false);
  }, [checkStockAlerts]);

  // Polling para verificar stock cada 30 segundos
  useEffect(() => {
    // Primera carga
    refreshNotifications();

    // Configurar polling
    const interval = setInterval(() => {
      checkStockAlerts();
    }, POLLING_INTERVAL);

    return () => clearInterval(interval);
  }, [refreshNotifications, checkStockAlerts]);

  // Marcar como leída
  const markAsRead = useCallback((id: string) => {
    setNotifications(prev =>
      prev.map(n => (n.id === id ? { ...n, read: true } : n))
    );
  }, []);

  // Marcar todas como leídas
  const markAllAsRead = useCallback(() => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  }, []);

  // Eliminar notificación
  const clearNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  }, []);

  // Limpiar todas
  const clearAll = useCallback(() => {
    setNotifications([]);
  }, []);

  // Calcular no leídas
  const unreadCount = notifications.filter(n => !n.read).length;

  return {
    notifications,
    unreadCount,
    loading,
    markAsRead,
    markAllAsRead,
    clearNotification,
    clearAll,
    refreshNotifications,
  };
};
