import React, { useState } from 'react';
import { XMarkIcon, DocumentArrowDownIcon, TableCellsIcon } from '@heroicons/react/24/outline';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import toast from 'react-hot-toast';

interface ExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  data: Record<string, unknown>[];
  filename?: string;
}

const ExportModal: React.FC<ExportModalProps> = ({
  isOpen,
  onClose,
  title,
  data,
  filename = 'export',
}) => {
  const [exportFormat, setExportFormat] = useState<'pdf' | 'excel' | 'csv'>('pdf');
  const [dateRange, setDateRange] = useState({
    desde: format(new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), 'yyyy-MM-dd'),
    hasta: format(new Date(), 'yyyy-MM-dd'),
  });
  const [includeCharts, setIncludeCharts] = useState(true);
  const [isExporting, setIsExporting] = useState(false);

  const handleExport = async () => {
    setIsExporting(true);
    
    try {
      // Simular proceso de exportación
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      if (exportFormat === 'csv') {
        exportToCSV();
      } else if (exportFormat === 'excel') {
        exportToExcel();
      } else {
        exportToPDF();
      }
      
      onClose();
    } catch (error) {
      console.error('Error exporting:', error);
    } finally {
      setIsExporting(false);
    }
  };

  const exportToCSV = () => {
    if (!data.length) return;
    
    const headers = Object.keys(data[0]);
    const csvContent = [
      headers.join(','),
      ...data.map(row => 
        headers.map(header => {
          const value = row[header];
          return typeof value === 'string' && value.includes(',') 
            ? `"${value}"` 
            : value;
        }).join(',')
      )
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `${filename}_${format(new Date(), 'yyyy-MM-dd')}.csv`;
    link.click();
  };

  const exportToExcel = () => {
    try {
      // Crear CSV con formato Excel
      const headers = Object.keys(data[0]);
      const csvContent = [
        headers.join('\t'),
        ...data.map(row => 
          headers.map(header => {
            const value = row[header];
            return typeof value === 'string' && value.includes('\t') 
              ? `"${value}"` 
              : value;
          }).join('\t')
        )
      ].join('\n');
      
      const blob = new Blob([csvContent], { type: 'application/vnd.ms-excel;charset=utf-8;' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `${filename}_${format(new Date(), 'yyyy-MM-dd')}.xls`;
      link.click();
      
      toast.success('Archivo Excel generado exitosamente');
    } catch (error) {
      console.error('Error al exportar a Excel:', error);
      toast.error('Error al generar archivo Excel');
    }
  };

  const exportToPDF = () => {
    try {
      // Crear PDF simple con HTML y print
      const headers = Object.keys(data[0] || {});
      
      // Crear contenido HTML para imprimir
      const printWindow = window.open('', '', 'width=800,height=600');
      if (!printWindow) {
        toast.error('No se pudo abrir la ventana de impresión');
        return;
      }
      
      printWindow.document.write(`
        <!DOCTYPE html>
        <html>
          <head>
            <title>${title}</title>
            <style>
              body { font-family: Arial, sans-serif; padding: 20px; }
              h1 { color: #333; }
              .info { margin: 20px 0; color: #666; }
              table { width: 100%; border-collapse: collapse; margin-top: 20px; }
              th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
              th { background-color: #3B82F6; color: white; }
              tr:nth-child(even) { background-color: #f9f9f9; }
              @media print {
                body { margin: 0; }
              }
            </style>
          </head>
          <body>
            <h1>${title}</h1>
            <div class="info">
              <p><strong>Generado:</strong> ${format(new Date(), "dd/MM/yyyy 'a las' HH:mm", { locale: es })}</p>
              <p><strong>Período:</strong> ${format(new Date(dateRange.desde), 'dd/MM/yyyy', { locale: es })} - ${format(new Date(dateRange.hasta), 'dd/MM/yyyy', { locale: es })}</p>
              <p><strong>Total de registros:</strong> ${data.length}</p>
            </div>
            <table>
              <thead>
                <tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr>
              </thead>
              <tbody>
                ${data.map(row => `
                  <tr>${headers.map(h => `<td>${row[h] ?? ''}</td>`).join('')}</tr>
                `).join('')}
              </tbody>
            </table>
          </body>
        </html>
      `);
      
      printWindow.document.close();
      printWindow.focus();
      
      setTimeout(() => {
        printWindow.print();
        printWindow.close();
      }, 250);
      
      toast.success('PDF generado - Use Ctrl+P para guardar como PDF');
    } catch (error) {
      console.error('Error al exportar a PDF:', error);
      toast.error('Error al generar archivo PDF');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={onClose} />

        <span className="hidden sm:inline-block sm:align-middle sm:h-screen">&#8203;</span>

        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg leading-6 font-medium text-gray-900">
                Exportar {title}
              </h3>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Formato de Exportación
                </label>
                <div className="grid grid-cols-3 gap-3">
                  <button
                    onClick={() => setExportFormat('pdf')}
                    className={`p-3 border rounded-lg text-center transition-colors ${
                      exportFormat === 'pdf'
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                  >
                    <DocumentArrowDownIcon className="h-6 w-6 mx-auto mb-1" />
                    <div className="text-sm font-medium">PDF</div>
                  </button>
                  
                  <button
                    onClick={() => setExportFormat('excel')}
                    className={`p-3 border rounded-lg text-center transition-colors ${
                      exportFormat === 'excel'
                        ? 'border-green-500 bg-green-50 text-green-700'
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                  >
                    <TableCellsIcon className="h-6 w-6 mx-auto mb-1" />
                    <div className="text-sm font-medium">Excel</div>
                  </button>
                  
                  <button
                    onClick={() => setExportFormat('csv')}
                    className={`p-3 border rounded-lg text-center transition-colors ${
                      exportFormat === 'csv'
                        ? 'border-purple-500 bg-purple-50 text-purple-700'
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                  >
                    <TableCellsIcon className="h-6 w-6 mx-auto mb-1" />
                    <div className="text-sm font-medium">CSV</div>
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Rango de Fechas
                </label>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs text-gray-500">Desde</label>
                    <input
                      type="date"
                      value={dateRange.desde}
                      onChange={(e) => setDateRange(prev => ({ ...prev, desde: e.target.value }))}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500">Hasta</label>
                    <input
                      type="date"
                      value={dateRange.hasta}
                      onChange={(e) => setDateRange(prev => ({ ...prev, hasta: e.target.value }))}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>
              </div>

              {exportFormat === 'pdf' && (
                <div>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={includeCharts}
                      onChange={(e) => setIncludeCharts(e.target.checked)}
                      className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                    />
                    <span className="ml-2 text-sm text-gray-700">
                      Incluir gráficos en el PDF
                    </span>
                  </label>
                </div>
              )}

              <div className="bg-gray-50 p-3 rounded-lg">
                <div className="text-sm text-gray-600">
                  <strong>Registros a exportar:</strong> {data.length}
                </div>
                <div className="text-sm text-gray-600">
                  <strong>Período:</strong> {format(new Date(dateRange.desde), 'dd/MM/yyyy', { locale: es })} - {format(new Date(dateRange.hasta), 'dd/MM/yyyy', { locale: es })}
                </div>
              </div>
            </div>

            <div className="flex justify-end space-x-3 pt-6">
              <button
                type="button"
                onClick={onClose}
                disabled={isExporting}
                className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                Cancelar
              </button>
              <button
                onClick={handleExport}
                disabled={isExporting}
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isExporting ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Exportando...
                  </div>
                ) : (
                  `Exportar ${exportFormat.toUpperCase()}`
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExportModal;