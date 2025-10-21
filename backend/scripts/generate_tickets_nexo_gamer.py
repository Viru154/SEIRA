"""
Generador Masivo de Tickets para NEXO GAMER
Tienda de Gaming: Videojuegos, Hardware, Trade-in, Reparación

Este generador crea tickets realistas que serán analizados por SEIRA 2.0
para determinar qué categorías vale la pena automatizar con IA.

Uso:
    python backend/scripts/generate_tickets_nexo_gamer.py --cantidad 150000
    python backend/scripts/generate_tickets_nexo_gamer.py --cantidad 1000000 --batch-size 5000 --sin-confirmar
    python backend/scripts/generate_tickets_nexo_gamer.py --cantidad 50000 --output-log stats.json
"""
import sys
import json
import argparse
import random
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Callable

from faker import Faker
from tqdm import tqdm
from sqlalchemy.exc import SQLAlchemyError

# Añadir directorio raíz al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from utils.database import db_manager
from models import Ticket

# Configuración
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

fake = Faker('es_ES')
Faker.seed(42)


# ============================================================================
# FUNCIONES GENERADORAS MODULARES (Patrón Strategy)
# ============================================================================

def _gen_preventa_juego(config: Dict, juegos_base: List[str]) -> Dict[str, Any]:
    """Genera contenido para preventas de juegos"""
    juego = random.choice(config['juegos'])
    plantilla = random.choice(config['plantillas'])
    titulo = plantilla.format(juego=juego)
    
    detalles_extra = [
        f"Vi que ya está en preventa en {fake.company()}.",
        f"¿Incluye algún bonus exclusivo?",
        f"¿Cuándo es el lanzamiento exacto?",
        f"Me interesa la edición {random.choice(['estándar', 'deluxe', 'coleccionista'])}.",
        f"¿Tienen stock garantizado?",
    ]
    descripcion = f"{titulo}. {random.choice(detalles_extra)} {fake.sentence(nb_words=8)}"
    
    return {
        'titulo': titulo[:255],
        'descripcion': descripcion[:1000],
        'producto': juego,
        'orden_id': None
    }


def _gen_preventa_hardware(config: Dict, _) -> Dict[str, Any]:
    """Genera contenido para preventas de hardware"""
    item = random.choice(config['items'])
    plantilla = random.choice(config['plantillas'])
    titulo = plantilla.format(item=item)
    
    preguntas = [
        "¿Cuál es el precio de lanzamiento?",
        "¿Viene con algún juego incluido?",
        "¿Tienen bundle disponible?",
        "¿Garantía internacional?",
        "¿Envío gratis a departamentos?",
    ]
    descripcion = f"{titulo}. {random.choice(preguntas)} {fake.sentence(nb_words=6)}"
    
    return {
        'titulo': titulo[:255],
        'descripcion': descripcion[:1000],
        'producto': item,
        'orden_id': None
    }


def _gen_venta_adicional(config: Dict, juegos_base: List[str]) -> Dict[str, Any]:
    """Genera contenido para DLCs, Season Pass, etc."""
    item = random.choice(config['items'])
    juego = random.choice(juegos_base)
    plantilla = random.choice(config['plantillas'])
    titulo = plantilla.format(item=item).replace('[juego]', juego)
    
    situaciones = [
        f"Compré el {item} hace 2 días.",
        f"El {item} no se refleja en mi biblioteca.",
        f"¿El {item} incluye todos los mapas nuevos?",
        f"Ya tengo el juego base, ¿puedo comprar solo el {item}?",
    ]
    descripcion = f"{titulo}. {random.choice(situaciones)} {fake.sentence(nb_words=7)}"
    
    return {
        'titulo': titulo[:255],
        'descripcion': descripcion[:1000],
        'producto': f"{item} - {juego}",
        'orden_id': None
    }


def _gen_consulta_producto(config: Dict, juegos_base: List[str]) -> Dict[str, Any]:
    """Genera consultas generales sobre productos"""
    juego = random.choice(juegos_base)
    plantilla = random.choice(config['plantillas'])
    titulo = plantilla.replace('[Juego]', juego).replace('[juego]', juego)
    
    contextos = [
        "Antes de comprarlo quisiera saber.",
        "Leí reseñas contradictorias.",
        "Mi hijo me preguntó y no sé qué responder.",
        "Comparando con otros juegos similares.",
    ]
    descripcion = f"{titulo}. {random.choice(contextos)} {fake.sentence(nb_words=9)}"
    
    return {
        'titulo': titulo[:255],
        'descripcion': descripcion[:1000],
        'producto': juego,
        'orden_id': None
    }


def _gen_problema_producto(config: Dict, juegos_base: List[str]) -> Dict[str, Any]:
    """Genera problemas técnicos con productos"""
    problema = random.choice(config['problemas'])
    juego = random.choice(juegos_base)
    plantilla = random.choice(config['plantillas'])
    titulo = plantilla.format(problema=problema).replace('[juego]', juego)
    
    urgencias = [
        "Es urgente, no puedo jugarlo.",
        "Llevo 3 días intentando solucionarlo.",
        "Ya reinstalé 2 veces y sigue igual.",
        "Probé en otra PC y funciona, ¿será mi equipo?",
        "El soporte de Steam no me ayudó.",
    ]
    descripcion = f"{titulo}. {random.choice(urgencias)} {fake.paragraph(nb_sentences=2)}"
    
    return {
        'titulo': titulo[:255],
        'descripcion': descripcion[:1000],
        'producto': juego,
        'orden_id': None
    }


def _gen_soporte_tecnico(config: Dict, juegos_base: List[str]) -> Dict[str, Any]:
    """Genera tickets de soporte técnico"""
    juego = random.choice(juegos_base)
    plantilla = random.choice(config['plantillas'])
    titulo = plantilla.replace('[juego]', juego).replace('[Juego]', juego)
    
    specs = [
        f"Tengo {random.choice(['RTX 3060', 'GTX 1660', 'RX 6700 XT', 'RTX 4070'])}.",
        f"{random.randint(8, 32)}GB RAM, {random.choice(['Ryzen 5', 'i5', 'Ryzen 7', 'i7'])}.",
        "¿Con mi PC actual podré jugarlo?",
        "¿Cuánto espacio en disco necesito?",
    ]
    descripcion = f"{titulo}. {random.choice(specs)} {fake.sentence(nb_words=8)}"
    
    return {
        'titulo': titulo[:255],
        'descripcion': descripcion[:1000],
        'producto': juego,
        'orden_id': None
    }


def _gen_problema_pago(config: Dict, juegos_base: List[str]) -> Dict[str, Any]:
    """Genera problemas de pago"""
    juego = random.choice(juegos_base)
    plantilla = random.choice(config['plantillas'])
    titulo = plantilla.replace('[juego]', juego)
    
    detalles = [
        f"Mi banco me confirmó el cargo de Q{random.randint(100, 500)}.",
        "Tengo el comprobante de pago.",
        "¿Puedo pagar con transferencia bancaria?",
        "La tarjeta es válida, ya la usé antes.",
        "¿Aceptan pagos en efectivo en tienda física?",
    ]
    descripcion = f"{titulo}. {random.choice(detalles)} {fake.sentence(nb_words=7)}"
    
    return {
        'titulo': titulo[:255],
        'descripcion': descripcion[:1000],
        'producto': juego,
        'orden_id': None
    }


def _gen_trade_in(config: Dict, _) -> Dict[str, Any]:
    """Genera consultas de trade-in (compra de usados)"""
    item = random.choice(config['items'])
    plantilla = random.choice(config['plantillas'])
    titulo = plantilla.format(item=item)
    
    condiciones = [
        "Está en excelente estado, casi sin uso.",
        "Tiene algunos rayones leves pero funciona perfecto.",
        "Incluye caja original y accesorios.",
        "¿Aceptan consolas sin caja?",
        f"¿Puedo usar el crédito para comprar {random.choice(['un juego nuevo', 'accesorios', 'otra consola'])}?",
    ]
    descripcion = f"{titulo}. {random.choice(condiciones)} {fake.sentence(nb_words=6)}"
    
    return {
        'titulo': titulo[:255],
        'descripcion': descripcion[:1000],
        'producto': item,
        'orden_id': None
    }


def _gen_reparacion_consola(config: Dict, _) -> Dict[str, Any]:
    """Genera solicitudes de reparación de consolas"""
    item = random.choice(config['items'])
    problema = random.choice(config['problemas'])
    plantilla = random.choice(config['plantillas'])
    titulo = plantilla.format(item=item, problema=problema)
    
    urgencias = [
        "¿Cuánto cuesta la reparación aproximadamente?",
        "¿Cuánto tiempo tarda?",
        "¿Tienen técnicos certificados?",
        "¿Pierdo la garantía si la reparan ustedes?",
        f"Empezó a fallar después de {random.randint(3, 18)} meses de uso.",
    ]
    descripcion = f"{titulo}. {random.choice(urgencias)} {fake.sentence(nb_words=10)}"
    
    return {
        'titulo': titulo[:255],
        'descripcion': descripcion[:1000],
        'producto': item,
        'orden_id': None
    }


def _gen_reparacion_pc(config: Dict, _) -> Dict[str, Any]:
    """Genera solicitudes de reparación de PC gaming"""
    problema = random.choice(config['problemas'])
    plantilla = random.choice(config['plantillas'])
    titulo = plantilla.format(problema=problema)
    
    specs_problema = [
        f"Tengo {random.choice(['RTX 3080', 'RX 6800 XT', 'RTX 4090', 'RTX 3070'])}.",
        "Es una laptop MSI Gaming de hace 2 años.",
        "Desktop custom build con refrigeración líquida.",
        "¿Pueden revisar fuente de poder?",
        f"Las temperaturas llegan a {random.randint(75, 95)}°C.",
    ]
    descripcion = f"{titulo}. {random.choice(specs_problema)} {fake.sentence(nb_words=9)}"
    
    return {
        'titulo': titulo[:255],
        'descripcion': descripcion[:1000],
        'producto': "PC Gaming",
        'orden_id': None
    }


def _gen_consulta_pedido(config: Dict, juegos_base: List[str]) -> Dict[str, Any]:
    """Genera consultas sobre órdenes de compra"""
    orden_id = f"ORD-{random.randint(100000, 999999)}"
    juego = random.choice(juegos_base)
    plantilla = random.choice(config['plantillas'])
    titulo = plantilla.format(order_id=orden_id).replace('[juego]', juego)
    
    situaciones = [
        f"Compré hace {random.randint(3, 10)} días.",
        "El tracking no se actualiza desde ayer.",
        "¿Envían a toda Guatemala?",
        "¿Puedo recogerlo en tienda?",
        "¿Cuándo llega a mi dirección?",
    ]
    descripcion = f"{titulo}. {random.choice(situaciones)} {fake.sentence(nb_words=6)}"
    
    return {
        'titulo': titulo[:255],
        'descripcion': descripcion[:1000],
        'producto': juego,
        'orden_id': orden_id
    }


def _gen_devolucion(config: Dict, juegos_base: List[str]) -> Dict[str, Any]:
    """Genera solicitudes de devolución/reembolso"""
    juego = random.choice(juegos_base)
    plantilla = random.choice(config['plantillas'])
    titulo = plantilla.replace('[juego]', juego).replace('[Juego]', juego)
    
    razones = [
        "No es lo que esperaba según los trailers.",
        "Mi PC no lo corre bien.",
        "Lo compré por error, quería otro juego.",
        "Ya lo tengo en otra plataforma.",
        f"Jugué {random.randint(15, 90)} minutos y no me gustó.",
    ]
    descripcion = f"{titulo}. {random.choice(razones)} {fake.sentence(nb_words=7)}"
    
    return {
        'titulo': titulo[:255],
        'descripcion': descripcion[:1000],
        'producto': juego,
        'orden_id': None
    }


def _gen_cuenta_acceso(config: Dict, _) -> Dict[str, Any]:
    """Genera problemas de cuenta y acceso"""
    plantilla = random.choice(config['plantillas'])
    titulo = plantilla
    
    situaciones = [
        f"Mi email es {fake.email()}.",
        "No recibo el código de verificación.",
        "¿Pueden resetear mi contraseña manualmente?",
        "Creo que alguien accedió sin mi permiso.",
        "Compré desde mi cuenta hace 6 meses, debería estar registrado.",
    ]
    descripcion = f"{titulo}. {random.choice(situaciones)} {fake.sentence(nb_words=6)}"
    
    return {
        'titulo': titulo[:255],
        'descripcion': descripcion[:1000],
        'producto': None,
        'orden_id': None
    }


def _gen_promocion(config: Dict, juegos_base: List[str]) -> Dict[str, Any]:
    """Genera consultas sobre promociones"""
    juego = random.choice(juegos_base)
    plantilla = random.choice(config['plantillas'])
    titulo = plantilla.replace('[juego]', juego).replace('[Juego]', juego)
    
    contextos = [
        "Vi un cupón en redes sociales.",
        "¿Tienen descuentos por cumpleaños?",
        "¿Cuándo es la próxima oferta grande?",
        "El código expiró ayer, ¿puedo usarlo?",
        "¿Descuentos por compra de varios juegos?",
    ]
    descripcion = f"{titulo}. {random.choice(contextos)} {fake.sentence(nb_words=7)}"
    
    return {
        'titulo': titulo[:255],
        'descripcion': descripcion[:1000],
        'producto': juego,
        'orden_id': None
    }


def _gen_compatibilidad(config: Dict, juegos_base: List[str]) -> Dict[str, Any]:
    """Genera consultas de compatibilidad regional"""
    juego = random.choice(juegos_base)
    plantilla = random.choice(config['plantillas'])
    titulo = plantilla.replace('[juego]', juego).replace('[Juego]', juego)
    
    preocupaciones = [
        "Soy de Guatemala, ¿funcionará?",
        "¿Tiene bloqueo de región?",
        "¿Viene con idioma español?",
        "¿Servidores latinoamericanos disponibles?",
    ]
    descripcion = f"{titulo}. {random.choice(preocupaciones)} {fake.sentence(nb_words=8)}"
    
    return {
        'titulo': titulo[:255],
        'descripcion': descripcion[:1000],
        'producto': juego,
        'orden_id': None
    }


def _gen_feedback(config: Dict, _) -> Dict[str, Any]:
    """Genera feedback y sugerencias"""
    plantilla = random.choice(config['plantillas'])
    titulo = plantilla
    
    comentarios = [
        "El servicio al cliente fue excelente.",
        "La página web es muy intuitiva.",
        "Podrían mejorar los tiempos de envío.",
        "Sería genial tener más opciones de pago.",
        f"Mi experiencia fue {random.choice(['excelente', 'buena', 'regular'])}.",
    ]
    descripcion = f"{titulo}. {random.choice(comentarios)} {fake.sentence(nb_words=10)}"
    
    return {
        'titulo': titulo[:255],
        'descripcion': descripcion[:1000],
        'producto': None,
        'orden_id': None
    }


# ============================================================================
# CLASE PRINCIPAL DEL GENERADOR
# ============================================================================

class GeneradorNexoGamer:
    """
    Generador Premium de Tickets para NEXO GAMER
    Optimizado para PostgreSQL con arquitectura modular
    """
    
    # Juegos base compartidos por todas las categorías
    JUEGOS_BASE = [
        'Grand Theft Auto VI', 'The Elder Scrolls VI', 'Hollow Knight: Silksong',
        'Metroid Prime 4', 'Final Fantasy XVII', 'God of War: Ragnarok II',
        'The Witcher 4', 'Starfield 2', 'Resident Evil 10', 'Silent Hill f',
        'Cyberpunk 2088', 'Fable 4', 'Perfect Dark', 'Avowed', 'Dragon Age: Dreadwolf'
    ]
    
    # 16 Categorías con funciones generadoras asociadas
    CATEGORIAS: Dict[str, Dict[str, Any]] = {
        'preventa_juego': {
            'peso': 12,
            'generator': _gen_preventa_juego,
            'juegos': JUEGOS_BASE[:10],
            'plantillas': [
                '¿Cuándo sale {juego}? Quiero hacer preventa',
                'Información sobre preventa de {juego}',
                'Bonos de preventa para {juego}',
                'Cancelar preventa de {juego}',
                '¿Qué incluye la edición especial de {juego}?'
            ]
        },
        'preventa_hardware': {
            'peso': 8,
            'generator': _gen_preventa_hardware,
            'items': [
                'PlayStation 6', 'Xbox Series Z', 'Nintendo Switch 2', 'Steam Deck 2',
                'NVIDIA RTX 5090', 'AMD Radeon RX 8900 XT', 'Meta Quest 4', 
                'ASUS ROG Ally 2', 'Razer Blade 18 2025', 'Logitech G Pro X 2'
            ],
            'plantillas': [
                '¿Cuándo llega {item}? Quiero reservar',
                'Disponibilidad de {item} en Guatemala',
                'Especificaciones de {item}',
                'Diferencias entre modelos de {item}',
                'Precio de preventa {item}'
            ]
        },
        'venta_adicional': {
            'peso': 10,
            'generator': _gen_venta_adicional,
            'items': ['Season Pass', 'DLC Expansión', 'Battle Pass', 'Pack de Skins', 'Moneda Premium'],
            'plantillas': [
                'No puedo activar {item} que compré',
                '¿{item} incluye todo el contenido de [juego]?',
                'Precio del {item} para [juego]',
                '{item} no aparece en mi cuenta',
                '¿Vale la pena el {item} de [juego]?'
            ]
        },
        'consulta_producto': {
            'peso': 7,
            'generator': _gen_consulta_producto,
            'plantillas': [
                '¿[Juego] tiene multijugador local?',
                'Diferencias entre edición estándar y deluxe de [juego]',
                '¿Cuántas horas dura [juego]?',
                'Requisitos de espacio de [juego]',
                '¿[Juego] tiene doblaje al español?'
            ]
        },
        'problema_producto': {
            'peso': 15,
            'generator': _gen_problema_producto,
            'problemas': [
                'código no válido', 'juego no descarga', 'error al instalar',
                'crashes constantes', 'bugs gráficos', 'pantalla negra', 'no inicia',
                'se congela', 'error de conexión', 'saves corruptos'
            ],
            'plantillas': [
                'Compré [juego] pero tengo: {problema}',
                'Ayuda urgente: {problema} en [juego]',
                '{problema} después de actualización de [juego]',
                'Error {problema} al abrir [juego]'
            ]
        },
        'soporte_tecnico_juego': {
            'peso': 8,
            'generator': _gen_soporte_tecnico,
            'plantillas': [
                '¿Cuáles son los requisitos mínimos de [juego]?',
                'No puedo instalar [juego] en mi PC',
                '[Juego] se crashea al iniciar, ¿solución?',
                'Problemas de FPS bajo en [juego]',
                'Configuración gráfica óptima para [juego]'
            ]
        },
        'problema_pago': {
            'peso': 7,
            'generator': _gen_problema_pago,
            'plantillas': [
                'Mi pago fue rechazado pero me cobraron',
                'Error al procesar pago de [juego]',
                'Doble cobro en mi tarjeta por [juego]',
                'No puedo completar compra de [juego]',
                '¿Aceptan PayPal para comprar [juego]?'
            ]
        },
        'trade_in_compra': {
            'peso': 6,
            'generator': _gen_trade_in,
            'items': [
                'PlayStation 4 Pro', 'Xbox One X', 'Nintendo Switch OLED',
                'PlayStation 5 Digital', 'Steam Deck 512GB', 'Colección de juegos PS4',
                'Xbox Series S', 'Nintendo 3DS XL', 'PSP Go'
            ],
            'plantillas': [
                '¿Cuánto pagan por {item} usado?',
                'Quiero vender mi {item}, ¿qué necesito?',
                'Cotización de {item} en buen estado',
                '¿Aceptan {item} con rayones?',
                'Trade-in: {item} por crédito para [juego]'
            ]
        },
        'reparacion_consola': {
            'peso': 8,
            'generator': _gen_reparacion_consola,
            'items': ['PlayStation 5', 'Xbox Series X', 'Nintendo Switch', 'PlayStation 4', 'Xbox One'],
            'problemas': [
                'no enciende', 'error de disco', 'sobrecalentamiento',
                'no lee juegos', 'pantalla azul', 'ventilador ruidoso',
                'puerto HDMI dañado', 'joystick con drift'
            ],
            'plantillas': [
                'Mi {item} {problema}, ¿pueden reparar?',
                '{item} {problema} desde actualización',
                'Cotización reparación {item}: {problema}',
                '¿Cuánto tarda reparar {item} con {problema}?'
            ]
        },
        'reparacion_pc': {
            'peso': 5,
            'generator': _gen_reparacion_pc,
            'problemas': [
                'no enciende', 'pantalla negra', 'reinicia solo',
                'temperaturas altas', 'bajo rendimiento', 'ruidos extraños',
                'BSoD frecuentes', 'artefactos gráficos'
            ],
            'plantillas': [
                'Mi PC gaming {problema}, necesito soporte',
                'PC con RTX {problema} al jugar',
                'Laptop gaming {problema}, ¿pueden revisar?',
                'Presupuesto reparación: PC {problema}'
            ]
        },
        'consulta_pedido': {
            'peso': 10,
            'generator': _gen_consulta_pedido,
            'plantillas': [
                '¿Dónde está mi pedido #{order_id}?',
                'Estado de orden #{order_id} de [juego]',
                'No he recibido código de [juego], orden #{order_id}',
                '¿Cuánto tarda en llegar pedido #{order_id}?',
                'Tracking de orden #{order_id}'
            ]
        },
        'devolucion_reembolso': {
            'peso': 8,
            'generator': _gen_devolucion,
            'plantillas': [
                'Quiero devolver [juego], no es lo esperado',
                'Política de reembolso para [juego]',
                'Solicitud reembolso [juego], jugué 30 minutos',
                '¿Cuánto tarda reembolso de [juego]?',
                '[Juego] llegó defectuoso, quiero devolución'
            ]
        },
        'cuenta_acceso': {
            'peso': 4,
            'generator': _gen_cuenta_acceso,
            'plantillas': [
                'No puedo acceder a mi cuenta Nexo Gamer',
                'Recuperar contraseña olvidada',
                'Mi cuenta fue hackeada, ayuda urgente',
                'Cambiar email asociado a cuenta',
                'Verificación de dos pasos no funciona'
            ]
        },
        'promocion_descuento': {
            'peso': 4,
            'generator': _gen_promocion,
            'plantillas': [
                '¿Cuándo hay descuentos en [juego]?',
                'Cupón NEXO25 no funciona',
                'Ofertas de Black Friday gaming',
                '¿[Juego] estará en oferta pronto?',
                'Código de descuento expirado, ¿puedo usarlo?'
            ]
        },
        'compatibilidad_region': {
            'peso': 3,
            'generator': _gen_compatibilidad,
            'plantillas': [
                '¿[Juego] funciona en Guatemala?',
                'Restricciones regionales de [juego]',
                'Compré [juego] en USA, ¿funciona aquí?',
                'VPN para activar [juego] región bloqueada',
                'Versión latinoamericana de [juego]'
            ]
        },
        'sugerencia_feedback': {
            'peso': 1,
            'generator': _gen_feedback,
            'plantillas': [
                'Sugerencia: agregar más formas de pago',
                'Excelente servicio, muy satisfecho',
                'Podrían vender más accesorios gaming',
                'La tienda online es muy lenta',
                'Gracias por el soporte rápido en Nexo Gamer'
            ]
        }
    }
    
    def __init__(self, total_tickets: int = 100000, batch_size: int = 1000):
        if total_tickets <= 0 or batch_size <= 0:
            raise ValueError("Cantidad y batch_size deben ser positivos")
        
        self.total_tickets = total_tickets
        self.batch_size = batch_size
        self.tickets_generados = 0
        self.fecha_inicio = datetime.now() - timedelta(days=365)
        
        # Optimización: Precalcular listas
        self._categorias_lista = list(self.CATEGORIAS.keys())
        self._pesos_lista = [self.CATEGORIAS[cat]['peso'] for cat in self._categorias_lista]
        
        logger.info(f"Generador inicializado: {total_tickets:,} tickets, batch {batch_size:,}")
    
    def _generar_ticket_id(self) -> str:
        """Genera ID único secuencial"""
        return f"TKT-{self.tickets_generados + 1:08d}"
    
    def _seleccionar_categoria(self) -> str:
        """Selecciona categoría ponderada (optimizado con precalc)"""
        return random.choices(self._categorias_lista, weights=self._pesos_lista)[0]
    
    def _generar_contenido(self, categoria: str) -> Dict[str, Any]:
        """Genera contenido usando función generadora asociada"""
        config = self.CATEGORIAS[categoria]
        generator_func: Callable = config['generator']
        return generator_func(config, self.JUEGOS_BASE)
    
    def _generar_lote(self, tamaño: int) -> List[Ticket]:
        """Genera un lote de tickets"""
        lote = []
        
        for _ in range(tamaño):
            categoria = self._seleccionar_categoria()
            contenido = self._generar_contenido(categoria)
            
            # Fecha aleatoria con hora (más realista)
            fecha = self.fecha_inicio + timedelta(
                days=random.randint(0, 365),
                seconds=random.randint(0, 86400)
            )
            
            ticket = Ticket(
                ticket_id=self._generar_ticket_id(),
                titulo=contenido['titulo'],
                descripcion=contenido['descripcion'],
                categoria=categoria,
                fecha_creacion=fecha,
                estado=random.choices(
                    ['abierto', 'en_proceso', 'cerrado'],
                    weights=[30, 45, 25]  # Más tickets cerrados (realista)
                )[0],
                prioridad=random.choices(
                    ['baja', 'media', 'alta', 'critica'],
                    weights=[40, 35, 20, 5]  # Distribución realista
                )[0],
                cliente_id=f"CLI-{random.randint(1000, 99999)}",
                producto_relacionado=contenido['producto'],
                orden_id=contenido['orden_id'],
                procesado=False,
                created_at=datetime.now()
            )
            
            lote.append(ticket)
            self.tickets_generados += 1
        
        return lote
    
    def _guardar_lote(self, lote: List[Ticket]):
        """Guarda lote en PostgreSQL con manejo de errores"""
        try:
            with db_manager.session_scope() as session:
                session.bulk_save_objects(lote)
        except SQLAlchemyError as e:
            logger.error(f"Error al guardar lote: {e}")
            raise
    
    def generar(self, output_log: str = None):
        """
        Genera todos los tickets con barra de progreso
        
        Args:
            output_log: Path opcional para guardar estadísticas en JSON
        """
        print("\n" + "="*70)
        print("🎮 NEXO GAMER - Generador Premium de Tickets")
        print("="*70)
        print(f"📊 Total a generar: {self.total_tickets:,} tickets")
        print(f"📦 Batch size: {self.batch_size:,}")
        print(f"🗂️  Categorías: 16 (E-commerce gaming completo)")
        print("="*70 + "\n")
        
        db_manager.init_engine()
        num_lotes = (self.total_tickets + self.batch_size - 1) // self.batch_size
        inicio = datetime.now()
        
        # Barra de progreso con tqdm
        try:
            with tqdm(total=self.total_tickets, desc="🎮 Generando", unit=" tickets", 
                     ncols=100, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]') as pbar:
                
                for i in range(num_lotes):
                    tamaño_lote = min(self.batch_size, self.total_tickets - self.tickets_generados)
                    if tamaño_lote <= 0:
                        break
                    
                    lote = self._generar_lote(tamaño_lote)
                    self._guardar_lote(lote)
                    pbar.update(tamaño_lote)
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Generación interrumpida por el usuario")
            logger.warning(f"Generación detenida en {self.tickets_generados:,} tickets")
        
        except Exception as e:
            print(f"\n\n❌ Error durante generación: {e}")
            logger.error(f"Error crítico: {e}", exc_info=True)
            raise
        
        # Resumen final
        duracion = (datetime.now() - inicio).total_seconds()
        tasa = self.tickets_generados / duracion if duracion > 0 else 0
        
        print("\n" + "="*70)
        print("✅ GENERACIÓN COMPLETADA")
        print("="*70)
        print(f"📊 Tickets generados: {self.tickets_generados:,}")
        print(f"⏱️  Tiempo total: {duracion:.2f}s ({duracion/60:.1f} min)")
        print(f"🚀 Velocidad: {tasa:.0f} tickets/seg")
        
        # Estadísticas de PostgreSQL
        try:
            stats = db_manager.get_table_stats()
            print(f"📈 Total en PostgreSQL: {stats.get('tickets', 0):,} tickets")
        except Exception as e:
            logger.warning(f"No se pudieron obtener stats: {e}")
        
        print("="*70 + "\n")
        
        # Guardar log JSON si se especificó
        if output_log:
            stats_data = {
                'timestamp': datetime.now().isoformat(),
                'tickets_generados': self.tickets_generados,
                'objetivo': self.total_tickets,
                'batch_size': self.batch_size,
                'duracion_segundos': duracion,
                'duracion_minutos': duracion / 60,
                'tasa_tickets_seg': tasa,
                'categorias': 16,
                'rango_fechas': {
                    'inicio': self.fecha_inicio.isoformat(),
                    'fin': datetime.now().isoformat()
                }
            }
            
            try:
                with open(output_log, 'w', encoding='utf-8') as f:
                    json.dump(stats_data, f, indent=2, ensure_ascii=False)
                print(f"📄 Estadísticas guardadas en: {output_log}\n")
            except Exception as e:
                logger.error(f"Error al guardar log: {e}")


def main():
    """Punto de entrada principal"""
    parser = argparse.ArgumentParser(
        description='🎮 Generador Premium de Tickets para NEXO GAMER',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Generar 150,000 tickets (recomendado)
  python %(prog)s --cantidad 150000
  
  # Generar 1M con batch grande y sin confirmación
  python %(prog)s --cantidad 1000000 --batch-size 5000 --sin-confirmar
  
  # Generar con log de estadísticas
  python %(prog)s --cantidad 100000 --output-log stats_nexo.json
        """
    )
    
    parser.add_argument(
        '--cantidad', 
        type=int, 
        default=100000,
        help='Cantidad total de tickets a generar (default: 100,000)'
    )
    parser.add_argument(
        '--batch-size', 
        type=int, 
        default=1000,
        help='Tamaño de lote para inserciones (default: 1,000)'
    )
    parser.add_argument(
        '--sin-confirmar', 
        action='store_true',
        help='Ejecutar sin confirmación interactiva (modo automático)'
    )
    parser.add_argument(
        '--output-log',
        type=str,
        help='Archivo JSON para guardar estadísticas de generación'
    )
    
    args = parser.parse_args()
    
    # Confirmación interactiva
    if not args.sin_confirmar:
        print("\n" + "="*70)
        print("🎮 NEXO GAMER - Generador Premium de Tickets")
        print("="*70)
        print(f"   📊 Cantidad: {args.cantidad:,} tickets")
        print(f"   📦 Batch: {args.batch_size:,}")
        print(f"   🗂️  Categorías: 16 (gaming completo)")
        print(f"   ⏱️  Tiempo estimado: ~{args.cantidad/600:.1f} minutos")
        if args.output_log:
            print(f"   📄 Log: {args.output_log}")
        print("="*70)
        print("\n⚠️  Esto generará una gran cantidad de datos en PostgreSQL.")
        
        try:
            respuesta = input("\n¿Continuar con la generación? (s/n): ").lower().strip()
        except KeyboardInterrupt:
            print("\n\n❌ Cancelado por el usuario")
            return
        
        # Respuestas válidas
        respuestas_si = {'s', 'si', 'sí', 'y', 'yes', 'yeah', 'ok', '1'}
        respuestas_no = {'n', 'no', 'nop', 'nope', 'cancel', '0'}
        
        if respuesta in respuestas_si:
            print("✅ Iniciando generación de tickets...")
        elif respuesta in respuestas_no:
            print("❌ Generación cancelada por el usuario")
            return
        else:
            print(f"⚠️  Respuesta '{respuesta}' no reconocida. Cancelando por seguridad.")
            print("    (Respuestas válidas: s/si/yes/y para confirmar, n/no para cancelar)")
            return
    
    # Ejecutar generación
    try:
        generador = GeneradorNexoGamer(
            total_tickets=args.cantidad,
            batch_size=args.batch_size
        )
        generador.generar(output_log=args.output_log)
        
    except ValueError as e:
        logger.error(f"Error en parámetros: {e}")
        print(f"\n❌ Error: {e}")
    except Exception as e:
        logger.critical(f"Error crítico: {e}", exc_info=True)
        print(f"\n❌ Error inesperado: {e}")


if __name__ == '__main__':
    main()