#!/bin/bash
# Script para actualizar imports de los modelos a usar base.py
# Uso: bash update_models.sh

set -e

echo "🔄 Actualizando imports de modelos SQLAlchemy..."
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Función para actualizar un modelo
update_model() {
    local file=$1
    local model_name=$2
    
    echo -n "Actualizando $model_name... "
    
    # Backup
    cp "$file" "${file}.backup"
    
    # Reemplazar import de Base
    sed -i 's/from sqlalchemy.ext.declarative import declarative_base/from backend.models.base import Base/' "$file"
    
    # Eliminar línea que define Base
    sed -i '/^Base = declarative_base()$/d' "$file"
    
    # Eliminar líneas vacías duplicadas
    sed -i '/^$/N;/^\n$/D' "$file"
    
    echo -e "${GREEN}✓${NC}"
}

# Actualizar cada modelo
update_model "backend/models/ticket.py" "ticket.py"
update_model "backend/models/analisis.py" "analisis.py"
update_model "backend/models/recomendacion.py" "recomendacion.py"
update_model "backend/models/metrica.py" "metrica.py"

# Actualizar __init__.py
echo -n "Actualizando __init__.py... "
cat > backend/models/__init__.py << 'EOF'
"""
Modelos SQLAlchemy para SEIRA 2.0
PostgreSQL con soporte para millones de registros
"""
# Importar Base primero desde su módulo dedicado
from backend.models.base import Base

# Importar todos los modelos
from backend.models.ticket import Ticket
from backend.models.analisis import Analisis
from backend.models.recomendacion import Recomendacion
from backend.models.metrica import MetricaCategoria

# Exportar todo
__all__ = [
    'Base',
    'Ticket',
    'Analisis',
    'Recomendacion',
    'MetricaCategoria'
]
EOF
echo -e "${GREEN}✓${NC}"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ ACTUALIZACIÓN COMPLETADA${NC}"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "📋 Archivos actualizados:"
echo "  ✓ backend/models/ticket.py"
echo "  ✓ backend/models/analisis.py"
echo "  ✓ backend/models/recomendacion.py"
echo "  ✓ backend/models/metrica.py"
echo "  ✓ backend/models/__init__.py"
echo ""
echo "💾 Backups guardados con extensión .backup"
echo ""
echo "🧪 SIGUIENTE PASO: Probar conexión"
echo "   $ python test_connection.py"
echo ""