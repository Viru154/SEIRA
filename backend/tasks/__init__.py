"""
Paquete de tareas de Celery
"""
from tasks.process_tickets import (
    procesar_ticket_task,
    procesar_batch_tickets_task,
    procesar_todos_tickets_task
)

__all__ = [
    'procesar_ticket_task',
    'procesar_batch_tickets_task',
    'procesar_todos_tickets_task'
]