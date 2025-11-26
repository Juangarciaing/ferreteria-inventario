/**
 * Servicio de productos - Lógica de negocio
 */
import { apiClient } from '../lib/api';
import { Producto, Categoria } from '../types';

export class ProductoService {
  /**
   * Obtener todos los productos
   */
  static async getProductos(): Promise<Producto[]> {
    try {
      const productos = await apiClient.getProductos();
      return productos;
    } catch (error) {
      console.error('Error al cargar productos:', error);
      throw new Error('No se pudieron cargar los productos');
    }
  }

  /**
   * Crear nuevo producto
   */
  static async createProducto(producto: Omit<Producto, 'id' | 'created_at' | 'updated_at'>): Promise<Producto> {
    try {
      // Validaciones locales
      this.validateProducto(producto);
      
      const newProducto = await apiClient.createProducto(producto);
      return newProducto;
    } catch (error) {
      console.error('Error al crear producto:', error);
      throw error instanceof Error ? error : new Error('No se pudo crear el producto');
    }
  }

  /**
   * Actualizar producto existente
   */
  static async updateProducto(id: number, producto: Partial<Producto>): Promise<Producto> {
    try {
      if (producto.nombre || producto.precio) {
        this.validateProducto(producto as any);
      }
      
      const updatedProducto = await apiClient.updateProducto(id, producto);
      return updatedProducto;
    } catch (error) {
      console.error('Error al actualizar producto:', error);
      throw error instanceof Error ? error : new Error('No se pudo actualizar el producto');
    }
  }

  /**
   * Eliminar producto
   */
  static async deleteProducto(id: number): Promise<void> {
    try {
      await apiClient.deleteProducto(id);
    } catch (error) {
      console.error('Error al eliminar producto:', error);
      throw error instanceof Error ? error : new Error('No se pudo eliminar el producto');
    }
  }

  /**
   * Obtener productos con stock bajo
   */
  static async getProductosStockBajo(): Promise<Producto[]> {
    try {
      const productos = await apiClient.getProductosStockBajo();
      return productos;
    } catch (error) {
      console.error('Error al obtener productos con stock bajo:', error);
      throw new Error('No se pudieron cargar las alertas de stock');
    }
  }

  /**
   * Buscar productos por nombre
   */
  static async searchProductos(searchTerm: string): Promise<Producto[]> {
    try {
      if (!searchTerm.trim()) {
        return await this.getProductos();
      }
      
      const results = await apiClient.searchProductos(searchTerm);
      return results;
    } catch (error) {
      console.error('Error al buscar productos:', error);
      throw new Error('Error al buscar productos');
    }
  }

  /**
   * Validar datos del producto
   */
  private static validateProducto(producto: Partial<Producto>): void {
    if (producto.nombre && producto.nombre.trim().length < 2) {
      throw new Error('El nombre del producto debe tener al menos 2 caracteres');
    }
    
    if (producto.precio !== undefined && producto.precio <= 0) {
      throw new Error('El precio debe ser mayor a 0');
    }
    
    if (producto.stock !== undefined && producto.stock < 0) {
      throw new Error('El stock no puede ser negativo');
    }
    
    if (producto.stock_minimo !== undefined && producto.stock_minimo < 0) {
      throw new Error('El stock mínimo no puede ser negativo');
    }
  }
}

export class CategoriaService {
  /**
   * Obtener todas las categorías
   */
  static async getCategorias(): Promise<Categoria[]> {
    try {
      const response = await apiClient.getCategorias();
      return Array.isArray(response) ? response : [];
    } catch (error) {
      console.error('Error al cargar categorías:', error);
      throw new Error('No se pudieron cargar las categorías');
    }
  }

  /**
   * Crear nueva categoría
   */
  static async createCategoria(categoria: Omit<Categoria, 'id' | 'created_at'>): Promise<Categoria> {
    try {
      this.validateCategoria(categoria);
      
      const response = await apiClient.createCategoria(categoria);
      return response.data || response;
    } catch (error) {
      console.error('Error al crear categoría:', error);
      throw new Error('No se pudo crear la categoría');
    }
  }

  /**
   * Actualizar categoría
   */
  static async updateCategoria(id: number, categoria: Partial<Categoria>): Promise<Categoria> {
    try {
      if (categoria.nombre) {
        this.validateCategoria(categoria as any);
      }
      
      const response = await apiClient.updateCategoria(id, categoria);
      return response;
    } catch (error) {
      console.error('Error al actualizar categoría:', error);
      throw new Error('No se pudo actualizar la categoría');
    }
  }

  /**
   * Eliminar categoría
   */
  static async deleteCategoria(id: number): Promise<void> {
    try {
      await apiClient.deleteCategoria(id);
    } catch (error) {
      console.error('Error al eliminar categoría:', error);
      throw new Error('No se pudo eliminar la categoría');
    }
  }

  /**
   * Validar datos de la categoría
   */
  private static validateCategoria(categoria: Partial<Categoria>): void {
    if (categoria.nombre && categoria.nombre.trim().length < 2) {
      throw new Error('El nombre de la categoría debe tener al menos 2 caracteres');
    }
  }
}