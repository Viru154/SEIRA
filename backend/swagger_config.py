"""
Configuración de Swagger UI para documentación de API
"""

SWAGGER_CONFIG = {
    "swagger": "2.0",
    "info": {
        "title": "SEIRA 2.0 API",
        "description": "Sistema de Evaluación Inteligente para Implementación Responsable de IA - NEXO GAMER",
        "version": "2.0.0",
        "contact": {
            "name": "Equipo SEIRA",
            "email": "soporte@nexogamer.com"
        }
    },
    "host": "localhost:5000",
    "basePath": "/",
    "schemes": ["http", "https"],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header usando Bearer scheme. Ejemplo: 'Bearer {token}'"
        }
    },
    "tags": [
        {
            "name": "Autenticación",
            "description": "Endpoints de autenticación y autorización"
        },
        {
            "name": "Dashboard",
            "description": "Endpoints del dashboard principal"
        },
        {
            "name": "Recomendaciones",
            "description": "Endpoints de recomendaciones IAR"
        },
        {
            "name": "Métricas",
            "description": "Endpoints de métricas por categoría"
        },
        {
            "name": "Análisis",
            "description": "Endpoints de análisis NLP"
        },
        {
            "name": "Tickets",
            "description": "Gestión de tickets de soporte"
        },
        {
            "name": "Administración",
            "description": "Endpoints administrativos (solo admin)"
        }
    ],
    "paths": {
        "/api/health": {
            "get": {
                "tags": ["Dashboard"],
                "summary": "Health check de la API",
                "responses": {
                    "200": {
                        "description": "API funcionando correctamente"
                    }
                }
            }
        },
        "/api/auth/register": {
            "post": {
                "tags": ["Autenticación"],
                "summary": "Registrar nuevo usuario",
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "required": ["username", "email", "password"],
                            "properties": {
                                "username": {"type": "string", "example": "juan_perez"},
                                "email": {"type": "string", "example": "juan@example.com"},
                                "password": {"type": "string", "example": "Password123"},
                                "nombre_completo": {"type": "string", "example": "Juan Pérez"}
                            }
                        }
                    }
                ],
                "responses": {
                    "201": {"description": "Usuario registrado exitosamente"},
                    "400": {"description": "Error de validación"}
                }
            }
        },
        "/api/auth/login": {
            "post": {
                "tags": ["Autenticación"],
                "summary": "Iniciar sesión",
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {
                            "type": "object",
                            "required": ["username", "password"],
                            "properties": {
                                "username": {"type": "string", "example": "admin"},
                                "password": {"type": "string", "example": "Admin123"}
                            }
                        }
                    }
                ],
                "responses": {
                    "200": {"description": "Login exitoso"},
                    "401": {"description": "Credenciales inválidas"}
                }
            }
        },
        "/api/dashboard/resumen": {
            "get": {
                "tags": ["Dashboard"],
                "summary": "Obtener KPIs principales",
                "security": [{"Bearer": []}],
                "responses": {
                    "200": {"description": "KPIs del dashboard"}
                }
            }
        },
        "/api/recomendaciones": {
            "get": {
                "tags": ["Recomendaciones"],
                "summary": "Obtener todas las recomendaciones",
                "security": [{"Bearer": []}],
                "responses": {
                    "200": {"description": "Lista de recomendaciones"}
                }
            }
        }
    }
}

def get_swagger_template():
    """Generar template de Swagger UI"""
    return SWAGGER_CONFIG