"""
Modelo User - Sistema de autenticación y autorización
Soporte para usuarios clientes y administradores
"""
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from .base import Base
import enum

class RolUsuario(enum.Enum):
    """Roles del sistema"""
    ADMIN = "admin"
    ANALISTA = "analista"
    OPERADOR = "operador"
    CLIENTE = "cliente"

class User(Base, UserMixin):  # ← AGREGADO UserMixin
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nombre_completo = Column(String(150))
    telefono = Column(String(20))
    rol = Column(Enum(RolUsuario), default=RolUsuario.CLIENTE, nullable=False)
    activo = Column(Boolean, default=True)
    verificado = Column(Boolean, default=False)
    ultimo_login = Column(DateTime)
    intentos_fallidos = Column(Integer, default=0)
    bloqueado_hasta = Column(DateTime, nullable=True)
    token_verificacion = Column(String(100), nullable=True)
    token_reset_password = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}', rol='{self.rol.value}')>"

    def to_dict(self, include_sensitive=False):
        """Serializar a diccionario"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'nombre_completo': self.nombre_completo,
            'telefono': self.telefono,
            'rol': self.rol.value,
            'activo': self.activo,
            'verificado': self.verificado,
            'ultimo_login': self.ultimo_login.isoformat() if self.ultimo_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_sensitive:
            data['intentos_fallidos'] = self.intentos_fallidos
            data['bloqueado_hasta'] = self.bloqueado_hasta.isoformat() if self.bloqueado_hasta else None
        return data

    def es_admin(self):
        return self.rol == RolUsuario.ADMIN

    def es_analista(self):
        return self.rol in [RolUsuario.ADMIN, RolUsuario.ANALISTA]

    def puede_gestionar_tickets(self):
        return self.rol in [RolUsuario.ADMIN, RolUsuario.OPERADOR]