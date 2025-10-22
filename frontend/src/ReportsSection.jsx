import React, { useState, useEffect } from 'react';
import { FileText, RefreshCw, Filter } from 'lucide-react';

const API_BASE = 'http://localhost:5000/api';

export default function ReportsSection() {
  const [recomendaciones, setRecomendaciones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  // Los filtros ahora viven DENTRO de esta sección
  const [filters, setFilters] = useState({
    minIAR: 0,
    nivelRecomendacion: 'TODOS'
  });

  useEffect(() => {
    cargarRecomendaciones();
  }, []);

  const cargarRecomendaciones = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/recomendaciones`, { credentials: 'include' });
      if (response.status === 401) throw new Error('Sesión expirada. Por favor, inicia sesión de nuevo.');
      if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText || 'No se pudieron cargar las recomendaciones'}`);
      const data = await response.json();
      setRecomendaciones(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Error en ReportsSection:", err);
      setError(err.message);
      setRecomendaciones([]);
    } finally {
      setLoading(false);
    }
  };

  // Filtrado se aplica a las recomendaciones cargadas aquí
  const recomendacionesFiltradas = recomendaciones.filter(r =>
    (r.iar_score ?? 0) >= filters.minIAR &&
    (filters.nivelRecomendacion === 'TODOS' || r.nivel_recomendacion === filters.nivelRecomendacion)
  );

  // Funciones de formato
  const formatearMoneda = (valor) => new Intl.NumberFormat('es-GT', { style: 'currency', currency: 'USD', minimumFractionDigits: 0 }).format(valor || 0);
  const formatearPorcentaje = (valor) => `${(valor || 0).toFixed(1)}%`;

  // --- Renderizado ---
  return (
    <div className="space-y-6">
      {/* Header de la sección */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h2 className="text-3xl font-bold text-white flex items-center gap-3">
            <FileText size={32} className="text-purple-400" />
            Reporte de Recomendaciones
          </h2>
          <p className="text-purple-400 mt-1">Tabla detallada y filtrable de las recomendaciones de la IA.</p>
        </div>
        <button onClick={cargarRecomendaciones} className="p-2 rounded-lg bg-slate-700 hover:bg-slate-600 transition-colors" title="Refrescar datos">
          <RefreshCw className="text-purple-400" size={20} />
        </button>
      </div>

      {/* Indicador de Carga */}
      {loading && (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-purple-500 border-t-transparent"></div>
        </div>
      )}

      {/* Mensaje de Error */}
      {error && !loading && (
        <div className="text-center p-10 bg-red-900/30 border border-red-500/50 rounded-xl">
          <p className="text-red-300 mb-4 font-semibold">Error al cargar:</p>
          <p className="text-red-200 mb-4">{error}</p>
          <button onClick={cargarRecomendaciones} className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg">Reintentar</button>
        </div>
      )}

      {/* Contenido Principal (Filtros y Tabla) */}
      {!loading && !error && (
        <>
          {/* Filtros */}
          <div className="bg-slate-800/50 backdrop-blur-sm border border-purple-500/20 rounded-xl p-6">
            <div className="flex items-center gap-4 flex-wrap">
              <Filter className="text-purple-400" size={20} />
              <div className="flex-1 min-w-[200px]">
                <label className="text-purple-200 text-sm block mb-2">IAR Mínimo: {filters.minIAR}</label>
                <input type="range" min="0" max="100" value={filters.minIAR} onChange={(e) => setFilters({ ...filters, minIAR: parseInt(e.target.value) })} className="w-full accent-purple-500" />
              </div>
              <div className="flex-1 min-w-[200px]">
                <label className="text-purple-200 text-sm block mb-2">Nivel de Recomendación</label>
                <select value={filters.nivelRecomendacion} onChange={(e) => setFilters({ ...filters, nivelRecomendacion: e.target.value })} className="w-full bg-slate-700 text-white border border-purple-500/30 rounded-lg px-4 py-2">
                  <option value="TODOS">Todos</option>
                  <option value="ALTAMENTE_RECOMENDADO">Altamente Recomendado</option>
                  <option value="EVALUAR">Evaluar</option>
                  <option value="NO_RECOMENDADO">No Recomendado</option>
                </select>
              </div>
            </div>
          </div>

          {/* Tabla de Recomendaciones */}
          <div className="bg-slate-800/50 backdrop-blur-sm border border-purple-500/20 rounded-xl shadow-xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-purple-900/50">
                  <tr>
                    <th className="px-6 py-4 text-left text-purple-200 font-semibold">Categoría</th>
                    <th className="px-6 py-4 text-center text-purple-200 font-semibold">IAR</th>
                    <th className="px-6 py-4 text-center text-purple-200 font-semibold">Nivel</th>
                    <th className="px-6 py-4 text-right text-purple-200 font-semibold">Tickets</th>
                    <th className="px-6 py-4 text-right text-purple-200 font-semibold">ROI Anual</th>
                    <th className="px-6 py-4 text-right text-purple-200 font-semibold">ROI %</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-purple-500/20">
                  {recomendacionesFiltradas.length > 0 ? (
                    recomendacionesFiltradas.map((rec) => (
                      <tr key={rec.id} className="hover:bg-purple-900/20 transition-colors">
                        <td className="px-6 py-4 text-white font-medium capitalize">{rec.categoria.replace(/_/g, ' ')}</td>
                        <td className="px-6 py-4 text-center"><span className="px-3 py-1 bg-purple-600 text-white rounded-full text-sm font-bold">{rec.iar_score.toFixed(1)}</span></td>
                        <td className="px-6 py-4 text-center">
                          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${rec.nivel_recomendacion === 'ALTAMENTE_RECOMENDADO' ? 'bg-green-500/20 text-green-300' : rec.nivel_recomendacion === 'EVALUAR' ? 'bg-yellow-500/20 text-yellow-300' : 'bg-red-500/20 text-red-300'}`}>
                            {rec.nivel_recomendacion.replace(/_/g, ' ')}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-right text-purple-100">{rec.total_tickets.toLocaleString()}</td>
                        <td className="px-6 py-4 text-right text-green-300 font-semibold">{formatearMoneda(rec.roi_anual_estimado)}</td>
                        <td className="px-6 py-4 text-right text-blue-300 font-semibold">{formatearPorcentaje(rec.roi_porcentaje)}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="6" className="text-center py-10 text-purple-300">No hay recomendaciones que coincidan con los filtros.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
            <div className="px-6 py-4 bg-purple-900/30 border-t border-purple-500/20">
              <p className="text-purple-200 text-sm">Mostrando {recomendacionesFiltradas.length} de {recomendaciones.length} categorías</p>
            </div>
          </div>
        </>
      )}
    </div>
  );
}