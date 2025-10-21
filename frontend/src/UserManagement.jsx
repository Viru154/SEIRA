import { useState, useEffect } from 'react';
import { Users, UserPlus, Edit2, X, Check } from 'lucide-react';

const API_BASE = 'http://localhost:5000/api';

export default function UserManagement({ user }) {
  const [usuarios, setUsuarios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [modalMode, setModalMode] = useState('create');
  const [selectedUser, setSelectedUser] = useState(null);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    rol: 'operador'
  });
  const [filtroRol, setFiltroRol] = useState('TODOS');
  const [error, setError] = useState(null);

  useEffect(() => {
    cargarUsuarios();
  }, []);

  const cargarUsuarios = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const res = await fetch(`${API_BASE}/auth/admin/users`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (res.status === 401) {
        throw new Error('Sesión expirada. Por favor, inicia sesión nuevamente.');
      }

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.error || 'Error al cargar usuarios');
      }

      const data = await res.json();
      
      if (data.users && Array.isArray(data.users)) {
        setUsuarios(data.users);
      } else {
        console.error('Formato inesperado:', data);
        setUsuarios([]);
      }
    } catch (error) {
      console.error('Error cargando usuarios:', error);
      setError(error.message);
      setUsuarios([]);
    } finally {
      setLoading(false);
    }
  };

  const abrirModalCrear = () => {
    setModalMode('create');
    setFormData({
      username: '',
      email: '',
      password: '',
      rol: 'operador'
    });
    setShowModal(true);
  };

  const abrirModalEditar = (usuario) => {
    setModalMode('edit');
    setSelectedUser(usuario);
    setFormData({
      username: usuario.username,
      email: usuario.email,
      password: '',
      rol: usuario.rol
    });
    setShowModal(true);
  };

  const cerrarModal = () => {
    setShowModal(false);
    setSelectedUser(null);
    setFormData({ username: '', email: '', password: '', rol: 'operador' });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      if (modalMode === 'create') {
        const res = await fetch(`${API_BASE}/auth/admin/users`, {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(formData)
        });
        
        if (res.status === 401) {
          throw new Error('Sesión expirada');
        }

        const data = await res.json();
        
        if (res.ok) {
          alert('Usuario creado exitosamente');
          cargarUsuarios();
          cerrarModal();
        } else {
          throw new Error(data.error || 'No se pudo crear el usuario');
        }
      } else {
        const res = await fetch(`${API_BASE}/auth/admin/users/${selectedUser.id}`, {
          method: 'PUT',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ rol: formData.rol })
        });
        
        if (res.status === 401) {
          throw new Error('Sesión expirada');
        }

        if (res.ok) {
          alert('Usuario actualizado exitosamente');
          cargarUsuarios();
          cerrarModal();
        } else {
          const data = await res.json();
          throw new Error(data.error || 'Error al actualizar usuario');
        }
      }
    } catch (error) {
      console.error('Error en operación:', error);
      alert(`Error: ${error.message}`);
    }
  };

  const toggleActivarUsuario = async (usuario) => {
    try {
      const res = await fetch(`${API_BASE}/auth/admin/users/${usuario.id}`, {
        method: 'PUT',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ activo: !usuario.activo })
      });
      
      if (res.status === 401) {
        throw new Error('Sesión expirada');
      }

      if (res.ok) {
        alert(`Usuario ${!usuario.activo ? 'activado' : 'desactivado'} exitosamente`);
        cargarUsuarios();
      } else {
        const data = await res.json();
        throw new Error(data.error || 'Error al cambiar estado del usuario');
      }
    } catch (error) {
      console.error('Error:', error);
      alert(`Error: ${error.message}`);
    }
  };

  const usuariosFiltrados = usuarios.filter(u => {
    if (filtroRol === 'TODOS') return true;
    return u.rol === filtroRol;
  });

  const getRolColor = (rol) => {
    switch(rol) {
      case 'admin': return 'bg-purple-500/20 text-purple-300';
      case 'analista': return 'bg-blue-500/20 text-blue-300';
      case 'operador': return 'bg-green-500/20 text-green-300';
      case 'cliente': return 'bg-gray-500/20 text-gray-300';
      default: return 'bg-gray-500/20 text-gray-300';
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-4">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-purple-500 border-t-transparent"></div>
        <p className="text-purple-200">Cargando usuarios...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-4">
        <div className="p-6 bg-red-500/20 border border-red-500/50 rounded-xl">
          <p className="text-red-200 text-center">❌ {error}</p>
          <button
            onClick={cargarUsuarios}
            className="mt-4 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors mx-auto block"
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
            <Users size={32} className="text-purple-400" />
            Gestión de Usuarios
          </h2>
          <p className="text-purple-400 mt-1">Administra usuarios y permisos del sistema</p>
        </div>
        <button
          onClick={abrirModalCrear}
          className="px-4 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg flex items-center gap-2 transition-colors"
        >
          <UserPlus size={20} />
          Crear Usuario
        </button>
      </div>

      <div className="bg-slate-800/50 backdrop-blur-sm border border-purple-500/20 rounded-xl p-4">
        <div className="flex items-center gap-4 flex-wrap">
          <span className="text-purple-200 font-medium">Filtrar por rol:</span>
          <div className="flex gap-2 flex-wrap">
            {['TODOS', 'admin', 'analista', 'operador', 'cliente'].map(rol => (
              <button
                key={rol}
                onClick={() => setFiltroRol(rol)}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  filtroRol === rol
                    ? 'bg-purple-600 text-white'
                    : 'bg-slate-700 text-purple-200 hover:bg-slate-600'
                }`}
              >
                {rol === 'TODOS' ? 'Todos' : rol.charAt(0).toUpperCase() + rol.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-slate-800/50 backdrop-blur-sm border border-purple-500/20 rounded-xl shadow-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-purple-900/50">
              <tr>
                <th className="px-6 py-4 text-left text-purple-200 font-semibold">Usuario</th>
                <th className="px-6 py-4 text-left text-purple-200 font-semibold">Email</th>
                <th className="px-6 py-4 text-center text-purple-200 font-semibold">Rol</th>
                <th className="px-6 py-4 text-center text-purple-200 font-semibold">Estado</th>
                <th className="px-6 py-4 text-center text-purple-200 font-semibold">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-purple-500/20">
              {usuariosFiltrados.map(usuario => (
                <tr key={usuario.id} className="hover:bg-purple-900/20 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-purple-600 flex items-center justify-center text-white font-bold">
                        {usuario.username.charAt(0).toUpperCase()}
                      </div>
                      <span className="text-white font-medium">{usuario.username}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-purple-100">{usuario.email}</td>
                  <td className="px-6 py-4 text-center">
                    <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getRolColor(usuario.rol)}`}>
                      {usuario.rol.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-center">
                    {usuario.activo ? (
                      <span className="px-3 py-1 bg-green-500/20 text-green-300 rounded-full text-sm font-semibold">
                        Activo
                      </span>
                    ) : (
                      <span className="px-3 py-1 bg-red-500/20 text-red-300 rounded-full text-sm font-semibold">
                        Inactivo
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center justify-center gap-2">
                      <button
                        onClick={() => abrirModalEditar(usuario)}
                        className="p-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                        title="Editar rol"
                      >
                        <Edit2 size={18} />
                      </button>
                      <button
                        onClick={() => toggleActivarUsuario(usuario)}
                        className={`p-2 ${usuario.activo ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'} text-white rounded-lg transition-colors`}
                        title={usuario.activo ? 'Desactivar' : 'Activar'}
                      >
                        {usuario.activo ? <X size={18} /> : <Check size={18} />}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="px-6 py-4 bg-purple-900/30 border-t border-purple-500/20">
          <p className="text-purple-200 text-sm">
            Mostrando {usuariosFiltrados.length} de {usuarios.length} usuarios
          </p>
        </div>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-slate-800 border border-purple-500/30 rounded-2xl p-6 max-w-md w-full shadow-2xl">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-bold text-white flex items-center gap-2">
                {modalMode === 'create' ? <UserPlus size={24} /> : <Edit2 size={24} />}
                {modalMode === 'create' ? 'Crear Usuario' : 'Editar Usuario'}
              </h3>
              <button onClick={cerrarModal} className="text-purple-400 hover:text-purple-300">
                <X size={24} />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              {modalMode === 'create' && (
                <>
                  <div>
                    <label className="block text-purple-200 text-sm font-medium mb-2">
                      Usuario
                    </label>
                    <input
                      type="text"
                      value={formData.username}
                      onChange={(e) => setFormData({...formData, username: e.target.value})}
                      className="w-full bg-slate-700 text-white border border-purple-500/30 rounded-lg px-4 py-2 focus:outline-none focus:border-purple-500"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-purple-200 text-sm font-medium mb-2">
                      Email
                    </label>
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({...formData, email: e.target.value})}
                      className="w-full bg-slate-700 text-white border border-purple-500/30 rounded-lg px-4 py-2 focus:outline-none focus:border-purple-500"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-purple-200 text-sm font-medium mb-2">
                      Contraseña
                    </label>
                    <input
                      type="password"
                      value={formData.password}
                      onChange={(e) => setFormData({...formData, password: e.target.value})}
                      className="w-full bg-slate-700 text-white border border-purple-500/30 rounded-lg px-4 py-2 focus:outline-none focus:border-purple-500"
                      required
                      minLength={8}
                    />
                    <p className="text-xs text-purple-300 mt-1">
                      Mínimo 8 caracteres, 1 mayúscula, 1 minúscula, 1 número
                    </p>
                  </div>
                </>
              )}

              <div>
                <label className="block text-purple-200 text-sm font-medium mb-2">
                  Rol
                </label>
                <select
                  value={formData.rol}
                  onChange={(e) => setFormData({...formData, rol: e.target.value})}
                  className="w-full bg-slate-700 text-white border border-purple-500/30 rounded-lg px-4 py-2 focus:outline-none focus:border-purple-500"
                >
                  <option value="admin">Administrador</option>
                  <option value="analista">Analista</option>
                  <option value="operador">Operador</option>
                  <option value="cliente">Cliente</option>
                </select>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  type="button"
                  onClick={cerrarModal}
                  className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
                >
                  {modalMode === 'create' ? 'Crear' : 'Guardar'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}