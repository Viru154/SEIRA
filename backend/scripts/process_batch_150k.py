"""
Script para procesar los 150K tickets en batch con Celery
"""
import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.database import db_manager
from models.ticket import Ticket
from tasks.process_tickets import procesar_ticket_task
from celery_app import celery
from tqdm import tqdm
from datetime import datetime
import logging
import time

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('process_batch.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def obtener_tickets_pendientes():
    """Obtiene todos los tickets que no han sido procesados"""
    logger.info("🔍 Consultando tickets pendientes...")
    
    session = db_manager.get_session()
    
    try:
        tickets = session.query(Ticket).filter_by(procesado=False).all()
        total = len(tickets)
        
        logger.info(f"📊 Tickets pendientes: {total}")
        
        return tickets, total
        
    except Exception as e:
        logger.error(f"❌ Error consultando tickets: {str(e)}")
        raise
    finally:
        session.close()

def procesar_batch_sincrono(batch_size=1000):
    """
    Procesa tickets en batches de forma síncrona
    Útil para debug o cuando Celery no está disponible
    """
    from services.nlp_processor import NLPProcessor
    from models.analisis import Analisis
    
    logger.info("🔄 Iniciando procesamiento SÍNCRONO")
    
    session = db_manager.get_session()
    processor = NLPProcessor()
    
    try:
        tickets_pendientes = session.query(Ticket).filter_by(procesado=False).all()
        total = len(tickets_pendientes)
        
        logger.info(f"📊 Total a procesar: {total} tickets")
        
        if total == 0:
            logger.info("✅ No hay tickets pendientes")
            return
        
        # Barra de progreso
        with tqdm(total=total, desc="Procesando tickets", unit="ticket") as pbar:
            
            for i in range(0, total, batch_size):
                batch = tickets_pendientes[i:i + batch_size]
                
                for ticket in batch:
                    try:
                        inicio = time.time()
                        
                        # Procesar ticket
                        resultado = processor.procesar_ticket(
                            ticket.id,
                            ticket.descripcion,
                            ticket.categoria
                        )
                        
                        tiempo_procesamiento = (time.time() - inicio) * 1000
                        
                        # Guardar análisis
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
                            confianza_clasificacion=0.8,
                            longitud_texto=len(resultado.get('texto_limpio', '')),
                            num_palabras=resultado.get('estadisticas', {}).get('num_palabras', 0),
                            num_entidades=len(resultado.get('entidades_ner', {}).get('personas', [])),
                            fecha_analisis=datetime.utcnow(),
                            tiempo_procesamiento_ms=tiempo_procesamiento
                        )
                        
                        session.add(analisis)
                        
                        # Marcar como procesado
                        ticket.procesado = True
                        ticket.fecha_procesamiento = datetime.utcnow()
                        
                        pbar.update(1)
                        
                    except Exception as e:
                        logger.error(f"❌ Error en ticket #{ticket.id}: {str(e)}")
                        pbar.update(1)
                        continue
                
                # Commit cada batch
                session.commit()
                logger.info(f"✅ Batch {i//batch_size + 1} guardado ({len(batch)} tickets)")
        
        logger.info("✅ Procesamiento síncrono completado")
        
    except Exception as e:
        logger.error(f"❌ Error en procesamiento: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()

def procesar_batch_celery(batch_size=100):
    """
    Procesa tickets usando Celery (asíncrono)
    Más eficiente para grandes volúmenes
    """
    logger.info("🔄 Iniciando procesamiento ASÍNCRONO con Celery")
    
    tickets, total = obtener_tickets_pendientes()
    
    if total == 0:
        logger.info("✅ No hay tickets pendientes")
        return
    
    logger.info(f"📊 Total a procesar: {total} tickets")
    logger.info(f"📦 Tamaño de batch: {batch_size} tickets")
    
    num_batches = (total // batch_size) + (1 if total % batch_size > 0 else 0)
    logger.info(f"📦 Número de batches: {num_batches}")
    
    # Enviar tareas a Celery
    task_ids = []
    
    with tqdm(total=total, desc="Enviando tareas a Celery", unit="ticket") as pbar:
        
        for i in range(0, total, batch_size):
            batch = tickets[i:i + batch_size]
            
            for ticket in batch:
                # Enviar tarea a Celery de forma asíncrona
                task = procesar_ticket_task.delay(ticket.id)
                task_ids.append(task.id)
                pbar.update(1)
    
    logger.info(f"✅ {len(task_ids)} tareas enviadas a Celery")
    logger.info("⏳ Esperando a que los workers procesen las tareas...")
    logger.info("💡 Puedes monitorear el progreso en los logs de Celery")
    logger.info("💡 O usar Flower: http://localhost:5555")
    
    # Opcional: Esperar a que todas las tareas terminen
    print("\n¿Deseas esperar a que todas las tareas terminen? (y/n): ", end="")
    respuesta = input().strip().lower()
    
    if respuesta == 'y':
        logger.info("⏳ Monitoreando progreso de tareas...")
        
        from celery.result import AsyncResult
        
        completadas = 0
        fallidas = 0
        
        with tqdm(total=len(task_ids), desc="Tareas completadas", unit="tarea") as pbar:
            
            while completadas + fallidas < len(task_ids):
                time.sleep(5)  # Chequear cada 5 segundos
                
                temp_completadas = 0
                temp_fallidas = 0
                
                for task_id in task_ids:
                    result = AsyncResult(task_id, app=celery)
                    
                    if result.ready():
                        if result.successful():
                            temp_completadas += 1
                        else:
                            temp_fallidas += 1
                
                nuevas_completadas = temp_completadas - completadas
                nuevas_fallidas = temp_fallidas - fallidas
                
                if nuevas_completadas > 0 or nuevas_fallidas > 0:
                    completadas = temp_completadas
                    fallidas = temp_fallidas
                    pbar.update(nuevas_completadas + nuevas_fallidas)
                    pbar.set_postfix({
                        'exitosas': completadas,
                        'fallidas': fallidas
                    })
        
        logger.info(f"✅ Procesamiento completado")
        logger.info(f"✅ Exitosas: {completadas}")
        logger.info(f"❌ Fallidas: {fallidas}")
    else:
        logger.info("✅ Tareas enviadas. El procesamiento continúa en background.")

def verificar_progreso():
    """Verifica el progreso del procesamiento"""
    logger.info("🔍 Verificando progreso...")
    
    session = db_manager.get_session()
    
    try:
        total = session.query(Ticket).count()
        procesados = session.query(Ticket).filter_by(procesado=True).count()
        pendientes = total - procesados
        
        porcentaje = (procesados / total * 100) if total > 0 else 0
        
        logger.info(f"📊 Progreso del procesamiento:")
        logger.info(f"   Total de tickets: {total}")
        logger.info(f"   ✅ Procesados: {procesados} ({porcentaje:.2f}%)")
        logger.info(f"   ⏳ Pendientes: {pendientes}")
        
        return {
            'total': total,
            'procesados': procesados,
            'pendientes': pendientes,
            'porcentaje': porcentaje
        }
        
    finally:
        session.close()

def main():
    """Función principal"""
    print("=" * 60)
    print("🎮 SEIRA 2.0 - Procesamiento Batch de Tickets")
    print("=" * 60)
    print()
    
    # Inicializar base de datos
    try:
        db_manager.init_engine()
    except Exception as e:
        logger.error(f"❌ Error conectando a la base de datos: {str(e)}")
        return
    
    # Verificar progreso actual
    verificar_progreso()
    print()
    
    # Menú de opciones
    print("Selecciona el modo de procesamiento:")
    print("1. Procesamiento SÍNCRONO (sin Celery, más lento pero simple)")
    print("2. Procesamiento ASÍNCRONO (con Celery, más rápido)")
    print("3. Solo verificar progreso")
    print("4. Salir")
    print()
    
    opcion = input("Opción (1-4): ").strip()
    print()
    
    if opcion == '1':
        batch_size = input("Tamaño de batch (default: 1000): ").strip()
        batch_size = int(batch_size) if batch_size else 1000
        
        inicio = time.time()
        procesar_batch_sincrono(batch_size=batch_size)
        fin = time.time()
        
        logger.info(f"⏱️  Tiempo total: {(fin - inicio) / 60:.2f} minutos")
        
    elif opcion == '2':
        batch_size = input("Tamaño de batch (default: 100): ").strip()
        batch_size = int(batch_size) if batch_size else 100
        
        procesar_batch_celery(batch_size=batch_size)
        
    elif opcion == '3':
        verificar_progreso()
        
    elif opcion == '4':
        logger.info("👋 Saliendo...")
        return
    else:
        logger.error("❌ Opción inválida")
        return
    
    print()
    print("=" * 60)
    print("✅ Script finalizado")
    print("=" * 60)

if __name__ == "__main__":
    main()