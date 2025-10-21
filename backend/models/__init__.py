"""
Modelos SQLAlchemy para SEIRA 2.0
PostgreSQL con soporte para millones de registros
"""
# Importar Base primero desde su módulo dedicado
from .base import Base

# Importar todos los modelos
from .ticket import Ticket
from .analisis import Analisis
from .recomendacion import Recomendacion
from .metrica import MetricaCategoria
from .user import User, RolUsuario

# Exportar todo
__all__ = [
    'Base',
    'Ticket',
    'Analisis',
    'Recomendacion',
    'MetricaCategoria'
    'Base',
    'Ticket',
    'Analisis', 
    'Recomendacion',
    'MetricaCategoria',
    'User',              # ← NUEVO
    'RolUsuario'         # ← NUEVO
]