import { useState, useEffect } from 'react';
import UserManagement from './UserManagement';
import TicketsSection from './TicketsSection';
import AnalysisSection from './AnalysisSection';
import { BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { 
  TrendingUp, DollarSign, Target, AlertCircle, Filter, Download, 
  Menu, X, Search, Bell, Settings, LogOut, Home, FileText,
  BarChart2, Database, ChevronRight, Moon, Sun, RefreshCw, 
  Shield, HelpCircle
} from 'lucide-react';

const API_BASE = 'http://localhost:5000/api';

const COLORS = {
  primary: '#8B5CF6',
  secondary: '#C084FC',
  success: '#10B981',
  warning: '#F59E0B',
  danger: '#EF4444',
  info: '#3B82F6'
};

const CHART_COLORS = ['#8B5CF6', '#C084FC', '#A78BFA', '#DDD6FE', '#EDE9FE'];

export default function AdminDashboard({ user, onLogout }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeSection, setActiveSection] = useState('dashboard');
  const [activeTab, setActiveTab] = useState('overview');
  const [darkMode, setDarkMode] = useState(true);
  const [resumen, setResumen] = useState(null);
  const [recomendaciones, setRecomendaciones] = useState([]);
  const [metricas, setMetricas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [accessDenied, setAccessDenied] = useState(false);
  const [filters, setFilters] = useState({
    minIAR: 0,
    nivelRecomendacion: 'TODOS'
  });

  useEffect(() => {
    if (!user) {
      onLogout();
      return;
    }
    
    if (user.rol === 'cliente') {
      setAccessDenied(true);
      setLoading(false);
      return;
    }

    cargarDatos();
  }, [user]);

  const cargarDatos = async () => {
    setLoading(true);
    try {
      const [resumenRes, recRes, metricasRes] = await Promise.all([
        fetch(`${API_BASE}/dashboard/resumen`, { credentials: 'include' }),
        fetch(`${API_BASE}/recomendaciones`, { credentials: 'include' }),
        fetch(`${API_BASE}/metricas`, { credentials: 'include' })
      ]);

      if (resumenRes.status === 401 || recRes.status === 401 || metricasRes.status === 401) {
        alert('Sesión expirada. Por favor, inicia sesión nuevamente.');
        onLogout();
        return;
      }

      if (!resumenRes.ok || !recRes.ok || !metricasRes.ok) {
        throw new Error('Error al cargar datos del dashboard');
      }

      const resumenData = await resumenRes.json();
      const recData = await recRes.json();
      const metricasData = await metricasRes.json();

      setResumen(resumenData);
      setRecomendaciones(recData);
      setMetricas(metricasData);
    } catch (error) {
      console.error('Error cargando datos:', error);
      alert(`Error al cargar datos: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    if (confirm('¿Estás seguro que deseas cerrar sesión?')) {
      onLogout();
    }
  };

  const tienePermiso = (permiso) => {
    const rol = user?.rol;
    if (permiso === 'admin') return rol === 'admin';
    if (permiso === 'analisis') return ['admin', 'analista'].includes(rol);
    if (permiso === 'tickets') return ['admin', 'operador'].includes(rol);
    if (permiso === 'dashboard') return ['admin', 'analista', 'operador'].includes(rol);
    return false;
  };

  const formatearMoneda = (valor) => {
    return new Intl.NumberFormat('es-GT', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0
    }).format(valor);
  };

  const formatearPorcentaje = (valor) => {
    return `${valor.toFixed(1)}%`;
  };

  const exportarDatos = (formato) => {
    alert(`Función de exportar ${formato} en desarrollo`);
  };

  if (accessDenied) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-6">
        <div className="text-center">
          <div className="inline-block p-8 bg-slate-800/80 backdrop-blur-xl border border-red-500/30 rounded-2xl shadow-2xl">
            <Shield className="text-red-400 mx-auto mb-4" size={80} />
            <h1 className="text-3xl font-bold text-white mb-2">Acceso Denegado</h1>
            <p className="text-purple-200 mb-6">
              Esta sección es solo para administradores y personal autorizado.
            </p>
            <div className="space-y-3 mb-6">
              <p className="text-purple-300 text-sm">
                Usuario: <span className="font-semibold">{user?.username}</span>
              </p>
              <p className="text-purple-300 text-sm">
                Rol: <span className="font-semibold capitalize">{user?.rol}</span>
              </p>
            </div>
            <button
              onClick={handleLogout}
              className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg flex items-center gap-2 mx-auto transition-colors"
            >
              <LogOut size={20} />
              Cerrar Sesión
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-20 w-20 border-4 border-purple-500 border-t-transparent mx-auto mb-4"></div>
          <p className="text-purple-200 text-xl font-semibold">Cargando SEIRA 2.0...</p>
          <p className="text-purple-400 text-sm mt-2">Bienvenido, {user?.username}</p>
        </div>
      </div>
    );
  }

  const recomendacionesFiltradas = recomendaciones.filter(r => {
    if (r.iar_score < filters.minIAR) return false;
    if (filters.nivelRecomendacion !== 'TODOS' && r.nivel_recomendacion !== filters.nivelRecomendacion) return false;
    return true;
  });

  const dataGraficoIAR = recomendacionesFiltradas
    .sort((a, b) => b.iar_score - a.iar_score)
    .slice(0, 10)
    .map(r => ({
      categoria: r.categoria.replace(/_/g, ' ').substring(0, 20),
      IAR: r.iar_score
    }));

  const dataGraficoROI = recomendacionesFiltradas
    .sort((a, b) => b.roi_anual_estimado - a.roi_anual_estimado)
    .slice(0, 8)
    .map(r => ({
      categoria: r.categoria.replace(/_/g, ' ').substring(0, 15),
      ahorro: r.roi_anual_estimado / 1000
    }));

  const dataNivelRecomendacion = [
    {
      nombre: 'Altamente Recomendado',
      valor: recomendaciones.filter(r => r.nivel_recomendacion === 'ALTAMENTE_RECOMENDADO').length
    },
    {
      nombre: 'Evaluar',
      valor: recomendaciones.filter(r => r.nivel_recomendacion === 'EVALUAR').length
    },
    {
      nombre: 'No Recomendado',
      valor: recomendaciones.filter(r => r.nivel_recomendacion === 'NO_RECOMENDADO').length
    }
  ];

  const menuItems = [
    { id: 'dashboard', icon: Home, label: 'Dashboard', section: 'dashboard', permiso: 'dashboard' },
    { id: 'analytics', icon: BarChart2, label: 'Análisis', section: 'analytics', permiso: 'analisis' },
    { id: 'tickets', icon: Database, label: 'Tickets', section: 'tickets', permiso: 'tickets' },
    { id: 'reports', icon: FileText, label: 'Reportes', section: 'reports', permiso: 'analisis' },
    { id: 'users', icon: Shield, label: 'Usuarios', section: 'users', permiso: 'admin' },
    { id: 'docs', icon: FileText, label: 'Documentación', section: 'docs', permiso: 'dashboard' }
  ];

  const notifications = [
    { id: 1, text: '2 nuevas categorías ALTAMENTE_RECOMENDADO', time: 'Hace 5 min' },
    { id: 2, text: 'ROI mensual supera expectativas', time: 'Hace 1 hora' },
    { id: 3, text: 'Actualización de datos completada', time: 'Hace 2 horas' }
  ];

  return (
    <div className={`min-h-screen ${darkMode ? 'bg-slate-900' : 'bg-gray-100'} transition-colors duration-300`}>
      {/* Sidebar */}
      <aside className={`fixed top-0 left-0 h-full ${darkMode ? 'bg-slate-800' : 'bg-white'} border-r ${darkMode ? 'border-purple-500/20' : 'border-gray-200'} transition-all duration-300 z-50 ${sidebarOpen ? 'w-64' : 'w-20'}`}>
        <div className="flex flex-col h-full">
          <div className="p-6 border-b border-purple-500/20">
            <div className="flex items-center justify-between">
              {sidebarOpen && (
                <div>
                  <h1 className="text-2xl font-bold text-purple-400">SEIRA 2.0</h1>
                  <p className="text-xs text-purple-300">Admin Panel</p>
                </div>
              )}
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className={`p-2 rounded-lg hover:bg-slate-700 transition-colors ${!sidebarOpen && 'mx-auto'}`}
              >
                {sidebarOpen ? <X className="text-purple-400" size={20} /> : <Menu className="text-purple-400" size={20} />}
              </button>
            </div>
          </div>

          <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
            {menuItems
              .filter(item => tienePermiso(item.permiso))
              .map(item => {
                const Icon = item.icon;
                const isActive = activeSection === item.section;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveSection(item.section)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                      isActive
                        ? 'bg-purple-600 text-white shadow-lg'
                        : 'text-purple-200 hover:bg-slate-700'
                    }`}
                  >
                    <Icon size={20} />
                    {sidebarOpen && <span className="font-medium">{item.label}</span>}
                  </button>
                );
              })}
          </nav>

          <div className="p-4 border-t border-purple-500/20">
            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="w-full flex items-center gap-3 p-3 rounded-lg bg-slate-700 hover:bg-slate-600 transition-colors"
              >
                <div className="w-10 h-10 rounded-full bg-purple-600 flex items-center justify-center text-white font-bold">
                  {user?.username?.charAt(0).toUpperCase()}
                </div>
                {sidebarOpen && (
                  <div className="flex-1 text-left">
                    <p className="font-semibold text-sm text-white truncate">
                      {user?.username}
                    </p>
                    <p className="text-xs text-purple-400 capitalize">{user?.rol}</p>
                  </div>
                )}
              </button>

              {showUserMenu && sidebarOpen && (
                <div className="absolute bottom-full left-0 w-full mb-2 bg-slate-700 rounded-lg shadow-xl border border-purple-500/20 overflow-hidden">
                  <div className="p-3 border-b border-purple-500/20">
                    <p className="text-sm font-semibold text-white">
                      {user?.nombre_completo || user?.username}
                    </p>
                    <p className="text-xs text-purple-400">{user?.email}</p>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center gap-2 px-4 py-3 hover:bg-slate-600 text-red-300 transition-colors"
                  >
                    <LogOut size={18} />
                    <span className="text-sm font-medium">Cerrar Sesión</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className={`transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-20'}`}>
        <header className="sticky top-0 z-40 bg-slate-800/95 backdrop-blur-sm border-b border-purple-500/20 shadow-lg">
          <div className="px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm">
                <Home size={16} className="text-purple-400" />
                <ChevronRight size={16} className="text-purple-400" />
                <span className="text-purple-200">
                  {activeSection === 'dashboard' && 'Dashboard Principal'}
                  {activeSection === 'analytics' && 'Análisis Avanzado'}
                  {activeSection === 'tickets' && 'Gestión de Tickets'}
                  {activeSection === 'reports' && 'Reportes'}
                  {activeSection === 'users' && 'Gestión de Usuarios'}
                  {activeSection === 'docs' && 'Documentación'}
                </span>
              </div>

              <div className="flex items-center gap-4">
                <div className="relative hidden md:block">
                  <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-purple-400" />
                  <input
                    type="text"
                    placeholder="Buscar..."
                    className="pl-10 pr-4 py-2 rounded-lg bg-slate-700 text-white border border-purple-500/30 focus:outline-none focus:border-purple-500 w-64"
                  />
                </div>

                <button
                  onClick={() => setDarkMode(!darkMode)}
                  className="p-2 rounded-lg bg-slate-700 hover:bg-slate-600 transition-colors"
                >
                  {darkMode ? <Sun className="text-yellow-400" size={20} /> : <Moon className="text-slate-700" size={20} />}
                </button>

                <button
                  onClick={cargarDatos}
                  className="p-2 rounded-lg bg-slate-700 hover:bg-slate-600 transition-colors"
                  title="Refrescar datos"
                >
                  <RefreshCw className="text-purple-400" size={20} />
                </button>

                <div className="relative">
                  <button
                    onClick={() => setShowNotifications(!showNotifications)}
                    className="p-2 rounded-lg bg-slate-700 hover:bg-slate-600 transition-colors relative"
                  >
                    <Bell className="text-purple-400" size={20} />
                    <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
                  </button>

                  {showNotifications && (
                    <div className="absolute right-0 mt-2 w-80 bg-slate-800 rounded-lg shadow-xl border border-purple-500/20 overflow-hidden">
                      <div className="p-4 border-b border-purple-500/20">
                        <h3 className="font-semibold text-white">Notificaciones</h3>
                      </div>
                      <div className="max-h-96 overflow-y-auto">
                        {notifications.map(notif => (
                          <div key={notif.id} className="p-4 border-b border-slate-700 hover:bg-slate-700 transition-colors cursor-pointer">
                            <p className="text-sm text-white">{notif.text}</p>
                            <p className="text-xs text-purple-400 mt-1">{notif.time}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {tienePermiso('admin') && (
                  <button className="p-2 rounded-lg bg-slate-700 hover:bg-slate-600 transition-colors" title="Configuración">
                    <Settings className="text-purple-400" size={20} />
                  </button>
                )}
              </div>
            </div>
          </div>
        </header>

        <main className="p-6">
          {activeSection === 'dashboard' && tienePermiso('dashboard') && (
            <div className="space-y-6">
              <div className="flex items-center justify-between flex-wrap gap-4">
                <div>
                  <h2 className="text-3xl font-bold text-white">Dashboard Principal</h2>
                  <p className="text-purple-400 mt-1">Sistema de Evaluación Inteligente - NEXO GAMER</p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => exportarDatos('PDF')}
                    className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg flex items-center gap-2 transition-colors"
                  >
                    <Download size={18} />
                    Exportar PDF
                  </button>
                  <button
                    onClick={() => exportarDatos('Excel')}
                    className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg flex items-center gap-2 transition-colors"
                  >
                    <Download size={18} />
                    Excel
                  </button>
                </div>
              </div>

              {resumen && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <div className="bg-gradient-to-br from-slate-800/80 to-slate-800/40 backdrop-blur-sm border border-purple-500/20 rounded-xl p-6 shadow-xl hover:shadow-2xl hover:border-purple-500/40 transition-all duration-300">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-purple-300 text-sm font-medium">Total Tickets</span>
                      <div className="p-2 bg-purple-500/20 rounded-lg">
                        <AlertCircle className="text-purple-400" size={24} />
                      </div>
                    </div>
                    <p className="text-4xl font-bold text-white mb-2">{resumen.total_tickets.toLocaleString()}</p>
                    <p className="text-purple-200 text-sm">{resumen.total_categorias} categorías activas</p>
                    <div className="mt-4 flex items-center gap-2 text-green-400 text-sm">
                      <TrendingUp size={16} />
                      <span>+12% vs mes anterior</span>
                    </div>
                  </div>

                  <div className="bg-gradient-to-br from-green-900/20 to-slate-800/40 backdrop-blur-sm border border-green-500/20 rounded-xl p-6 shadow-xl hover:shadow-2xl hover:border-green-500/40 transition-all duration-300">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-green-300 text-sm font-medium">Ahorro Anual</span>
                      <div className="p-2 bg-green-500/20 rounded-lg">
                        <DollarSign className="text-green-400" size={24} />
                      </div>
                    </div>
                    <p className="text-4xl font-bold text-white mb-2">{formatearMoneda(resumen.ahorro_total_anual)}</p>
                    <p className="text-green-200 text-sm">ROI: {formatearPorcentaje(resumen.roi_promedio_porcentaje)}</p>
                    <div className="mt-4 flex items-center gap-2 text-green-400 text-sm">
                      <TrendingUp size={16} />
                      <span>Excelente rendimiento</span>
                    </div>
                  </div>

                  <div className="bg-gradient-to-br from-blue-900/20 to-slate-800/40 backdrop-blur-sm border border-blue-500/20 rounded-xl p-6 shadow-xl hover:shadow-2xl hover:border-blue-500/40 transition-all duration-300">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-blue-300 text-sm font-medium">IAR Promedio</span>
                      <div className="p-2 bg-blue-500/20 rounded-lg">
                        <Target className="text-blue-400" size={24} />
                      </div>
                    </div>
                    <p className="text-4xl font-bold text-white mb-2">{resumen.promedio_iar.toFixed(1)}</p>
                    <p className="text-blue-200 text-sm mb-3">Índice de Automatización</p>
                    <div className="w-full bg-slate-700 rounded-full h-2.5">
                      <div className="bg-gradient-to-r from-blue-500 to-purple-500 h-2.5 rounded-full transition-all duration-500" style={{ width: `${resumen.promedio_iar}%` }}></div>
                    </div>
                  </div>

                  <div className="bg-gradient-to-br from-yellow-900/20 to-slate-800/40 backdrop-blur-sm border border-yellow-500/20 rounded-xl p-6 shadow-xl hover:shadow-2xl hover:border-yellow-500/40 transition-all duration-300">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-yellow-300 text-sm font-medium">Prioritarias</span>
                      <div className="p-2 bg-yellow-500/20 rounded-lg">
                        <TrendingUp className="text-yellow-400" size={24} />
                      </div>
                    </div>
                    <p className="text-4xl font-bold text-white mb-2">{resumen.categorias_altamente_recomendadas}</p>
                    <p className="text-yellow-200 text-sm">Altamente Recomendadas</p>
                    <div className="mt-4 flex items-center gap-2 text-yellow-400 text-sm">
                      <AlertCircle size={16} />
                      <span>Requieren atención</span>
                    </div>
                  </div>
                </div>
              )}

              <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl p-2 border border-purple-500/20 shadow-lg">
                <div className="flex gap-2 overflow-x-auto">
                  {['overview', 'recomendaciones'].map(tab => (
                    <button
                      key={tab}
                      onClick={() => setActiveTab(tab)}
                      className={`px-6 py-3 rounded-lg font-medium transition-all whitespace-nowrap ${
                        activeTab === tab
                          ? 'bg-gradient-to-r from-purple-600 to-purple-700 text-white shadow-lg shadow-purple-500/50 scale-105'
                          : 'text-purple-200 hover:bg-slate-700 hover:text-white'
                      }`}
                    >
                      {tab === 'overview' && '📊 Overview'}
                      {tab === 'recomendaciones' && '🎯 Recomendaciones'}
                    </button>
                  ))}
                </div>
              </div>

              {activeTab === 'overview' && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="bg-slate-800/50 backdrop-blur-sm border border-purple-500/20 rounded-xl p-6 shadow-xl">
                    <h3 className="text-xl font-bold text-white mb-4">Top 10 Categorías por IAR</h3>
                    <ResponsiveContainer width="100%" height={350}>
                      <BarChart data={dataGraficoIAR} layout="vertical" margin={{ left: 100 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#4B5563" />
                        <XAxis type="number" stroke="#D8B4FE" />
                        <YAxis dataKey="categoria" type="category" stroke="#D8B4FE" width={90} style={{ fontSize: '12px' }} />
                        <Tooltip contentStyle={{ backgroundColor: '#1E293B', border: '1px solid #8B5CF6', borderRadius: '8px', color: '#FFF' }} />
                        <Bar dataKey="IAR" fill={COLORS.primary} radius={[0, 8, 8, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>

                  <div className="bg-slate-800/50 backdrop-blur-sm border border-purple-500/20 rounded-xl p-6 shadow-xl">
                    <h3 className="text-xl font-bold text-white mb-4">Distribución por Nivel</h3>
                    <ResponsiveContainer width="100%" height={350}>
                      <PieChart>
                        <Pie
                          data={dataNivelRecomendacion}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={(entry) => `${entry.nombre}: ${entry.valor}`}
                          outerRadius={120}
                          fill="#8884d8"
                          dataKey="valor"
                        >
                          {dataNivelRecomendacion.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip contentStyle={{ backgroundColor: '#1E293B', borderRadius: '8px' }} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>

                  <div className="lg:col-span-2 bg-slate-800/50 backdrop-blur-sm border border-purple-500/20 rounded-xl p-6 shadow-xl">
                    <h3 className="text-xl font-bold text-white mb-4">Ahorro Anual por Categoría (Miles USD)</h3>
                    <ResponsiveContainer width="100%" height={350}>
                      <AreaChart data={dataGraficoROI}>
                        <defs>
                          <linearGradient id="colorAhorro" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor={COLORS.success} stopOpacity={0.8} />
                            <stop offset="95%" stopColor={COLORS.success} stopOpacity={0} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#4B5563" />
                        <XAxis dataKey="categoria" stroke="#D8B4FE" angle={-45} textAnchor="end" height={100} style={{ fontSize: '11px' }} />
                        <YAxis stroke="#D8B4FE" />
                        <Tooltip contentStyle={{ backgroundColor: '#1E293B', borderRadius: '8px' }} />
                        <Area type="monotone" dataKey="ahorro" stroke={COLORS.success} fillOpacity={1} fill="url(#colorAhorro)" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}

              {activeTab === 'recomendaciones' && (
                <div className="space-y-6">
                  <div className="bg-slate-800/50 backdrop-blur-sm border border-purple-500/20 rounded-xl p-6">
                    <div className="flex items-center gap-4 flex-wrap">
                      <Filter className="text-purple-400" size={20} />
                      <div className="flex-1 min-w-[200px]">
                        <label className="text-purple-200 text-sm block mb-2">IAR Mínimo: {filters.minIAR}</label>
                        <input
                          type="range"
                          min="0"
                          max="100"
                          value={filters.minIAR}
                          onChange={(e) => setFilters({ ...filters, minIAR: parseInt(e.target.value) })}
                          className="w-full accent-purple-500"
                        />
                      </div>
                      <div className="flex-1 min-w-[200px]">
                        <label className="text-purple-200 text-sm block mb-2">Nivel de Recomendación</label>
                        <select
                          value={filters.nivelRecomendacion}
                          onChange={(e) => setFilters({ ...filters, nivelRecomendacion: e.target.value })}
                          className="w-full bg-slate-700 text-white border border-purple-500/30 rounded-lg px-4 py-2"
                        >
                          <option value="TODOS">Todos</option>
                          <option value="ALTAMENTE_RECOMENDADO">Altamente Recomendado</option>
                          <option value="EVALUAR">Evaluar</option>
                          <option value="NO_RECOMENDADO">No Recomendado</option>
                        </select>
                      </div>
                    </div>
                  </div>

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
                          {recomendacionesFiltradas.map((rec) => (
                            <tr key={rec.id} className="hover:bg-purple-900/20 transition-colors">
                              <td className="px-6 py-4 text-white font-medium">
                                {rec.categoria.replace(/_/g, ' ')}
                              </td>
                              <td className="px-6 py-4 text-center">
                                <span className="px-3 py-1 bg-purple-600 text-white rounded-full text-sm font-bold">
                                  {rec.iar_score.toFixed(1)}
                                </span>
                              </td>
                              <td className="px-6 py-4 text-center">
                                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                                  rec.nivel_recomendacion === 'ALTAMENTE_RECOMENDADO'
                                    ? 'bg-green-500/20 text-green-300'
                                    : rec.nivel_recomendacion === 'EVALUAR'
                                    ? 'bg-yellow-500/20 text-yellow-300'
                                    : 'bg-red-500/20 text-red-300'
                                }`}>
                                  {rec.nivel_recomendacion.replace(/_/g, ' ')}
                                </span>
                              </td>
                              <td className="px-6 py-4 text-right text-purple-100">
                                {rec.total_tickets.toLocaleString()}
                              </td>
                              <td className="px-6 py-4 text-right text-green-300 font-semibold">
                                {formatearMoneda(rec.roi_anual_estimado)}
                              </td>
                              <td className="px-6 py-4 text-right text-blue-300 font-semibold">
                                {formatearPorcentaje(rec.roi_porcentaje)}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    <div className="px-6 py-4 bg-purple-900/30 border-t border-purple-500/20">
                      <p className="text-purple-200 text-sm">
                        Mostrando {recomendacionesFiltradas.length} de {recomendaciones.length} categorías
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeSection === 'analytics' && tienePermiso('analisis') && (
            <AnalysisSection />
          )}

          {activeSection === 'tickets' && tienePermiso('tickets') && (
            <TicketsSection />
          )}

          {activeSection === 'users' && tienePermiso('admin') && (
            <UserManagement user={user} />
          )}

          {activeSection === 'docs' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-3xl font-bold text-white">Documentación del Proyecto</h2>
                <p className="text-purple-400 mt-1">Acceso a documentos clave del sistema SEIRA 2.0</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <a 
                  href="/docs/Checklist.html" 
                  target="_blank"
                  rel="noopener noreferrer"
                  className="bg-slate-800/50 backdrop-blur-sm border border-purple-500/20 rounded-xl p-6 shadow-xl hover:shadow-2xl transition-all hover:scale-105 hover:border-purple-500/50"
                >
                  <FileText className="text-purple-400 mb-4" size={40} />
                  <h3 className="text-xl font-bold text-white mb-2">Checklist</h3>
                  <p className="text-purple-200 text-sm">Lista de verificación del proyecto</p>
                </a>

                <a 
                  href="/docs/Gannt.html" 
                  target="_blank"
                  rel="noopener noreferrer"
                  className="bg-slate-800/50 backdrop-blur-sm border border-purple-500/20 rounded-xl p-6 shadow-xl hover:shadow-2xl transition-all hover:scale-105 hover:border-purple-500/50"
                >
                  <BarChart2 className="text-purple-400 mb-4" size={40} />
                  <h3 className="text-xl font-bold text-white mb-2">Diagrama Gantt</h3>
                  <p className="text-purple-200 text-sm">Cronograma del proyecto</p>
                </a>

                <a 
                  href="/docs/Matriz.html" 
                  target="_blank"
                  rel="noopener noreferrer"
                  className="bg-slate-800/50 backdrop-blur-sm border border-purple-500/20 rounded-xl p-6 shadow-xl hover:shadow-2xl transition-all hover:scale-105 hover:border-purple-500/50"
                >
                  <Database className="text-purple-400 mb-4" size={40} />
                  <h3 className="text-xl font-bold text-white mb-2">Matriz</h3>
                  <p className="text-purple-200 text-sm">Matriz de análisis del proyecto</p>
                </a>
              </div>
            </div>
          )}

          {activeSection === 'reports' && (
            <div className="text-center py-20">
              <div className="inline-block p-6 bg-slate-800 rounded-xl shadow-xl">
                <HelpCircle className="text-purple-400 mx-auto mb-4" size={60} />
                <h3 className="text-2xl font-bold text-white mb-2">
                  Sección en Desarrollo
                </h3>
                <p className="text-purple-200">
                  Sistema de reportes en construcción
                </p>
              </div>
            </div>
          )}
        </main>

        <footer className="mt-12 py-6 border-t border-purple-500/20 bg-slate-800/50">
          <div className="px-6 flex items-center justify-between">
            <p className="text-sm text-purple-200">
              © 2025 SEIRA 2.0 - Sistema de Evaluación Inteligente | NEXO GAMER
            </p>
            <div className="flex items-center gap-4">
              <a href="#" className="text-sm text-purple-400 hover:text-purple-300">
                Soporte
              </a>
              <a href="#" className="text-sm text-purple-400 hover:text-purple-300">
                Documentación
              </a>
              <a href="http://localhost:5000/api/docs" target="_blank" rel="noopener noreferrer" className="text-sm text-purple-400 hover:text-purple-300">
                API
              </a>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}