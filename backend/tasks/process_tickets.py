"""
Tareas de Celery para procesamiento de tickets
"""
from celery_app import celery
from services.nlp_processor import NLPProcessor
from models.ticket import Ticket
from models.analisis import Analisis
from utils.database import db_manager
import logging
from datetime import datetime
import time

logger = logging.getLogger(__name__)

@celery.task(bind=True, max_retries=3)
def procesar_ticket_task(self, ticket_id):
    """
    Tarea para procesar un ticket individual
    
    Args:
        ticket_id (int): ID del ticket a procesar
        
    Returns:
        dict: Resultado del procesamiento
    """
    inicio = time.time()
    
    try:
        logger.info(f"🔄 Task iniciada para ticket #{ticket_id}")
        
        # Obtener sesión de base de datos
        session = db_manager.get_session()
        
        # Obtener ticket
        ticket = session.query(Ticket).filter_by(id=ticket_id).first()
        
        if not ticket:
            logger.error(f"❌ Ticket #{ticket_id} no encontrado")
            session.close()
            return {'error': 'Ticket no encontrado', 'ticket_id': ticket_id}
        
        # Procesar con NLP
        processor = NLPProcessor()
        resultado = processor.procesar_ticket(
            ticket.id,
            ticket.descripcion,
            ticket.categoria
        )
        
        # Calcular tiempo de procesamiento
        tiempo_procesamiento = (time.time() - inicio) * 1000  # ms
        
        # Guardar análisis en la base de datos
        analisis = Analisis(
            ticket_id=ticket.id,
            texto_limpio=resultado.get('texto_limpio', ''),
            palabras_clave=resultado.get('palabras_clave', []),
            entidades=resultado.get('entidades_ner', {}),
            tokens=resultado.get('num_tokens', 0),
            complejidad_score=resultado.get('complejidad', 0.0),
            sentimiento=resultado.get('sentimiento', {}).get('tipo', 'neutral'),
            urgencia=resultado.get('urgencia', {}).get('nivel', 'baja'),
            categoria_detectada=resultado.get('categoria', ticket.categoria),
            confianza_clasificacion=0.8,  # Placeholder
            longitud_texto=len(resultado.get('texto_limpio', '')),
            num_palabras=resultado.get('estadisticas', {}).get('num_palabras', 0),
            num_entidades=len(resultado.get('entidades_ner', {}).get('personas', [])),
            fecha_analisis=datetime.utcnow(),
            tiempo_procesamiento_ms=tiempo_procesamiento
        )
        
        session.add(analisis)
        
        # Marcar ticket como procesado
        ticket.procesado = True
        ticket.fecha_procesamiento = datetime.utcnow()
        
        session.commit()
        session.close()
        
        logger.info(f"✅ Ticket #{ticket_id} procesado ({tiempo_procesamiento:.2f}ms)")
        
        return {
            'ticket_id': ticket_id,
            'procesado': True,
            'urgencia': resultado['urgencia']['nivel'],
            'complejidad': resultado['complejidad'],
            'tiempo_ms': tiempo_procesamiento
        }
        
    except Exception as e:
        logger.error(f"❌ Error procesando ticket #{ticket_id}: {str(e)}")
        
        # Reintentar la tarea
        raise self.retry(exc=e, countdown=60)

@celery.task(bind=True)
def procesar_batch_tickets_task(self, ticket_ids):
    """
    Tarea para procesar un lote de tickets
    
    Args:
        ticket_ids (list): Lista de IDs de tickets a procesar
        
    Returns:
        dict: Resumen del procesamiento
    """
    try:
        logger.info(f"🔄 Procesando batch de {len(ticket_ids)} tickets")
        
        resultados = {
            'total': len(ticket_ids),
            'exitosos': 0,
            'fallidos': 0,
            'errores': []
        }
        
        # Procesar cada ticket individualmente
        for ticket_id in ticket_ids:
            try:
                resultado = procesar_ticket_task.apply(args=[ticket_id])
                
                if resultado.get('procesado'):
                    resultados['exitosos'] += 1
                else:
                    resultados['fallidos'] += 1
                    resultados['fallidos'] += 1
                    resultados['errores'].append({
                        'ticket_id': ticket_id,
                        'error': resultado.get('error', 'Error desconocido')
                    })
                    
            except Exception as e:
                logger.error(f"❌ Error en ticket #{ticket_id}: {str(e)}")
                resultados['fallidos'] += 1
                resultados['errores'].append({
                    'ticket_id': ticket_id,
                    'error': str(e)
                })
        
        logger.info(f"✅ Batch completado: {resultados['exitosos']}/{resultados['total']} exitosos")
        
        return resultados
        
    except Exception as e:
        logger.error(f"❌ Error en batch: {str(e)}")
        return {
            'error': str(e),
            'total': len(ticket_ids),
            'exitosos': 0,
            'fallidos': len(ticket_ids)
        }

@celery.task(bind=True)
def procesar_todos_tickets_task(self):
    """
    Tarea para procesar todos los tickets no procesados
    
    Returns:
        dict: Resumen del procesamiento total
    """
    try:
        logger.info("🔄 Iniciando procesamiento de todos los tickets no procesados")
        
        session = get_session()
        
        # Obtener todos los tickets no procesados
        tickets_pendientes = session.query(Ticket).filter_by(procesado_nlp=False).all()
        total_tickets = len(tickets_pendientes)
        
        logger.info(f"📊 Total de tickets pendientes: {total_tickets}")
        
        if total_tickets == 0:
            logger.info("✅ No hay tickets pendientes de procesar")
            session.close()
            return {'mensaje': 'No hay tickets pendientes', 'total': 0}
        
        # Dividir en batches para mejor rendimiento
        batch_size = 100
        num_batches = (total_tickets // batch_size) + (1 if total_tickets % batch_size > 0 else 0)
        
        logger.info(f"📦 Dividiendo en {num_batches} batches de {batch_size} tickets")
        
        resultados_globales = {
            'total_tickets': total_tickets,
            'batches_procesados': 0,
            'tickets_exitosos': 0,
            'tickets_fallidos': 0,
            'inicio': datetime.utcnow().isoformat()
        }
        
        # Procesar por batches
        for i in range(0, total_tickets, batch_size):
            batch = tickets_pendientes[i:i + batch_size]
            batch_ids = [ticket.id for ticket in batch]
            
            logger.info(f"🔄 Procesando batch {i//batch_size + 1}/{num_batches}")
            
            # Procesar batch
            resultado_batch = procesar_batch_tickets_task.apply(args=[batch_ids])
            
            resultados_globales['batches_procesados'] += 1
            resultados_globales['tickets_exitosos'] += resultado_batch.get('exitosos', 0)
            resultados_globales['tickets_fallidos'] += resultado_batch.get('fallidos', 0)
            
            # Actualizar progreso
            progreso = ((i + len(batch)) / total_tickets) * 100
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': i + len(batch),
                    'total': total_tickets,
                    'porcentaje': round(progreso, 2),
                    'exitosos': resultados_globales['tickets_exitosos'],
                    'fallidos': resultados_globales['tickets_fallidos']
                }
            )
        
        session.close()
        
        resultados_globales['fin'] = datetime.utcnow().isoformat()
        
        logger.info(f"✅ Procesamiento completo: {resultados_globales['tickets_exitosos']}/{total_tickets} exitosos")
        
        return resultados_globales
        
    except Exception as e:
        logger.error(f"❌ Error en procesamiento global: {str(e)}")
        return {'error': str(e)}