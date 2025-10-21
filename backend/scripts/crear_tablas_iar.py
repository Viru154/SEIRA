"""
Script para crear las tablas de IAR en PostgreSQL
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.database import db_manager
from models.base import Base
from models.recomendacion import Recomendacion
from models.metrica import MetricaCategoria  # Cambio: usar metrica
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def crear_tablas():
    """Crea las tablas de recomendaciones y métricas (si no existen)"""
    
    print("=" * 60)
    print("🗄️  SEIRA 2.0 - Verificación de Tablas IAR")
    print("=" * 60)
    print()
    
    try:
        # Inicializar engine
        engine = db_manager.init_engine()
        
        # Verificar si las tablas ya existen
        logger.info("📋 Verificando tablas: recomendaciones, metricas_categoria")
        
        # Crear tablas solo si no existen
        Recomendacion.__table__.create(engine, checkfirst=True)
        MetricaCategoria.__table__.create(engine, checkfirst=True)
        
        logger.info("✅ Tablas verificadas/creadas exitosamente")
        
        # Verificar
        print("\n📊 Verificando tablas...")
        session = db_manager.get_session()
        
        try:
            # Contar registros
            count_recom = session.query(Recomendacion).count()
            count_metricas = session.query(MetricaCategoria).count()
            
            print(f"✅ Tabla 'recomendaciones': {count_recom} registros")
            print(f"✅ Tabla 'metricas_categoria': {count_metricas} registros")
            
        finally:
            session.close()
        
        print("\n" + "=" * 60)
        print("✅ Tablas IAR listas para usar")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Error creando tablas: {str(e)}")
        raise

if __name__ == "__main__":
    crear_tablas()