"""
Gestión de conexión a PostgreSQL con SQLAlchemy
"""
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from contextlib import contextmanager
import logging

from config import get_config
from models import Base

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestor de base de datos PostgreSQL"""
    
    def __init__(self):
        self.config = get_config()
        self.engine = None
        self.SessionLocal = None
        
    def init_engine(self):
        """Inicializar engine de SQLAlchemy"""
        if self.engine is not None:
            logger.info("Engine ya inicializado")
            return self.engine
        
        logger.info(f"Conectando a PostgreSQL: {self.config.DATABASE_URL.split('@')[1]}")
        
        # Crear engine con configuración optimizada
        self.engine = create_engine(
            self.config.DATABASE_URL,
            echo=self.config.SQLALCHEMY_ECHO,
            **self.config.SQLALCHEMY_ENGINE_OPTIONS
        )
        
        # Event listeners para optimización
        @event.listens_for(self.engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            """Configurar conexión al conectar"""
            logger.debug("Nueva conexión PostgreSQL establecida")
        
        @event.listens_for(self.engine, "checkout")
        def receive_checkout(dbapi_conn, connection_record, connection_proxy):
            """Verificar conexión al obtenerla del pool"""
            pass
        
        # Crear SessionLocal
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        logger.info("✅ Engine PostgreSQL inicializado correctamente")
        return self.engine
    
    def create_all_tables(self):
        """Crear todas las tablas definidas en los modelos"""
        if self.engine is None:
            self.init_engine()
        
        logger.info("Creando tablas en PostgreSQL...")
        Base.metadata.create_all(bind=self.engine)
        logger.info("✅ Tablas creadas correctamente")
    
    def drop_all_tables(self):
        """Eliminar todas las tablas (¡CUIDADO!)"""
        if self.engine is None:
            self.init_engine()
        
        logger.warning("⚠️  ELIMINANDO todas las tablas...")
        Base.metadata.drop_all(bind=self.engine)
        logger.info("Tablas eliminadas")
    
    def get_session(self) -> Session:
        """Obtener sesión de base de datos"""
        if self.SessionLocal is None:
            self.init_engine()
        return self.SessionLocal()
    
    @contextmanager
    def session_scope(self):
        """Context manager para sesiones con auto-commit/rollback"""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error en sesión DB: {e}")
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """Probar conexión a la base de datos"""
        try:
            if self.engine is None:
                self.init_engine()
            
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                logger.info(f"✅ Conexión exitosa: {version}")
                return True
        except Exception as e:
            logger.error(f"❌ Error de conexión: {e}")
            return False
    
    def get_table_stats(self) -> dict:
        """Obtener estadísticas de las tablas"""
        try:
            with self.engine.connect() as conn:
                stats = {}
                
                # Contar registros por tabla
                tables = ['tickets', 'analisis', 'recomendaciones', 'metricas_categoria']
                for table in tables:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.fetchone()[0]
                    stats[table] = count
                
                return stats
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    def close(self):
        """Cerrar conexiones"""
        if self.engine:
            self.engine.dispose()
            logger.info("Conexiones cerradas")


# Instancia global
db_manager = DatabaseManager()

# Funciones de conveniencia
def get_db_session() -> Session:
    """Obtener sesión de base de datos (para usar con dependencias)"""
    return db_manager.get_session()

def init_db():
    """Inicializar base de datos"""
    db_manager.init_engine()
    db_manager.create_all_tables()

def test_db_connection():
    """Probar conexión"""
    return db_manager.test_connection()