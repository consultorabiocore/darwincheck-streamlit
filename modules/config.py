# ============================================================================ #
#          DarwinCheck Vol.1 - Auditoría Taxonómica y Geográfica             #
#                         MÓDULO: CONFIGURACIÓN                              #
# ============================================================================ #

import os
from pathlib import Path

# ==================== DIRECTORIOS ====================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = BASE_DIR / "cache"
TEMP_DIR = BASE_DIR / "temp"

# Crear directorios si no existen
for directory in [DATA_DIR, CACHE_DIR, TEMP_DIR]:
    directory.mkdir(exist_ok=True)

# ==================== ARCHIVOS ====================
SIMBIO_FILE = DATA_DIR / "SIMBIO_Especies_2026-02-19.xlsx"
LOGO_FILE = BASE_DIR / "logo.png"

# ==================== CONFIGURACIÓN ====================
MAX_FILE_SIZE_MB = 50
MAX_ROWS_PROCESS = 100000
MAX_ROWS_DISPLAY = 5000
MAX_SPECIES_CHARTS = 30
TOP_SPECIES_DISPLAY = 20

# ==================== GBIF ====================
GBIF_API_URL = "https://api.gbif.org/v1/species/match"
GBIF_TIMEOUT = 5
GBIF_CACHE_EXPIRY = 86400  # 24 horas

# ==================== COORDENADAS CHILE ====================
CHILE_BOUNDS = {
    "continental": {
        "lat_min": -56.0,
        "lat_max": -17.5,
        "lon_min": -76.0,
        "lon_max": -66.0
    },
    "rapa_nui": {
        "lat": -27.1,
        "lon": -109.4,
        "tolerance": 0.5
    },
    "juan_fernandez": {
        "lat": -33.6,
        "lon": -78.8,
        "tolerance": 0.5
    }
}

# ==================== COLUMNAS DARWIN CORE ====================
DARWIN_CORE_COLUMNS = {
    "reino": 15,
    "filo": 16,
    "clase": 17,
    "orden": 18,
    "familia": 19,
    "genero": 20,
    "epiteto": 22,
    "nombre_comun": 24,
    "valor": 30,
    "anio": 5,
    "mes": 6,
    "dia": 7,
    "hora_inicio": 8,
    "lat": 32,
    "lon": 33,
    "hora_registro": 34
}

# ==================== ESTILOS ====================
COLOR_SUCCESS = "#27ae60"
COLOR_WARNING = "#f39c12"
COLOR_ERROR = "#e74c3c"
COLOR_INFO = "#3498db"
COLOR_SIDEBAR = "#2c3e50"
COLOR_BG = "#ecf0f1"

# ==================== TEXTO ====================
APP_TITLE = "DarwinCheck Vol.1 - Auditoría Taxonómica y Geográfica"
APP_AUTHOR = "Loreto Campos © 2026 - BioCore"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeY63B4iIxCthAPo1eHgOySie6ljdkX_yiLSeto8MaEf2EOdg/viewform?usp=dialog"

# ==================== MENSAJES ====================
MSG_LOADING_FILE = "📂 Leyendo archivo..."
MSG_PROCESSING = "⏳ Procesando archivo..."
MSG_COMPLETE = "✅ Procesamiento completado"
MSG_NO_DATA = "❌ Archivo vacío o no válido"
MSG_NO_AMBIGUITIES = "✅ No se detectaron ambigüedades. Todos los registros fueron corregidos correctamente."
