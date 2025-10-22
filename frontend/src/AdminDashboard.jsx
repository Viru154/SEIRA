import React, { useState, useEffect } from 'react';
// Importa los componentes de sección
import UserManagement from './UserManagement';
import TicketsSection from './TicketsSection'; // Tu componente de Métricas
import AnalysisSection from './AnalysisSection';
import ReportsSection from './ReportsSection';   // El nuevo componente de Reportes/Recomendaciones

import { BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import {
  TrendingUp, DollarSign, Target, AlertCircle, /* Filter ya no aquí */ Download,
  Menu, X, Search, Bell, Settings, LogOut, Home, FileText,
  BarChart2, Database, ChevronRight, Moon, Sun, RefreshCw,
  Shield, HelpCircle
} from 'lucide-react';

const API_BASE = 'http://localhost:5000/api';

// Constantes de colores (restauradas)
const COLORS = {
  primary: '#8B5CF6',
  secondary: '#C084FC',
  success: '#10B981',
  warning: '#F59E0B',
  danger: '#EF4444',
  info: '#3B82F6'
};
const CHART_COLORS = ['#8B5CF6', '#C084FC', '#A78BFA', '#DDD6FE', '#EDE9FE'];


// Componente principal del Dashboard
export default function AdminDashboard({ user, onLogout }) {
  // --- Estados ---
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeSection, setActiveSection] = useState('dashboard');
  const [darkMode, setDarkMode] = useState(true); // Modo oscuro por defecto
  const [resumen, setResumen] = useState(null);
  const [recomendaciones, setRecomendaciones] = useState([]); // Para gráficos del dashboard
  const [loading, setLoading] = useState(true);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [accessDenied, setAccessDenied] = useState(false);
  // 'filters' y 'activeTab' ya no son necesarios aquí

  // --- Carga Inicial ---
  useEffect(() => {
    if (!user) { onLogout(); return; }
    if (user.rol === 'cliente') { setAccessDenied(true); setLoading(false); return; }
    cargarDatosResumenYRecomendaciones();
  }, [user, onLogout]);

  // --- Carga Datos para KPIs y gráficos ---
  const cargarDatosResumenYRecomendaciones = async () => {
    setLoading(true);
    setAccessDenied(false); // Reiniciar por si acaso
    try {
      // Solo cargamos resumen y recomendaciones (para los gráficos)
      const [resumenRes, recRes] = await Promise.all([
        fetch(`${API_BASE}/dashboard/resumen`, { credentials: 'include' }),
        fetch(`${API_BASE}/recomendaciones`, { credentials: 'include' })
      ]);
      if (resumenRes.status === 401 || recRes.status === 401) { alert('Sesión expirada.'); onLogout(); return; }
      if (!resumenRes.ok || !recRes.ok) { throw new Error('Error al cargar datos del dashboard'); }
      const resumenData = await resumenRes.json();
      const recData = await recRes.json();
      setResumen(resumenData);
      setRecomendaciones(Array.isArray(recData) ? recData : []); // Asegurar array
    } catch (error) { console.error('Error cargando datos:', error); alert(`Error: ${error.message}`); setRecomendaciones([]); }
    finally { setLoading(false); }
  };

  // --- Funciones Utilitarias ---
  const handleLogout = () => { if (confirm('¿Estás seguro que deseas cerrar sesión?')) { onLogout(); } };
  const tienePermiso = (permiso) => {
    const rol = user?.rol;
    if (!rol) return false;
    if (permiso === 'admin') return rol === 'admin'; // Para sección Usuarios
    if (permiso === 'analisis') return ['admin', 'analista'].includes(rol); // Para Análisis, Reportes, Métricas
    // Mantenemos 'dashboard' para la sección principal y Documentación
    if (permiso === 'dashboard') return ['admin', 'analista', 'operador'].includes(rol);
    return false;
  };
  const formatearMoneda = (valor) => new Intl.NumberFormat('es-GT', { style: 'currency', currency: 'USD', minimumFractionDigits: 0 }).format(valor || 0);
  const formatearPorcentaje = (valor) => `${(valor || 0).toFixed(1)}%`;
  const exportarDatos = (formato) => alert(`Función de exportar ${formato} en desarrollo`);

  // --- Renderizado Condicional: Acceso Denegado ---
  if (accessDenied) {
    // Código JSX completo para Acceso Denegado (restaurado)
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-6">
        <div className="text-center">
          <div className="inline-block p-8 bg-slate-800/80 backdrop-blur-xl border border-red-500/30 rounded-2xl shadow-2xl">
            <Shield className="text-red-400 mx-auto mb-4" size={80} />
            <h1 className="text-3xl font-bold text-white mb-2">Acceso Denegado</h1>
            <p className="text-purple-200 mb-6">Esta sección es solo para personal autorizado.</p>
            <div className="space-y-3 mb-6">
              <p className="text-purple-300 text-sm">Usuario: <span className="font-semibold">{user?.username}</span></p>
              <p className="text-purple-300 text-sm">Rol: <span className="font-semibold capitalize">{user?.rol}</span></p>
            </div>
            <button onClick={handleLogout} className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg flex items-center gap-2 mx-auto transition-colors">
              <LogOut size={20} /> Cerrar Sesión
            </button>
          </div>
        </div>
      </div>
    );
  }

  // --- Renderizado Condicional: Cargando ---
  // Muestra 'Cargando' solo si estamos en dashboard y no hay resumen
  if (loading && !resumen && activeSection === 'dashboard') {
     // Código JSX completo para Loading (restaurado)
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-20 w-20 border-4 border-purple-500 border-t-transparent mx-auto mb-4"></div>
          <p className="text-purple-200 text-xl font-semibold">Cargando SEIRA 2.0...</p>
          {user && <p className="text-purple-400 text-sm mt-2">Bienvenido, {user.username}</p>}
        </div>
      </div>
    );
  }

  // --- Preparación datos gráficos ---
  const recsArray = Array.isArray(recomendaciones) ? recomendaciones : [];
  const dataGraficoIAR = recsArray.sort((a, b) => (b.iar_score ?? 0) - (a.iar_score ?? 0)).slice(0, 10).map(r => ({ categoria: (r.categoria || '').replace(/_/g, ' ').substring(0, 20), IAR: r.iar_score ?? 0 }));
  const dataGraficoROI = recsArray.sort((a, b) => (b.roi_anual_estimado ?? 0) - (a.roi_anual_estimado ?? 0)).slice(0, 8).map(r => ({ categoria: (r.categoria || '').replace(/_/g, ' ').substring(0, 15), ahorro: (r.roi_anual_estimado || 0) / 1000 }));
  const dataNivelRecomendacion = [
    { nombre: 'Altamente Rec.', valor: recsArray.filter(r => r.nivel_recomendacion === 'ALTAMENTE_RECOMENDADO').length },
    { nombre: 'Evaluar', valor: recsArray.filter(r => r.nivel_recomendacion === 'EVALUAR').length },
    { nombre: 'No Rec.', valor: recsArray.filter(r => r.nivel_recomendacion === 'NO_RECOMENDADO').length }
  ];

  // --- Items Menú ---
  // Verificamos IDs y permisos
  const menuItems = [
    { id: 'dashboard', icon: Home, label: 'Dashboard', section: 'dashboard', permiso: 'dashboard' },
    { id: 'analytics', icon: BarChart2, label: 'Análisis', section: 'analytics', permiso: 'analisis' },
    { id: 'reports', icon: FileText, label: 'Reportes', section: 'reports', permiso: 'analisis' }, // Contendrá Recomendaciones
    { id: 'tickets', icon: Database, label: 'Métricas', section: 'tickets', permiso: 'analisis' }, // Contendrá Métricas por categoría
    { id: 'users', icon: Shield, label: 'Usuarios', section: 'users', permiso: 'admin' },
    { id: 'docs', icon: FileText, label: 'Documentación', section: 'docs', permiso: 'dashboard' }
  ];
  const notifications = [ /* ... Tus notificaciones ... */ ];

  // --- JSX Principal ---
  return (
    <div className={`min-h-screen ${darkMode ? 'bg-slate-900 text-slate-100' : 'bg-gray-100 text-gray-900'} transition-colors duration-300 font-sans`}>
      {/* Sidebar */}
      <aside className={`fixed top-0 left-0 h-full ${darkMode ? 'bg-slate-800' : 'bg-white'} border-r ${darkMode ? 'border-purple-500/20' : 'border-gray-200'} transition-all duration-300 z-50 ${sidebarOpen ? 'w-64' : 'w-20'}`}>
        <div className="flex flex-col h-full">
          {/* Header Sidebar */}
          <div className="p-6 border-b border-purple-500/20 flex items-center justify-between">
            {sidebarOpen && ( <div> <h1 className="text-2xl font-bold text-purple-400">SEIRA 2.0</h1> <p className="text-xs text-purple-300">Admin Panel</p> </div> )}
            <button onClick={() => setSidebarOpen(!sidebarOpen)} className={`p-2 rounded-lg ${darkMode ? 'hover:bg-slate-700' : 'hover:bg-gray-100'} transition-colors ${!sidebarOpen && 'mx-auto'}`}> {sidebarOpen ? <X size={20} className="text-purple-400" /> : <Menu size={20} className="text-purple-400" />} </button>
          </div>
          {/* Navegación Sidebar */}
          <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
            {menuItems.filter(item => tienePermiso(item.permiso)).map(item => {
              const Icon = item.icon; const isActive = activeSection === item.section;
              return ( <button key={item.id} onClick={() => setActiveSection(item.section)} className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${isActive ? 'bg-purple-600 text-white shadow-lg' : `${darkMode ? 'text-purple-200 hover:bg-slate-700' : 'text-gray-600 hover:bg-gray-100'}`}`} title={item.label}> <Icon size={20} className={isActive ? 'text-white' : `${darkMode ? 'text-purple-400' : 'text-purple-600'}`} /> {sidebarOpen && <span className="font-medium">{item.label}</span>} </button> );
            })}
          </nav>
          {/* Menú Usuario Sidebar */}
          <div className="p-4 border-t border-purple-500/20">
             <div className="relative">
                <button onClick={() => setShowUserMenu(!showUserMenu)} className={`w-full flex items-center gap-3 p-3 rounded-lg ${darkMode ? 'bg-slate-700 hover:bg-slate-600' : 'bg-gray-100 hover:bg-gray-200'} transition-colors`}>
                  <div className="w-10 h-10 rounded-full bg-purple-600 flex items-center justify-center text-white font-bold">{user?.username?.charAt(0).toUpperCase()}</div>
                  {sidebarOpen && ( <div className="flex-1 text-left"> <p className={`font-semibold text-sm ${darkMode ? 'text-white' : 'text-slate-800'} truncate`}>{user?.username}</p> <p className={`text-xs ${darkMode ? 'text-purple-400' : 'text-purple-600'} capitalize`}>{user?.rol}</p> </div> )}
                </button>
                {showUserMenu && sidebarOpen && (
                  <div className={`absolute bottom-full left-0 w-full mb-2 ${darkMode ? 'bg-slate-700' : 'bg-white'} rounded-lg shadow-xl border ${darkMode ? 'border-purple-500/20' : 'border-gray-200'} overflow-hidden`}>
                    <div className="p-3 border-b border-purple-500/20"><p className={`text-sm font-semibold ${darkMode ? 'text-white' : 'text-slate-800'}`}>{user?.nombre_completo || user?.username}</p><p className={`text-xs ${darkMode ? 'text-purple-400' : 'text-purple-600'}`}>{user?.email}</p></div>
                    <button onClick={handleLogout} className={`w-full flex items-center gap-2 px-4 py-3 ${darkMode ? 'hover:bg-slate-600 text-red-300' : 'hover:bg-gray-100 text-red-600'} transition-colors`}><LogOut size={18} /> <span className="text-sm font-medium">Cerrar Sesión</span></button>
                  </div>
                )}
             </div>
          </div>
        </div>
      </aside>

      {/* Contenido Principal */}
      <div className={`transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-20'}`}>
        {/* Header */}
        <header className={`sticky top-0 z-40 ${darkMode ? 'bg-slate-800/95' : 'bg-white/95'} backdrop-blur-sm border-b ${darkMode ? 'border-purple-500/20' : 'border-gray-200'} shadow-lg`}>
          <div className="px-6 py-4">
            <div className="flex items-center justify-between">
              {/* Breadcrumb */}
              <div className="flex items-center gap-2 text-sm">
                {React.createElement(menuItems.find(item => item.section === activeSection)?.icon || Home, { size: 16, className: darkMode ? "text-purple-400" : "text-purple-600" })}
                <ChevronRight size={16} className={darkMode ? "text-purple-400" : "text-gray-400"} />
                <span className={`${darkMode ? 'text-purple-200' : 'text-gray-700'} capitalize font-medium`}>
                  {menuItems.find(item => item.section === activeSection)?.label || 'Dashboard'}
                </span>
              </div>
              {/* Iconos Header */}
              <div className="flex items-center gap-4">
                 <div className="relative hidden md:block"> <Search size={18} className={`absolute left-3 top-1/2 -translate-y-1/2 ${darkMode ? 'text-purple-400' : 'text-gray-400'}`} /> <input type="text" placeholder="Buscar..." className={`pl-10 pr-4 py-2 rounded-lg ${darkMode ? 'bg-slate-700 text-white border-purple-500/30 focus:border-purple-500' : 'bg-gray-100 text-slate-800 border-gray-300 focus:border-purple-500'} border focus:outline-none w-64`}/> </div>
                 <button onClick={() => setDarkMode(!darkMode)} className={`p-2 rounded-lg ${darkMode ? 'bg-slate-700 hover:bg-slate-600' : 'bg-gray-100 hover:bg-gray-200'} transition-colors`}> {darkMode ? <Sun size={20} className="text-yellow-400" /> : <Moon size={20} className="text-slate-700" />} </button>
                 <button onClick={cargarDatosResumenYRecomendaciones} className={`p-2 rounded-lg ${darkMode ? 'bg-slate-700 hover:bg-slate-600' : 'bg-gray-100 hover:bg-gray-200'} transition-colors`} title="Refrescar Dashboard"> <RefreshCw size={20} className={darkMode ? "text-purple-400" : "text-purple-600"}/> </button>
                 <div className="relative"> <button onClick={() => setShowNotifications(!showNotifications)} className={`p-2 rounded-lg ${darkMode ? 'bg-slate-700 hover:bg-slate-600' : 'bg-gray-100 hover:bg-gray-200'} transition-colors relative`}> <Bell size={20} className={darkMode ? "text-purple-400" : "text-purple-600"}/> <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full border border-white dark:border-slate-800"></span> </button> {showNotifications && ( <div className={`absolute right-0 mt-2 w-80 ${darkMode ? 'bg-slate-800 border-purple-500/20' : 'bg-white border-gray-200'} rounded-lg shadow-xl border overflow-hidden`}> {/* ... Notificaciones ... */} </div> )} </div>
                 {tienePermiso('admin') && ( <button className={`p-2 rounded-lg ${darkMode ? 'bg-slate-700 hover:bg-slate-600' : 'bg-gray-100 hover:bg-gray-200'} transition-colors`} title="Configuración"> <Settings size={20} className={darkMode ? "text-purple-400" : "text-purple-600"}/> </button> )}
              </div>
            </div>
          </div>
        </header>

        {/* Main: Contenido Dinámico */}
        <main className="p-6">
          {/* Contenedor base */}
          <div className="space-y-6">

            {/* --- Sección Dashboard Principal (SOLO OVERVIEW) --- */}
            {activeSection === 'dashboard' && tienePermiso('dashboard') && (
              <>
                <div className="flex items-center justify-between flex-wrap gap-4">
                  <div> <h2 className={`text-3xl font-bold ${darkMode ? 'text-white' : 'text-slate-800'}`}>Dashboard Principal</h2> <p className={`${darkMode ? 'text-purple-400' : 'text-purple-600'} mt-1`}>Visión general del sistema SEIRA 2.0</p> </div>
                  <div className="flex gap-2">
                     <button onClick={() => exportarDatos('PDF')} className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg flex items-center gap-2 transition-colors"> <Download size={18} /> PDF </button>
                     <button onClick={() => exportarDatos('Excel')} className={`px-4 py-2 ${darkMode ? 'bg-slate-700 hover:bg-slate-600' : 'bg-gray-200 hover:bg-gray-300'} ${darkMode ? 'text-white' : 'text-slate-700'} rounded-lg flex items-center gap-2 transition-colors`}> <Download size={18} /> Excel </button>
                  </div>
                </div>

                {/* KPIs */}
                {resumen && (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {/* Tarjeta Total Tickets */}
                    <div className={`bg-gradient-to-br ${darkMode ? 'from-slate-800/80 to-slate-800/40 border-purple-500/20 hover:border-purple-500/40' : 'from-white to-gray-50 border-gray-200 hover:border-purple-300'} backdrop-blur-sm border rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-300`}> <div className="flex items-center justify-between mb-3"><span className={`${darkMode ? 'text-purple-300' : 'text-gray-500'} text-sm font-medium`}>Total Tickets</span><div className={`p-2 ${darkMode ? 'bg-purple-500/20' : 'bg-purple-100'} rounded-lg`}> <AlertCircle className={`${darkMode ? 'text-purple-400' : 'text-purple-600'}`} size={20} /> </div></div> <p className={`text-3xl font-bold ${darkMode ? 'text-white' : 'text-slate-800'} mb-1`}>{resumen.total_tickets.toLocaleString()}</p> <p className={`${darkMode ? 'text-purple-200' : 'text-gray-500'} text-sm`}>{resumen.total_categorias} categorías</p> <div className={`mt-3 flex items-center gap-1 ${darkMode ? 'text-green-400' : 'text-green-600'} text-xs`}> <TrendingUp size={14} /> <span>+12% vs mes anterior</span> </div> </div>
                    {/* Tarjeta Ahorro Anual */}
                    <div className={`bg-gradient-to-br ${darkMode ? 'from-green-900/20 to-slate-800/40 border-green-500/20 hover:border-green-500/40' : 'from-green-50 to-gray-50 border-green-200 hover:border-green-400'} backdrop-blur-sm border rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-300`}> <div className="flex items-center justify-between mb-3"><span className={`${darkMode ? 'text-green-300' : 'text-green-700'} text-sm font-medium`}>Ahorro Anual</span><div className={`p-2 ${darkMode ? 'bg-green-500/20' : 'bg-green-100'} rounded-lg`}> <DollarSign className={`${darkMode ? 'text-green-400' : 'text-green-600'}`} size={20} /> </div></div> <p className={`text-3xl font-bold ${darkMode ? 'text-white' : 'text-slate-800'} mb-1`}>{formatearMoneda(resumen.ahorro_total_anual)}</p> <p className={`${darkMode ? 'text-green-200' : 'text-green-600'} text-sm`}>ROI: {formatearPorcentaje(resumen.roi_promedio_porcentaje)}</p> <div className={`mt-3 flex items-center gap-1 ${darkMode ? 'text-green-400' : 'text-green-600'} text-xs`}> <TrendingUp size={14} /> <span>Excelente rendimiento</span> </div> </div>
                    {/* Tarjeta IAR Promedio */}
                    <div className={`bg-gradient-to-br ${darkMode ? 'from-blue-900/20 to-slate-800/40 border-blue-500/20 hover:border-blue-500/40' : 'from-blue-50 to-gray-50 border-blue-200 hover:border-blue-400'} backdrop-blur-sm border rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-300`}> <div className="flex items-center justify-between mb-3"><span className={`${darkMode ? 'text-blue-300' : 'text-blue-700'} text-sm font-medium`}>IAR Promedio</span><div className={`p-2 ${darkMode ? 'bg-blue-500/20' : 'bg-blue-100'} rounded-lg`}> <Target className={`${darkMode ? 'text-blue-400' : 'text-blue-600'}`} size={20} /> </div></div> <p className={`text-3xl font-bold ${darkMode ? 'text-white' : 'text-slate-800'} mb-1`}>{resumen.promedio_iar.toFixed(1)}</p> <p className={`${darkMode ? 'text-blue-200' : 'text-blue-600'} text-sm mb-3`}>Índice de Automatización</p> <div className={`w-full ${darkMode ? 'bg-slate-700' : 'bg-gray-200'} rounded-full h-1.5`}> <div className="bg-gradient-to-r from-blue-500 to-purple-500 h-1.5 rounded-full" style={{ width: `${resumen.promedio_iar}%` }}></div> </div> </div>
                    {/* Tarjeta Prioritarias */}
                    <div className={`bg-gradient-to-br ${darkMode ? 'from-yellow-900/20 to-slate-800/40 border-yellow-500/20 hover:border-yellow-500/40' : 'from-yellow-50 to-gray-50 border-yellow-200 hover:border-yellow-400'} backdrop-blur-sm border rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-300`}> <div className="flex items-center justify-between mb-3"><span className={`${darkMode ? 'text-yellow-300' : 'text-yellow-700'} text-sm font-medium`}>Prioritarias</span><div className={`p-2 ${darkMode ? 'bg-yellow-500/20' : 'bg-yellow-100'} rounded-lg`}> <TrendingUp className={`${darkMode ? 'text-yellow-400' : 'text-yellow-600'}`} size={20} /> </div></div> <p className={`text-3xl font-bold ${darkMode ? 'text-white' : 'text-slate-800'} mb-1`}>{resumen.categorias_altamente_recomendadas}</p> <p className={`${darkMode ? 'text-yellow-200' : 'text-yellow-600'} text-sm`}>Altamente Recomendadas</p> <div className={`mt-3 flex items-center gap-1 ${darkMode ? 'text-yellow-400' : 'text-yellow-600'} text-xs`}> <AlertCircle size={14} /> <span>Requieren atención</span> </div> </div>
                  </div>
                )}

                {/* Gráficos */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Gráfico IAR */}
                  <div className={`${darkMode ? 'bg-slate-800/50 border-purple-500/20' : 'bg-white border-gray-200'} backdrop-blur-sm border rounded-xl p-6 shadow-lg`}>
                    <h3 className={`text-xl font-semibold ${darkMode ? 'text-white' : 'text-slate-800'} mb-4`}>Top 10 Categorías por IAR</h3>
                    <ResponsiveContainer width="100%" height={350}> <BarChart data={dataGraficoIAR} layout="vertical" margin={{ left: 100 }}> <CartesianGrid strokeDasharray="3 3" stroke={darkMode ? "#4B5563" : "#E5E7EB"} /> <XAxis type="number" stroke={darkMode ? "#D8B4FE" : "#6B7280"} tick={{ fontSize: 12 }} /> <YAxis dataKey="categoria" type="category" stroke={darkMode ? "#D8B4FE" : "#6B7280"} width={90} tick={{ fontSize: 12 }} /> <Tooltip contentStyle={{ backgroundColor: darkMode ? '#1E293B' : '#FFFFFF', border: `1px solid ${COLORS.primary}`, borderRadius: '8px', color: darkMode ? '#FFF' : '#1E293B' }} cursor={{ fill: darkMode ? 'rgba(139, 92, 246, 0.1)' : 'rgba(139, 92, 246, 0.05)' }} /> <Bar dataKey="IAR" fill={COLORS.primary} radius={[0, 8, 8, 0]} /> </BarChart> </ResponsiveContainer>
                  </div>
                  {/* Gráfico Nivel */}
                  <div className={`${darkMode ? 'bg-slate-800/50 border-purple-500/20' : 'bg-white border-gray-200'} backdrop-blur-sm border rounded-xl p-6 shadow-lg`}>
                     <h3 className={`text-xl font-semibold ${darkMode ? 'text-white' : 'text-slate-800'} mb-4`}>Distribución por Nivel</h3>
                    <ResponsiveContainer width="100%" height={350}> <PieChart> <Pie data={dataNivelRecomendacion} cx="50%" cy="50%" labelLine={false} label={(e) => `${e.nombre}: ${e.valor}`} outerRadius={120} dataKey="valor" stroke={darkMode ? 'none' : '#E5E7EB'}> {dataNivelRecomendacion.map((entry, index) => <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />)} </Pie> <Tooltip contentStyle={{ backgroundColor: darkMode ? '#1E293B' : '#FFFFFF', border: `1px solid ${COLORS.secondary}`, borderRadius: '8px' }} itemStyle={{ color: darkMode ? '#FFF' : '#1E293B' }}/> </PieChart> </ResponsiveContainer>
                  </div>
                </div>
                 {/* Gráfico ROI */}
                <div className={`${darkMode ? 'bg-slate-800/50 border-purple-500/20' : 'bg-white border-gray-200'} backdrop-blur-sm border rounded-xl p-6 shadow-lg lg:col-span-2`}>
                   <h3 className={`text-xl font-semibold ${darkMode ? 'text-white' : 'text-slate-800'} mb-4`}>Ahorro Anual Estimado (Top 8 - Miles USD)</h3>
                  <ResponsiveContainer width="100%" height={350}> <AreaChart data={dataGraficoROI} margin={{ top: 10, right: 30, left: 0, bottom: 50 }}> <defs> <linearGradient id="colorAhorro" x1="0" y1="0" x2="0" y2="1"> <stop offset="5%" stopColor={COLORS.success} stopOpacity={0.8} /> <stop offset="95%" stopColor={COLORS.success} stopOpacity={0} /> </linearGradient> </defs> <CartesianGrid strokeDasharray="3 3" stroke={darkMode ? "#4B5563" : "#E5E7EB"} /> <XAxis dataKey="categoria" stroke={darkMode ? "#D8B4FE" : "#6B7280"} angle={-30} textAnchor="end" height={60} tick={{ fontSize: 11 }} interval={0}/> <YAxis stroke={darkMode ? "#D8B4FE" : "#6B7280"} tick={{ fontSize: 12 }} /> <Tooltip contentStyle={{ backgroundColor: darkMode ? '#1E293B' : '#FFFFFF', border: `1px solid ${COLORS.success}`, borderRadius: '8px' }} itemStyle={{ color: darkMode ? '#FFF' : '#1E293B' }} labelStyle={{ color: darkMode ? '#D8B4FE' : '#6B7280' }}/> <Area type="monotone" dataKey="ahorro" stroke={COLORS.success} fillOpacity={1} fill="url(#colorAhorro)" /> </AreaChart> </ResponsiveContainer>
                </div>
              </>
            )}

            {/* --- Renderizado de Secciones Externas --- */}
            {activeSection === 'analytics' && tienePermiso('analisis') && <AnalysisSection />}
            {activeSection === 'tickets' && tienePermiso('analisis') && <TicketsSection />} {/* Muestra Métricas */}
            {activeSection === 'reports' && tienePermiso('analisis') && <ReportsSection />} {/* Muestra Recomendaciones */}
            {activeSection === 'users' && tienePermiso('admin') && <UserManagement user={user} />}
            {activeSection === 'docs' && tienePermiso('dashboard') && (
              <div className="space-y-6"> {/* Sección Documentación */}
                <div> <h2 className={`text-3xl font-bold ${darkMode ? 'text-white' : 'text-slate-800'}`}>Documentación</h2> <p className={`${darkMode ? 'text-purple-400' : 'text-purple-600'} mt-1`}>Acceso a documentos clave.</p> </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <a href="/docs/Checklist.html" target="_blank" rel="noopener noreferrer" className={`${darkMode ? 'bg-slate-800/50 border-purple-500/20 hover:border-purple-500/50' : 'bg-white border-gray-200 hover:border-purple-300'} backdrop-blur-sm border rounded-xl p-6 shadow-lg hover:shadow-xl transition-all hover:scale-105`}> <FileText className={`${darkMode ? 'text-purple-400' : 'text-purple-600'} mb-4`} size={40} /> <h3 className={`text-xl font-semibold ${darkMode ? 'text-white' : 'text-slate-800'} mb-2`}>Checklist</h3> <p className={`${darkMode ? 'text-purple-200' : 'text-gray-500'} text-sm`}>Lista de verificación</p> </a>
                  <a href="/docs/Gannt.html" target="_blank" rel="noopener noreferrer" className={`${darkMode ? 'bg-slate-800/50 border-purple-500/20 hover:border-purple-500/50' : 'bg-white border-gray-200 hover:border-purple-300'} backdrop-blur-sm border rounded-xl p-6 shadow-lg hover:shadow-xl transition-all hover:scale-105`}> <BarChart2 className={`${darkMode ? 'text-purple-400' : 'text-purple-600'} mb-4`} size={40} /> <h3 className={`text-xl font-semibold ${darkMode ? 'text-white' : 'text-slate-800'} mb-2`}>Diagrama Gantt</h3> <p className={`${darkMode ? 'text-purple-200' : 'text-gray-500'} text-sm`}>Cronograma</p> </a>
                  <a href="/docs/Matriz.html" target="_blank" rel="noopener noreferrer" className={`${darkMode ? 'bg-slate-800/50 border-purple-500/20 hover:border-purple-500/50' : 'bg-white border-gray-200 hover:border-purple-300'} backdrop-blur-sm border rounded-xl p-6 shadow-lg hover:shadow-xl transition-all hover:scale-105`}> <Database className={`${darkMode ? 'text-purple-400' : 'text-purple-600'} mb-4`} size={40} /> <h3 className={`text-xl font-semibold ${darkMode ? 'text-white' : 'text-slate-800'} mb-2`}>Matriz</h3> <p className={`${darkMode ? 'text-purple-200' : 'text-gray-500'} text-sm`}>Matriz de análisis</p> </a>
                </div>
              </div>
            )}

            {/* Placeholder Secciones Desconocidas */}
            { !menuItems.find(item => item.section === activeSection) && (
              <div className="text-center py-20"> <div className={`inline-block p-6 ${darkMode ? 'bg-slate-800' : 'bg-white'} rounded-xl shadow-xl`}> <HelpCircle className={`${darkMode ? 'text-purple-400' : 'text-purple-600'} mx-auto mb-4`} size={60} /> <h3 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-slate-800'} mb-2`}>Sección Desconocida</h3> <p className={`${darkMode ? 'text-purple-200' : 'text-gray-500'}`}>Esta sección no está definida.</p> </div> </div>
            )}

          </div> {/* Cierre del div.space-y-6 base */}
        </main>

        {/* Footer */}
        <footer className={`mt-12 py-6 border-t ${darkMode ? 'border-purple-500/20 bg-slate-800/50' : 'border-gray-200 bg-gray-50'}`}>
          <div className="px-6 flex items-center justify-between">
            <p className={`text-sm ${darkMode ? 'text-purple-200' : 'text-gray-500'}`}> © 2025 SEIRA 2.0 | NEXO GAMER </p>
            <div className="flex items-center gap-4">
              <a href="#" className={`text-sm ${darkMode ? 'text-purple-400 hover:text-purple-300' : 'text-purple-600 hover:text-purple-800'}`}>Soporte</a>
              <button onClick={() => setActiveSection('docs')} className={`text-sm ${darkMode ? 'text-purple-400 hover:text-purple-300' : 'text-purple-600 hover:text-purple-800'}`}> Documentación </button>
              <a href="http://localhost:5000/api/docs" target="_blank" rel="noopener noreferrer" className={`text-sm ${darkMode ? 'text-purple-400 hover:text-purple-300' : 'text-purple-600 hover:text-purple-800'}`}> API (Swagger) </a>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}