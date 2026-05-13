# ============================================================================ #
#          DarwinCheck Vol.1 - Auditoría Taxonómica y Geográfica             #
#                         MÓDULO: UTILIDADES                                 #
# ============================================================================ #

import re
import unicodedata
from typing import Optional, Union, List
import numpy as np

def safe_val(value, default: str = "") -> str:
    """
    Función universal segura para obtener valores limpios
    
    Args:
        value: Valor a procesar
        default: Valor por defecto si es nulo
        
    Returns:
        String limpio
    """
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return default
    
    value_str = str(value).strip()
    
    if not value_str or value_str.lower() in ['na', 'null', 'n/a', 'nan']:
        return default
    
    return value_str


def clean_text(text: str) -> str:
    """
    Limpia texto: elimina acentos, espacios raros, normaliza
    """
    if not isinstance(text, str):
        return ""
    
    # Normalizar unicode
    text = unicodedata.normalize('NFD', text)
    text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
    
    # Eliminar espacios múltiples
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def detect_header_row(row: dict) -> bool:
    """
    Detecta si una fila es encabezado (header)
    
    Args:
        row: Diccionario con datos de la fila
        
    Returns:
        True si parece ser encabezado
    """
    header_keywords = [
        'reino', 'filo', 'clase', 'orden', 'familia', 'genero',
        'epiteto', 'especie', 'nombre', 'coordinat', 'latitude',
        'longitud', 'valor', 'año', 'mes', 'dia', 'hora'
    ]
    
    row_values = [str(v).lower().strip() for v in row.values() if v]
    matches = sum(1 for val in row_values if any(kw in val for kw in header_keywords))
    
    return matches >= 3


def gms_a_decimal(coord: Union[str, float]) -> Optional[float]:
    """
    Convierte coordenadas GMS (Grados, Minutos, Segundos) a decimal
    
    Args:
        coord: Coordenada en formato GMS o decimal
        
    Returns:
        Coordenada en decimal o None
    """
    if coord is None or (isinstance(coord, float) and np.isnan(coord)):
        return None
    
    coord_str = str(coord).strip()
    
    if not coord_str:
        return None
    
    # Si ya es decimal
    if '°' not in coord_str and "'" not in coord_str and '"' not in coord_str:
        try:
            return float(coord_str.replace(',', '.'))
        except ValueError:
            return None
    
    # Extraer números
    nums = re.findall(r'[\d.]+', coord_str)
    
    if not nums:
        return None
    
    try:
        nums = [float(n) for n in nums]
    except ValueError:
        return None
    
    # Convertir GMS a decimal
    result = nums[0] + (nums[1] / 60 if len(nums) > 1 else 0) + (nums[2] / 3600 if len(nums) > 2 else 0)
    
    # Aplicar negativo si es S o W
    if any(char in coord_str.upper() for char in ['S', 'W', 'O', '-']):
        result = -result
    
    return result


def format_integer(value: Union[int, float]) -> str:
    """Formatea entero con separador de miles"""
    if not isinstance(value, (int, float)) or np.isnan(value if isinstance(value, float) else 0):
        return "0"
    
    return f"{int(value):,.0f}".replace(',', '.')


def format_decimal(value: Union[int, float], digits: int = 2) -> str:
    """Formatea decimal con coma como separador"""
    if not isinstance(value, (int, float)) or np.isnan(value if isinstance(value, float) else 0):
        return "0"
    
    formatted = f"{value:.{digits}f}"
    return formatted.replace('.', ',')


def format_coordinate(value: Union[str, float], digits: int = 5) -> str:
    """Formatea coordenada con al menos N decimales y coma como separador"""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return ""
    
    try:
        num = float(str(value).replace(',', '.'))
        formatted = f"{num:.{digits}f}"
        return formatted.replace('.', ',')
    except ValueError:
        return str(value)


def format_time(value: str) -> Optional[str]:
    """
    Convierte valor a formato HH:MM
    
    Soporta:
    - HH:MM (directo)
    - H (0-23 -> H:00)
    - HHMM (0-2400)
    - Decimal 0-1 (fracción del día)
    """
    if not value or (isinstance(value, float) and np.isnan(value)):
        return None
    
    value_str = str(value).strip()
    
    # Si ya tiene formato HH:MM
    if ':' in value_str:
        match = re.search(r'(\d{2}):(\d{2})', value_str)
        if match:
            return match.group(0)
    
    # Intentar como número
    try:
        num = float(value_str.replace(',', '.'))
        
        # 0-23: horas
        if 0 <= num <= 23 and num == int(num):
            return f"{int(num):02d}:00"
        
        # 24-2400: HHMM
        if 24 < num < 2400 and num == int(num):
            horas = int(num // 100)
            minutos = int(num % 100)
            if horas < 24 and minutos < 60:
                return f"{horas:02d}:{minutos:02d}"
        
        # 0-1: fracción del día
        if 0 <= num <= 1:
            total_segundos = round(num * 86400)
            horas = (total_segundos // 3600) % 24
            minutos = (total_segundos % 3600) // 60
            return f"{horas:02d}:{minutos:02d}"
    
    except ValueError:
        pass
    
    return None
