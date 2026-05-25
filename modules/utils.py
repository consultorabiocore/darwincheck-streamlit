# ============================================================================ #
#                    DarwinCheck - Funciones Auxiliares                       #
# ============================================================================ #

import re
import unicodedata
from datetime import datetime
import logging
from pathlib import Path
import numpy as np
import pandas as pd
from modules.config import LOGS_DIR

# ==================== LOGGING ====================
LOG_FILE = LOGS_DIR / f"darwincheck_{datetime.now().strftime('%Y%m%d')}.log"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler(LOG_FILE)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def registrar_log(mensaje, nivel="INFO"):
    """Registra mensaje en log."""
    if nivel == "ERROR":
        logger.error(mensaje)
    elif nivel == "WARNING":
        logger.warning(mensaje)
    else:
        logger.info(mensaje)


# ==================== VALORES SEGUROS ====================
def safe_val(x, default=""):
    """Convierte valor a string seguro."""
    if x is None or pd.isna(x):
        return default
    
    x = str(x).strip()
    
    # Remover valores nulos conocidos
    if x.lower() in ["na", "null", "n/a", "none", "nan"]:
        return default
    
    if x == "":
        return default
    
    return x


# ==================== NORMALIZACIÓN ====================
def normalizar_texto(texto):
    """Normaliza texto: remove acentos, espacios extras."""
    if not isinstance(texto, str):
        return ""
    
    # Remover espacios extras
    texto = re.sub(r'\s+', ' ', texto).strip()
    
    # Remover acentos (opcional, para búsquedas)
    # texto = ''.join(c for c in unicodedata.normalize('NFD', texto)
    #                if unicodedata.category(c) != 'Mn')
    
    return texto


def limpiar_dataframe(df):
    """Limpia dataframe: valores nulos, espacios, etc."""
    df = df.copy()
    
    # Convertir a string
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace(['NA', 'na', 'null', 'None'], '')
    
    return df


# ==================== FORMATOS ====================
def fmt_entero(x, default="0"):
    """Formatea número entero con miles."""
    try:
        if pd.isna(x) or x is None:
            return default
        
        x = float(x)
        return f"{int(x):,.0f}".replace(",", ".")
    except:
        return default


def fmt_decimal(x, decimales=2, default="0"):
    """Formatea número decimal con miles y coma decimal."""
    try:
        if pd.isna(x) or x is None:
            return default
        
        x = float(x)
        formato = f"{{:,.{decimales}f}}"
        resultado = formato.format(x)
        
        # Cambiar punto a coma en decimales
        return resultado.replace(",", "|").replace(".", ",").replace("|", ".")
    except:
        return default


def fmt_coordenada(x, decimales=5):
    """Formatea coordenada con coma decimal y al menos 5 decimales."""
    if pd.isna(x) or x is None or x == "":
        return None
    
    try:
        num = float(str(x).replace(",", "."))
        resultado = f"{num:.{decimales}f}".replace(".", ",")
        return resultado
    except:
        return None


# ==================== COORDENADAS ====================
def gms_a_decimal(coord):
    """Convierte GMS (Grados Minutos Segundos) a Decimal."""
    if coord is None or coord == "" or pd.isna(coord):
        return np.nan
    
    coord = str(coord).strip()
    
    # Si no tiene símbolos de GMS, es decimal
    if not re.search(r'°|\'|"', coord):
        try:
            return float(coord.replace(",", "."))
        except:
            return np.nan
    
    # Extraer números
    nums = re.findall(r'[\d.,]+', coord)
    try:
        nums = [float(n.replace(",", ".")) for n in nums]
    except:
        return np.nan
    
    if len(nums) == 0:
        return np.nan
    
    # GMS to Decimal: D + M/60 + S/3600
    decimal = nums[0]
    if len(nums) > 1:
        decimal += nums[1] / 60
    if len(nums) > 2:
        decimal += nums[2] / 3600
    
    # Negativo si S, W, O
    if re.search(r'S|W|O|-', coord, re.IGNORECASE):
        decimal *= -1
    
    return decimal


# ==================== HORA ====================
def formatar_hora(valor):
    """Formatea hora a formato HH:MM."""
    if valor is None or valor == "" or pd.isna(valor):
        return None
    
    valor = str(valor).strip()
    
    # Si ya está en formato HH:MM
    if re.match(r'^\d{2}:\d{2}', valor):
        return re.search(r'\d{2}:\d{2}', valor).group()
    
    # Intentar parsear número
    try:
        num = float(valor.replace(",", "."))
        
        # Si es 0-23, horas
        if 0 <= num <= 23 and num == int(num):
            return f"{int(num):02d}:00"
        
        # Si es 0-2400, formato HHMM
        if 0 < num < 2400 and num == int(num):
            horas = int(num) // 100
            minutos = int(num) % 100
            if horas < 24 and minutos < 60:
                return f"{horas:02d}:{minutos:02d}"
        
        # Si es 0-1, fracción del día
        if 0 <= num <= 1:
            segundos_totales = int(num * 86400)
            horas = (segundos_totales // 3600) % 24
            minutos = (segundos_totales % 3600) // 60
            return f"{horas:02d}:{minutos:02d}"
    
    except:
        pass
    
    return None


# ==================== DETECCIÓN ====================
def detectar_encabezado(reino, filo, clase, orden, familia, genero):
    """Detecta si una fila es encabezado."""
    palabras_clave = [
        "reino", "phylum", "class", "order", "family", "genus",
        "clase", "orden", "familia", "género", "filo",
        "epiteto", "specific", "name", "nombre"
    ]
    
    valores = [reino, filo, clase, orden, familia, genero]
    valores_lower = [str(v).lower() for v in valores if v and v != ""]
    
    coincidencias = sum(1 for v in valores_lower if any(k in v for k in palabras_clave))
    
    return coincidencias >= 3


def filtrar_especies_validas(df):
    """Filtra especies válidas (elimina vacíos)."""
    df = df.copy()
    
    # Normalizar
    df['genero_clean'] = df['genero_corr'].str.lower().str.strip()
    df['epiteto_clean'] = df['epiteto_corr'].str.lower().str.strip()
    
    # Filtrar
    validas = (
        (df['genero_clean'] != "") &
        (df['epiteto_clean'] != "") &
        (~df['genero_clean'].isin(['genero', 'género', 'na'])) &
        (~df['epiteto_clean'].isin(['epiteto especifico', 'epíteto específico', 'na']))
    )
    
    df = df[validas].drop(['genero_clean', 'epiteto_clean'], axis=1)
    
    return df


# ==================== VALIDACIÓN ====================
def validar_entrada_archivo(df):
    """Valida que el Excel tenga formato Darwin Core."""
    errores = []
    
    if df.shape[0] == 0:
        errores.append("Archivo vacío")
    
    if df.shape[1] < 34:
        errores.append(f"Solo {df.shape[1]} columnas (se requieren 34+)")
    
    return errores


# ==================== ESTADÍSTICAS BÁSICAS ====================
def contar_valores_validos(serie):
    """Cuenta valores válidos (no nulos, no vacíos)."""
    return sum((serie != "") & (serie.notna()))


def obtener_unicas(serie):
    """Obtiene valores únicos válidos."""
    validas = serie[(serie != "") & (serie.notna())].unique()
    return validas


print("✅ Módulo utils.py cargado correctamente")
