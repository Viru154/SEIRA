"""
SEIRA 2.0 - Flask Application con Flask-Login
Sistema de usuarios simple sin JWT
"""
import os
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_login import LoginManager
from flask_swagger_ui import get_swaggerui_blueprint
from api.routes import api
from api.auth import auth_bp
from swagger_config import get_swagger_template
from models.user import User
from utils.database import db_manager

def create_app():
    app = Flask(__name__, static_folder='../frontend/build')
    
    # Config simple
    app.config['SECRET_KEY'] = 'seira-secret-2024-simple'
    app.config['JSON_SORT_KEYS'] = False
    
    # Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        with db_manager.session_scope() as session:
            user = session.query(User).get(int(user_id))
            if user:
                # Hacer expunge para que el objeto no esté ligado a la sesión
                session.expunge(user)
            return user
    
    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({
            'success': False,
            'error': 'No autorizado. Inicia sesión primero.'
        }), 401
    
    # CORS CORREGIDO - Permitir credenciales
    CORS(app, 
         origins=["http://localhost:3000"],
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         expose_headers=["Content-Type"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    # Agregar headers CORS a todas las respuestas
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    # Blueprints
    app.register_blueprint(api)
    app.register_blueprint(auth_bp)
    
    # Swagger
    SWAGGER_URL = '/api/docs'
    API_URL = '/api/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    @app.route('/api/swagger.json')
    def swagger_json():
        return jsonify(get_swagger_template())
    
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'version': '2.0.0',
            'auth': 'flask-login'
        }), 200
    
    # Frontend
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        if path != "" and os.path.exists(app.static_folder + '/' + path):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, 'index.html')
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*70)
    print("🚀 SEIRA 2.0 - Sistema con Flask-Login")
    print("="*70)
    print("📊 Dashboard: http://localhost:5000")
    print("🔐 API Docs: http://localhost:5000/api/docs")
    print("✅ Auth simple sin JWT")
    print("="*70 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)