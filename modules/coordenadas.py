# ============================================================================ #
#          DarwinCheck Vol.1 - Auditoría Taxonómica y Geográfica             #
#                         MÓDULO: COORDENADAS                                #
# ============================================================================ #

from typing import Optional, Tuple
import numpy as np
from modules.utils import gms_a_decimal, format_coordinate
from modules.config import CHILE_BOUNDS

class CoordinateValidator:
    """
    Validador de coordenadas geográficas para Chile
    """
    
    @staticmethod
    def validar_coordenada_chile(lat: str, lon: str) -> Tuple[str, Optional[str]]:
        """
        Valida si una coordenada está dentro de Chile (continental, islas)
        
        Args:
            lat: Latitud (string o número)
            lon: Longitud (string o número)
            
        Returns:
            (estado_str, ubicacion)
            - estado_str: "✅ OK (...)" o "❌ Error (...)"
            - ubicacion: Descripción de la zona (continental, Rapa Nui, etc.)
        """
        
        if not lat or not lon:
            return "❌ Coordenada faltante", None
        
        # Convertir a decimal
        lat_num = gms_a_decimal(lat)
        lon_num = gms_a_decimal(lon)
        
        if lat_num is None or lon_num is None:
            return "❌ Formato inválido", None
        
        # Validar rango general
        if lat_num < -90 or lat_num > 90 or lon_num < -180 or lon_num > 180:
            return "❌ Coordenadas fuera de rango", None
        
        # Chile continental
        bounds = CHILE_BOUNDS['continental']
        if (bounds['lat_min'] <= lat_num <= bounds['lat_max'] and
            bounds['lon_min'] <= lon_num <= bounds['lon_max']):
            return "✅ OK (Chile continental)", "Chile continental"
        
        # Rapa Nui
        rapa_nui = CHILE_BOUNDS['rapa_nui']
        if (abs(lat_num - rapa_nui['lat']) < rapa_nui['tolerance'] and
            abs(lon_num - rapa_nui['lon']) < rapa_nui['tolerance']):
            return "✅ OK (Rapa Nui)", "Rapa Nui"
        
        # Juan Fernández
        jf = CHILE_BOUNDS['juan_fernandez']
        if (abs(lat_num - jf['lat']) < jf['tolerance'] and
            abs(lon_num - jf['lon']) < jf['tolerance']):
            return "✅ OK (Juan Fernández)", "Juan Fernández"
        
        # Fuera de Chile
        return "❌ Fuera de Chile / Mar", None
    
    @staticmethod
    def procesar_coordenadas(df_col) -> list:
        """
        Procesa columna de coordenadas (GMS -> decimal)
        
        Args:
            df_col: Pandas Series con coordenadas
            
        Returns:
            Lista de coordenadas formateadas
        """
        resultado = []
        
        for coord in df_col:
            try:
                num = gms_a_decimal(coord)
                if num is not None:
                    formateado = format_coordinate(num)
                    resultado.append(formateado)
                else:
                    resultado.append(None)
            except:
                resultado.append(None)
        
        return resultado
