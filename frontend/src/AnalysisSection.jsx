import { useState, useEffect } from 'react';
import { BarChart2, RefreshCw, Filter } from 'lucide-react';

const API_BASE = 'http://localhost:5000/api';

export default function AnalysisSection() {
  const [recomendaciones, setRecomendaciones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filtroNivel, setFiltroNivel] = useState('TODOS');
  const [filtroIAR, setFiltroIAR] = useState(0);

  useEffect(() => {
    cargarRecomendaciones();
  }, []);

  const cargarRecomendaciones = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/recomendaciones`, {
        credentials: 'include'
      });

      if (response.status === 401) {
        throw new Error('Sesión expirada');
      }

      if (!response.ok) {
        throw new Error('Error al cargar recomendaciones');
      }

      const data = await response.json();
      setRecomendaciones(data);
    } catch (error) {
      console.error('Error:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const recomendacionesFiltradas = recomendaciones.filter(r => {
    if (r.iar_score < filtroIAR) return false;
    if (filtroNivel !== 'TODOS' && r.nivel_recomendacion !== filtroNivel) return false;
    return true;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-purple-500 border-t-transparent mx-auto mb-4"></div>
          <p className="text-purple-200">Cargando análisis...</p>
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
            onClick={cargarRecomendaciones}
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
            <BarChart2 size={32} className="text-purple-400" />
            Análisis Detallado
          </h2>
          <p className="text-purple-400 mt-1">Análisis profundo de categorías y recomendaciones</p>
        </div>
        <button
          onClick={cargarRecomendaciones}
          className="p-2 rounded-lg bg-slate-700 hover:bg-slate-600 transition-colors"
          title="Refrescar datos"
        >
          <RefreshCw className="text-purple-400" size={20} />
        </button>
      </div>

      {/* Filtros */}
      <div className="bg-slate-800/50 backdrop-blur-sm border border-purple-500/20 rounded-xl p-6">
        <div className="flex items-center gap-4 flex-wrap">
          <Filter className="text-purple-400" size={20} />
          <div className="flex-1 min-w-[200px]">
            <label className="text-purple-200 text-sm block mb-2">IAR Mínimo: {filtroIAR}</label>
            <input
              type="range"
              min="0"
              max="100"
              value={filtroIAR}
              onChange={(e) => setFiltroIAR(parseInt(e.target.value))}
              className="w-full accent-purple-500"
            />
          </div>
          <div className="flex-1 min-w-[200px]">
            <label className="text-purple-200 text-sm block mb-2">Nivel de Recomendación</label>
            <select
              value={filtroNivel}
              onChange={(e) => setFiltroNivel(e.target.value)}
              className="w-full bg-slate-700 text-white border border-purple-500/30 rounded-lg px-4 py-2"
            >
              <option value="TODOS">Todos</option>
              <option value="ALTAMENTE_RECOMENDADO">Altamente Recomendado</option>
              <option value="EVALUAR">Evaluar</option>
              <option value="NO_RECOMENDADO">No Recomendado</option>
            </select>
          </div>
        </div>
        <p className="text-purple-300 text-sm mt-4">
          Mostrando {recomendacionesFiltradas.length} de {recomendaciones.length} categorías
        </p>
      </div>

      {/* Análisis detallado */}
      <div className="space-y-4">
        {recomendacionesFiltradas.map(rec => (
          <div key={rec.id} className="bg-slate-800/50 rounded-xl p-6 border border-purple-500/30 shadow-lg hover:shadow-2xl transition-shadow">
            <div className="flex items-center justify-between mb-4 flex-wrap gap-4">
              <h3 className="text-xl font-bold text-white">{rec.categoria.replace(/_/g, ' ')}</h3>
              <div className="flex items-center gap-3">
                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                  rec.nivel_recomendacion === 'ALTAMENTE_RECOMENDADO'
                    ? 'bg-green-500/20 text-green-300'
                    : rec.nivel_recomendacion === 'EVALUAR'
                    ? 'bg-yellow-500/20 text-yellow-300'
                    : 'bg-red-500/20 text-red-300'
                }`}>
                  {rec.nivel_recomendacion.replace(/_/g, ' ')}
                </span>
                <span className="px-4 py-2 bg-purple-600 text-white rounded-full font-bold text-lg">
                  IAR: {rec.iar_score.toFixed(1)}
                </span>
              </div>
            </div>
            
            <p className="text-purple-100 mb-4 leading-relaxed">{rec.recomendacion_texto}</p>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div className="bg-slate-700/50 rounded-lg p-4">
                <p className="text-purple-300 text-sm mb-1">Razón Principal:</p>
                <p className="text-white font-medium">{rec.razon_principal}</p>
              </div>
              <div className="bg-slate-700/50 rounded-lg p-4">
                <p className="text-purple-300 text-sm mb-1">Prioridad:</p>
                <span className={`inline-block px-3 py-1 rounded text-sm font-semibold ${
                  rec.prioridad === 'ALTA' ? 'bg-red-500/20 text-red-300' :
                  rec.prioridad === 'MEDIA' ? 'bg-yellow-500/20 text-yellow-300' :
                  'bg-green-500/20 text-green-300'
                }`}>
                  {rec.prioridad}
                </span>
              </div>
              <div className="bg-slate-700/50 rounded-lg p-4">
                <p className="text-purple-300 text-sm mb-1">Total Tickets:</p>
                <p className="text-white font-bold text-lg">{rec.total_tickets.toLocaleString()}</p>
              </div>
            </div>
            
            {rec.acciones_sugeridas && rec.acciones_sugeridas.length > 0 && (
              <div className="bg-slate-700/30 rounded-lg p-4">
                <p className="text-purple-300 text-sm font-semibold mb-2">Acciones Sugeridas:</p>
                <ul className="space-y-2">
                  {rec.acciones_sugeridas.map((accion, idx) => (
                    <li key={idx} className="text-purple-100 text-sm flex items-start gap-2">
                      <span className="text-purple-400 mt-1">▸</span>
                      <span>{accion}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}