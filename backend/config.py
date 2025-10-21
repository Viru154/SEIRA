"""
Configuración de SEIRA 2.0
"""
import os

class Config:
    # Base de datos
    DATABASE_URL = os.getenv(
        'DATABASE_URL',
        'postgresql://seira_user:seira_password_2024@localhost:5435/seira_db'
    )
    
    # SQLAlchemy
    SQLALCHEMY_ECHO = False  # ← AGREGADO
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'max_overflow': 40,
        'pool_pre_ping': True,
        'pool_recycle': 3600
    }
    
    # Frontend
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')

def get_config():
    return Config()