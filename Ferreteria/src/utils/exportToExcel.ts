import { Venta } from '../types';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

/**
 * Convierte ventas a formato CSV y descarga el archivo
 */
export const exportVentasToCSV = (ventas: Venta[], fileName: string = 'ventas'): void => {
  try {
    if (ventas.length === 0) {
      throw new Error('No hay ventas para exportar');
    }

    // Definir encabezados
    const headers = ['ID', 'Fecha', 'Vendedor', 'Total', 'Productos', 'Cantidades'];
    
    // Convertir datos a filas CSV
    const rows = ventas.map(venta => {
      const fecha = venta.fecha 
        ? format(new Date(venta.fecha), 'dd/MM/yyyy HH:mm', { locale: es })
        : 'Sin fecha';
      
      const vendedor = venta.usuario?.nombre || 'N/A';
      const total = venta.total.toFixed(2);
      
      // Concatenar productos y cantidades
      const productos = venta.detalles?.map(d => 
        d.producto?.nombre || `Producto ${d.producto_id}`
      ).join('; ') || '';
      
      const cantidades = venta.detalles?.map(d => 
        d.cantidad
      ).join('; ') || '';
      
      return [
        venta.id,
        fecha,
        vendedor,
        total,
        productos,
        cantidades
      ];
    });

    // Construir CSV
    const csvContent = [
      headers.join(','),
      ...rows.map(row => 
        row.map(cell => {
          // Escapar comillas y envolver en comillas si contiene comas o punto y coma
          const cellStr = String(cell);
          if (cellStr.includes(',') || cellStr.includes(';') || cellStr.includes('"')) {
            return `"${cellStr.replace(/"/g, '""')}"`;
          }
          return cellStr;
        }).join(',')
      )
    ].join('\n');

    // Crear Blob y descargar
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', `${fileName}_${format(new Date(), 'yyyy-MM-dd')}.csv`);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    console.log(`✅ CSV exportado: ${fileName}.csv`);
  } catch (error) {
    console.error('❌ Error exportando CSV:', error);
    throw error;
  }
};

/**
 * Exporta ventas con detalles completos a CSV
 */
export const exportVentasDetalladoToCSV = (ventas: Venta[], fileName: string = 'ventas_detallado'): void => {
  try {
    if (ventas.length === 0) {
      throw new Error('No hay ventas para exportar');
    }

    // Encabezados expandidos
    const headers = [
      'ID Venta',
      'Fecha',
      'Vendedor',
      'Producto',
      'Cantidad',
      'Precio Unitario',
      'Subtotal',
      'Total Venta'
    ];
    
    // Expandir cada detalle como una fila
    const rows: any[] = [];
    ventas.forEach(venta => {
      const fecha = venta.fecha 
        ? format(new Date(venta.fecha), 'dd/MM/yyyy HH:mm', { locale: es })
        : 'Sin fecha';
      
      const vendedor = venta.usuario?.nombre || 'N/A';
      const total = venta.total.toFixed(2);
      
      if (venta.detalles && venta.detalles.length > 0) {
        venta.detalles.forEach(detalle => {
          rows.push([
            venta.id,
            fecha,
            vendedor,
            detalle.producto?.nombre || `Producto ${detalle.producto_id}`,
            detalle.cantidad,
            detalle.precio_unitario.toFixed(2),
            detalle.subtotal.toFixed(2),
            total
          ]);
        });
      } else {
        rows.push([
          venta.id,
          fecha,
          vendedor,
          'Sin productos',
          0,
          '0.00',
          '0.00',
          total
        ]);
      }
    });

    // Construir CSV
    const csvContent = [
      headers.join(','),
      ...rows.map(row => 
        row.map((cell: any) => {
          const cellStr = String(cell);
          if (cellStr.includes(',') || cellStr.includes(';') || cellStr.includes('"')) {
            return `"${cellStr.replace(/"/g, '""')}"`;
          }
          return cellStr;
        }).join(',')
      )
    ].join('\n');

    // Crear Blob y descargar
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', `${fileName}_${format(new Date(), 'yyyy-MM-dd')}.csv`);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    console.log(`✅ CSV detallado exportado: ${fileName}.csv`);
  } catch (error) {
    console.error('❌ Error exportando CSV detallado:', error);
    throw error;
  }
};
