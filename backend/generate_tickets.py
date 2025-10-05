"""
SEIRA - Generador de Tickets Sintéticos
Genera 650 tickets realistas para pruebas del sistema
"""

import random
from datetime import datetime, timedelta
from faker import Faker
import csv
import json

# Inicializar Faker en español
fake = Faker('es_ES')
Faker.seed(42)  # Para reproducibilidad
random.seed(42)

# Configuración
NUM_TICKETS = 150
FECHA_INICIO = datetime.now() - timedelta(days=365)
FECHA_FIN = datetime.now()

# Categorías y sus porcentajes
CATEGORIAS = {
    'error_solicitud': {
        'peso': 20,
        'titulos': [
            'Error al procesar solicitud de {}',
            'Fallo en sistema de {}',
            'Bug en módulo de {}',
            'Error 500 en proceso de {}',
            'Problema técnico con {}'
        ],
        'problemas': [
            'registro de usuarios', 'facturación', 'inventario', 
            'reportes', 'exportación de datos', 'carga de archivos',
            'validación de formularios', 'integración API'
        ],
        'descripciones': [
            'El sistema arroja error {} al intentar procesar {}. Los usuarios no pueden completar la operación. Se requiere revisión urgente del código.',
            'Se detectó un bug crítico en {}. El error {} aparece intermitentemente. Afecta a aproximadamente {} usuarios.',
            'Fallo técnico en el módulo de {}. Error: {}. Se reproduce en ambiente de producción. Prioridad alta.',
            'El proceso de {} falla con código de error {}. Los logs muestran {}. Necesitamos solución inmediata.'
        ],
        'errores': ['500', '404', '403', 'timeout', 'null reference', 'database connection'],
        'prioridades': ['Alta', 'Alta', 'Crítica', 'Alta', 'Media']
    },
    'cotizacion': {
        'peso': 15,
        'titulos': [
            'Solicitud de cotización para {}',
            'Consulta de precio de {}',
            'Presupuesto requerido para {}',
            'Información de costos de {}'
        ],
        'items': [
            'licencias de software', 'servicio de mantenimiento', 
            'módulo adicional', 'capacitación', 'actualización de sistema',
            'soporte técnico premium', 'implementación de funcionalidad',
            'consultoría especializada'
        ],
        'descripciones': [
            'Buenos días, necesito una cotización para {}. La empresa requiere {} unidades. Por favor incluir costos de implementación.',
            'Solicito presupuesto detallado de {}. Necesitamos para {} personas. ¿Incluye soporte técnico?',
            'Requerimos información sobre precios de {}. El proyecto necesita comenzar en {}. Favor enviar cotización formal.',
            '¿Cuál es el costo de {}? Necesitamos {} licencias. ¿Hay descuento por volumen?'
        ],
        'prioridades': ['Media', 'Media', 'Baja', 'Media', 'Baja']
    },
    'ayuda_tecnica': {
        'peso': 25,
        'titulos': [
            '¿Cómo {} en el sistema?',
            'Ayuda con {}',
            'No puedo {}',
            'Problema al intentar {}',
            'Consulta sobre {}'
        ],
        'acciones': [
            'exportar reportes', 'configurar permisos', 'crear usuarios',
            'generar facturas', 'modificar datos', 'acceder al módulo',
            'restablecer contraseña', 'cambiar configuración',
            'integrar con otro sistema', 'personalizar dashboard'
        ],
        'descripciones': [
            'Necesito ayuda para {}. He intentado siguiendo el manual pero no funciona. ¿Pueden orientarme?',
            'No logro {}. ¿Hay algún tutorial o video explicativo? Es urgente para mi trabajo.',
            'Tengo problemas al intentar {}. El sistema no responde como esperaba. ¿Qué debo hacer?',
            '¿Cómo se hace para {}? No encuentro la opción en el menú. Gracias por la ayuda.'
        ],
        'prioridades': ['Media', 'Baja', 'Media', 'Alta', 'Baja']
    },
    'metodo_pago': {
        'peso': 15,
        'titulos': [
            'Error en procesamiento de pago',
            'Problema con tarjeta de crédito',
            'Pago rechazado - {}',
            'No puedo completar el pago',
            'Transacción fallida'
        ],
        'metodos': ['tarjeta Visa', 'tarjeta Mastercard', 'PayPal', 'transferencia bancaria', 'pago en línea'],
        'descripciones': [
            'Intenté realizar el pago con {} pero fue rechazado. El mensaje dice "{}". Mi tarjeta está activa y tiene fondos.',
            'El sistema no acepta mi {}. Ya intenté {} veces. ¿Hay problemas con la pasarela de pagos?',
            'Error al procesar pago: {}. Necesito completar la transacción urgentemente. ¿Pueden revisar?',
            'Mi pago con {} fue rechazado. Código de error: {}. Por favor ayuda para completar la compra.'
        ],
        'errores_pago': ['transacción denegada', 'fondos insuficientes', 'error del banco', 'tiempo agotado', 'datos incorrectos'],
        'prioridades': ['Alta', 'Alta', 'Crítica', 'Alta', 'Media']
    },
    'proceso_manual': {
        'peso': 15,
        'titulos': [
            'Automatizar proceso de {}',
            'Tarea repetitiva: {}',
            'Mejora en proceso de {}',
            'Optimización de {}'
        ],
        'procesos': [
            'generación de reportes', 'envío de correos', 'actualización de inventario',
            'carga de datos', 'respaldo de información', 'validación de datos',
            'asignación de tickets', 'clasificación de solicitudes',
            'notificaciones a usuarios', 'consolidación de información'
        ],
        'descripciones': [
            'Todos los días debo {} manualmente. Toma aproximadamente {} horas. ¿Se puede automatizar?',
            'El proceso de {} es muy repetitivo. Lo hago {} veces por semana. Sugiero implementar automatización.',
            'Pierdo mucho tiempo en {}. Son tareas idénticas que se repiten {}. ¿Hay forma de optimizar esto?',
            'Necesitamos automatizar el {}. El equipo invierte {} horas semanales en esto. Es ineficiente.'
        ],
        'frecuencias': ['5', '10', '15', '20', '3'],
        'prioridades': ['Media', 'Baja', 'Media', 'Baja', 'Media']
    },
    'consulta_general': {
        'peso': 10,
        'titulos': [
            'Consulta sobre {}',
            'Información general de {}',
            'Pregunta acerca de {}',
            '¿Información sobre {}?'
        ],
        'temas': [
            'funcionalidades del sistema', 'planes disponibles', 'horarios de soporte',
            'requisitos técnicos', 'compatibilidad', 'actualizaciones',
            'políticas de uso', 'términos de servicio', 'capacitación disponible'
        ],
        'descripciones': [
            'Quisiera información sobre {}. ¿Dónde puedo encontrar documentación detallada?',
            'Tengo una consulta general sobre {}. ¿Pueden orientarme o enviarme material informativo?',
            'Necesito saber más acerca de {}. ¿Hay algún contacto específico para esto?',
            '¿Me pueden proporcionar información sobre {}? Gracias de antemano.'
        ],
        'prioridades': ['Baja', 'Baja', 'Media', 'Baja', 'Baja']
    }
}

def generar_fecha_random():
    """Genera una fecha aleatoria en el último año"""
    delta = FECHA_FIN - FECHA_INICIO
    random_days = random.randint(0, delta.days)
    fecha_creacion = FECHA_INICIO + timedelta(days=random_days)
    
    # Fecha de resolución: entre 2 horas y 72 horas después
    horas_resolucion = random.uniform(2, 72)
    fecha_resolucion = fecha_creacion + timedelta(hours=horas_resolucion)
    
    return fecha_creacion, fecha_resolucion, horas_resolucion

def generar_ticket(categoria, datos_cat):
    """Genera un ticket individual"""
    titulo_template = random.choice(datos_cat['titulos'])
    
    # Generar contenido según categoría
    if categoria == 'error_solicitud':
        problema = random.choice(datos_cat['problemas'])
        titulo = titulo_template.format(problema)
        desc_template = random.choice(datos_cat['descripciones'])
        error = random.choice(datos_cat['errores'])
        descripcion = desc_template.format(problema, error, random.randint(5, 50))
        
    elif categoria == 'cotizacion':
        item = random.choice(datos_cat['items'])
        titulo = titulo_template.format(item)
        desc_template = random.choice(datos_cat['descripciones'])
        descripcion = desc_template.format(item, random.randint(5, 50), random.choice(['2 semanas', '1 mes', 'próximo trimestre']))
        
    elif categoria == 'ayuda_tecnica':
        accion = random.choice(datos_cat['acciones'])
        titulo = titulo_template.format(accion)
        desc_template = random.choice(datos_cat['descripciones'])
        descripcion = desc_template.format(accion)
        
    elif categoria == 'metodo_pago':
        if '{}' in titulo_template:
            metodo = random.choice(datos_cat['metodos'])
            titulo = titulo_template.format(metodo)
        else:
            titulo = titulo_template
        desc_template = random.choice(datos_cat['descripciones'])
        metodo = random.choice(datos_cat['metodos'])
        error_pago = random.choice(datos_cat['errores_pago'])
        descripcion = desc_template.format(metodo, error_pago, random.randint(2, 5))
        
    elif categoria == 'proceso_manual':
        proceso = random.choice(datos_cat['procesos'])
        titulo = titulo_template.format(proceso)
        desc_template = random.choice(datos_cat['descripciones'])
        frecuencia = random.choice(datos_cat['frecuencias'])
        descripcion = desc_template.format(proceso, frecuencia, random.choice(['diariamente', 'semanalmente', 'mensualmente']))
        
    else:  # consulta_general
        tema = random.choice(datos_cat['temas'])
        titulo = titulo_template.format(tema)
        desc_template = random.choice(datos_cat['descripciones'])
        descripcion = desc_template.format(tema)
    
    prioridad = random.choice(datos_cat['prioridades'])
    fecha_creacion, fecha_resolucion, horas = generar_fecha_random()
    
    # 90% resueltos, 10% pendientes
    estado = 'Resuelto' if random.random() < 0.9 else 'Pendiente'
    
    return {
        'id': None,  # Se asignará después
        'titulo': titulo,
        'descripcion': descripcion,
        'categoria': categoria,
        'prioridad': prioridad,
        'fecha_creacion': fecha_creacion.strftime('%Y-%m-%d %H:%M:%S'),
        'fecha_resolucion': fecha_resolucion.strftime('%Y-%m-%d %H:%M:%S') if estado == 'Resuelto' else '',
        'tiempo_resolucion_horas': round(horas, 2) if estado == 'Resuelto' else 0,
        'estado': estado
    }

def generar_tickets():
    """Genera todos los tickets según distribución de categorías"""
    tickets = []
    
    # Calcular cantidad por categoría
    for categoria, datos in CATEGORIAS.items():
        cantidad = int(NUM_TICKETS * datos['peso'] / 100)
        print(f"Generando {cantidad} tickets de categoría: {categoria}")
        
        for _ in range(cantidad):
            ticket = generar_ticket(categoria, datos)
            tickets.append(ticket)
    
    # Asignar IDs
    for i, ticket in enumerate(tickets, 1):
        ticket['id'] = i
    
    # Mezclar aleatoriamente
    random.shuffle(tickets)
    
    return tickets

def guardar_csv(tickets, filename='data/synthetic/tickets_sinteticos.csv'):
    """Guarda tickets en formato CSV"""
    fieldnames = ['id', 'titulo', 'descripcion', 'categoria', 'prioridad', 
                  'fecha_creacion', 'fecha_resolucion', 'tiempo_resolucion_horas', 'estado']
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(tickets)
    
    print(f"\n✅ Archivo CSV guardado: {filename}")

def guardar_json(tickets, filename='data/synthetic/tickets_sinteticos.json'):
    """Guarda tickets en formato JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(tickets, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Archivo JSON guardado: {filename}")

def mostrar_estadisticas(tickets):
    """Muestra estadísticas de los tickets generados"""
    print("\n" + "="*50)
    print("ESTADÍSTICAS DE TICKETS GENERADOS")
    print("="*50)
    
    # Por categoría
    print("\nDistribución por categoría:")
    categorias_count = {}
    for ticket in tickets:
        cat = ticket['categoria']
        categorias_count[cat] = categorias_count.get(cat, 0) + 1
    
    for cat, count in sorted(categorias_count.items()):
        porcentaje = (count / len(tickets)) * 100
        print(f"  {cat:20s}: {count:3d} tickets ({porcentaje:.1f}%)")
    
    # Por prioridad
    print("\nDistribución por prioridad:")
    prioridades_count = {}
    for ticket in tickets:
        pri = ticket['prioridad']
        prioridades_count[pri] = prioridades_count.get(pri, 0) + 1
    
    for pri, count in sorted(prioridades_count.items()):
        porcentaje = (count / len(tickets)) * 100
        print(f"  {pri:10s}: {count:3d} tickets ({porcentaje:.1f}%)")
    
    # Por estado
    resueltos = sum(1 for t in tickets if t['estado'] == 'Resuelto')
    pendientes = len(tickets) - resueltos
    print(f"\nEstado:")
    print(f"  Resueltos:  {resueltos:3d} ({resueltos/len(tickets)*100:.1f}%)")
    print(f"  Pendientes: {pendientes:3d} ({pendientes/len(tickets)*100:.1f}%)")
    
    # Tiempo promedio de resolución
    tiempos = [t['tiempo_resolucion_horas'] for t in tickets if t['tiempo_resolucion_horas'] > 0]
    if tiempos:
        promedio = sum(tiempos) / len(tiempos)
        print(f"\nTiempo promedio de resolución: {promedio:.2f} horas")
    
    print("="*50 + "\n")

if __name__ == '__main__':
    print("SEIRA - Generador de Tickets Sintéticos")
    print("="*50)
    print(f"Generando {NUM_TICKETS} tickets...")
    print()
    
    tickets = generar_tickets()
    
    # Guardar archivos
    guardar_csv(tickets)
    guardar_json(tickets)
    
    # Mostrar estadísticas
    mostrar_estadisticas(tickets)
    
    print("✅ Generación completada exitosamente!")

