import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { Venta } from '../types';

/**
 * Genera y descarga un PDF de factura para una venta
 */
export const generateInvoicePdf = (venta: Venta): void => {
  try {
    // Crear documento PDF
    const doc = new jsPDF();
    
    // Configurar márgenes y posición inicial
    const pageWidth = doc.internal.pageSize.width;
    const pageHeight = doc.internal.pageSize.height;
    let yPos = 20;

    // --- ENCABEZADO ---
    doc.setFontSize(20);
    doc.setFont('helvetica', 'bold');
    doc.text('FACTURA DE VENTA', pageWidth / 2, yPos, { align: 'center' });
    
    yPos += 10;
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.text('Sistema de Inventario Ferretería', pageWidth / 2, yPos, { align: 'center' });
    
    yPos += 15;

    // --- INFORMACIÓN DE LA VENTA ---
    doc.setFontSize(11);
    doc.setFont('helvetica', 'bold');
    doc.text('Información de Venta', 14, yPos);
    
    yPos += 7;
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(10);
    
    // Número de factura
    doc.text(`Factura No: ${venta.id || 'N/A'}`, 14, yPos);
    yPos += 6;
    
    // Fecha
    const fecha = venta.fecha 
      ? new Date(venta.fecha).toLocaleString('es-ES', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit'
        })
      : 'N/A';
    doc.text(`Fecha: ${fecha}`, 14, yPos);
    yPos += 6;
    
    // Vendedor
    const vendedor = venta.usuario?.nombre || 'N/A';
    doc.text(`Vendedor: ${vendedor}`, 14, yPos);
    
    yPos += 6;
    
    // Información del cliente (si está disponible)
    if (venta.cliente_nombre || venta.cliente_documento) {
      doc.setFont('helvetica', 'bold');
      doc.text('Cliente:', 14, yPos);
      yPos += 6;
      doc.setFont('helvetica', 'normal');
      
      if (venta.cliente_nombre) {
        doc.text(`  Nombre: ${venta.cliente_nombre}`, 14, yPos);
        yPos += 6;
      }
      if (venta.cliente_documento) {
        doc.text(`  Documento: ${venta.cliente_documento}`, 14, yPos);
        yPos += 6;
      }
      if (venta.cliente_telefono) {
        doc.text(`  Teléfono: ${venta.cliente_telefono}`, 14, yPos);
        yPos += 6;
      }
    }
    
    yPos += 12;

    // --- TABLA DE PRODUCTOS ---
    if (!venta.detalles || venta.detalles.length === 0) {
      doc.setFontSize(10);
      doc.text('No hay productos en esta venta', 14, yPos);
    } else {
      // Preparar datos para la tabla
      const tableData = venta.detalles.map((detalle) => {
        const nombreProducto = detalle.producto?.nombre || `Producto ID: ${detalle.producto_id}`;
        const cantidad = detalle.cantidad || 0;
        const precioUnitario = Number(detalle.precio_unitario || 0);
        const subtotal = Number(detalle.subtotal || 0);
        
        return [
          nombreProducto,
          cantidad.toString(),
          `$${precioUnitario.toFixed(2)}`,
          `$${subtotal.toFixed(2)}`
        ];
      });

      // Generar tabla con autoTable
      autoTable(doc, {
        startY: yPos,
        head: [['Producto', 'Cantidad', 'Precio Unit.', 'Subtotal']],
        body: tableData,
        theme: 'striped',
        headStyles: {
          fillColor: [41, 128, 185],
          textColor: 255,
          fontStyle: 'bold',
          halign: 'center'
        },
        styles: {
          fontSize: 10,
          cellPadding: 3
        },
        columnStyles: {
          0: { cellWidth: 80 },
          1: { halign: 'center', cellWidth: 30 },
          2: { halign: 'right', cellWidth: 35 },
          3: { halign: 'right', cellWidth: 35 }
        },
        margin: { left: 14, right: 14 }
      });

      // Obtener posición Y después de la tabla
      const finalY = (doc as any).lastAutoTable.finalY || yPos + 40;
      yPos = finalY + 10;
    }

    // --- TOTAL ---
    // Línea divisoria
    doc.setLineWidth(0.5);
    doc.line(pageWidth - 80, yPos, pageWidth - 14, yPos);
    yPos += 8;

    // Total
    const total = Number(venta.total || 0);
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.text(`TOTAL: $${total.toFixed(2)}`, pageWidth - 14, yPos, { align: 'right' });
    
    yPos += 15;

    // --- PIE DE PÁGINA ---
    if (yPos < pageHeight - 30) {
      doc.setFontSize(9);
      doc.setFont('helvetica', 'italic');
      doc.setTextColor(100);
      doc.text(
        'Gracias por su compra',
        pageWidth / 2,
        pageHeight - 20,
        { align: 'center' }
      );
    }

    // --- GUARDAR PDF ---
    const fileName = `Factura-${venta.id || 'temp'}.pdf`;
    doc.save(fileName);
    
    console.log(`✅ PDF generado: ${fileName}`);
    
  } catch (error) {
    console.error('❌ Error generando PDF:', error);
    throw error;
  }
};
