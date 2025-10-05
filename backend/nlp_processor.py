"""
SEIRA - Motor de Procesamiento NLP
Procesa y analiza tickets usando spaCy y técnicas de NLP
"""

import spacy
import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import json

# Cargar modelo de spaCy en español
print("Cargando modelo de spaCy...")
nlp = spacy.load('es_core_news_sm')

# Stopwords personalizadas adicionales
STOPWORDS_CUSTOM = {
    'ticket', 'sistema', 'favor', 'gracias', 'solicito', 'necesito',
    'quisiera', 'buenos', 'días', 'hola', 'saludos', 'estimado',
    'att', 'atentamente', 'cordialmente'
}


class TicketNLPProcessor:
    """Procesador NLP para tickets de soporte"""
    
    def __init__(self):
        self.nlp = nlp
        self.tfidf_vectorizer = None
        self.tickets_procesados = []
    
    def limpiar_texto(self, texto):
        """
        Limpia y normaliza el texto del ticket
        """
        if not texto:
            return ""
        
        # Convertir a minúsculas
        texto = texto.lower()
        
        # Eliminar URLs
        texto = re.sub(r'http[s]?://\S+', '', texto)
        
        # Eliminar emails
        texto = re.sub(r'\S+@\S+', '', texto)
        
        # Eliminar números largos (IDs, teléfonos)
        texto = re.sub(r'\b\d{5,}\b', '', texto)
        
        # Eliminar caracteres especiales pero mantener tildes y ñ
        texto = re.sub(r'[^\w\sáéíóúñü]', ' ', texto)
        
        # Eliminar espacios múltiples
        texto = re.sub(r'\s+', ' ', texto)
        
        return texto.strip()
    
    def tokenizar_y_lematizar(self, texto):
        """
        Tokeniza y lematiza el texto, eliminando stopwords
        """
        doc = self.nlp(texto)
        
        # Extraer tokens lematizados, sin stopwords, sin puntuación
        tokens = [
            token.lemma_ for token in doc
            if not token.is_stop 
            and not token.is_punct
            and not token.is_space
            and len(token.text) > 2
            and token.lemma_.lower() not in STOPWORDS_CUSTOM
        ]
        
        return tokens
    
    def extraer_entidades(self, texto):
        """
        Extrae entidades nombradas del texto
        """
        doc = self.nlp(texto)
        entidades = {
            'personas': [],
            'organizaciones': [],
            'lugares': [],
            'fechas': [],
            'dinero': []
        }
        
        for ent in doc.ents:
            if ent.label_ == 'PER':
                entidades['personas'].append(ent.text)
            elif ent.label_ == 'ORG':
                entidades['organizaciones'].append(ent.text)
            elif ent.label_ == 'LOC':
                entidades['lugares'].append(ent.text)
            elif ent.label_ == 'DATE':
                entidades['fechas'].append(ent.text)
            elif ent.label_ == 'MONEY':
                entidades['dinero'].append(ent.text)
        
        return entidades
    
    def calcular_complejidad(self, texto):
        """
        Calcula un índice de complejidad del texto (0-100)
        Basado en longitud, vocabulario único, entidades
        """
        doc = self.nlp(texto)
        
        num_palabras = len([t for t in doc if not t.is_punct])
        num_oraciones = len(list(doc.sents))
        palabras_unicas = len(set([t.text.lower() for t in doc if not t.is_punct]))
        num_entidades = len(doc.ents)
        
        # Calcular métricas
        longitud_score = min(num_palabras / 100, 1.0) * 30
        diversidad_score = (palabras_unicas / max(num_palabras, 1)) * 30
        oraciones_score = min(num_oraciones / 10, 1.0) * 20
        entidades_score = min(num_entidades / 5, 1.0) * 20
        
        complejidad = longitud_score + diversidad_score + oraciones_score + entidades_score
        
        return round(complejidad, 2)
    
    def extraer_palabras_clave_tfidf(self, textos, top_n=10):
        """
        Extrae palabras clave usando TF-IDF
        """
        # Preparar textos limpios
        textos_limpios = [self.limpiar_texto(t) for t in textos]
        
        # Aplicar TF-IDF
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),  # unigramas y bigramas
            min_df=2,
            max_df=0.8
        )
        
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(textos_limpios)
        feature_names = self.tfidf_vectorizer.get_feature_names_out()
        
        # Extraer top keywords por documento
        keywords_por_doc = []
        for row in range(tfidf_matrix.shape[0]):
            scores = tfidf_matrix[row].toarray().flatten()
            top_indices = scores.argsort()[-top_n:][::-1]
            keywords = [feature_names[i] for i in top_indices if scores[i] > 0]
            keywords_por_doc.append(keywords)
        
        return keywords_por_doc
    
    def clasificar_urgencia(self, texto, prioridad_original):
        """
        Clasifica la urgencia basándose en palabras clave
        """
        palabras_urgentes = {
            'urgente', 'crítico', 'inmediato', 'emergencia', 'bloqueado',
            'down', 'caído', 'no funciona', 'error crítico', 'producción'
        }
        
        texto_lower = texto.lower()
        palabras_encontradas = sum(1 for p in palabras_urgentes if p in texto_lower)
        
        # Ajustar score de urgencia
        if palabras_encontradas >= 2:
            return 'Crítica'
        elif palabras_encontradas == 1 or prioridad_original == 'Alta':
            return 'Alta'
        elif prioridad_original == 'Media':
            return 'Media'
        else:
            return 'Baja'
    
    def procesar_ticket(self, ticket):
        """
        Procesa un ticket completo
        """
        # Combinar título y descripción
        texto_completo = f"{ticket['titulo']}. {ticket['descripcion']}"
        
        # Limpiar texto
        texto_limpio = self.limpiar_texto(texto_completo)
        
        # Tokenizar y lematizar
        tokens = self.tokenizar_y_lematizar(texto_limpio)
        
        # Extraer entidades
        entidades = self.extraer_entidades(texto_completo)
        
        # Calcular complejidad
        complejidad = self.calcular_complejidad(texto_completo)
        
        # Clasificar urgencia
        urgencia = self.clasificar_urgencia(texto_completo, ticket.get('prioridad', 'Media'))
        
        # Crear objeto procesado
        ticket_procesado = {
            'id': ticket['id'],
            'titulo': ticket['titulo'],
            'descripcion': ticket['descripcion'],
            'categoria': ticket['categoria'],
            'prioridad_original': ticket.get('prioridad', 'Media'),
            'prioridad_calculada': urgencia,
            'fecha_creacion': ticket['fecha_creacion'],
            'estado': ticket['estado'],
            'texto_limpio': texto_limpio,
            'tokens': tokens,
            'num_tokens': len(tokens),
            'entidades': entidades,
            'complejidad': complejidad,
            'tiempo_resolucion_horas': ticket.get('tiempo_resolucion_horas', 0)
        }
        
        return ticket_procesado
    
    def procesar_lote(self, tickets):
        """
        Procesa un lote de tickets
        """
        print(f"\nProcesando {len(tickets)} tickets...")
        
        tickets_procesados = []
        for i, ticket in enumerate(tickets, 1):
            if i % 50 == 0:
                print(f"  Procesados: {i}/{len(tickets)}")
            
            ticket_proc = self.procesar_ticket(ticket)
            tickets_procesados.append(ticket_proc)
        
        self.tickets_procesados = tickets_procesados
        
        # Extraer keywords globales con TF-IDF
        print("\nExtrayendo palabras clave con TF-IDF...")
        textos = [t['texto_limpio'] for t in tickets_procesados]
        keywords_list = self.extraer_palabras_clave_tfidf(textos, top_n=10)
        
        # Agregar keywords a cada ticket
        for i, ticket in enumerate(tickets_procesados):
            ticket['palabras_clave'] = keywords_list[i]
        
        print(f"✅ Procesamiento completado: {len(tickets_procesados)} tickets")
        
        return tickets_procesados
    
    def generar_estadisticas(self):
        """
        Genera estadísticas del procesamiento
        """
        if not self.tickets_procesados:
            print("No hay tickets procesados")
            return
        
        print("\n" + "="*60)
        print("ESTADÍSTICAS DE PROCESAMIENTO NLP")
        print("="*60)
        
        # Complejidad promedio por categoría
        df = pd.DataFrame(self.tickets_procesados)
        
        print("\nComplejidad promedio por categoría:")
        comp_por_cat = df.groupby('categoria')['complejidad'].mean().sort_values(ascending=False)
        for cat, comp in comp_por_cat.items():
            print(f"  {cat:25s}: {comp:.2f}")
        
        # Tokens promedio
        print(f"\nTokens promedio por ticket: {df['num_tokens'].mean():.2f}")
        
        # Palabras más frecuentes globalmente
        print("\nPalabras más frecuentes (top 15):")
        all_tokens = []
        for ticket in self.tickets_procesados:
            all_tokens.extend(ticket['tokens'])
        
        counter = Counter(all_tokens)
        for palabra, freq in counter.most_common(15):
            print(f"  {palabra:20s}: {freq} veces")
        
        # Distribución de urgencia calculada
        print("\nDistribución de urgencia calculada:")
        urgencia_dist = df['prioridad_calculada'].value_counts()
        for urgencia, count in urgencia_dist.items():
            porcentaje = (count / len(df)) * 100
            print(f"  {urgencia:10s}: {count:3d} ({porcentaje:.1f}%)")
        
        print("="*60 + "\n")
    
    def guardar_resultados(self, filename='data/processed/tickets_procesados.json'):
        """
        Guarda los tickets procesados
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.tickets_procesados, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Tickets procesados guardados en: {filename}")


def main():
    """Función principal"""
    print("SEIRA - Procesamiento NLP de Tickets")
    print("="*60)
    
    # Cargar tickets sintéticos
    print("\nCargando tickets desde CSV...")
    df = pd.read_csv('data/synthetic/tickets_sinteticos.csv')
    tickets = df.to_dict('records')
    print(f"✅ Cargados {len(tickets)} tickets")
    
    # Crear procesador
    processor = TicketNLPProcessor()
    
    # Procesar tickets
    tickets_procesados = processor.procesar_lote(tickets)
    
    # Generar estadísticas
    processor.generar_estadisticas()
    
    # Guardar resultados
    processor.guardar_resultados()
    
    print("\n✅ Procesamiento NLP completado exitosamente!")


if __name__ == '__main__':
    main()
