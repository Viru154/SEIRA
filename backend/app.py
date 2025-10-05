"""
SEIRA - API Flask Backend
Proporciona endpoints REST para el frontend
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
import os

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)  # Permitir peticiones desde el frontend

# Configuración
DATABASE = 'seira.db'


def get_db():
    """Obtiene conexión a la base de datos"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    """Página principal"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/status')
def status():
    """Endpoint de estado del sistema"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM tickets')
        total_tickets = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM recomendaciones')
        total_recomendaciones = cursor.fetchone()['count']
        
        cursor.execute('SELECT fecha_analisis FROM analisis ORDER BY id DESC LIMIT 1')
        ultimo_analisis = cursor.fetchone()
        
        conn.close()
        
        return jsonify({
            'status': 'online',
            'total_tickets': total_tickets,
            'total_recomendaciones': total_recomendaciones,
            'ultimo_analisis': ultimo_analisis['fecha_analisis'] if ultimo_analisis else None
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/resumen')
def resumen():
    """Endpoint que retorna el resumen general del último análisis"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Último análisis
        cursor.execute('SELECT * FROM analisis ORDER BY id DESC LIMIT 1')
        analisis = cursor.fetchone()
        
        if not analisis:
            return jsonify({'error': 'No hay análisis disponibles'}), 404
        
        analisis_dict = dict(analisis)
        
        # Recomendaciones del último análisis
        cursor.execute('''
        SELECT * FROM recomendaciones 
        WHERE analisis_id = ? 
        ORDER BY iar DESC
        ''', (analisis_dict['id'],))
        recomendaciones = cursor.fetchall()
        
        # Tickets por categoría
        cursor.execute('''
        SELECT categoria, COUNT(*) as total
        FROM tickets
        GROUP BY categoria
        ''')
        tickets_por_categoria = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            'analisis': analisis_dict,
            'recomendaciones': [dict(r) for r in recomendaciones],
            'tickets_por_categoria': [dict(t) for t in tickets_por_categoria]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/recomendaciones')
def get_recomendaciones():
    """Obtiene todas las recomendaciones del último análisis"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT r.*, m.frecuencia_score, m.complejidad_score, 
               m.impacto_score, m.viabilidad_score, m.total_tickets
        FROM recomendaciones r
        JOIN metricas_categoria m ON r.analisis_id = m.analisis_id 
            AND r.categoria = m.categoria
        WHERE r.analisis_id = (SELECT MAX(id) FROM analisis)
        ORDER BY r.iar DESC
        ''')
        
        recomendaciones = cursor.fetchall()
        conn.close()
        
        return jsonify([dict(r) for r in recomendaciones])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/recomendaciones/<categoria>')
def get_recomendacion_categoria(categoria):
    """Obtiene recomendación de una categoría específica"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT r.*, m.frecuencia_score, m.complejidad_score, 
               m.impacto_score, m.viabilidad_score, m.total_tickets
        FROM recomendaciones r
        JOIN metricas_categoria m ON r.analisis_id = m.analisis_id 
            AND r.categoria = m.categoria
        WHERE r.categoria = ? AND r.analisis_id = (SELECT MAX(id) FROM analisis)
        ''', (categoria,))
        
        recomendacion = cursor.fetchone()
        conn.close()
        
        if recomendacion:
            return jsonify(dict(recomendacion))
        else:
            return jsonify({'error': 'Categoría no encontrada'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/tickets')
def get_tickets():
    """Obtiene todos los tickets con paginación opcional"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        categoria = request.args.get('categoria', None)
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Query base
        query = 'SELECT * FROM tickets'
        params = []
        
        # Filtrar por categoría si se especifica
        if categoria:
            query += ' WHERE categoria = ?'
            params.append(categoria)
        
        # Ordenar y paginar
        query += ' ORDER BY id DESC LIMIT ? OFFSET ?'
        params.extend([per_page, (page - 1) * per_page])
        
        cursor.execute(query, params)
        tickets = cursor.fetchall()
        
        # Contar total
        count_query = 'SELECT COUNT(*) as total FROM tickets'
        if categoria:
            count_query += ' WHERE categoria = ?'
            cursor.execute(count_query, [categoria] if categoria else [])
        else:
            cursor.execute(count_query)
        
        total = cursor.fetchone()['total']
        
        conn.close()
        
        return jsonify({
            'tickets': [dict(t) for t in tickets],
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/estadisticas')
def estadisticas():
    """Obtiene estadísticas generales del sistema"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Total de tickets
        cursor.execute('SELECT COUNT(*) as total FROM tickets')
        total_tickets = cursor.fetchone()['total']
        
        # Tickets por estado
        cursor.execute('''
        SELECT estado, COUNT(*) as count
        FROM tickets
        GROUP BY estado
        ''')
        tickets_por_estado = {row['estado']: row['count'] for row in cursor.fetchall()}
        
        # Tickets por prioridad
        cursor.execute('''
        SELECT prioridad, COUNT(*) as count
        FROM tickets
        GROUP BY prioridad
        ''')
        tickets_por_prioridad = {row['prioridad']: row['count'] for row in cursor.fetchall()}
        
        # Complejidad promedio por categoría
        cursor.execute('''
        SELECT categoria, AVG(complejidad) as avg_complejidad
        FROM tickets
        GROUP BY categoria
        ORDER BY avg_complejidad DESC
        ''')
        complejidad_por_categoria = [dict(row) for row in cursor.fetchall()]
        
        # IAR por categoría
        cursor.execute('''
        SELECT categoria, iar
        FROM recomendaciones
        WHERE analisis_id = (SELECT MAX(id) FROM analisis)
        ORDER BY iar DESC
        ''')
        iar_por_categoria = [dict(row) for row in cursor.fetchall()]
        
        # ROI total potencial
        cursor.execute('''
        SELECT SUM(ahorro_anual_usd) as total_ahorro
        FROM recomendaciones
        WHERE analisis_id = (SELECT MAX(id) FROM analisis)
        ''')
        total_ahorro = cursor.fetchone()['total_ahorro'] or 0
        
        conn.close()
        
        return jsonify({
            'total_tickets': total_tickets,
            'tickets_por_estado': tickets_por_estado,
            'tickets_por_prioridad': tickets_por_prioridad,
            'complejidad_por_categoria': complejidad_por_categoria,
            'iar_por_categoria': iar_por_categoria,
            'ahorro_total_potencial_usd': round(total_ahorro, 2)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/categorias')
def get_categorias():
    """Obtiene lista de todas las categorías"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT DISTINCT categoria 
        FROM tickets 
        ORDER BY categoria
        ''')
        
        categorias = [row['categoria'] for row in cursor.fetchall()]
        conn.close()
        
        return jsonify(categorias)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/metricas/<categoria>')
def get_metricas_categoria(categoria):
    """Obtiene métricas detalladas de una categoría"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM metricas_categoria
        WHERE categoria = ? AND analisis_id = (SELECT MAX(id) FROM analisis)
        ''', (categoria,))
        
        metricas = cursor.fetchone()
        conn.close()
        
        if metricas:
            return jsonify(dict(metricas))
        else:
            return jsonify({'error': 'Categoría no encontrada'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/palabras-clave/<categoria>')
def get_palabras_clave(categoria):
    """Obtiene palabras clave más frecuentes de una categoría"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT palabras_clave
        FROM tickets
        WHERE categoria = ?
        ''', (categoria,))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Contar frecuencia de palabras clave
        from collections import Counter
        all_keywords = []
        
        for row in rows:
            if row['palabras_clave']:
                keywords = json.loads(row['palabras_clave'])
                all_keywords.extend(keywords)
        
        counter = Counter(all_keywords)
        top_keywords = [{'palabra': k, 'frecuencia': v} for k, v in counter.most_common(20)]
        
        return jsonify(top_keywords)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Manejo de error 404"""
    return jsonify({'error': 'Endpoint no encontrado'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Manejo de error 500"""
    return jsonify({'error': 'Error interno del servidor'}), 500


if __name__ == '__main__':
    # Verificar que la BD existe
    if not os.path.exists(DATABASE):
        print("⚠️  ADVERTENCIA: Base de datos no encontrada.")
        print("   Ejecuta primero: python backend/database.py")
        print()
    
    print("="*60)
    print("SEIRA - API Backend")
    print("="*60)
    print(f"Servidor corriendo en: http://localhost:5000")
    print(f"API disponible en: http://localhost:5000/api/")
    print()
    print("Endpoints disponibles:")
    print("  GET  /api/status              - Estado del sistema")
    print("  GET  /api/resumen             - Resumen general")
    print("  GET  /api/recomendaciones     - Todas las recomendaciones")
    print("  GET  /api/recomendaciones/:cat - Recomendación por categoría")
    print("  GET  /api/tickets             - Lista de tickets")
    print("  GET  /api/estadisticas        - Estadísticas generales")
    print("  GET  /api/categorias          - Lista de categorías")
    print("  GET  /api/metricas/:categoria - Métricas de categoría")
    print("="*60)
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)