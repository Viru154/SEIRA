"""
Utilidades para limpieza y normalización de texto
"""
import re
import unicodedata

def limpiar_texto(texto):
    """
    Limpia y normaliza texto para procesamiento NLP
    
    Args:
        texto (str): Texto a limpiar
        
    Returns:
        str: Texto limpio y normalizado
    """
    if not texto or not isinstance(texto, str):
        return ""
    
    # Convertir a minúsculas
    texto = texto.lower()
    
    # Eliminar URLs
    texto = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', texto)
    
    # Eliminar emails
    texto = re.sub(r'\S+@\S+', '', texto)
    
    # Eliminar números de teléfono comunes
    texto = re.sub(r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}', '', texto)
    
    # Eliminar menciones y hashtags (si aplica)
    texto = re.sub(r'@\w+', '', texto)
    texto = re.sub(r'#\w+', '', texto)
    
    # Normalizar espacios en blanco
    texto = re.sub(r'\s+', ' ', texto)
    
    # Eliminar caracteres especiales pero mantener puntuación básica
    texto = re.sub(r'[^a-záéíóúñü\s.,;:¿?¡!-]', '', texto)
    
    # Normalizar acentos (opcional, pero útil para consistencia)
    # Descomenta si prefieres eliminar acentos
    # texto = ''.join(c for c in unicodedata.normalize('NFD', texto) 
    #                 if unicodedata.category(c) != 'Mn')
    
    # Eliminar espacios al inicio y final
    texto = texto.strip()
    
    return texto

def extraer_entidades_basicas(texto):
    """
    Extrae entidades básicas del texto (emails, URLs, números)
    
    Args:
        texto (str): Texto original sin limpiar
        
    Returns:
        dict: Diccionario con entidades encontradas
    """
    entidades = {
        'emails': [],
        'urls': [],
        'telefonos': [],
        'numeros_orden': []
    }
    
    if not texto:
        return entidades
    
    # Extraer emails
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', texto)
    entidades['emails'] = list(set(emails))
    
    # Extraer URLs
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', texto)
    entidades['urls'] = list(set(urls))
    
    # Extraer teléfonos
    telefonos = re.findall(r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}', texto)
    entidades['telefonos'] = list(set(telefonos))
    
    # Extraer números de orden (ej: ORD-12345, #12345)
    numeros_orden = re.findall(r'(?:ORD|ORDEN|#)\s*[-:]?\s*(\d{4,})', texto, re.IGNORECASE)
    entidades['numeros_orden'] = list(set(numeros_orden))
    
    return entidades

def calcular_estadisticas_texto(texto):
    """
    Calcula estadísticas básicas del texto
    
    Args:
        texto (str): Texto limpio
        
    Returns:
        dict: Estadísticas del texto
    """
    if not texto:
        return {
            'num_palabras': 0,
            'num_oraciones': 0,
            'num_caracteres': 0,
            'palabras_unicas': 0,
            'longitud_promedio_palabra': 0
        }
    
    palabras = texto.split()
    oraciones = re.split(r'[.!?]+', texto)
    oraciones = [o for o in oraciones if o.strip()]
    
    palabras_unicas = set(palabras)
    
    longitud_promedio = sum(len(p) for p in palabras) / len(palabras) if palabras else 0
    
    return {
        'num_palabras': len(palabras),
        'num_oraciones': len(oraciones),
        'num_caracteres': len(texto),
        'palabras_unicas': len(palabras_unicas),
        'longitud_promedio_palabra': round(longitud_promedio, 2)
    }

def es_texto_valido(texto, min_palabras=3):
    """
    Verifica si el texto es válido para procesamiento
    
    Args:
        texto (str): Texto a validar
        min_palabras (int): Mínimo de palabras requeridas
        
    Returns:
        bool: True si el texto es válido
    """
    if not texto or not isinstance(texto, str):
        return False
    
    texto_limpio = limpiar_texto(texto)
    palabras = texto_limpio.split()
    
    return len(palabras) >= min_palabras