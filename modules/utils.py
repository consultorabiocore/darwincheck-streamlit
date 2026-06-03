# ============================================================================ #
#                 DarwinCheck - Funciones Auxiliares Generales                 #
# ============================================================================ #

import pandas as pd
import numpy as np
import re
import unicodedata
from datetime import datetime
from pathlib import Path

# ==================== UTILIDADES DE DATOS ====================

def safe_val(x, default=""):
    """Retorna valor seguro, manejando nulos y valores especiales."""
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return default
    x = str(x).strip()
    if x.lower() in ['', 'na', 'null', 'none', 'nan']:
        return default
    return x


def normalizar_texto(texto):
    """Normaliza texto: limpia acentos, espacios, convierte a lowercase."""
    if not texto or pd.isna(texto):
        return ""
    texto = str(texto).strip()
    # Quitar acentos
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    return texto.lower()


def limpiar_dataframe(df):
    """Limpia DataFrame: quita espacios en nombres de columnas y valores nulos."""
    df.columns = df.columns.str.strip()
    return df.fillna("")


def fmt_entero(x):
    """Formatea entero con separadores de miles."""
    try:
        return f"{int(float(x)):,}".replace(',', '.')
    except:
        return str(x)


def fmt_decimal(x, decimales=2):
    """Formatea decimal."""
    try:
        return f"{float(x):.{decimales}f}".replace('.', ',')
    except:
        return str(x)


def fmt_coordenada(valor, formato='decimal'):
    """Formatea una coordenada individual (lat o lon) segun formato especificado."""
    try:
        valor = float(valor)
        if formato == 'decimal':
            return f"{valor:.4f}"
        elif formato == 'gms':
            return decimal_a_gms(valor)
        return str(valor)
    except:
        return str(valor)


def detectar_encabezado(genero, orden, filo='', clase='', familia='', reino=''):
    """Detecta si una fila es encabezado por palabras clave."""
    palabras_clave = ['genero', 'genero', 'orden', 'familia', 'filo', 'clase', 'reino']
    g = normalizar_texto(genero)
    o = normalizar_texto(orden)
    
    for palabra in palabras_clave:
        if palabra in g or palabra in o:
            return True
    return False


def formatar_hora(hora_str):
    """Formatea hora a HH:MM:SS."""
    if not hora_str or pd.isna(hora_str):
        return ""
    
    hora_str = str(hora_str).strip()
    
    # Intentar parsear diferentes formatos
    formatos = [
        "%H:%M:%S", "%H:%M", "%H%M%S", "%H%M",
        "%H:%M:%S.%f", "%I:%M:%S %p"
    ]
    
    for fmt in formatos:
        try:
            tiempo = datetime.strptime(hora_str, fmt)
            return tiempo.strftime("%H:%M:%S")
        except:
            continue
    
    return hora_str


def gms_a_decimal(coord_str):
    """Convierte coordenada sexagesimal (GMS) a decimal."""
    if not coord_str or pd.isna(coord_str):
        return None
    
    coord_str = str(coord_str).strip()
    
    # Si ya es decimal, devolverlo
    try:
        valor = float(coord_str.replace(',', '.'))
        if -180 <= valor <= 180:
            return valor
    except:
        pass
    
    # Patrones para sexagesimal
    # 23°30'15"S, 23° 30' 15" S, 23:30:15, etc.
    
    # Reemplazar caracteres especiales
    coord_str = re.sub(r'[°º]', ' ', coord_str)
    coord_str = re.sub(r"[''´`]", ' ', coord_str)
    coord_str = re.sub(r'[""‟]', ' ', coord_str)
    coord_str = re.sub(r'[NSEWnsew]', ' ', coord_str)
    coord_str = re.sub(r'[:;/]', ' ', coord_str)
    
    # Extraer numeros
    numeros = re.findall(r'[\d.]+', coord_str)
    
    if len(numeros) >= 1:
        try:
            grados = float(numeros[0])
            minutos = float(numeros[1]) if len(numeros) > 1 else 0
            segundos = float(numeros[2]) if len(numeros) > 2 else 0
            
            decimal = grados + minutos/60 + segundos/3600
            
            # Detectar si es Sur u Oeste
            if 'S' in coord_str.upper() or 'O' in coord_str.upper() or 'W' in coord_str.upper():
                decimal = -abs(decimal)
            
            if -180 <= decimal <= 180:
                return decimal
        except:
            pass
    
    return None


def decimal_a_gms(decimal):
    """Convierte coordenada decimal a sexagesimal (GMS)."""
    if not decimal or pd.isna(decimal):
        return ""
    
    try:
        decimal = float(decimal)
    except:
        return ""
    
    signo = 'S' if decimal < 0 else 'N'
    if ',' in str(decimal):  # Es longitud
        signo = 'O' if decimal < 0 else 'E'
    
    decimal = abs(decimal)
    grados = int(decimal)
    minutos_float = (decimal - grados) * 60
    minutos = int(minutos_float)
    segundos = (minutos_float - minutos) * 60
    
    return f"{grados}°{minutos}'{segundos:.2f}\"{signo}"


def registrar_log(mensaje, tipo='info', archivo='auditoria.log'):
    """Registra mensajes en archivo log."""
    try:
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_path = log_dir / archivo
        
        prefijo = f"[{timestamp}] [{tipo.upper()}] "
        log_msg = prefijo + mensaje + "\n"
        
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(log_msg)
        except Exception as e:
            print(f"Error al registrar log: {e}")
    except:
        pass

# ==================== VALIDACIONES ====================

def validar_rango(valor, min_val, max_val):
    """Valida si un valor esta en rango."""
    try:
        v = float(valor)
        return min_val <= v <= max_val
    except:
        return False


def es_numero(valor):
    """Verifica si un valor es numerico."""
    try:
        float(valor)
        return True
    except:
        return False


def es_vacio(valor):
    """Verifica si un valor esta vacio."""
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return True
    return str(valor).strip().lower() in ['', 'na', 'null', 'none', 'nan']
