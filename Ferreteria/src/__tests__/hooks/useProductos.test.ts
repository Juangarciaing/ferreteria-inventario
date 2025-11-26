/**
 * Tests para el hook useProductos
 */
import { renderHook, act } from '@testing-library/react';
import { useProductos } from '../../hooks/useProductos';
import { apiClient } from '../../lib/api';

// Mock de react-hot-toast
jest.mock('react-hot-toast', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn()
  }
}));

// apiClient will be automatically mocked by Jest using the manual mock in __mocks__
jest.mock('../../lib/api');

describe('useProductos Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('should initialize with empty state', () => {
    const { result } = renderHook(() => useProductos());
    
    expect(result.current.productos).toEqual([]);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  test('should load productos successfully', async () => {
    const mockProductos = [
      { id: 1, nombre: 'Producto 1', precio: 10.99, stock: 5, categoria_id: 1, stock_minimo: 2 },
      { id: 2, nombre: 'Producto 2', precio: 20.99, stock: 10, categoria_id: 1, stock_minimo: 3 }
    ];

    (apiClient.get as jest.Mock).mockResolvedValue({ data: mockProductos });

    const { result } = renderHook(() => useProductos());

    await act(async () => {
      await result.current.loadProductos();
    });

    expect(result.current.productos).toEqual(mockProductos);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  test('should handle load productos error', async () => {
    (apiClient.get as jest.Mock).mockRejectedValue(new Error('Network error'));

    const { result } = renderHook(() => useProductos());

    await act(async () => {
      await result.current.loadProductos();
    });

    expect(result.current.productos).toEqual([]);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBe('Network error');
  });

  test('should create producto successfully', async () => {
    const newProducto = { 
      nombre: 'Nuevo Producto', 
      precio: 15.99, 
      stock: 8,
      categoria_id: 1,
      stock_minimo: 2
    };
    const createdProducto = { id: 3, ...newProducto };

    (apiClient.post as jest.Mock).mockResolvedValue({ data: createdProducto });

    const { result } = renderHook(() => useProductos());

    await act(async () => {
      await result.current.createProducto(newProducto);
    });

    expect(result.current.productos).toContainEqual(createdProducto);
    expect(apiClient.post).toHaveBeenCalledWith('/productos', newProducto);
  });

  test('should update producto successfully', async () => {
    const existingProducto = { 
      id: 1, 
      nombre: 'Producto 1', 
      precio: 10.99, 
      stock: 5,
      categoria_id: 1,
      stock_minimo: 2
    };
    const updatedProducto = { ...existingProducto, precio: 12.99 };

    (apiClient.put as jest.Mock).mockResolvedValue({ data: updatedProducto });

    const { result } = renderHook(() => useProductos());

    // Set initial state
    act(() => {
      result.current.productos = [existingProducto];
    });

    await act(async () => {
      await result.current.updateProducto(1, { precio: 12.99 });
    });

    expect(result.current.productos).toContainEqual(updatedProducto);
    expect(apiClient.put).toHaveBeenCalledWith('/productos/1', { precio: 12.99 });
  });

  test('should delete producto successfully', async () => {
    const existingProducto = { 
      id: 1, 
      nombre: 'Producto 1', 
      precio: 10.99, 
      stock: 5,
      categoria_id: 1,
      stock_minimo: 2
    };

    (apiClient.delete as jest.Mock).mockResolvedValue({ data: { message: 'Producto eliminado' } });

    const { result } = renderHook(() => useProductos());

    // Set initial state
    act(() => {
      result.current.productos = [existingProducto];
    });

    await act(async () => {
      await result.current.deleteProducto(1);
    });

    expect(result.current.productos).not.toContainEqual(existingProducto);
    expect(apiClient.delete).toHaveBeenCalledWith('/productos/1');
  });

  test('should search productos successfully', async () => {
    const mockSearchResults = [
      { id: 1, nombre: 'Martillo', precio: 10.99, stock: 5 }
    ];

    const { api } = require('../../lib/api');
    api.get.mockResolvedValue({ data: mockSearchResults });

    const { result } = renderHook(() => useProductos());

    await act(async () => {
      await result.current.searchProductos('martillo');
    });

    expect(result.current.productos).toEqual(mockSearchResults);
    expect(api.get).toHaveBeenCalledWith('/productos/search?q=martillo');
  });
});
