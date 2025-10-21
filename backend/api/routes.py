"""
SEIRA 2.0 - API REST Routes
Endpoints para consultar recomendaciones, métricas y análisis
"""

from flask import Blueprint, jsonify, request
from sqlalchemy import desc, func
from models.recomendacion import Recomendacion
from models.metrica import MetricaCategoria
from models.ticket import Ticket
from models.analisis import Analisis
from utils.database import get_db_session
from models.metrica import MetricaCategoria  
from datetime import datetime, timedelta
import json

api = Blueprint('api', __name__, url_prefix='/api')

# ========== RECOMENDACIONES ==========

@api.route('/recomendaciones', methods=['GET'])
def get_recomendaciones():
    """Obtiene todas las recomendaciones ordenadas por IAR"""
    session = get_db_session()
    try:
        recomendaciones = session.query(Recomendacion)\
            .order_by(desc(Recomendacion.iar_score))\
            .all()
        
        result = [{
            'id': r.id,
            'categoria': r.categoria,
            'iar_score': float(r.iar_score),
            'nivel_recomendacion': r.nivel_recomendacion,
            'total_tickets': r.total_tickets,
            'roi_anual_estimado': float(r.roi_anual_estimado),
            'roi_porcentaje': float(r.roi_porcentaje),
            'meses_recuperacion': float(r.meses_recuperacion),
            'costo_implementacion': float(r.costo_implementacion),
            'recomendacion_texto': r.recomendacion_texto,
            'razon_principal': r.razon_principal,
            'acciones_sugeridas': r.acciones_sugeridas,
            'prioridad': r.prioridad
        } for r in recomendaciones]
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@api.route('/recomendaciones/top/<int:n>', methods=['GET'])
def get_top_recomendaciones(n):
    """Obtiene las top N recomendaciones por IAR"""
    session = get_db_session()
    try:
        recomendaciones = session.query(Recomendacion)\
            .order_by(desc(Recomendacion.iar_score))\
            .limit(n)\
            .all()
        
        result = [{
            'id': r.id,
            'categoria': r.categoria,
            'iar_score': float(r.iar_score),
            'nivel_recomendacion': r.nivel_recomendacion,
            'total_tickets': r.total_tickets,
            'roi_anual_estimado': float(r.roi_anual_estimado),
            'roi_porcentaje': float(r.roi_porcentaje)
        } for r in recomendaciones]
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@api.route('/recomendaciones/<string:categoria>', methods=['GET'])
def get_recomendacion_categoria(categoria):
    """Obtiene recomendación específica por categoría"""
    session = get_db_session()
    try:
        recomendacion = session.query(Recomendacion)\
            .filter(Recomendacion.categoria == categoria)\
            .first()
        
        if not recomendacion:
            return jsonify({'error': 'Categoría no encontrada'}), 404
        
        result = {
            'id': recomendacion.id,
            'categoria': recomendacion.categoria,
            'iar_score': float(recomendacion.iar_score),
            'nivel_recomendacion': recomendacion.nivel_recomendacion,
            'frecuencia_score': float(recomendacion.frecuencia_score),
            'complejidad_score': float(recomendacion.complejidad_score),
            'impacto_productividad': float(recomendacion.impacto_productividad),
            'viabilidad_tecnica': float(recomendacion.viabilidad_tecnica),
            'total_tickets': recomendacion.total_tickets,
            'roi_anual_estimado': float(recomendacion.roi_anual_estimado),
            'roi_porcentaje': float(recomendacion.roi_porcentaje),
            'meses_recuperacion': float(recomendacion.meses_recuperacion),
            'costo_implementacion': float(recomendacion.costo_implementacion),
            'recomendacion_texto': recomendacion.recomendacion_texto,
            'razon_principal': recomendacion.razon_principal,
            'acciones_sugeridas': recomendacion.acciones_sugeridas,
            'prioridad': recomendacion.prioridad
        }
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


# ========== MÉTRICAS ==========

@api.route('/metricas', methods=['GET'])
def get_metricas():
    """Obtiene todas las métricas por categoría"""
    session = get_db_session()
    try:
        metricas = session.query(MetricaCategoria).all()
        
        result = [{
            'id': m.id,
            'categoria': m.categoria,
            'total_tickets': m.total_tickets,
            'complejidad_promedio': float(m.complejidad_promedio),
            'urgencia_critica': m.urgencia_critica,
            'urgencia_alta': m.urgencia_alta,
            'urgencia_media': m.urgencia_media,
            'urgencia_baja': m.urgencia_baja,
            'sentimiento_positivo': m.sentimiento_positivo,
            'sentimiento_neutral': m.sentimiento_neutral,
            'sentimiento_negativo': m.sentimiento_negativo,
            'tasa_resolucion': float(m.tasa_resolucion) if m.tasa_resolucion else 0
        } for m in metricas]
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@api.route('/metricas/<string:categoria>', methods=['GET'])
def get_metrica_categoria(categoria):
    """Obtiene métrica específica por categoría"""
    session = get_db_session()
    try:
        metrica = session.query(MetricaCategoria)\
            .filter(MetricaCategoria.categoria == categoria)\
            .first()
        
        if not metrica:
            return jsonify({'error': 'Categoría no encontrada'}), 404
        
        result = {
            'id': metrica.id,
            'categoria': metrica.categoria,
            'total_tickets': metrica.total_tickets,
            'complejidad_promedio': float(metrica.complejidad_promedio),
            'urgencia_critica': metrica.urgencia_critica,
            'urgencia_alta': metrica.urgencia_alta,
            'urgencia_media': metrica.urgencia_media,
            'urgencia_baja': metrica.urgencia_baja,
            'sentimiento_positivo': metrica.sentimiento_positivo,
            'sentimiento_neutral': metrica.sentimiento_neutral,
            'sentimiento_negativo': metrica.sentimiento_negativo,
            'tasa_resolucion': float(metrica.tasa_resolucion) if metrica.tasa_resolucion else 0
        }
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@api.route('/metricas/<string:categoria>/detalle', methods=['GET'])
def get_metrica_detalle(categoria):
    """Obtiene detalle completo de una categoría (métrica + recomendación)"""
    session = get_db_session()
    try:
        metrica = session.query(MetricaCategoria)\
            .filter(MetricaCategoria.categoria == categoria)\
            .first()
        
        recomendacion = session.query(Recomendacion)\
            .filter(Recomendacion.categoria == categoria)\
            .first()
        
        if not metrica or not recomendacion:
            return jsonify({'error': 'Categoría no encontrada'}), 404
        
        result = {
            'categoria': categoria,
            'metrica': {
                'total_tickets': metrica.total_tickets,
                'complejidad_promedio': float(metrica.complejidad_promedio),
                'urgencia': {
                    'critica': metrica.urgencia_critica,
                    'alta': metrica.urgencia_alta,
                    'media': metrica.urgencia_media,
                    'baja': metrica.urgencia_baja
                },
                'sentimiento': {
                    'positivo': metrica.sentimiento_positivo,
                    'neutral': metrica.sentimiento_neutral,
                    'negativo': metrica.sentimiento_negativo
                },
                'tasa_resolucion': float(metrica.tasa_resolucion) if metrica.tasa_resolucion else 0
            },
            'recomendacion': {
                'iar_score': float(recomendacion.iar_score),
                'nivel': recomendacion.nivel_recomendacion,
                'roi_anual': float(recomendacion.roi_anual_estimado),
                'roi_porcentaje': float(recomendacion.roi_porcentaje),
                'meses_recuperacion': float(recomendacion.meses_recuperacion),
                'costo_implementacion': float(recomendacion.costo_implementacion),
                'texto': recomendacion.recomendacion_texto,
                'acciones': recomendacion.acciones_sugeridas
            }
        }
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


# ========== DASHBOARD ==========

@api.route('/dashboard/resumen', methods=['GET'])
def get_dashboard_resumen():
    """KPIs principales del dashboard"""
    session = get_db_session()
    try:
        # Total de tickets
        total_tickets = session.query(func.count(Ticket.id)).scalar()
        
        # Total de categorías
        total_categorias = session.query(func.count(Recomendacion.id)).scalar()
        
        # Promedio IAR
        avg_iar = session.query(func.avg(Recomendacion.iar_score)).scalar()
        
        # Suma de ROI anual
        total_roi = session.query(func.sum(Recomendacion.roi_anual_estimado)).scalar()
        
        # Categorías altamente recomendadas
        altamente_recomendadas = session.query(func.count(Recomendacion.id))\
            .filter(Recomendacion.nivel_recomendacion == 'ALTAMENTE_RECOMENDADO')\
            .scalar()
        
        # ROI promedio
        avg_roi_porcentaje = session.query(func.avg(Recomendacion.roi_porcentaje)).scalar()
        
        result = {
            'total_tickets': total_tickets,
            'total_categorias': total_categorias,
            'promedio_iar': float(avg_iar) if avg_iar else 0,
            'ahorro_total_anual': float(total_roi) if total_roi else 0,
            'categorias_altamente_recomendadas': altamente_recomendadas,
            'roi_promedio_porcentaje': float(avg_roi_porcentaje) if avg_roi_porcentaje else 0
        }
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@api.route('/dashboard/estadisticas', methods=['GET'])
def get_estadisticas():
    """Estadísticas generales del sistema"""
    session = get_db_session()
    try:
        # Tickets procesados
        tickets_procesados = session.query(func.count(Ticket.id))\
            .filter(Ticket.procesado == True)\
            .scalar()
        
        # Análisis completados
        total_analisis = session.query(func.count(Analisis.id)).scalar()
        
        # Complejidad promedio
        avg_complejidad = session.query(func.avg(Analisis.complejidad_score)).scalar()
        
        # Distribución de sentimiento
        sentimiento_stats = session.query(
            Analisis.sentimiento,
            func.count(Analisis.id)
        ).group_by(Analisis.sentimiento).all()
        
        sentimiento_dist = {s[0]: s[1] for s in sentimiento_stats}
        
        # Distribución de urgencia
        urgencia_stats = session.query(
            Analisis.urgencia,
            func.count(Analisis.id)
        ).group_by(Analisis.urgencia).all()
        
        urgencia_dist = {u[0]: u[1] for u in urgencia_stats}
        
        result = {
            'tickets_procesados': tickets_procesados,
            'total_analisis': total_analisis,
            'complejidad_promedio': float(avg_complejidad) if avg_complejidad else 0,
            'distribucion_sentimiento': sentimiento_dist,
            'distribucion_urgencia': urgencia_dist
        }
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@api.route('/dashboard/categorias', methods=['GET'])
def get_categorias_list():
    """Lista de todas las categorías con IAR"""
    session = get_db_session()
    try:
        categorias = session.query(Recomendacion)\
            .order_by(desc(Recomendacion.iar_score))\
            .all()
        
        result = [{
            'categoria': c.categoria,
            'iar_score': float(c.iar_score),
            'nivel': c.nivel_recomendacion,
            'total_tickets': c.total_tickets
        } for c in categorias]
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


# ========== ANÁLISIS ==========

@api.route('/analisis/distribucion', methods=['GET'])
def get_distribucion_analisis():
    """Distribución de análisis por categoría"""
    session = get_db_session()
    try:
        distribucion = session.query(
            Ticket.categoria,
            func.count(Analisis.id).label('total')
        ).join(Analisis, Ticket.id == Analisis.ticket_id)\
         .group_by(Ticket.categoria)\
         .all()
        
        result = [{
            'categoria': d[0],
            'total': d[1]
        } for d in distribucion]
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@api.route('/analisis/sentimiento', methods=['GET'])
def get_analisis_sentimiento():
    """Análisis de sentimiento por categoría"""
    session = get_db_session()
    try:
        sentimiento = session.query(
            Ticket.categoria,
            Analisis.sentimiento,
            func.count(Analisis.id).label('total')
        ).join(Analisis, Ticket.id == Analisis.ticket_id)\
         .group_by(Ticket.categoria, Analisis.sentimiento)\
         .all()
        
        # Organizar por categoría
        result = {}
        for cat, sent, total in sentimiento:
            if cat not in result:
                result[cat] = {}
            result[cat][sent] = total
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@api.route('/analisis/urgencia', methods=['GET'])
def get_distribucion_urgencia():
    """Distribución de urgencia por categoría"""
    session = get_db_session()
    try:
        urgencia = session.query(
            Ticket.categoria,
            Analisis.urgencia,
            func.count(Analisis.id).label('total')
        ).join(Analisis, Ticket.id == Analisis.ticket_id)\
         .group_by(Ticket.categoria, Analisis.urgencia)\
         .all()
        
        # Organizar por categoría
        result = {}
        for cat, urg, total in urgencia:
            if cat not in result:
                result[cat] = {}
            result[cat][urg] = total
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


# ========== TICKETS ==========

@api.route('/tickets', methods=['GET'])
def get_tickets():
    """Obtiene tickets con paginación y filtros"""
    session = get_db_session()
    try:
        # Parámetros de query
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        categoria = request.args.get('categoria', None)
        estado = request.args.get('estado', None)
        
        # Query base
        query = session.query(Ticket)
        
        # Aplicar filtros
        if categoria:
            query = query.filter(Ticket.categoria == categoria)
        if estado:
            query = query.filter(Ticket.estado == estado)
        
        # Paginación
        total = query.count()
        tickets = query.order_by(desc(Ticket.fecha_creacion))\
                      .limit(per_page)\
                      .offset((page - 1) * per_page)\
                      .all()
        
        result = {
            'tickets': [{
                'id': t.id,
                'ticket_id': t.ticket_id,
                'titulo': t.titulo,
                'categoria': t.categoria,
                'estado': t.estado,
                'prioridad': t.prioridad,
                'fecha_creacion': t.fecha_creacion.isoformat()
            } for t in tickets],
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@api.route('/tickets/<int:ticket_id>', methods=['GET'])
def get_ticket_detalle(ticket_id):
    """Obtiene detalles de un ticket específico"""
    session = get_db_session()
    try:
        ticket = session.query(Ticket).filter(Ticket.id == ticket_id).first()
        
        if not ticket:
            return jsonify({'error': 'Ticket no encontrado'}), 404
        
        result = {
            'id': ticket.id,
            'ticket_id': ticket.ticket_id,
            'titulo': ticket.titulo,
            'descripcion': ticket.descripcion,
            'categoria': ticket.categoria,
            'estado': ticket.estado,
            'prioridad': ticket.prioridad,
            'fecha_creacion': ticket.fecha_creacion.isoformat(),
            'cliente_id': ticket.cliente_id,
            'producto_relacionado': ticket.producto_relacionado,
            'orden_id': ticket.orden_id
        }
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@api.route('/tickets/<int:ticket_id>/analisis', methods=['GET'])
def get_ticket_analisis(ticket_id):
    """Obtiene el análisis de un ticket específico"""
    session = get_db_session()
    try:
        analisis = session.query(Analisis)\
            .filter(Analisis.ticket_id == ticket_id)\
            .first()
        
        if not analisis:
            return jsonify({'error': 'Análisis no encontrado'}), 404
        
        result = {
            'id': analisis.id,
            'ticket_id': analisis.ticket_id,
            'texto_limpio': analisis.texto_limpio,
            'palabras_clave': analisis.palabras_clave,
            'entidades': analisis.entidades,
            'complejidad_score': float(analisis.complejidad_score),
            'sentimiento': analisis.sentimiento,
            'urgencia': analisis.urgencia,
            'categoria_detectada': analisis.categoria_detectada,
            'confianza_clasificacion': float(analisis.confianza_clasificacion),
            'fecha_analisis': analisis.fecha_analisis.isoformat()
        }
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


# Health check
@api.route('/health', methods=['GET'])
def health_check():
    """Verifica el estado de la API"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0'
    }), 200