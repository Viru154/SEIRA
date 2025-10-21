"""
Modelo Ticket - Tabla principal de tickets de soporte
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Index
from sqlalchemy.orm import relationship
from .base import Base

class Ticket(Base):
    __tablename__ = 'tickets'
    
    # Campos principales
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(50), unique=True, nullable=False, index=True)
    titulo = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=False)
    categoria = Column(String(100), nullable=False, index=True)
    
    # Metadatos
    fecha_creacion = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    estado = Column(String(50), default='abierto')
    prioridad = Column(String(50), default='media')
    
    # Campos adicionales para e-commerce
    cliente_id = Column(String(100), index=True)
    producto_relacionado = Column(String(255))
    orden_id = Column(String(100))
    
    # Control de procesamiento
    procesado = Column(Boolean, default=False, index=True)
    fecha_procesamiento = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    analisis = relationship("Analisis", back_populates="ticket", uselist=False, cascade="all, delete-orphan")
    
    # Índices compuestos para queries comunes
# Cambiar el __table_args__ al final de la clase Ticket
    __table_args__ = (
        Index('idx_ticket_categoria_fecha', 'categoria', 'fecha_creacion'), 
        Index('idx_ticket_procesado_fecha', 'procesado', 'fecha_creacion'),  
        Index('idx_ticket_estado_prioridad', 'estado', 'prioridad'),          
    )
    
    def __repr__(self):
        return f"<Ticket(id={self.id}, ticket_id='{self.ticket_id}', categoria='{self.categoria}')>"
    
    def to_dict(self):
        """Serializar a diccionario"""
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'titulo': self.titulo,
            'descripcion': self.descripcion,
            'categoria': self.categoria,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'estado': self.estado,
            'prioridad': self.prioridad,
            'cliente_id': self.cliente_id,
            'producto_relacionado': self.producto_relacionado,
            'orden_id': self.orden_id,
            'procesado': self.procesado,
            'fecha_procesamiento': self.fecha_procesamiento.isoformat() if self.fecha_procesamiento else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }