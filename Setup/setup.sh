#!/bin/bash

# SEIRA - Script de Setup Inicial
# Para Linux (Kubuntu)

echo "=========================================="
echo "SEIRA - Configuración Inicial"
echo "=========================================="

# Crear estructura de directorios
echo "📁 Creando estructura de directorios..."
mkdir -p seira/{backend/{models,services,utils},data/{raw,processed,synthetic},frontend/{static/{css,js},templates},tests,docs}

# Crear archivos base
touch seira/backend/app.py
touch seira/backend/__init__.py
touch seira/backend/models/__init__.py
touch seira/backend/services/__init__.py
touch seira/backend/utils/__init__.py
touch seira/backend/config.py
touch seira/backend/database.py

echo "✅ Estructura creada"

# Crear requirements.txt
echo "📝 Creando requirements.txt..."
cat > seira/requirements.txt << EOF
# Core
Flask==3.0.0
Flask-CORS==4.0.0

# Data processing
pandas==2.1.0
numpy==1.24.0

# NLP - spaCy
spacy==3.7.0

# NLP - Hugging Face (sin PyTorch pesado)
transformers==4.35.0
sentencepiece==0.1.99

# Utilities
python-dotenv==1.0.0
faker==20.0.0

# Database
SQLAlchemy==2.0.0
EOF

echo "✅ requirements.txt creado"

# Crear archivo .env para configuración
echo "🔧 Creando archivo de configuración..."
cat > seira/.env << EOF
# Configuración SEIRA

# Modo de IA (huggingface u openai)
AI_MODE=huggingface

# API Keys (dejar vacío si no se usa)
OPENAI_API_KEY=

# Base de datos
DATABASE_URL=sqlite:///seira.db

# Flask
FLASK_ENV=development
FLASK_DEBUG=True
EOF

echo "✅ .env creado"

# Crear .gitignore
cat > seira/.gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# Database
*.db
*.sqlite

# Environment
.env

# IDE
.vscode/
.idea/

# Data
data/raw/*
data/processed/*
!data/raw/.gitkeep
!data/processed/.gitkeep
EOF

echo "✅ .gitignore creado"

echo ""
echo "=========================================="
echo "Instalando dependencias..."
echo "=========================================="

cd seira

# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Actualizar pip
pip install --upgrade pip

# Instalar dependencias
pip install -r requirements.txt

# Descargar modelo de spaCy en español
echo ""
echo "📥 Descargando modelo de spaCy (español)..."
python -m spacy download es_core_news_sm

echo ""
echo "=========================================="
echo "✅ Setup completado!"
echo "=========================================="
echo ""
echo "Próximos pasos:"
echo "1. cd seira"
echo "2. source venv/bin/activate"
echo "3. Ejecutar scripts de desarrollo"
echo ""
echo "El entorno virtual está activado."
EOF

chmod +x setup.sh
echo "✅ Script de setup creado"

# SEIRA - Script de Setup Inicial
# Para Linux (Kubuntu)

echo "=========================================="
echo "SEIRA - Configuración Inicial"
echo "=========================================="

# Crear estructura de directorios
echo "📁 Creando estructura de directorios..."
mkdir -p seira/{backend/{models,services,utils},data/{raw,processed,synthetic},frontend/{static/{css,js},templates},tests,docs}

# Crear archivos base
touch seira/backend/app.py
touch seira/backend/__init__.py
touch seira/backend/models/__init__.py
touch seira/backend/services/__init__.py
touch seira/backend/utils/__init__.py
touch seira/backend/config.py
touch seira/backend/database.py

echo "✅ Estructura creada"

# Crear requirements.txt
echo "📝 Creando requirements.txt..."
cat > seira/requirements.txt << EOF
# Core
Flask==3.0.0
Flask-CORS==4.0.0

# Data processing
pandas==2.1.0
numpy==1.24.0

# NLP - spaCy
spacy==3.7.0

# NLP - Hugging Face (sin PyTorch pesado)
transformers==4.35.0
sentencepiece==0.1.99

# Utilities
python-dotenv==1.0.0
faker==20.0.0

# Database
SQLAlchemy==2.0.0
EOF

echo "✅ requirements.txt creado"

# Crear archivo .env para configuración
echo "🔧 Creando archivo de configuración..."
cat > seira/.env << EOF
# Configuración SEIRA

# Modo de IA (huggingface u openai)
AI_MODE=huggingface

# API Keys (dejar vacío si no se usa)
OPENAI_API_KEY=

# Base de datos
DATABASE_URL=sqlite:///seira.db

# Flask
FLASK_ENV=development
FLASK_DEBUG=True
EOF

echo "✅ .env creado"

# Crear .gitignore
cat > seira/.gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# Database
*.db
*.sqlite

# Environment
.env

# IDE
.vscode/
.idea/

# Data
data/raw/*
data/processed/*
!data/raw/.gitkeep
!data/processed/.gitkeep
EOF

echo "✅ .gitignore creado"

echo ""
echo "=========================================="
echo "Instalando dependencias..."
echo "=========================================="

cd seira

# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Actualizar pip
pip install --upgrade pip

# Instalar dependencias
pip install -r requirements.txt

# Descargar modelo de spaCy en español
echo ""
echo "📥 Descargando modelo de spaCy (español)..."
python -m spacy download es_core_news_sm

echo ""
echo "=========================================="
echo "✅ Setup completado!"
echo "=========================================="
echo ""
echo "Próximos pasos:"
echo "1. cd seira"
echo "2. source venv/bin/activate"
echo "3. Ejecutar scripts de desarrollo"
echo ""
echo "El entorno virtual está activado."
EOF

chmod +x setup.sh
echo "✅ Script de setup creado"
