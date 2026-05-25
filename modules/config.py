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
SIMBIO_FILE = DATA_DIR / "SIMBIO_Especies_2026-02-19.xlsx"

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

# ==================== VERSIÓN ====================
VERSION = "1.0.0"
FECHA = datetime.now().strftime("%Y-%m-%d")
