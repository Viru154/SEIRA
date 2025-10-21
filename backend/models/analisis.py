"""
Modelo Analisis - Resultados del procesamiento NLP
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from .base import Base

class Analisis(Base):
    __tablename__ = 'analisis'
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    ticket_id = Column(Integer, ForeignKey('tickets.id', ondelete='CASCADE'), unique=True, nullable=False)
    
    # Análisis NLP
    texto_limpio = Column(Text)
    palabras_clave = Column(JSON)  # Lista de palabras clave extraídas
    entidades = Column(JSON)  # Entidades nombradas (NER)
    tokens = Column(JSON)  # Tokens procesados
    
    # Métricas de complejidad
    complejidad_score = Column(Float, default=0.0)
    sentimiento = Column(String(50))  # positivo, negativo, neutral
    urgencia = Column(String(50))  # baja, media, alta, critica
    
    # Clasificación
    categoria_detectada = Column(String(100))
    confianza_clasificacion = Column(Float, default=0.0)
    
    # Métricas adicionales
    longitud_texto = Column(Integer)
    num_palabras = Column(Integer)
    num_entidades = Column(Integer, default=0)
    
    # Timestamps
    fecha_analisis = Column(DateTime, default=datetime.utcnow, nullable=False)
    tiempo_procesamiento_ms = Column(Float)  # Tiempo en milisegundos
    
    # Relaciones
    ticket = relationship("Ticket", back_populates="analisis")
    
    # Índices
    __table_args__ = (
        Index('idx_categoria_detectada', 'categoria_detectada'),
        Index('idx_urgencia', 'urgencia'),
        Index('idx_sentimiento', 'sentimiento'),
    )
    
    def __repr__(self):
        return f"<Analisis(id={self.id}, ticket_id={self.ticket_id}, categoria='{self.categoria_detectada}')>"
    
    def to_dict(self):
        """Serializar a diccionario"""
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'texto_limpio': self.texto_limpio,
            'palabras_clave': self.palabras_clave,
            'entidades': self.entidades,
            'complejidad_score': self.complejidad_score,
            'sentimiento': self.sentimiento,
            'urgencia': self.urgencia,
            'categoria_detectada': self.categoria_detectada,
            'confianza_clasificacion': self.confianza_clasificacion,
            'longitud_texto': self.longitud_texto,
            'num_palabras': self.num_palabras,
            'num_entidades': self.num_entidades,
            'fecha_analisis': self.fecha_analisis.isoformat() if self.fecha_analisis else None,
            'tiempo_procesamiento_ms': self.tiempo_procesamiento_ms
        }