import { useState, useEffect } from 'react';
import { Database, RefreshCw } from 'lucide-react';

const API_BASE = 'http://localhost:5000/api';

export default function TicketsSection() {
  const [metricas, setMetricas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    cargarMetricas();
  }, []);

  const cargarMetricas = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/metricas`, {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (response.status === 401) {
        throw new Error('Sesión expirada');
      }

      if (!response.ok) {
        throw new Error('Error al cargar métricas');
      }

      const data = await response.json();
      setMetricas(data);
    } catch (error) {
      console.error('Error:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-purple-500 border-t-transparent mx-auto mb-4"></div>
          <p className="text-purple-200">Cargando métricas...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <p className="text-red-300 mb-4">{error}</p>
          <button
            onClick={cargarMetricas}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white flex items-center gap-3">
            <Database size={32} className="text-purple-400" />
            Métricas por Categoría
          </h2>
          <p className="text-purple-400 mt-1">Análisis detallado de tickets por categoría</p>
        </div>
        <button
          onClick={cargarMetricas}
          className="p-2 rounded-lg bg-slate-700 hover:bg-slate-600 transition-colors"
          title="Refrescar datos"
        >
          <RefreshCw className="text-purple-400" size={20} />
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {metricas.map(metrica => (
          <div key={metrica.id} className="bg-slate-800/50 backdrop-blur-sm border border-purple-500/20 rounded-xl p-6 shadow-xl">
            <h3 className="text-xl font-bold text-white mb-4 border-b border-purple-500/30 pb-2">
              {metrica.categoria.replace(/_/g, ' ')}
            </h3>
            
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-purple-200">Total Tickets:</span>
                <span className="text-white font-bold text-lg">{metrica.total_tickets.toLocaleString()}</span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-purple-200">Complejidad:</span>
                <span className="text-white font-bold">{metrica.complejidad_promedio.toFixed(1)}</span>
              </div>
              
              <div className="mt-4">
                <p className="text-purple-300 text-sm mb-3 font-semibold">Urgencia:</p>
                <div className="space-y-2">
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-red-300 flex items-center gap-2">
                      <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                      Crítica:
                    </span>
                    <span className="text-white">{metrica.urgencia_critica}</span>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-orange-300 flex items-center gap-2">
                      <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
                      Alta:
                    </span>
                    <span className="text-white">{metrica.urgencia_alta}</span>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-yellow-300 flex items-center gap-2">
                      <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                      Media:
                    </span>
                    <span className="text-white">{metrica.urgencia_media}</span>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-green-300 flex items-center gap-2">
                      <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                      Baja:
                    </span>
                    <span className="text-white">{metrica.urgencia_baja}</span>
                  </div>
                </div>
              </div>
              
              <div className="mt-4">
                <p className="text-purple-300 text-sm mb-3 font-semibold">Sentimiento:</p>
                <div className="space-y-2">
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-green-300">😊 Positivo:</span>
                    <span className="text-white">{metrica.sentimiento_positivo}</span>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-300">😐 Neutral:</span>
                    <span className="text-white">{metrica.sentimiento_neutral}</span>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-red-300">😞 Negativo:</span>
                    <span className="text-white">{metrica.sentimiento_negativo}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}