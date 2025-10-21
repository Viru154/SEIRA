"""
Script para calcular el IAR de todas las categorías
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.database import db_manager
from models.ticket import Ticket
from models.analisis import Analisis
from models.recomendacion import Recomendacion
from models.metrica import MetricaCategoria  # Cambio: metrica en lugar de metrica_categoria
from services.iar_calculator import IARCalculator
from sqlalchemy import func
from collections import Counter
import logging
import json
from datetime import datetime, date

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def calcular_metricas_categoria(session, categoria):
    """
    Calcula todas las métricas para una categoría específica
    
    Args:
        session: Sesión de SQLAlchemy
        categoria: Nombre de la categoría
        
    Returns:
        dict: Métricas calculadas
    """
    logger.info(f"📊 Calculando métricas para: {categoria}")
    
    # Obtener todos los tickets y análisis de esta categoría
    tickets = session.query(Ticket).filter_by(categoria=categoria).all()
    total_tickets = len(tickets)
    
    if total_tickets == 0:
        logger.warning(f"⚠️  No hay tickets para la categoría: {categoria}")
        return None
    
    # Obtener análisis
    analisis_list = session.query(Analisis).join(Ticket).filter(
        Ticket.categoria == categoria
    ).all()
    
    if not analisis_list:
        logger.warning(f"⚠️  No hay análisis para la categoría: {categoria}")
        return None
    
    # Métricas de complejidad
    complejidades = [a.complejidad_score for a in analisis_list if a.complejidad_score]
    complejidad_promedio = sum(complejidades) / len(complejidades) if complejidades else 0
    complejidad_min = min(complejidades) if complejidades else 0
    complejidad_max = max(complejidades) if complejidades else 0
    
    # Desviación estándar
    if len(complejidades) > 1:
        media = complejidad_promedio
        varianza = sum((x - media) ** 2 for x in complejidades) / len(complejidades)
        complejidad_std = varianza ** 0.5
    else:
        complejidad_std = 0
    
    # Métricas de urgencia
    urgencia_counts = Counter(a.urgencia for a in analisis_list if a.urgencia)
    
    # Métricas de sentimiento
    sentimiento_counts = Counter(a.sentimiento for a in analisis_list if a.sentimiento)
    
    # Métricas de tiempo (estimadas)
    # Asumimos tiempo promedio según urgencia
    tiempo_map = {
        'critica': 0.5,   # 30 minutos
        'alta': 1.0,      # 1 hora
        'media': 2.0,     # 2 horas
        'baja': 3.0       # 3 horas
    }
    
    tiempo_total_horas = sum(
        urgencia_counts.get(urgencia, 0) * horas 
        for urgencia, horas in tiempo_map.items()
    )
    tiempo_promedio = tiempo_total_horas / total_tickets if total_tickets > 0 else 0
    
    # Extraer top palabras clave
    todas_palabras = []
    for analisis in analisis_list:
        if analisis.palabras_clave and isinstance(analisis.palabras_clave, list):
            for item in analisis.palabras_clave:
                if isinstance(item, dict) and 'palabra' in item:
                    todas_palabras.append(item['palabra'])
    
    top_palabras = Counter(todas_palabras).most_common(10)
    top_palabras_json = json.dumps([{'palabra': p, 'count': c} for p, c in top_palabras])
    
    # Calcular métricas de viabilidad
    # Repetitividad: basada en uniformidad de palabras clave
    if len(todas_palabras) > 0:
        top_10_freq = sum(c for _, c in top_palabras)
        repetitividad = min((top_10_freq / len(todas_palabras)) * 100, 100)
    else:
        repetitividad = 0
    
    # Uniformidad: basada en desviación estándar de complejidad
    if complejidad_std > 0:
        uniformidad = max(100 - complejidad_std, 0)
    else:
        uniformidad = 100
    
    # Tasa de resolución (asumimos 85% como baseline)
    tasa_resolucion = 0.85
    
    metricas = {
        'categoria': categoria,
        'total_tickets': total_tickets,
        'tickets_procesados': len(analisis_list),
        'complejidad_promedio': complejidad_promedio,
        'complejidad_min': complejidad_min,
        'complejidad_max': complejidad_max,
        'complejidad_std': complejidad_std,
        'urgencia_critica': urgencia_counts.get('critica', 0),
        'urgencia_alta': urgencia_counts.get('alta', 0),
        'urgencia_media': urgencia_counts.get('media', 0),
        'urgencia_baja': urgencia_counts.get('baja', 0),
        'sentimiento_positivo': sentimiento_counts.get('positivo', 0),
        'sentimiento_neutral': sentimiento_counts.get('neutral', 0),
        'sentimiento_negativo': sentimiento_counts.get('negativo', 0),
        'tiempo_promedio_resolucion_horas': tiempo_promedio,
        'tiempo_total_anual_horas': tiempo_total_horas,
        'repetitividad_score': repetitividad,
        'uniformidad_score': uniformidad,
        'tasa_resolucion': tasa_resolucion,
        'top_palabras_clave': top_palabras_json
    }
    
    return metricas

def calcular_iar_todas_categorias():
    """Calcula el IAR para todas las categorías"""
    
    print("=" * 60)
    print("🎯 SEIRA 2.0 - Cálculo del IAR")
    print("=" * 60)
    print()
    
    # Inicializar base de datos
    db_manager.init_engine()
    session = db_manager.get_session()
    
    # Inicializar calculador
    calculator = IARCalculator()
    
    try:
        # Obtener todas las categorías únicas
        categorias = session.query(Ticket.categoria).distinct().all()
        categorias = [c[0] for c in categorias]
        
        total_categorias = len(categorias)
        logger.info(f"📊 Total de categorías encontradas: {total_categorias}")
        print(f"📊 Categorías a procesar: {total_categorias}\n")
        
        # Limpiar tablas anteriores
        session.query(MetricaCategoria).delete()
        session.query(Recomendacion).delete()
        session.commit()
        logger.info("🗑️  Tablas de métricas y recomendaciones limpiadas")
        
        # Obtener total global de tickets
        total_global = session.query(Ticket).count()
        
        resultados = []
        
        for i, categoria in enumerate(categorias, 1):
            print(f"\n[{i}/{total_categorias}] Procesando: {categoria}")
            print("-" * 60)
            
            # Calcular métricas base
            metricas = calcular_metricas_categoria(session, categoria)
            
            if not metricas:
                continue
            
            # Calcular scores individuales
            frecuencia_score = calculator.calcular_frecuencia_score(
                metricas['total_tickets'],
                total_global
            )
            
            complejidad_score = calculator.calcular_complejidad_score(
                metricas['complejidad_promedio']
            )
            
            impacto_score = calculator.calcular_impacto_score(
                metricas['tiempo_total_anual_horas']
            )
            
            viabilidad_score = calculator.calcular_viabilidad_score(
                metricas['repetitividad_score'],
                metricas['uniformidad_score'],
                metricas['tasa_resolucion']
            )
            
            # Calcular IAR final
            iar = calculator.calcular_iar(
                frecuencia_score,
                complejidad_score,
                impacto_score,
                viabilidad_score
            )
            
            # Determinar nivel
            nivel = calculator.determinar_nivel(iar)
            
            # Sugerir tipo de IA
            tipo_ia = calculator.sugerir_tipo_ia(
                categoria,
                metricas['urgencia_critica'],
                metricas['sentimiento_negativo']
            )
            
            # Estimar ROI
            roi_info = calculator.estimar_roi(metricas['tiempo_total_anual_horas'])
            
            # Generar recomendación
            recomendacion_texto, justificacion = calculator.generar_recomendacion(
                categoria,
                iar,
                nivel,
                roi_info,
                metricas['total_tickets']
            )
            
            # Calcular impacto ambiental
            ahorro_carbono = calculator.calcular_impacto_ambiental(
                metricas['tiempo_total_anual_horas']
            )
            
            # Guardar métrica de categoría (usando tu modelo existente)
            # Los scores del IAR van en datos_adicionales como JSON
            metrica_cat = MetricaCategoria(
                categoria=categoria,
                fecha=date.today(),
                periodo='global',
                total_tickets=metricas['total_tickets'],
                tickets_procesados=metricas['tickets_procesados'],
                tickets_pendientes=0,
                complejidad_promedio=metricas['complejidad_promedio'],
                tiempo_resolucion_promedio=metricas['tiempo_promedio_resolucion_horas'],
                urgencia_critica=metricas['urgencia_critica'],
                urgencia_alta=metricas['urgencia_alta'],
                urgencia_media=metricas['urgencia_media'],
                urgencia_baja=metricas['urgencia_baja'],
                sentimiento_positivo=metricas['sentimiento_positivo'],
                sentimiento_neutral=metricas['sentimiento_neutral'],
                sentimiento_negativo=metricas['sentimiento_negativo'],
                tasa_resolucion=metricas['tasa_resolucion'],
                satisfaccion_promedio=75.0,  # Placeholder
                datos_adicionales={
                    'frecuencia_score': frecuencia_score,
                    'complejidad_score': complejidad_score,
                    'impacto_score': impacto_score,
                    'viabilidad_score': viabilidad_score,
                    'repetitividad': metricas['repetitividad_score'],
                    'uniformidad': metricas['uniformidad_score'],
                    'complejidad_min': metricas['complejidad_min'],
                    'complejidad_max': metricas['complejidad_max'],
                    'complejidad_std': metricas['complejidad_std'],
                    'tiempo_total_anual_horas': metricas['tiempo_total_anual_horas'],
                    'top_palabras_clave': json.loads(metricas['top_palabras_clave'])
                },
                es_anomalia=0,
                score_anomalia=0.0
            )
            
            session.add(metrica_cat)
            
            # Guardar recomendación (usando tu modelo existente)
            # Determinar prioridad (1-10)
            if nivel == 'ALTAMENTE_RECOMENDADO':
                prioridad = 9 + min(int((iar - 80) / 2), 1)  # 9-10
            elif nivel == 'RECOMENDADO':
                prioridad = 6 + min(int((iar - 60) / 6), 2)  # 6-8
            elif nivel == 'EVALUAR':
                prioridad = 3 + min(int((iar - 30) / 10), 2)  # 3-5
            else:
                prioridad = 1 + min(int(iar / 15), 1)  # 1-2
            
            recomendacion = Recomendacion(
                categoria=categoria,
                iar_score=iar,
                nivel_recomendacion=nivel,
                frecuencia_score=frecuencia_score,
                complejidad_score=complejidad_score,
                impacto_productividad=impacto_score,
                viabilidad_tecnica=viabilidad_score,
                total_tickets=metricas['total_tickets'],
                tickets_resolubles=int(metricas['total_tickets'] * 0.85),
                complejidad_promedio=metricas['complejidad_promedio'],
                roi_anual_estimado=roi_info['ahorro_anual_usd'],
                roi_porcentaje=roi_info['roi_porcentaje'],
                meses_recuperacion=roi_info['meses_recuperacion'],
                costo_implementacion=calculator.costo_base,
                costo_mantenimiento_anual=roi_info['costo_mantenimiento_anual'],
                ahorro_horas_anual=metricas['tiempo_total_anual_horas'] * 0.7,
                recomendacion_texto=recomendacion_texto,
                razon_principal=justificacion,
                acciones_sugeridas=[
                    f"Implementar {tipo_ia}",
                    "Realizar análisis de viabilidad detallado",
                    "Preparar dataset de entrenamiento",
                    "Definir métricas de éxito"
                ],
                prioridad=prioridad,
                aprobada=False,
                fecha_calculo=datetime.utcnow()
            )
            
            session.add(recomendacion)
            
            # Imprimir resultado
            print(f"✅ IAR: {iar}/100")
            print(f"📊 Nivel: {nivel}")
            print(f"💡 Tipo IA: {tipo_ia}")
            print(f"💰 ROI: {roi_info['roi_porcentaje']:.1f}%")
            print(f"⏱️  Recuperación: {roi_info['meses_recuperacion']} meses")
            print(f"🌱 Ahorro CO2: {ahorro_carbono:.1f} kg/año")
            
            resultados.append({
                'categoria': categoria,
                'iar': iar,
                'nivel': nivel,
                'tickets': metricas['total_tickets']
            })
        
        # Commit todas las métricas y recomendaciones
        session.commit()
        
        print("\n" + "=" * 60)
        print("✅ CÁLCULO DE IAR COMPLETADO")
        print("=" * 60)
        print()
        
        # Resumen
        print("📊 RESUMEN POR NIVEL:")
        print("-" * 60)
        
        niveles_count = Counter(r['nivel'] for r in resultados)
        
        print(f"🟢 ALTAMENTE_RECOMENDADO: {niveles_count.get('ALTAMENTE_RECOMENDADO', 0)} categorías")
        print(f"🔵 RECOMENDADO: {niveles_count.get('RECOMENDADO', 0)} categorías")
        print(f"🟡 EVALUAR: {niveles_count.get('EVALUAR', 0)} categorías")
        print(f"🔴 NO_RECOMENDADO: {niveles_count.get('NO_RECOMENDADO', 0)} categorías")
        print()
        
        # Top 5 categorías por IAR
        top_5 = sorted(resultados, key=lambda x: x['iar'], reverse=True)[:5]
        
        print("🏆 TOP 5 CATEGORÍAS POR IAR:")
        print("-" * 60)
        for idx, resultado in enumerate(top_5, 1):
            print(f"{idx}. {resultado['categoria']}: IAR={resultado['iar']:.1f} ({resultado['nivel']}) - {resultado['tickets']:,} tickets")
        
        print("\n" + "=" * 60)
        print("💾 Datos guardados en PostgreSQL")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Error durante el cálculo: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    calcular_iar_todas_categorias()