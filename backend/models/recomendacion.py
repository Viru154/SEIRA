"""
Modelo Recomendacion - Recomendaciones de automatización por categoría
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, Index, JSON
from .base import Base

class Recomendacion(Base):
    __tablename__ = 'recomendaciones'
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Identificación
    categoria = Column(String(100), nullable=False, unique=True, index=True)
    
    # Índice IAR
    iar_score = Column(Float, nullable=False)
    nivel_recomendacion = Column(String(50))  # Alta, Media, Baja, No Recomendado
    
    # Componentes del IAR
    frecuencia_score = Column(Float, default=0.0)
    complejidad_score = Column(Float, default=0.0)
    impacto_productividad = Column(Float, default=0.0)
    viabilidad_tecnica = Column(Float, default=0.0)
    
    # Estadísticas
    total_tickets = Column(Integer, default=0)
    tickets_resolubles = Column(Integer, default=0)
    complejidad_promedio = Column(Float, default=0.0)
    
    # ROI Estimado
    roi_anual_estimado = Column(Float, default=0.0)  # Ahorro anual en USD
    roi_porcentaje = Column(Float, default=0.0)  # Retorno de inversión %
    meses_recuperacion = Column(Float, default=0.0)  # Meses para recuperar inversión
    
    # Costos estimados
    costo_implementacion = Column(Float, default=0.0)
    costo_mantenimiento_anual = Column(Float, default=0.0)
    ahorro_horas_anual = Column(Float, default=0.0)
    
    # Recomendación textual
    recomendacion_texto = Column(Text)
    razon_principal = Column(Text)
    acciones_sugeridas = Column(JSON)  # Lista de acciones recomendadas
    
    # Priorización
    prioridad = Column(Integer, default=0)  # 1-10, mayor es más prioritario
    aprobada = Column(Boolean, default=False)
    
    # Timestamps
    fecha_calculo = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Índices
    __table_args__ = (
        Index('idx_iar_prioridad', 'iar_score', 'prioridad'),
        Index('idx_nivel_recomendacion', 'nivel_recomendacion'),
    )
    
    def __repr__(self):
        return f"<Recomendacion(categoria='{self.categoria}', IAR={self.iar_score:.2f}, nivel='{self.nivel_recomendacion}')>"
    
    def to_dict(self):
        """Serializar a diccionario"""
        return {
            'id': self.id,
            'categoria': self.categoria,
            'iar_score': round(self.iar_score, 2),
            'nivel_recomendacion': self.nivel_recomendacion,
            'frecuencia_score': round(self.frecuencia_score, 2),
            'complejidad_score': round(self.complejidad_score, 2),
            'impacto_productividad': round(self.impacto_productividad, 2),
            'viabilidad_tecnica': round(self.viabilidad_tecnica, 2),
            'total_tickets': self.total_tickets,
            'tickets_resolubles': self.tickets_resolubles,
            'complejidad_promedio': round(self.complejidad_promedio, 2),
            'roi_anual_estimado': round(self.roi_anual_estimado, 2),
            'roi_porcentaje': round(self.roi_porcentaje, 2),
            'meses_recuperacion': round(self.meses_recuperacion, 2),
            'costo_implementacion': round(self.costo_implementacion, 2),
            'costo_mantenimiento_anual': round(self.costo_mantenimiento_anual, 2),
            'ahorro_horas_anual': round(self.ahorro_horas_anual, 2),
            'recomendacion_texto': self.recomendacion_texto,
            'razon_principal': self.razon_principal,
            'acciones_sugeridas': self.acciones_sugeridas,
            'prioridad': self.prioridad,
            'aprobada': self.aprobada,
            'fecha_calculo': self.fecha_calculo.isoformat() if self.fecha_calculo else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }