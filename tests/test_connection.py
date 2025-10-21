#!/usr/bin/env python3
"""Probar conexión a PostgreSQL"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.utils.database import db_manager, init_db

# Probar conexión
print("🔧 Probando conexión a PostgreSQL...")
if db_manager.test_connection():
    print("✅ Conexión exitosa!")
    
    # Crear tablas
    print("\n🔧 Creando tablas...")
    init_db()
    print("✅ Tablas creadas!")
    
    # Ver estadísticas
    stats = db_manager.get_table_stats()
    print("\n📊 Estado de las tablas:")
    for table, count in stats.items():
        print(f"  {table}: {count:,} registros")
else:
    print("❌ Error de conexión")
    sys.exit(1)