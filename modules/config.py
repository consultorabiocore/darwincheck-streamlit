# ============================================================================ #
#                    DarwinCheck - Configuración Global                       #
# ============================================================================ #

from pathlib import Path
from datetime import datetime

# ==================== RUTAS ====================
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
CACHE_DIR = BASE_DIR / "cache"
TEMP_DIR = BASE_DIR / "temp"

# Crear directorios si no existen
for dir_path in [DATA_DIR, LOGS_DIR, CACHE_DIR, TEMP_DIR]:
    dir_path.mkdir(exist_ok=True)

# ==================== ARCHIVOS ====================
LOGO_FILE = BASE_DIR / "logo.png"
SIMBIO_FILE = BASE_DIR / "SIMBIO_Especies_2026-02-19.xlsx"

# ==================== DARWIN CORE - ÍNDICES DE COLUMNAS ====================
DARWIN_CORE_COLS = {
    'año': 4,
    'mes': 5,
    'dia': 6,
    'hora_inicio': 7,
    'reino': 14,
    'filo': 15,
    'clase': 16,
    'orden': 17,
    'familia': 18,
    'genero': 19,
    'epiteto_especifico': 21,
    'nombre_comun': 23,
    'valor': 29,
    'latitud': 31,
    'longitud': 32,
    'hora_registro': 33,
}

# ==================== SIMBIO - COLUMNAS ====================
SIMBIO_COLS = {
    'genero': 'Género',
    'epiteto': 'Epíteto específico',
    'estado_conservacion': 'Estado de Conservación vigente',
    'nombre_comun': 'Nombre común',
    'reino': 'Reino',
    'filo': 'Filo o División',
    'clase': 'Clase',
    'orden': 'Orden',
    'familia': 'Familia',
}

# ==================== GBIF ====================
GBIF_API_BASE = "https://api.gbif.org/v1"
GBIF_TIMEOUT = 5
GBIF_CACHE_SIZE = 1000

# ==================== COORDENADAS - CHILE ====================
CHILE_CONTINENTAL = {
    'lat_min': -56.0,
    'lat_max': -17.5,
    'lon_min': -76.0,
    'lon_max': -66.0,
}

RAPA_NUI = {
    'lat': -27.1,
    'lon': -109.4,
    'tolerancia': 0.5,
}

JUAN_FERNANDEZ = {
    'lat': -33.6,
    'lon': -78.8,
    'tolerancia': 0.5,
}

# ==================== MENSAJES ====================
MSG_INICIO = """
### 📖 ¿Cómo usar DarwinCheck Vol.1?

**DarwinCheck** es una herramienta de auditoría taxonómica y geográfica para datos Darwin Core.

#### 🎯 Pasos principales:

1. **Cargar archivo Excel** con estructura Darwin Core (mínimo 34 columnas)
2. **Seleccionar color** para los gráficos (opcional)
3. El sistema automáticamente:
   - ✅ Normaliza datos taxonómicos
   - ✅ Valida coordenadas dentro de Chile
   - ✅ Calcula índices ecológicos
   - ✅ Genera reportes de auditoría

#### 📊 Visualizaciones disponibles:
- **Abundancia**: Especies más representadas
- **Dominancia**: Distribución con Treemap
- **Riqueza**: Número de especies (Lollipop)
- **Curva de acumulación**: Rarefacción de especies
- **Conservación**: Estados de protección
- **Datos**: Tabla completa con correcciones

#### 🛠️ Archivos soportados:
- Formato: `.xlsx` o `.xls`
- Mínimo: 34 columnas Darwin Core
- Hoja requerida: "Ocurrencia"

#### 📝 Contacto:
BioCore © 2026 - Loreto Campos
"""

# ==================== VERSIÓN ====================
VERSION = "1.0.0"
FECHA = datetime.now().strftime("%Y-%m-%d")
