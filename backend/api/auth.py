"""
backend/api/auth.py - Sistema de autenticación con Flask-Login
"""
from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps
from models.user import User
from utils.database import db_manager
from werkzeug.security import check_password_hash
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def admin_required(f):
    """Decorador para rutas que requieren rol admin"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        # Recargar usuario desde BD para evitar DetachedInstanceError
        with db_manager.session_scope() as session:
            user = session.query(User).get(current_user.id)
            if not user or user.rol != 'admin':
                return jsonify({
                    'success': False,
                    'error': 'Acceso denegado. Se requiere rol de administrador.'
                }), 403
        return f(*args, **kwargs)
    return decorated_function

def validar_password(password):
    """Valida que la contraseña cumpla con los requisitos"""
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    if not re.search(r'[A-Z]', password):
        return False, "La contraseña debe contener al menos una mayúscula"
    if not re.search(r'[a-z]', password):
        return False, "La contraseña debe contener al menos una minúscula"
    if not re.search(r'\d', password):
        return False, "La contraseña debe contener al menos un número"
    return True, ""

@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    """Login de usuario - CRÍTICO: Debe retornar JSON correcto"""
    
    # Manejar preflight CORS
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        
        # Validar que existan los campos
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({
                'success': False,
                'error': 'Usuario y contraseña son requeridos'
            }), 400
        
        username = data.get('username')
        password = data.get('password')
        
        # Buscar usuario en BD
        with db_manager.session_scope() as db_session:
            user = db_session.query(User).filter(
                (User.username == username) | (User.email == username)
            ).first()
            
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'Usuario o contraseña incorrectos'
                }), 401
            
            # Verificar si está activo
            if not user.activo:
                return jsonify({
                    'success': False,
                    'error': 'Usuario desactivado. Contacta al administrador'
                }), 403
            
            # Verificar contraseña
            if not check_password_hash(user.password_hash, password):
                return jsonify({
                    'success': False,
                    'error': 'Usuario o contraseña incorrectos'
                }), 401
            
            # Login exitoso
            login_user(user, remember=True)
            
            # CRÍTICO: Retornar JSON con formato esperado por el frontend
            return jsonify({
                'success': True,
                'message': 'Login exitoso',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'rol': user.rol,
                    'activo': user.activo
                }
            }), 200
            
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Logout de usuario"""
    try:
        logout_user()
        return jsonify({
            'success': True,
            'message': 'Logout exitoso'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """Obtener usuario actual"""
    try:
        # Convertir rol a string
        if hasattr(current_user.rol, 'name'):
            rol_str = current_user.rol.name.lower()
        elif hasattr(current_user.rol, 'value'):
            rol_str = current_user.rol.value.lower()
        else:
            rol_str = str(current_user.rol).lower()
        
        return jsonify({
            'success': True,
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'email': current_user.email,
                'rol': rol_str,
                'activo': current_user.activo,
                'nombre_completo': getattr(current_user, 'nombre_completo', current_user.username)
            }
        }), 200
    except Exception as e:
        print(f"❌ Error en /me: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """Registro de nuevo usuario (solo admin puede crear usuarios)"""
    try:
        data = request.get_json()
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        rol = data.get('rol', 'cliente')
        
        # Validaciones
        if not username or not email or not password:
            return jsonify({
                'success': False,
                'error': 'Todos los campos son requeridos'
            }), 400
        
        # Validar password
        valido, mensaje = validar_password(password)
        if not valido:
            return jsonify({
                'success': False,
                'error': mensaje
            }), 400
        
        # Verificar si ya existe
        with db_manager.session_scope() as db_session:
            existe = db_session.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existe:
                return jsonify({
                    'success': False,
                    'error': 'Usuario o email ya existe'
                }), 409
            
            # Crear usuario
            nuevo_user = User(
                username=username,
                email=email,
                rol=rol
            )
            nuevo_user.set_password(password)
            
            db_session.add(nuevo_user)
            db_session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Usuario creado exitosamente',
                'user': {
                    'id': nuevo_user.id,
                    'username': nuevo_user.username,
                    'email': nuevo_user.email,
                    'rol': nuevo_user.rol
                }
            }), 201
            
    except Exception as e:
        print(f"❌ Error en registro: {e}")
        return jsonify({
            'success': False,
            'error': 'Error al crear usuario'
        }), 500

# Endpoints para admin
@auth_bp.route('/admin/users', methods=['GET'])
@admin_required
def get_users():
    """Obtener todos los usuarios (solo admin)"""
    try:
        with db_manager.session_scope() as db_session:
            users = db_session.query(User).all()
            
            users_list = []
            for u in users:
                # Convertir rol a string
                if hasattr(u.rol, 'name'):
                    rol_str = u.rol.name.lower()
                elif hasattr(u.rol, 'value'):
                    rol_str = u.rol.value.lower()
                else:
                    rol_str = str(u.rol).lower()
                
                users_list.append({
                    'id': u.id,
                    'username': u.username,
                    'email': u.email,
                    'rol': rol_str,
                    'activo': u.activo
                })
            
            return jsonify({
                'success': True,
                'users': users_list
            }), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/admin/users', methods=['POST'])
@admin_required
def create_user():
    """Crear usuario (solo admin)"""
    try:
        data = request.get_json()
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        rol = data.get('rol', 'operador')
        
        if not username or not email or not password:
            return jsonify({
                'success': False,
                'error': 'Todos los campos son requeridos'
            }), 400
        
        # Validar password
        valido, mensaje = validar_password(password)
        if not valido:
            return jsonify({
                'success': False,
                'error': mensaje
            }), 400
        
        with db_manager.session_scope() as db_session:
            # Verificar si existe
            existe = db_session.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existe:
                return jsonify({
                    'success': False,
                    'error': 'Usuario o email ya existe'
                }), 409
            
            # Crear usuario
            nuevo_user = User(
                username=username,
                email=email,
                rol=rol,
                activo=True
            )
            nuevo_user.set_password(password)
            
            db_session.add(nuevo_user)
            db_session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Usuario creado exitosamente'
            }), 201
            
    except Exception as e:
        print(f"❌ Error creando usuario: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """Actualizar usuario (solo admin)"""
    try:
        data = request.get_json()
        
        with db_manager.session_scope() as db_session:
            user = db_session.query(User).get(user_id)
            
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'Usuario no encontrado'
                }), 404
            
            # Actualizar campos permitidos
            if 'rol' in data:
                user.rol = data['rol']
            if 'activo' in data:
                user.activo = data['activo']
            
            db_session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Usuario actualizado exitosamente'
            }), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500