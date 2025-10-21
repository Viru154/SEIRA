"""
Configuración de Celery para procesamiento asíncrono
"""
from celery import Celery
from config import get_config
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Obtener configuración
config = get_config()

# Crear instancia de Celery
celery = Celery(
    'seira',
    broker=config.CELERY_BROKER_URL,
    backend=config.CELERY_RESULT_BACKEND
)

# Configuración optimizada para procesamiento masivo
celery.conf.update(
    # Workers
    worker_concurrency=config.MAX_WORKERS,
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,  # Reiniciar worker cada 1000 tareas para liberar memoria
    
    # Tasks
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Guatemala',
    enable_utc=True,
    
    # Resultados
    result_expires=3600,  # Los resultados expiran en 1 hora
    
    # Retry y confiabilidad
    task_acks_late=True,  # Confirmar tarea solo después de completarla
    task_reject_on_worker_lost=True,
    
    # Routing - diferentes colas para diferentes tipos de tareas
    task_routes={
        'backend.tasks.process_tickets.*': {'queue': 'nlp'},
        'backend.tasks.generate_reports.*': {'queue': 'reports'},
    },
    
    # Límites de tiempo
    task_time_limit=1800,  # 30 minutos máximo por tarea
    task_soft_time_limit=1500,  # Warning a los 25 minutos
    
    # Configuración de retry
    task_default_retry_delay=60,  # Reintentar después de 1 minuto
    task_max_retries=3,
)

# Auto-discover tasks en el módulo backend.tasks
celery.autodiscover_tasks(['backend.tasks'])

logger.info("✅ Celery configurado correctamente")
logger.info(f"📡 Broker: {config.CELERY_BROKER_URL}")
logger.info(f"💾 Backend: {config.CELERY_RESULT_BACKEND}")
logger.info(f"👷 Workers concurrentes: {config.MAX_WORKERS}")