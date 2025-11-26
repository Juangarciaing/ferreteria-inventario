import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const TestPage: React.FC = () => {
  const { user, loading, isAdmin } = useAuth();

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Página de Prueba</h1>
      <div className="bg-white p-4 rounded-lg shadow">
        <h2 className="text-lg font-semibold mb-2">Estado del Usuario:</h2>
        <pre className="bg-gray-100 p-2 rounded text-sm overflow-auto">
          {JSON.stringify({ user, loading, isAdmin }, null, 2)}
        </pre>
      </div>
      {user ? (
        <div className="mt-4 p-4 bg-green-100 border border-green-400 text-green-700 rounded">
          ✅ Usuario autenticado: {user.nombre}
        </div>
      ) : (
        <div className="mt-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          ❌ No hay usuario autenticado
        </div>
      )}
    </div>
  );
};

export default TestPage;