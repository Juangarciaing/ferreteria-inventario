import React from 'react';
import { BellIcon, XMarkIcon, ExclamationTriangleIcon, CheckCircleIcon, InformationCircleIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import { useNotifications, Notification } from '../hooks/useNotifications';
import { useNavigate } from 'react-router-dom';

interface NotificationCenterProps {
  isOpen: boolean;
  onClose: () => void;
}

const NotificationCenter: React.FC<NotificationCenterProps> = ({ isOpen, onClose }) => {
  const navigate = useNavigate();
  const {
    notifications,
    unreadCount,
    loading,
    markAsRead,
    markAllAsRead,
    clearNotification,
    clearAll,
    refreshNotifications,
  } = useNotifications();

  const getIcon = (type: Notification['type']) => {
    switch (type) {
      case 'sin_stock':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
      case 'stock_bajo':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
      case 'venta':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'compra':
        return <CheckCircleIcon className="h-5 w-5 text-blue-500" />;
      case 'sistema':
        return <InformationCircleIcon className="h-5 w-5 text-gray-500" />;
      default:
        return <InformationCircleIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getBgColor = (type: Notification['type']) => {
    switch (type) {
      case 'sin_stock':
        return 'bg-red-50 border-red-200';
      case 'stock_bajo':
        return 'bg-yellow-50 border-yellow-200';
      case 'venta':
        return 'bg-green-50 border-green-200';
      case 'compra':
        return 'bg-blue-50 border-blue-200';
      case 'sistema':
        return 'bg-gray-50 border-gray-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  const formatTime = (timestamp: Date) => {
    const now = new Date();
    const diff = now.getTime() - timestamp.getTime();
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (minutes < 1) {
      return 'ahora';
    } else if (minutes < 60) {
      return `hace ${minutes} min`;
    } else if (hours < 24) {
      return `hace ${hours}h`;
    } else {
      return `hace ${days}d`;
    }
  };

  const handleNotificationClick = (notification: Notification) => {
    markAsRead(notification.id);
    if (notification.producto_id) {
      navigate('/productos');
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 bg-gray-900 bg-opacity-75 transition-opacity" onClick={onClose} />

        <span className="hidden sm:inline-block sm:align-middle sm:h-screen">&#8203;</span>

        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div className="flex justify-between items-center mb-4">
              <div className="flex items-center">
                <BellIcon className="h-6 w-6 text-gray-600 mr-2" />
                <h3 className="text-lg leading-6 font-medium text-gray-900">
                  Notificaciones
                </h3>
                {unreadCount > 0 && (
                  <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                    {unreadCount}
                  </span>
                )}
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={refreshNotifications}
                  className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                  title="Refrescar"
                  disabled={loading}
                >
                  <ArrowPathIcon className={`h-5 w-5 ${loading ? 'animate-spin' : ''}`} />
                </button>
                {unreadCount > 0 && (
                  <button
                    onClick={markAllAsRead}
                    className="text-sm text-blue-600 hover:text-blue-800"
                  >
                    Marcar todas
                  </button>
                )}
                {notifications.length > 0 && (
                  <button
                    onClick={clearAll}
                    className="text-sm text-red-600 hover:text-red-800"
                  >
                    Limpiar todo
                  </button>
                )}
                <button
                  onClick={onClose}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>
            </div>

            <div className="space-y-3 max-h-96 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="text-center py-8">
                  <BellIcon className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">No hay notificaciones</p>
                  <p className="text-sm text-gray-400 mt-2">
                    Las alertas de stock aparecerán aquí
                  </p>
                </div>
              ) : (
                notifications.map((notification) => (
                  <div
                    key={notification.id}
                    onClick={() => handleNotificationClick(notification)}
                    className={`p-4 rounded-lg border cursor-pointer transition-all ${getBgColor(
                      notification.type
                    )} ${
                      !notification.read
                        ? 'ring-2 ring-blue-500 ring-opacity-50 hover:ring-opacity-75'
                        : 'hover:shadow-md'
                    }`}
                  >
                    <div className="flex items-start">
                      <div className="flex-shrink-0">{getIcon(notification.type)}</div>
                      <div className="ml-3 flex-1">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-medium text-gray-900">
                            {notification.title}
                            {!notification.read && (
                              <span className="ml-2 inline-block w-2 h-2 bg-blue-600 rounded-full"></span>
                            )}
                          </p>
                          <div className="flex items-center space-x-2">
                            <span className="text-xs text-gray-500">
                              {formatTime(notification.timestamp)}
                            </span>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                clearNotification(notification.id);
                              }}
                              className="text-gray-400 hover:text-gray-600"
                            >
                              <XMarkIcon className="h-4 w-4" />
                            </button>
                          </div>
                        </div>
                        <p className="text-sm text-gray-600 mt-1">{notification.message}</p>
                        {notification.producto_nombre && (
                          <p className="text-xs text-gray-500 mt-2">
                            Producto: <span className="font-medium">{notification.producto_nombre}</span>
                            {notification.stock !== undefined && (
                              <>
                                {' '}
                                | Stock: <span className="font-medium">{notification.stock}</span>
                                {notification.stock_minimo !== undefined && (
                                  <> / Mín: {notification.stock_minimo}</>
                                )}
                              </>
                            )}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotificationCenter;