"""
Calculador del Índice de Automatización Recomendada (IAR)
"""
import logging
from collections import Counter
import json
from config import get_config

logger = logging.getLogger(__name__)

class IARCalculator:
    """Calculador del IAR basado en 4 métricas ponderadas"""
    
    def __init__(self):
        """Inicializa el calculador con configuración"""
        config = get_config()
        
        # Ponderaciones del IAR (deben sumar 1.0)
        self.weights = config.IAR_WEIGHTS
        
        # Costos de implementación
        self.costo_base = config.COSTO_IMPLEMENTACION_BASE
        self.costo_hora_soporte = config.COSTO_HORA_SOPORTE
        self.costo_mantenimiento_porcentaje = config.COSTO_MANTENIMIENTO_ANUAL_PORCENTAJE
        
        logger.info(f"✅ IARCalculator inicializado con ponderaciones: {self.weights}")
    
    def calcular_frecuencia_score(self, total_tickets, total_global=150000):
        """
        Calcula el score de frecuencia (0-100)
        
        Lógica: A mayor cantidad de tickets, mayor score
        Formula: (total_tickets / total_global) * 100
        
        Args:
            total_tickets: Número de tickets de esta categoría
            total_global: Total de tickets en el sistema
            
        Returns:
            float: Score 0-100
        """
        if total_global == 0:
            return 0.0
        
        # Normalizar a 100
        score = (total_tickets / total_global) * 100
        
        # Aplicar factor de escala para que categorías con pocos tickets también puedan tener score alto
        # Si tiene más del 10% de tickets, ya es score alto
        if total_tickets / total_global > 0.10:
            score = 100.0
        elif total_tickets / total_global > 0.05:
            score = min(score * 1.5, 100.0)
        else:
            score = min(score * 2.0, 100.0)
        
        return round(min(score, 100.0), 2)
    
    def calcular_complejidad_score(self, complejidad_promedio):
        """
        Calcula el score de complejidad (0-100)
        
        Lógica: A MENOR complejidad, MAYOR score (invertido)
        Problemas simples son más automatizables
        
        Formula: 100 - complejidad_promedio
        
        Args:
            complejidad_promedio: Complejidad promedio (0-100)
            
        Returns:
            float: Score 0-100 (invertido)
        """
        # Invertir: problemas simples = score alto
        score = 100.0 - complejidad_promedio
        
        return round(max(0.0, min(score, 100.0)), 2)
    
    def calcular_impacto_score(self, tiempo_total_anual_horas):
        """
        Calcula el score de impacto en productividad (0-100)
        
        Lógica: A mayor tiempo invertido, mayor impacto de automatizar
        
        Formula: Escala logarítmica basada en horas anuales
        
        Args:
            tiempo_total_anual_horas: Tiempo total anual en horas
            
        Returns:
            float: Score 0-100
        """
        if tiempo_total_anual_horas <= 0:
            return 0.0
        
        # Escala:
        # 0-100 horas/año = 0-20 score
        # 100-500 horas/año = 20-50 score
        # 500-1000 horas/año = 50-75 score
        # 1000+ horas/año = 75-100 score
        
        if tiempo_total_anual_horas < 100:
            score = (tiempo_total_anual_horas / 100) * 20
        elif tiempo_total_anual_horas < 500:
            score = 20 + ((tiempo_total_anual_horas - 100) / 400) * 30
        elif tiempo_total_anual_horas < 1000:
            score = 50 + ((tiempo_total_anual_horas - 500) / 500) * 25
        else:
            score = 75 + min(((tiempo_total_anual_horas - 1000) / 2000) * 25, 25)
        
        return round(min(score, 100.0), 2)
    
    def calcular_viabilidad_score(self, repetitividad, uniformidad, tasa_resolucion):
        """
        Calcula el score de viabilidad técnica (0-100)
        
        Lógica: Combina 3 factores
        - Repetitividad (40%): Qué tan repetitivos son los problemas
        - Uniformidad (30%): Qué tan uniformes son las soluciones
        - Tasa resolución (30%): % de tickets que se resuelven exitosamente
        
        Args:
            repetitividad: Score 0-100
            uniformidad: Score 0-100
            tasa_resolucion: 0-1 (se convierte a 0-100)
            
        Returns:
            float: Score 0-100
        """
        # Convertir tasa de resolución a escala 0-100
        tasa_resolucion_score = tasa_resolucion * 100
        
        # Aplicar ponderaciones
        score = (
            repetitividad * 0.40 +
            uniformidad * 0.30 +
            tasa_resolucion_score * 0.30
        )
        
        return round(min(score, 100.0), 2)
    
    def calcular_iar(self, frecuencia, complejidad, impacto, viabilidad):
        """
        Calcula el IAR final usando la fórmula ponderada
        
        IAR = (frecuencia × 30%) + (complejidad × 25%) + 
              (impacto × 25%) + (viabilidad × 20%)
        
        Args:
            frecuencia: Score 0-100
            complejidad: Score 0-100
            impacto: Score 0-100
            viabilidad: Score 0-100
            
        Returns:
            float: IAR 0-100
        """
        iar = (
            frecuencia * self.weights['frecuencia'] +
            complejidad * self.weights['complejidad'] +
            impacto * self.weights['impacto_productividad'] +
            viabilidad * self.weights['viabilidad_tecnica']
        )
        
        return round(min(iar, 100.0), 2)
    
    def determinar_nivel(self, iar):
        """
        Determina el nivel de recomendación según el IAR
        
        Niveles:
        - 0-30: NO_RECOMENDADO
        - 31-60: EVALUAR
        - 61-80: RECOMENDADO  
        - 81-100: ALTAMENTE_RECOMENDADO
        
        Args:
            iar: Índice IAR (0-100)
            
        Returns:
            str: Nivel de recomendación
        """
        if iar <= 30:
            return 'NO_RECOMENDADO'
        elif iar <= 60:
            return 'EVALUAR'
        elif iar <= 80:
            return 'RECOMENDADO'
        else:
            return 'ALTAMENTE_RECOMENDADO'
    
    def sugerir_tipo_ia(self, categoria, urgencia_critica, sentimiento_negativo):
        """
        Sugiere el tipo de IA más apropiado
        
        Args:
            categoria: Categoría del problema
            urgencia_critica: Número de tickets críticos
            sentimiento_negativo: Número de tickets negativos
            
        Returns:
            str: Tipo de IA sugerida
        """
        categoria_lower = categoria.lower()
        
        # Mapeo de categorías a tipos de IA
        if 'consulta' in categoria_lower or 'información' in categoria_lower:
            return 'Chatbot/FAQ Inteligente'
        elif 'pago' in categoria_lower or 'envío' in categoria_lower or 'pedido' in categoria_lower:
            return 'RPA + Integración de Sistemas'
        elif 'técnico' in categoria_lower or 'error' in categoria_lower:
            return 'Sistema Experto + Diagnóstico Automático'
        elif 'devolución' in categoria_lower or 'garantía' in categoria_lower:
            return 'Workflow Automation + ML'
        elif sentimiento_negativo > urgencia_critica:
            return 'Chatbot Empático + Escalamiento Inteligente'
        else:
            return 'NLP + Clasificación Automática'
    
    def estimar_roi(self, tiempo_total_anual_horas, costo_implementacion=None):
        """
        Estima el ROI de automatizar esta categoría
        
        Formula:
        - Ahorro anual = tiempo_total_anual × $25/hora × 0.7 (70% automatizable)
        - ROI % = ((ahorro_anual - costo_mantenimiento) / costo_implementacion) × 100
        - Meses recuperación = costo_implementacion / (ahorro_mensual - costo_mantenimiento_mensual)
        
        Args:
            tiempo_total_anual_horas: Horas anuales dedicadas
            costo_implementacion: Costo de implementar (default: config)
            
        Returns:
            dict: {ahorro_anual, roi_porcentaje, meses_recuperacion, costo_mantenimiento}
        """
        if costo_implementacion is None:
            costo_implementacion = self.costo_base
        
        # Ahorro anual (asumiendo 70% de automatización exitosa)
        ahorro_anual = tiempo_total_anual_horas * self.costo_hora_soporte * 0.7
        
        # Costo de mantenimiento anual (15% del costo de implementación)
        costo_mantenimiento_anual = costo_implementacion * self.costo_mantenimiento_porcentaje
        
        # ROI porcentual
        beneficio_neto = ahorro_anual - costo_mantenimiento_anual
        
        if costo_implementacion > 0:
            roi_porcentaje = (beneficio_neto / costo_implementacion) * 100
        else:
            roi_porcentaje = 0.0
        
        # Meses para recuperar inversión
        ahorro_mensual = ahorro_anual / 12
        costo_mantenimiento_mensual = costo_mantenimiento_anual / 12
        beneficio_mensual = ahorro_mensual - costo_mantenimiento_mensual
        
        if beneficio_mensual > 0:
            meses_recuperacion = int(costo_implementacion / beneficio_mensual)
        else:
            meses_recuperacion = 999  # Nunca se recupera
        
        return {
            'ahorro_anual_usd': round(ahorro_anual, 2),
            'roi_porcentaje': round(roi_porcentaje, 2),
            'meses_recuperacion': meses_recuperacion,
            'costo_mantenimiento_anual': round(costo_mantenimiento_anual, 2),
            'beneficio_neto_anual': round(beneficio_neto, 2)
        }
    
    def generar_recomendacion(self, categoria, iar, nivel, roi_info, total_tickets):
        """
        Genera texto de recomendación personalizado
        
        Args:
            categoria: Categoría analizada
            iar: Valor del IAR
            nivel: Nivel de recomendación
            roi_info: Información de ROI
            total_tickets: Total de tickets de la categoría
            
        Returns:
            tuple: (recomendacion_texto, justificacion_texto)
        """
        if nivel == 'ALTAMENTE_RECOMENDADO':
            recomendacion = f"✅ ALTAMENTE RECOMENDADO automatizar '{categoria}'. "
            recomendacion += f"Con un IAR de {iar}/100, esta categoría muestra excelente potencial de automatización. "
            recomendacion += f"Se estima un ROI de {roi_info['roi_porcentaje']:.1f}% con recuperación en {roi_info['meses_recuperacion']} meses."
            
            justificacion = f"Esta categoría tiene {total_tickets:,} tickets, representando un alto volumen. "
            justificacion += f"El ahorro anual proyectado es de ${roi_info['ahorro_anual_usd']:,.2f}. "
            justificacion += "La automatización reducirá significativamente la carga operativa."
            
        elif nivel == 'RECOMENDADO':
            recomendacion = f"👍 RECOMENDADO considerar automatización para '{categoria}'. "
            recomendacion += f"Con un IAR de {iar}/100, esta categoría es un buen candidato. "
            recomendacion += f"ROI estimado: {roi_info['roi_porcentaje']:.1f}% en {roi_info['meses_recuperacion']} meses."
            
            justificacion = f"Con {total_tickets:,} tickets, hay suficiente volumen para justificar la inversión. "
            justificacion += "Se recomienda un piloto antes de implementación completa."
            
        elif nivel == 'EVALUAR':
            recomendacion = f"⚠️ EVALUAR CON CAUTELA la automatización de '{categoria}'. "
            recomendacion += f"IAR de {iar}/100 indica potencial moderado. "
            recomendacion += f"El ROI proyectado es {roi_info['roi_porcentaje']:.1f}%, recuperación en {roi_info['meses_recuperacion']} meses."
            
            justificacion = f"Aunque hay {total_tickets:,} tickets, otros factores sugieren cautela. "
            justificacion += "Considerar soluciones parciales o semi-automatizadas antes de IA completa."
            
        else:  # NO_RECOMENDADO
            recomendacion = f"❌ NO RECOMENDADO automatizar '{categoria}' en este momento. "
            recomendacion += f"Con IAR de {iar}/100, la automatización no es prioritaria. "
            
            justificacion = f"Los {total_tickets:,} tickets de esta categoría no justifican la inversión en IA. "
            justificacion += "Considerar mejoras en procesos manuales o documentación mejorada."
        
        return recomendacion, justificacion
    
    def calcular_impacto_ambiental(self, tiempo_total_anual_horas):
        """
        Estima el ahorro de carbono por automatización
        
        Asume que cada hora de trabajo humano consume ~0.5 kg CO2
        (computadora + iluminación + HVAC)
        
        Args:
            tiempo_total_anual_horas: Horas anuales
            
        Returns:
            float: kg de CO2 ahorrados anualmente
        """
        # 0.5 kg CO2 por hora × 70% de automatización
        ahorro_carbono = tiempo_total_anual_horas * 0.5 * 0.7
        
        return round(ahorro_carbono, 2)