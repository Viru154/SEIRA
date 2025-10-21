import { useState } from 'react';
import { Shield, User, Lock, LogIn, AlertCircle } from 'lucide-react';

const API_BASE = 'http://localhost:5000/api';

export default function LoginPage({ onLoginSuccess }) {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    console.log('🔐 Intentando login con:', formData.username);

    try {
      const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        credentials: 'include', // ← CRÍTICO para Flask-Login
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      console.log('📡 Status code:', response.status);

      // Leer la respuesta como texto primero para debug
      const textResponse = await response.text();
      console.log('📄 Respuesta raw:', textResponse);

      let data;
      try {
        data = JSON.parse(textResponse);
      } catch (parseError) {
        console.error('❌ Error parseando JSON:', parseError);
        throw new Error('Respuesta inválida del servidor');
      }

      console.log('✅ Datos parseados:', data);

      if (!response.ok) {
        throw new Error(data.error || 'Error en el login');
      }

      // ✅ CORREGIDO: Verificar que exista data.user con datos válidos
      if (data && data.user && data.user.username) {
        console.log('✅ Login exitoso:', data.user);
        // Asegurarse de pasar el objeto completo
        onLoginSuccess({
          id: data.user.id,
          username: data.user.username,
          email: data.user.email,
          rol: data.user.rol,
          activo: data.user.activo,
          nombre_completo: data.user.nombre_completo || data.user.username
        });
      } else {
        console.error('❌ Estructura de datos inesperada:', data);
        throw new Error('Respuesta inesperada del servidor');
      }

    } catch (error) {
      console.error('❌ Error completo:', error);
      setError(error.message || 'Error de conexión con el servidor');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        {/* Logo/Header */}
        <div className="text-center mb-8">
          <div className="inline-block p-4 bg-purple-600 rounded-2xl mb-4">
            <Shield size={48} className="text-white" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-2">SEIRA 2.0</h1>
          <p className="text-purple-300">Sistema de Evaluación Inteligente</p>
          <p className="text-purple-400 text-sm mt-1">NEXO GAMER</p>
        </div>

        {/* Login Form */}
        <div className="bg-slate-800/80 backdrop-blur-xl border border-purple-500/30 rounded-2xl shadow-2xl p-8">
          <h2 className="text-2xl font-bold text-white mb-6 text-center">Iniciar Sesión</h2>

          {error && (
            <div className="mb-6 p-4 bg-red-500/20 border border-red-500/50 rounded-lg flex items-start gap-3">
              <AlertCircle className="text-red-400 flex-shrink-0 mt-0.5" size={20} />
              <div>
                <p className="text-red-200 font-medium">Error</p>
                <p className="text-red-300 text-sm">{error}</p>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-purple-200 text-sm font-medium mb-2">
                Usuario o Email
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 text-purple-400" size={20} />
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  className="w-full pl-11 pr-4 py-3 bg-slate-700 text-white border border-purple-500/30 rounded-lg focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 transition-colors"
                  placeholder="admin"
                  required
                  autoFocus
                />
              </div>
            </div>

            <div>
              <label className="block text-purple-200 text-sm font-medium mb-2">
                Contraseña
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-purple-400" size={20} />
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full pl-11 pr-4 py-3 bg-slate-700 text-white border border-purple-500/30 rounded-lg focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 transition-colors"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                  <span>Iniciando sesión...</span>
                </>
              ) : (
                <>
                  <LogIn size={20} />
                  <span>Iniciar Sesión</span>
                </>
              )}
            </button>
          </form>

          <div className="mt-6 pt-6 border-t border-purple-500/20">
            <p className="text-purple-300 text-sm text-center">
              Credenciales de prueba:
            </p>
            <div className="mt-2 space-y-1 text-xs text-purple-400 text-center">
              <p><span className="font-mono bg-slate-700 px-2 py-1 rounded">admin</span> / <span className="font-mono bg-slate-700 px-2 py-1 rounded">Admin123</span></p>
            </div>
          </div>
        </div>

        <div className="mt-6 text-center">
          <p className="text-purple-400 text-sm">
            © 2025 SEIRA 2.0 - NEXO GAMER
          </p>
        </div>
      </div>
    </div>
  );
}