"""
SEIRA - Configuración de Base de Datos SQLite
"""

import sqlite3
import json
from datetime import datetime


class Database:
    """Manejador de base de datos SQLite"""
    
    def __init__(self, db_path='seira.db'):
        self.db_path = db_path
        self.conn = None
    
    def conectar(self):
        """Conecta a la base de datos"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Para obtener resultados como dict
        return self.conn
    
    def cerrar(self):
        """Cierra la conexión"""
        if self.conn:
            self.conn.close()
    
    def crear_tablas(self):
        """Crea las tablas necesarias"""
        cursor = self.conn.cursor()
        
        # Tabla: tickets
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            categoria TEXT,
            prioridad TEXT,
            fecha_creacion DATETIME,
            fecha_resolucion DATETIME,
            tiempo_resolucion_horas REAL,
            estado TEXT,
            palabras_clave TEXT,
            complejidad REAL,
            tokens INTEGER
        )
        ''')
        
        # Tabla: analisis
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS analisis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_analisis DATETIME DEFAULT CURRENT_TIMESTAMP,
            total_tickets INTEGER,
            categorias_identificadas INTEGER,
            iar_promedio REAL
        )
        ''')
        
        # Tabla: recomendaciones
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS recomendaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analisis_id INTEGER,
            categoria TEXT,
            iar REAL,
            nivel TEXT,
            tipo_ia_sugerida TEXT,
            roi_porcentaje REAL,
            ahorro_anual_usd REAL,
            fecha_generacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (analisis_id) REFERENCES analisis(id)
        )
        ''')
        
        # Tabla: metricas_categoria
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS metricas_categoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analisis_id INTEGER,
            categoria TEXT,
            total_tickets INTEGER,
            frecuencia_score REAL,
            complejidad_score REAL,
            impacto_score REAL,
            viabilidad_score REAL,
            FOREIGN KEY (analisis_id) REFERENCES analisis(id)
        )
        ''')
        
        self.conn.commit()
        print("✅ Tablas creadas exitosamente")
    
    def cargar_tickets(self, tickets_json_path='data/processed/tickets_procesados.json'):
        """Carga tickets desde JSON a la BD"""
        with open(tickets_json_path, 'r', encoding='utf-8') as f:
            tickets = json.load(f)
        
        cursor = self.conn.cursor()
        
        # Limpiar tabla primero
        cursor.execute('DELETE FROM tickets')
        
        for ticket in tickets:
            cursor.execute('''
            INSERT INTO tickets (
                titulo, descripcion, categoria, prioridad,
                fecha_creacion, fecha_resolucion, tiempo_resolucion_horas,
                estado, palabras_clave, complejidad, tokens
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                ticket['titulo'],
                ticket['descripcion'],
                ticket['categoria'],
                ticket.get('prioridad_calculada', 'Media'),
                ticket['fecha_creacion'],
                ticket.get('fecha_resolucion', ''),
                ticket.get('tiempo_resolucion_horas', 0),
                ticket['estado'],
                json.dumps(ticket.get('palabras_clave', [])),
                ticket.get('complejidad', 0),
                ticket.get('num_tokens', 0)
            ))
        
        self.conn.commit()
        print(f"✅ {len(tickets)} tickets cargados a la BD")
    
    def cargar_recomendaciones(self, recomendaciones_json_path='data/processed/recomendaciones.json'):
        """Carga recomendaciones desde JSON a la BD"""
        with open(recomendaciones_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cursor = self.conn.cursor()
        
        # Crear registro de análisis
        cursor.execute('''
        INSERT INTO analisis (
            fecha_analisis, total_tickets, categorias_identificadas, iar_promedio
        ) VALUES (?, ?, ?, ?)
        ''', (
            data['fecha_analisis'],
            data['total_tickets_analizados'],
            data['categorias_analizadas'],
            data['metricas_globales']['iar_promedio']
        ))
        
        analisis_id = cursor.lastrowid
        
        # Cargar recomendaciones
        for rec in data['recomendaciones']:
            cursor.execute('''
            INSERT INTO recomendaciones (
                analisis_id, categoria, iar, nivel, tipo_ia_sugerida,
                roi_porcentaje, ahorro_anual_usd
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                analisis_id,
                rec['categoria'],
                rec['iar'],
                rec['nivel'],
                rec['tipo_ia_sugerida'],
                rec['roi']['roi_porcentaje'],
                rec['roi']['ahorro_monetario_usd']
            ))
            
            # Cargar métricas de la categoría
            cursor.execute('''
            INSERT INTO metricas_categoria (
                analisis_id, categoria, total_tickets,
                frecuencia_score, complejidad_score, impacto_score, viabilidad_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                analisis_id,
                rec['categoria'],
                rec['metricas']['total_tickets'],
                rec['metricas']['frecuencia_score'],
                rec['metricas']['complejidad_score'],
                rec['metricas']['impacto_score'],
                rec['metricas']['viabilidad_score']
            ))
        
        self.conn.commit()
        print(f"✅ Recomendaciones cargadas a la BD (Análisis ID: {analisis_id})")
        return analisis_id
    
    def obtener_resumen(self):
        """Obtiene resumen general del último análisis"""
        cursor = self.conn.cursor()
        
        # Último análisis
        cursor.execute('SELECT * FROM analisis ORDER BY id DESC LIMIT 1')
        analisis = cursor.fetchone()
        
        if not analisis:
            return None
        
        # Recomendaciones del último análisis
        cursor.execute('''
        SELECT * FROM recomendaciones 
        WHERE analisis_id = ? 
        ORDER BY iar DESC
        ''', (analisis['id'],))
        recomendaciones = cursor.fetchall()
        
        return {
            'analisis': dict(analisis),
            'recomendaciones': [dict(r) for r in recomendaciones]
        }
    
    def obtener_metricas_categoria(self, categoria):
        """Obtiene métricas de una categoría específica"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
        SELECT m.*, r.iar, r.nivel, r.tipo_ia_sugerida
        FROM metricas_categoria m
        JOIN recomendaciones r ON m.analisis_id = r.analisis_id AND m.categoria = r.categoria
        WHERE m.categoria = ?
        ORDER BY m.id DESC
        LIMIT 1
        ''', (categoria,))
        
        result = cursor.fetchone()
        return dict(result) if result else None


def main():
    """Función principal"""
    print("SEIRA - Configuración de Base de Datos")
    print("="*60)
    
    # Crear/conectar BD
    db = Database()
    db.conectar()
    
    # Crear tablas
    print("\nCreando tablas...")
    db.crear_tablas()
    
    # Cargar tickets
    print("\nCargando tickets procesados...")
    db.cargar_tickets()
    
    # Cargar recomendaciones
    print("\nCargando recomendaciones...")
    analisis_id = db.cargar_recomendaciones()
    
    # Verificar carga
    print("\n" + "="*60)
    print("VERIFICACIÓN")
    print("="*60)
    
    cursor = db.conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as count FROM tickets')
    print(f"Tickets en BD: {cursor.fetchone()['count']}")
    
    cursor.execute('SELECT COUNT(*) as count FROM recomendaciones')
    print(f"Recomendaciones en BD: {cursor.fetchone()['count']}")
    
    cursor.execute('SELECT COUNT(*) as count FROM metricas_categoria')
    print(f"Métricas en BD: {cursor.fetchone()['count']}")
    
    # Cerrar conexión
    db.cerrar()
    
    print("\n✅ Base de datos configurada y cargada exitosamente!")


if __name__ == '__main__':
    main()
