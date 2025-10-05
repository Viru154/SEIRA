"""
SEIRA - Calculador del IAR (Índice de Automatización Recomendada)
Analiza métricas y genera recomendaciones sobre implementación de IA
"""

import json
import pandas as pd
from collections import Counter
from datetime import datetime
import math


class IARCalculator:
    """Calculador del Índice de Automatización Recomendada"""
    
    def __init__(self, tickets_procesados):
        self.tickets = tickets_procesados
        self.df = pd.DataFrame(tickets_procesados)
        self.metricas_por_categoria = {}
        self.recomendaciones = []
    
    def calcular_frecuencia_score(self, categoria):
        """
        Calcula score de frecuencia (0-100)
        Mayor frecuencia = mayor score
        """
        tickets_categoria = self.df[self.df['categoria'] == categoria]
        total_tickets = len(tickets_categoria)
        
        # Normalizar a escala 0-100
        # Consideramos 50+ tickets como frecuencia muy alta
        frecuencia_score = min((total_tickets / 50) * 100, 100)
        
        return round(frecuencia_score, 2)
    
    def calcular_complejidad_score(self, categoria):
        """
        Calcula score de complejidad invertido (0-100)
        Menor complejidad = mayor score (más automatizable)
        """
        tickets_categoria = self.df[self.df['categoria'] == categoria]
        complejidad_promedio = tickets_categoria['complejidad'].mean()
        
        # Invertir: baja complejidad = alto score de automatización
        # Complejidad 0-30 (simple) -> score 100-70
        # Complejidad 30-60 (media) -> score 70-40
        # Complejidad 60-100 (alta) -> score 40-0
        complejidad_score = 100 - complejidad_promedio
        
        return round(max(complejidad_score, 0), 2)
    
    def calcular_impacto_productividad_score(self, categoria):
        """
        Calcula score de impacto en productividad (0-100)
        Basado en tiempo de resolución y frecuencia
        """
        tickets_categoria = self.df[self.df['categoria'] == categoria]
        
        # Tickets resueltos con tiempo registrado
        resueltos = tickets_categoria[tickets_categoria['tiempo_resolucion_horas'] > 0]
        
        if len(resueltos) == 0:
            return 0
        
        tiempo_promedio = resueltos['tiempo_resolucion_horas'].mean()
        total_tickets = len(tickets_categoria)
        
        # Calcular horas totales invertidas
        horas_totales_mes = (tiempo_promedio * total_tickets) / 12  # Promedio mensual
        
        # Normalizar: 100+ horas/mes = score 100
        impacto_score = min((horas_totales_mes / 100) * 100, 100)
        
        return round(impacto_score, 2)
    
    def calcular_viabilidad_tecnica_score(self, categoria):
        """
        Calcula score de viabilidad técnica (0-100)
        Basado en patrones, repetitividad y tipo de problema
        """
        tickets_categoria = self.df[self.df['categoria'] == categoria]
        
        # Factores de viabilidad
        # 1. Repetitividad de palabras clave
        all_keywords = []
        for _, ticket in tickets_categoria.iterrows():
            if 'palabras_clave' in ticket and ticket['palabras_clave']:
                all_keywords.extend(ticket['palabras_clave'])
        
        if not all_keywords:
            repetitividad = 0
        else:
            counter = Counter(all_keywords)
            # % de keywords que se repiten al menos 3 veces
            repetidos = sum(1 for count in counter.values() if count >= 3)
            repetitividad = (repetidos / len(counter)) * 100 if counter else 0
        
        # 2. Uniformidad de complejidad (menor desviación = más viable)
        std_complejidad = tickets_categoria['complejidad'].std()
        uniformidad = 100 - min(std_complejidad * 2, 100)
        
        # 3. Tasa de resolución (alta = más predecible = más viable)
        tasa_resolucion = (len(tickets_categoria[tickets_categoria['estado'] == 'Resuelto']) / len(tickets_categoria)) * 100
        
        # Combinar factores
        viabilidad_score = (repetitividad * 0.4) + (uniformidad * 0.3) + (tasa_resolucion * 0.3)
        
        return round(viabilidad_score, 2)
    
    def calcular_iar(self, categoria):
        """
        Calcula el IAR final para una categoría
        IAR = (Frecuencia × 0.30) + (Complejidad × 0.25) + 
              (Impacto × 0.25) + (Viabilidad × 0.20)
        """
        freq_score = self.calcular_frecuencia_score(categoria)
        comp_score = self.calcular_complejidad_score(categoria)
        impact_score = self.calcular_impacto_productividad_score(categoria)
        viab_score = self.calcular_viabilidad_tecnica_score(categoria)
        
        iar = (freq_score * 0.30) + (comp_score * 0.25) + (impact_score * 0.25) + (viab_score * 0.20)
        
        return round(iar, 2)
    
    def estimar_roi(self, categoria):
        """
        Estima el ROI de implementar IA para una categoría
        Retorna ahorro anual estimado en horas y valor monetario
        """
        tickets_categoria = self.df[self.df['categoria'] == categoria]
        resueltos = tickets_categoria[tickets_categoria['tiempo_resolucion_horas'] > 0]
        
        if len(resueltos) == 0:
            return {'ahorro_horas_anual': 0, 'ahorro_monetario_usd': 0, 'roi_porcentaje': 0}
        
        # Calcular horas anuales dedicadas
        tiempo_promedio = resueltos['tiempo_resolucion_horas'].mean()
        tickets_mensuales = len(tickets_categoria) / 12  # Dataset de 1 año
        horas_mensuales = tiempo_promedio * tickets_mensuales
        horas_anuales = horas_mensuales * 12
        
        # Suponer 70% de automatización posible
        factor_automatizacion = 0.70
        ahorro_horas = horas_anuales * factor_automatizacion
        
        # Costo hora técnico: $25 USD promedio
        costo_hora = 25
        ahorro_monetario = ahorro_horas * costo_hora
        
        # ROI: (Ahorro - Costo implementación) / Costo implementación
        # Suponemos costo implementación IA: $5,000 - $15,000
        costo_implementacion = 10000
        roi_porcentaje = ((ahorro_monetario - costo_implementacion) / costo_implementacion) * 100
        
        return {
            'ahorro_horas_anual': round(ahorro_horas, 2),
            'ahorro_monetario_usd': round(ahorro_monetario, 2),
            'costo_implementacion_usd': costo_implementacion,
            'roi_porcentaje': round(roi_porcentaje, 2),
            'tiempo_recuperacion_meses': round(costo_implementacion / (ahorro_monetario / 12), 1) if ahorro_monetario > 0 else 999
        }
    
    def generar_recomendacion(self, categoria, iar, metricas):
        """
        Genera recomendación textual basada en IAR
        """
        roi = self.estimar_roi(categoria)
        
        # Clasificar IAR
        if iar >= 80:
            nivel = "ALTAMENTE RECOMENDADO"
            recomendacion = f"La implementación de IA para '{categoria}' está ALTAMENTE RECOMENDADA. "
            recomendacion += f"Con un IAR de {iar}, esta categoría muestra excelente potencial de automatización. "
            tipo_ia = "Sistema de clasificación y resolución automática con ML"
            
        elif iar >= 60:
            nivel = "RECOMENDADO"
            recomendacion = f"Se RECOMIENDA implementar IA para '{categoria}'. "
            recomendacion += f"IAR de {iar} indica buenas condiciones para automatización. "
            tipo_ia = "Chatbot con NLP y respuestas predefinidas inteligentes"
            
        elif iar >= 40:
            nivel = "EVALUAR CON CAUTELA"
            recomendacion = f"Evaluar cuidadosamente la implementación de IA para '{categoria}'. "
            recomendacion += f"IAR de {iar} sugiere beneficios moderados. "
            tipo_ia = "Sistema de asistencia semiautomática (sugerencias al operador)"
            
        else:
            nivel = "NO RECOMENDADO"
            recomendacion = f"NO se recomienda implementar IA para '{categoria}' en este momento. "
            recomendacion += f"IAR de {iar} indica bajo potencial de automatización. "
            tipo_ia = "Mejora de procesos manuales o soluciones simples"
        
        # Agregar análisis detallado
        recomendacion += f"\n\n📊 Análisis detallado:\n"
        recomendacion += f"  • Frecuencia: {metricas['frecuencia_score']}/100 ({metricas['total_tickets']} tickets)\n"
        recomendacion += f"  • Complejidad: {metricas['complejidad_score']}/100 (promedio: {metricas['complejidad_promedio']:.1f})\n"
        recomendacion += f"  • Impacto productividad: {metricas['impacto_score']}/100\n"
        recomendacion += f"  • Viabilidad técnica: {metricas['viabilidad_score']}/100\n"
        
        recomendacion += f"\n💰 ROI Estimado:\n"
        recomendacion += f"  • Ahorro anual: {roi['ahorro_horas_anual']:.0f} horas (~${roi['ahorro_monetario_usd']:,.0f} USD)\n"
        recomendacion += f"  • Inversión estimada: ${roi['costo_implementacion_usd']:,} USD\n"
        recomendacion += f"  • ROI: {roi['roi_porcentaje']:.1f}%\n"
        
        if roi['roi_porcentaje'] > 0:
            recomendacion += f"  • Tiempo de recuperación: {roi['tiempo_recuperacion_meses']:.1f} meses\n"
        
        recomendacion += f"\n🤖 Solución sugerida: {tipo_ia}\n"
        
        # Impacto ambiental
        recomendacion += f"\n🌱 Impacto ambiental:\n"
        if iar >= 60:
            co2 = roi['ahorro_horas_anual'] * 0.5  # kg CO2 por hora de servidor
            recomendacion += f"  • Emisiones de entrenamiento/operación IA: ~{co2:.0f} kg CO2/año\n"
            recomendacion += f"  • Considerar uso de modelos eficientes y servidores verdes\n"
        else:
            recomendacion += f"  • Impacto ambiental bajo (solución manual/simple)\n"
        
        return {
            'categoria': categoria,
            'iar': iar,
            'nivel': nivel,
            'recomendacion': recomendacion,
            'tipo_ia_sugerida': tipo_ia,
            'roi': roi,
            'metricas': metricas
        }
    
    def analizar_todas_categorias(self):
        """
        Analiza todas las categorías y genera recomendaciones
        """
        print("\n" + "="*70)
        print("CALCULANDO IAR POR CATEGORÍA")
        print("="*70)
        
        categorias = self.df['categoria'].unique()
        
        for categoria in sorted(categorias):
            print(f"\nAnalizando: {categoria}")
            
            # Calcular métricas
            tickets_cat = self.df[self.df['categoria'] == categoria]
            
            metricas = {
                'total_tickets': len(tickets_cat),
                'frecuencia_score': self.calcular_frecuencia_score(categoria),
                'complejidad_promedio': tickets_cat['complejidad'].mean(),
                'complejidad_score': self.calcular_complejidad_score(categoria),
                'impacto_score': self.calcular_impacto_productividad_score(categoria),
                'viabilidad_score': self.calcular_viabilidad_tecnica_score(categoria)
            }
            
            # Calcular IAR
            iar = self.calcular_iar(categoria)
            
            print(f"  IAR: {iar}/100")
            print(f"  - Frecuencia: {metricas['frecuencia_score']}")
            print(f"  - Complejidad: {metricas['complejidad_score']}")
            print(f"  - Impacto: {metricas['impacto_score']}")
            print(f"  - Viabilidad: {metricas['viabilidad_score']}")
            
            # Generar recomendación
            recomendacion = self.generar_recomendacion(categoria, iar, metricas)
            self.recomendaciones.append(recomendacion)
            self.metricas_por_categoria[categoria] = metricas
        
        print("\n" + "="*70)
    
    def mostrar_resumen(self):
        """
        Muestra resumen de recomendaciones
        """
        print("\n" + "="*70)
        print("RESUMEN DE RECOMENDACIONES")
        print("="*70)
        
        # Ordenar por IAR
        recomendaciones_ordenadas = sorted(self.recomendaciones, key=lambda x: x['iar'], reverse=True)
        
        for rec in recomendaciones_ordenadas:
            print(f"\n{'─'*70}")
            print(f"📁 Categoría: {rec['categoria']}")
            print(f"📊 IAR: {rec['iar']}/100 - {rec['nivel']}")
            print(f"💡 {rec['tipo_ia_sugerida']}")
            print(f"�� ROI: {rec['roi']['roi_porcentaje']:.1f}% | Ahorro: ${rec['roi']['ahorro_monetario_usd']:,.0f}/año")
        
        print("\n" + "="*70)
    
    def guardar_recomendaciones(self, filename='data/processed/recomendaciones.json'):
        """
        Guarda las recomendaciones en JSON
        """
        resultado = {
            'fecha_analisis': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_tickets_analizados': len(self.tickets),
            'categorias_analizadas': len(self.recomendaciones),
            'recomendaciones': self.recomendaciones,
            'metricas_globales': {
                'iar_promedio': round(sum(r['iar'] for r in self.recomendaciones) / len(self.recomendaciones), 2),
                'ahorro_total_potencial_usd': round(sum(r['roi']['ahorro_monetario_usd'] for r in self.recomendaciones), 2),
                'categorias_altamente_recomendadas': sum(1 for r in self.recomendaciones if r['iar'] >= 80),
                'categorias_recomendadas': sum(1 for r in self.recomendaciones if 60 <= r['iar'] < 80),
                'categorias_no_recomendadas': sum(1 for r in self.recomendaciones if r['iar'] < 40)
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Recomendaciones guardadas en: {filename}")


def main():
    """Función principal"""
    print("SEIRA - Calculador del IAR")
    print("="*70)
    
    # Cargar tickets procesados
    print("\nCargando tickets procesados...")
    with open('data/processed/tickets_procesados.json', 'r', encoding='utf-8') as f:
        tickets = json.load(f)
    print(f"✅ Cargados {len(tickets)} tickets procesados")
    
    # Crear calculador
    calculator = IARCalculator(tickets)
    
    # Analizar todas las categorías
    calculator.analizar_todas_categorias()
    
    # Mostrar resumen
    calculator.mostrar_resumen()
    
    # Guardar resultados
    calculator.guardar_recomendaciones()
    
    print("\n✅ Análisis IAR completado exitosamente!")


if __name__ == '__main__':
    main()
