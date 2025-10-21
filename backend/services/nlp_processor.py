"""
Procesador NLP principal usando spaCy y scikit-learn
"""
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter
import logging
from services.text_cleaner import (
    limpiar_texto, 
    extraer_entidades_basicas,
    calcular_estadisticas_texto,
    es_texto_valido
)
from config import get_config

logger = logging.getLogger(__name__)

class NLPProcessor:
    """Procesador de texto con spaCy para análisis de tickets"""
    
    def __init__(self):
        """Inicializa el modelo de spaCy"""
        config = get_config()
        
        try:
            self.nlp = spacy.load(config.SPACY_MODEL)
            logger.info(f"✅ Modelo spaCy cargado: {config.SPACY_MODEL}")
        except OSError:
            logger.error(f"❌ Modelo {config.SPACY_MODEL} no encontrado")
            logger.info("📥 Intentando descargar modelo...")
            try:
                # Intentar descargar directamente desde GitHub
                import subprocess
                result = subprocess.run([
                    'pip', 'install', 
                    'https://github.com/explosion/spacy-models/releases/download/es_core_news_sm-3.7.0/es_core_news_sm-3.7.0-py3-none-any.whl'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.nlp = spacy.load(config.SPACY_MODEL)
                    logger.info("✅ Modelo descargado y cargado")
                else:
                    logger.error("❌ Error descargando modelo")
                    logger.info("💡 Por favor ejecuta manualmente:")
                    logger.info("   pip install https://github.com/explosion/spacy-models/releases/download/es_core_news_sm-3.7.0/es_core_news_sm-3.7.0-py3-none-any.whl")
                    raise
            except Exception as e:
                logger.error(f"❌ No se pudo descargar el modelo: {str(e)}")
                logger.info("💡 Continuando con procesamiento básico sin spaCy...")
                self.nlp = None
        
        # Palabras clave de urgencia
        self.palabras_urgentes = {
            'urgente', 'inmediato', 'critico', 'emergencia', 'grave',
            'bloqueado', 'bloqueante', 'produccion', 'caido', 'error',
            'falla', 'problema', 'roto', 'no funciona', 'perdida',
            'importante', 'prioridad', 'rapido', 'asap', 'ya'
        }
    
    def procesar_ticket(self, ticket_id, descripcion, categoria=None):
        """
        Procesa un ticket completo con NLP
        
        Args:
            ticket_id (int): ID del ticket
            descripcion (str): Descripción del ticket
            categoria (str): Categoría del ticket
            
        Returns:
            dict: Resultados del análisis NLP
        """
        logger.info(f"🔄 Procesando ticket #{ticket_id}")
        
        # Validar texto
        if not es_texto_valido(descripcion):
            logger.warning(f"⚠️  Ticket #{ticket_id}: texto inválido o muy corto")
            return self._resultado_vacio(ticket_id, "Texto inválido")
        
        # Texto original para extracción de entidades
        entidades_basicas = extraer_entidades_basicas(descripcion)
        
        # Limpiar texto
        texto_limpio = limpiar_texto(descripcion)
        
        # Estadísticas básicas
        estadisticas = calcular_estadisticas_texto(texto_limpio)
        
        # Procesar con spaCy (si está disponible)
        if self.nlp is not None:
            doc = self.nlp(texto_limpio)
            
            # Extraer tokens útiles (lematización + stopwords)
            tokens = [
                token.lemma_ 
                for token in doc 
                if not token.is_stop and not token.is_punct and len(token.text) > 2
            ]
            
            # Entidades nombradas (NER)
            entidades_ner = self._extraer_entidades_ner(doc)
            
            # Análisis de sentimiento básico
            sentimiento = self._analizar_sentimiento_basico(doc, texto_limpio)
            
            # Complejidad lingüística
            complejidad = self._calcular_complejidad(doc, estadisticas)
        else:
            # Procesamiento básico sin spaCy
            logger.warning("⚠️  Procesando sin spaCy - funcionalidad limitada")
            tokens = [
                palabra.lower() 
                for palabra in texto_limpio.split() 
                if len(palabra) > 2
            ]
            entidades_ner = {}
            sentimiento = self._analizar_sentimiento_basico(None, texto_limpio)
            complejidad = self._calcular_complejidad_basica(estadisticas)
        
        # Palabras clave (TF-IDF simulado con frecuencia)
        palabras_clave = self._extraer_palabras_clave(tokens, top_n=10)
        
        # Clasificación de urgencia
        urgencia = self._clasificar_urgencia(texto_limpio, tokens)
        
        # Vocabulario técnico
        vocab_tecnico = self._detectar_vocabulario_tecnico(tokens)
        
        resultado = {
            'ticket_id': ticket_id,
            'procesado': True,
            'texto_limpio': texto_limpio,
            'estadisticas': estadisticas,
            'palabras_clave': palabras_clave,
            'entidades_basicas': entidades_basicas,
            'entidades_ner': entidades_ner,
            'sentimiento': sentimiento,
            'complejidad': complejidad,
            'urgencia': urgencia,
            'vocab_tecnico_score': vocab_tecnico,
            'num_tokens': len(tokens),
            'categoria': categoria
        }
        
        logger.info(f"✅ Ticket #{ticket_id} procesado - Urgencia: {urgencia['nivel']}, Complejidad: {complejidad}")
        return resultado
    
    def _extraer_palabras_clave(self, tokens, top_n=10):
        """Extrae palabras clave más frecuentes"""
        if not tokens:
            return []
        
        contador = Counter(tokens)
        return [{'palabra': palabra, 'frecuencia': freq} 
                for palabra, freq in contador.most_common(top_n)]
    
    def _extraer_entidades_ner(self, doc):
        """Extrae entidades nombradas con spaCy"""
        entidades = {
            'personas': [],
            'organizaciones': [],
            'ubicaciones': [],
            'productos': [],
            'fechas': [],
            'otros': []
        }
        
        for ent in doc.ents:
            if ent.label_ == 'PER':
                entidades['personas'].append(ent.text)
            elif ent.label_ == 'ORG':
                entidades['organizaciones'].append(ent.text)
            elif ent.label_ == 'LOC' or ent.label_ == 'GPE':
                entidades['ubicaciones'].append(ent.text)
            elif ent.label_ == 'MISC':
                entidades['productos'].append(ent.text)
            elif ent.label_ == 'DATE' or ent.label_ == 'TIME':
                entidades['fechas'].append(ent.text)
            else:
                entidades['otros'].append({'texto': ent.text, 'tipo': ent.label_})
        
        # Eliminar duplicados
        for key in entidades:
            if isinstance(entidades[key], list):
                entidades[key] = list(set(entidades[key]))
        
        return entidades
    
    def _analizar_sentimiento_basico(self, doc, texto):
        """Análisis de sentimiento básico por palabras clave"""
        palabras_negativas = {
            'mal', 'malo', 'peor', 'problema', 'error', 'falla', 'no funciona',
            'decepcionado', 'molesto', 'frustrado', 'terrible', 'horrible',
            'defectuoso', 'roto', 'dañado', 'incorrecto', 'insatisfecho'
        }
        
        palabras_positivas = {
            'bien', 'bueno', 'mejor', 'excelente', 'perfecto', 'funciona',
            'satisfecho', 'contento', 'feliz', 'gracias', 'genial',
            'rápido', 'eficiente', 'correcto'
        }
        
        tokens_texto = set(texto.lower().split())
        
        score_negativo = len(palabras_negativas.intersection(tokens_texto))
        score_positivo = len(palabras_positivas.intersection(tokens_texto))
        
        if score_negativo > score_positivo:
            return {'tipo': 'negativo', 'score': -score_negativo, 'confianza': 0.6}
        elif score_positivo > score_negativo:
            return {'tipo': 'positivo', 'score': score_positivo, 'confianza': 0.6}
        else:
            return {'tipo': 'neutral', 'score': 0, 'confianza': 0.5}
    
    def _calcular_complejidad(self, doc, estadisticas):
        """Calcula complejidad lingüística (0-100) con spaCy"""
        if doc is None:
            return self._calcular_complejidad_basica(estadisticas)
        
        # Factores de complejidad
        num_palabras = estadisticas['num_palabras']
        num_oraciones = estadisticas['num_oraciones']
        longitud_promedio = estadisticas['longitud_promedio_palabra']
        
        # Palabras por oración
        palabras_por_oracion = num_palabras / num_oraciones if num_oraciones > 0 else num_palabras
        
        # Score de complejidad (normalizado a 0-100)
        score_longitud = min((longitud_promedio / 10) * 100, 100)
        score_oraciones = min((palabras_por_oracion / 30) * 100, 100)
        
        complejidad = (score_longitud * 0.4 + score_oraciones * 0.6)
        
        return round(min(complejidad, 100), 2)
    
    def _calcular_complejidad_basica(self, estadisticas):
        """Calcula complejidad sin spaCy (versión simplificada)"""
        num_palabras = estadisticas['num_palabras']
        longitud_promedio = estadisticas['longitud_promedio_palabra']
        
        # Score simple basado en longitud
        score = min((longitud_promedio / 8) * 50 + (num_palabras / 100) * 50, 100)
        
        return round(score, 2)
    
    def _clasificar_urgencia(self, texto, tokens):
        """Clasifica urgencia del ticket"""
        tokens_set = set(tokens)
        palabras_urgencia_encontradas = self.palabras_urgentes.intersection(tokens_set)
        
        num_urgentes = len(palabras_urgencia_encontradas)
        
        if num_urgentes >= 3:
            nivel = 'critica'
        elif num_urgentes >= 2:
            nivel = 'alta'
        elif num_urgentes >= 1:
            nivel = 'media'
        else:
            nivel = 'baja'
        
        return {
            'nivel': nivel,
            'score': num_urgentes,
            'palabras_encontradas': list(palabras_urgencia_encontradas)
        }
    
    def _detectar_vocabulario_tecnico(self, tokens):
        """Detecta presencia de vocabulario técnico"""
        palabras_tecnicas = {
            'api', 'servidor', 'database', 'sql', 'error', 'codigo',
            'version', 'actualizacion', 'configuracion', 'sistema',
            'hardware', 'software', 'driver', 'firmware', 'backup',
            'red', 'conexion', 'wifi', 'ethernet', 'protocolo',
            'gpu', 'cpu', 'ram', 'disco', 'memoria', 'procesador'
        }
        
        tokens_set = set(tokens)
        palabras_tecnicas_encontradas = palabras_tecnicas.intersection(tokens_set)
        
        # Score 0-100 basado en porcentaje de palabras técnicas
        if not tokens:
            return 0
        
        score = (len(palabras_tecnicas_encontradas) / len(tokens_set)) * 100
        return round(min(score, 100), 2)
    
    def _resultado_vacio(self, ticket_id, razon):
        """Retorna resultado vacío cuando el procesamiento falla"""
        return {
            'ticket_id': ticket_id,
            'procesado': False,
            'error': razon,
            'palabras_clave': [],
            'entidades_basicas': {},
            'entidades_ner': {},
            'sentimiento': {'tipo': 'neutral', 'score': 0},
            'complejidad': 0,
            'urgencia': {'nivel': 'baja', 'score': 0},
            'vocab_tecnico_score': 0
        }
    
    def procesar_batch(self, tickets):
        """
        Procesa múltiples tickets en batch
        
        Args:
            tickets (list): Lista de diccionarios con ticket_id, descripcion, categoria
            
        Returns:
            list: Lista de resultados procesados
        """
        logger.info(f"🔄 Procesando batch de {len(tickets)} tickets")
        
        resultados = []
        for ticket in tickets:
            try:
                resultado = self.procesar_ticket(
                    ticket['id'],
                    ticket['descripcion'],
                    ticket.get('categoria')
                )
                resultados.append(resultado)
            except Exception as e:
                logger.error(f"❌ Error procesando ticket #{ticket['id']}: {str(e)}")
                resultados.append(self._resultado_vacio(ticket['id'], str(e)))
        
        logger.info(f"✅ Batch procesado: {len(resultados)} tickets")
        return resultados