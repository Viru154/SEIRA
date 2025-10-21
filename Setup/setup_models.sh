#!/bin/bash
# Script para configurar modelos SQLAlchemy de SEIRA 2.0
# Uso: bash setup_models.sh

set -e  # Salir si hay error

echo "🚀 Configurando modelos SQLAlchemy para SEIRA 2.0..."
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar que estamos en la raíz del proyecto
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ Error: Debes ejecutar este script desde la raíz del proyecto SEIRA${NC}"
    echo "   Usa: cd ~/Escritorio/10mo\ Semestre/Seminario\ de\ Tecnologias\ de\ Informacion/seira/seira/"
    exit 1
fi

echo -e "${GREEN}✓${NC} Directorio correcto detectado"

# Crear directorios necesarios
echo ""
echo "📁 Verificando estructura de directorios..."
mkdir -p backend/models
mkdir -p backend/utils
mkdir -p backend/scripts
mkdir -p backend/services

# Crear __init__.py necesarios
touch backend/__init__.py
touch backend/models/__init__.py
touch backend/utils/__init__.py
touch backend/scripts/__init__.py
touch backend/services/__init__.py

echo -e "${GREEN}✓${NC} Estructura de directorios creada"

# Verificar archivos que deben existir
echo ""
echo "🔍 Verificando archivos existentes..."

declare -A files_to_check=(
    ["backend/config.py"]="Config"
    ["backend/utils/database.py"]="Database Manager"
    ["backend/scripts/migrate_sqlite_to_postgres.py"]="Migration Script"
)

for file in "${!files_to_check[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} ${files_to_check[$file]}: $file"
    else
        echo -e "${YELLOW}⚠${NC}  ${files_to_check[$file]}: $file (falta, se creará)"
    fi
done

# Crear base.py
echo ""
echo "📝 Creando backend/models/base.py..."
cat > backend/models/base.py << 'EOF'
"""
Base declarativa de SQLAlchemy compartida por todos los modelos
"""
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
EOF

if [ -f "backend/models/base.py" ]; then
    echo -e "${GREEN}✓${NC} base.py creado correctamente"
else
    echo -e "${RED}❌${NC} Error al crear base.py"
    exit 1
fi

# Verificar modelos
echo ""
echo "🔍 Verificando modelos..."

declare -a models=("ticket" "analisis" "recomendacion" "metrica")

for model in "${models[@]}"; do
    file="backend/models/${model}.py"
    if [ -f "$file" ]; then
        # Verificar si ya importa desde base.py
        if grep -q "from backend.models.base import Base" "$file"; then
            echo -e "${GREEN}✓${NC} ${model}.py - Ya usa base.py"
        else
            echo -e "${YELLOW}⚠${NC}  ${model}.py - Necesita actualización"
        fi
    else
        echo -e "${RED}✗${NC} ${model}.py - NO EXISTE (se debe crear con artifacts)"
    fi
done

# Mostrar resumen
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "📊 RESUMEN DE VERIFICACIÓN"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Contar archivos existentes
total_files=0
existing_files=0

for model in "${models[@]}"; do
    total_files=$((total_files + 1))
    if [ -f "backend/models/${model}.py" ]; then
        existing_files=$((existing_files + 1))
    fi
done

echo "Archivos de modelos: $existing_files/$total_files"
echo ""

# Árbol de estructura
echo "📂 Estructura de backend/models/:"
tree backend/models/ -L 1 2>/dev/null || ls -la backend/models/

echo ""
echo "═══════════════════════════════════════════════════════════"

# Siguiente paso
echo ""
echo "🎯 SIGUIENTE PASO:"
echo ""
echo "Los modelos serán actualizados vía artifacts de Claude."
echo "Espera las actualizaciones de los archivos:"
echo "  - ticket.py"
echo "  - analisis.py"
echo "  - recomendacion.py"
echo "  - metrica.py"
echo "  - __init__.py"
echo ""
echo "Después ejecuta: python test_connection.py"
echo ""