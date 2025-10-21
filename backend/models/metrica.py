"""
Modelo MetricaCategoria - Métricas agregadas por categoría y período
Usado para análisis temporal y forecasting
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Index, JSON
from .base import Base  # ✅ Ruta relativa

class MetricaCategoria(Base):
    __tablename__ = 'metricas_categoria'
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Identificación
    categoria = Column(String(100), nullable=False, index=True)
    fecha = Column(Date, nullable=False, index=True)
    periodo = Column(String(20), default='dia')  # dia, semana, mes
    
    # Contadores
    total_tickets = Column(Integer, default=0)
    tickets_procesados = Column(Integer, default=0)
    tickets_pendientes = Column(Integer, default=0)
    
    # Métricas de calidad
    complejidad_promedio = Column(Float, default=0.0)
    tiempo_resolucion_promedio = Column(Float, default=0.0)  # En horas
    
    # Distribución de urgencia
    urgencia_critica = Column(Integer, default=0)
    urgencia_alta = Column(Integer, default=0)
    urgencia_media = Column(Integer, default=0)
    urgencia_baja = Column(Integer, default=0)
    
    # Distribución de sentimiento
    sentimiento_positivo = Column(Integer, default=0)
    sentimiento_neutral = Column(Integer, default=0)
    sentimiento_negativo = Column(Integer, default=0)
    
    # Métricas de rendimiento
    tasa_resolucion = Column(Float, default=0.0)  # % de tickets resueltos
    satisfaccion_promedio = Column(Float, default=0.0)  # Score 0-100
    
    # Datos adicionales (para forecasting)
    datos_adicionales = Column(JSON)  # Métricas personalizadas
    
    # Anomalías detectadas
    es_anomalia = Column(Integer, default=0)  # 0 = no, 1 = sí
    score_anomalia = Column(Float, default=0.0)  # Score de Isolation Forest
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Índices compuestos
    # Cambiar el __table_args__ al final de la clase MetricaCategoria
    __table_args__ = (
        Index('idx_metrica_categoria_fecha', 'categoria', 'fecha'),
        Index('idx_metrica_categoria_periodo', 'categoria', 'periodo'),
        Index('idx_metrica_fecha_periodo', 'fecha', 'periodo'),
        Index('idx_metrica_anomalia', 'es_anomalia', 'fecha'),
    )
    
    def __repr__(self):
        return f"<MetricaCategoria(categoria='{self.categoria}', fecha={self.fecha}, total={self.total_tickets})>"
    
    def to_dict(self):
        """Serializar a diccionario"""
        return {
            'id': self.id,
            'categoria': self.categoria,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'periodo': self.periodo,
            'total_tickets': self.total_tickets,
            'tickets_procesados': self.tickets_procesados,
            'tickets_pendientes': self.tickets_pendientes,
            'complejidad_promedio': round(self.complejidad_promedio, 2),
            'tiempo_resolucion_promedio': round(self.tiempo_resolucion_promedio, 2),
            'urgencia_critica': self.urgencia_critica,
            'urgencia_alta': self.urgencia_alta,
            'urgencia_media': self.urgencia_media,
            'urgencia_baja': self.urgencia_baja,
            'sentimiento_positivo': self.sentimiento_positivo,
            'sentimiento_neutral': self.sentimiento_neutral,
            'sentimiento_negativo': self.sentimiento_negativo,
            'tasa_resolucion': round(self.tasa_resolucion, 2),
            'satisfaccion_promedio': round(self.satisfaccion_promedio, 2),
            'datos_adicionales': self.datos_adicionales,
            'es_anomalia': self.es_anomalia,
            'score_anomalia': round(self.score_anomalia, 4),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }