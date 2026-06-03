# ============================================================================ #
#          DarwinCheck Vol.1 - Auditoría Taxonómica y Geográfica             #
#               Versión Python/Streamlit (MIGRACIÓN DESDE R)                 #
# ============================================================================ #

import streamlit as st
import sys
from pathlib import Path

print("🔍 [INICIO] Iniciando app.py...")

# ==================== CONFIGURAR RUTA ====================
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

print(f"✅ BASE_DIR: {BASE_DIR}")
print(f"✅ sys.path configurado")

# ==================== INICIALIZAR DIRECTORIOS ====================
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
CACHE_DIR = BASE_DIR / "cache"
TEMP_DIR = BASE_DIR / "temp"

for dir_path in [DATA_DIR, LOGS_DIR, CACHE_DIR, TEMP_DIR]:
    dir_path.mkdir(exist_ok=True)

print(f"✅ Directorios creados")

# ==================== IMPORTS ====================
try:
    print("📦 Importando pandas, numpy...")
    import pandas as pd
    import numpy as np
    from datetime import datetime
    from io import BytesIO
    import warnings
    warnings.filterwarnings('ignore')
    print("✅ Imports básicos OK")
except Exception as e:
    print(f"❌ Error en imports básicos: {e}")
    st.error(f"Error: {e}")
    sys.exit(1)

# ==================== IMPORTAR MÓDULOS ====================
try:
    print("📦 Importando modules.utils...")
    from modules.utils import (
        safe_val, normalizar_texto, limpiar_dataframe, fmt_entero, fmt_decimal,
        fmt_coordenada, detectar_encabezado, formatar_hora, gms_a_decimal,
        registrar_log
    )
    print("✅ modules.utils OK")
except Exception as e:
    print(f"❌ Error importando modules.utils: {e}")
    import traceback
    traceback.print_exc()
    st.error(f"Error en modules.utils: {e}")
    sys.exit(1)

try:
    print("📦 Importando modules.config...")
    from modules import config
    print("✅ modules.config OK")
except Exception as e:
    print(f"❌ Error importando modules.config: {e}")
    st.error(f"Error en modules.config: {e}")
    sys.exit(1)

try:
    print("📦 Importando modules.taxonomia...")
    from modules.taxonomia import gestor_taxonomia
    print("✅ modules.taxonomia OK")
except Exception as e:
    print(f"❌ Error importando modules.taxonomia: {e}")
    import traceback
    traceback.print_exc()
    st.error(f"Error en modules.taxonomia: {e}")
    sys.exit(1)

try:
    print("📦 Importando modules.coordenadas...")
    from modules.coordenadas import validador
    print("✅ modules.coordenadas OK")
except Exception as e:
    print(f"❌ Error importando modules.coordenadas: {e}")
    st.error(f"Error en modules.coordenadas: {e}")
    sys.exit(1)

try:
    print("📦 Importando modules.ecologia...")
    from modules.ecologia import calc_ecologico
    print("✅ modules.ecologia OK")
except Exception as e:
    print(f"❌ Error importando modules.ecologia: {e}")
    st.error(f"Error en modules.ecologia: {e}")
    sys.exit(1)

try:
    print("📦 Importando modules.graficos...")
    from modules.graficos import gen_graficos
    print("✅ modules.graficos OK")
except Exception as e:
    print(f"❌ Error importando modules.graficos: {e}")
    st.error(f"Error en modules.graficos: {e}")
    sys.exit(1)

try:
    print("📦 Importando modules.excel_io...")
    from modules.excel_io import gestor_excel
    print("✅ modules.excel_io OK")
except Exception as e:
    print(f"❌ Error importando modules.excel_io: {e}")
    st.error(f"Error en modules.excel_io: {e}")
    sys.exit(1)

print("✅ TODOS LOS MÓDULOS IMPORTADOS EXITOSAMENTE\n")

# ==================== CONFIGURACIÓN STREAMLIT ====================
st.set_page_config(
    page_title="DarwinCheck Vol.1",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== INICIALIZAR SESSION STATE ====================
if 'datos_originales' not in st.session_state:
    st.session_state.datos_originales = None
    st.session_state.datos_corregidos = None
    st.session_state.selecciones_manuales = {}
    st.session_state.color_grafico = "#27ae60"

# ==================== HEADER ====================
st.markdown("<h1>🔬 DarwinCheck Vol.1</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center; color:#7f8c8d;'>Auditoría Taxonómica y Geográfica</h3>", 
           unsafe_allow_html=True)

st.success("✅ Aplicación cargada correctamente")
st.info("👈 Carga un archivo Excel en el panel lateral para comenzar")
