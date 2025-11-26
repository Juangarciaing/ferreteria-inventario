import React, { useEffect, useRef } from 'react';
import JsBarcode from 'jsbarcode';
import { PrinterIcon, DocumentDuplicateIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

interface BarcodeGeneratorProps {
  value: string;
  productName?: string;
  price?: number;
  showLabel?: boolean;
  format?: 'CODE128' | 'EAN13' | 'EAN8' | 'CODE39';
  width?: number;
  height?: number;
}

const BarcodeGenerator: React.FC<BarcodeGeneratorProps> = ({
  value,
  productName,
  price,
  showLabel = true,
  format = 'CODE128',
  width = 2,
  height = 100
}) => {
  const barcodeRef = useRef<SVGSVGElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (barcodeRef.current && value) {
      try {
        JsBarcode(barcodeRef.current, value, {
          format,
          width,
          height,
          displayValue: showLabel,
          fontSize: 14,
          textMargin: 5,
          margin: 10,
        });
      } catch (error) {
        console.error('Error generando código de barras:', error);
      }
    }
  }, [value, format, width, height, showLabel]);

  const handlePrint = () => {
    const printWindow = window.open('', '_blank');
    if (!printWindow) {
      toast.error('No se pudo abrir ventana de impresión');
      return;
    }

    const svgElement = barcodeRef.current;
    if (!svgElement) return;

    const svgString = new XMLSerializer().serializeToString(svgElement);
    
    printWindow.document.write(`
      <!DOCTYPE html>
      <html>
        <head>
          <title>Imprimir Código de Barras</title>
          <style>
            @media print {
              @page {
                size: 60mm 40mm;
                margin: 2mm;
              }
              body {
                margin: 0;
                padding: 0;
                font-family: Arial, sans-serif;
              }
            }
            body {
              display: flex;
              flex-direction: column;
              align-items: center;
              justify-content: center;
              padding: 10px;
            }
            .product-name {
              font-size: 12px;
              font-weight: bold;
              margin-bottom: 5px;
              text-align: center;
              max-width: 200px;
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
            }
            .price {
              font-size: 16px;
              font-weight: bold;
              color: #059669;
              margin-top: 5px;
            }
            .barcode-container {
              margin: 5px 0;
            }
          </style>
        </head>
        <body>
          ${productName ? `<div class="product-name">${productName}</div>` : ''}
          <div class="barcode-container">
            ${svgString}
          </div>
          ${price !== undefined ? `<div class="price">$${price.toFixed(2)}</div>` : ''}
        </body>
      </html>
    `);

    printWindow.document.close();
    
    setTimeout(() => {
      printWindow.print();
      printWindow.close();
    }, 250);

    toast.success('Etiqueta lista para imprimir');
  };

  const handleCopyBarcode = () => {
    navigator.clipboard.writeText(value);
    toast.success('Código de barras copiado');
  };

  const handleDownloadPNG = () => {
    const canvas = canvasRef.current;
    const svg = barcodeRef.current;
    
    if (!canvas || !svg) return;

    const svgString = new XMLSerializer().serializeToString(svg);
    const svgBlob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(svgBlob);
    
    const img = new Image();
    img.onload = () => {
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      // Ajustar tamaño del canvas al SVG
      canvas.width = img.width;
      canvas.height = img.height;
      
      // Fondo blanco
      ctx.fillStyle = 'white';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      // Dibujar imagen
      ctx.drawImage(img, 0, 0);
      
      // Descargar
      canvas.toBlob((blob) => {
        if (blob) {
          const a = document.createElement('a');
          a.href = URL.createObjectURL(blob);
          a.download = `barcode-${value}.png`;
          a.click();
          toast.success('Código de barras descargado');
        }
      });
      
      URL.revokeObjectURL(url);
    };
    
    img.src = url;
  };

  return (
    <div className="flex flex-col items-center space-y-4">
      {/* Código de Barras */}
      <div className="bg-white p-4 rounded-lg border-2 border-gray-200 shadow-sm">
        {productName && (
          <div className="text-center mb-2">
            <p className="text-sm font-semibold text-gray-800">{productName}</p>
          </div>
        )}
        
        <svg ref={barcodeRef}></svg>
        
        {price !== undefined && (
          <div className="text-center mt-2">
            <p className="text-lg font-bold text-green-600">${price.toFixed(2)}</p>
          </div>
        )}
      </div>

      {/* Canvas oculto para convertir SVG a PNG */}
      <canvas ref={canvasRef} style={{ display: 'none' }}></canvas>

      {/* Botones de Acción */}
      <div className="flex gap-2">
        <button
          onClick={handlePrint}
          className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-cyan-600 to-cyan-700 text-white text-sm font-medium rounded-lg hover:from-cyan-700 hover:to-cyan-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-cyan-500 transition-all duration-200 shadow-lg"
        >
          <PrinterIcon className="h-4 w-4 mr-2" />
          Imprimir Etiqueta
        </button>

        <button
          onClick={handleCopyBarcode}
          className="inline-flex items-center px-4 py-2 bg-white border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-cyan-500 transition-all duration-200"
        >
          <DocumentDuplicateIcon className="h-4 w-4 mr-2" />
          Copiar Código
        </button>

        <button
          onClick={handleDownloadPNG}
          className="inline-flex items-center px-4 py-2 bg-white border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-cyan-500 transition-all duration-200"
        >
          📥 Descargar PNG
        </button>
      </div>
    </div>
  );
};

export default BarcodeGenerator;
