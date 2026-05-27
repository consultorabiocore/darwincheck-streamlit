# ============================================================================ #
#              DarwinCheck - Validación y Conversión de Coordenadas            #
# ============================================================================ #

import pandas as pd
import numpy as np
from modules.config import CHILE_CONTINENTAL, RAPA_NUI, JUAN_FERNANDEZ
from modules.utils import gms_a_decimal, es_vacio

class ValidadorCoordenadas:
    """Valida y convierte coordenadas geográficas."""
    
    @staticmethod
    def es_decimal(coord_str):
        """Verifica si coordenada está en formato decimal."""
        if es_vacio(coord_str):
            return False
        
        try:
            float(str(coord_str).replace(',', '.'))
            return True
        except:
            return False
    
    @staticmethod
    def convertir_a_decimal(lat_str, lon_str):
        """Convierte coordenadas a decimal (si es necesario)."""
        
        # Intentar como decimal primero
        try:
            if ValidadorCoordenadas.es_decimal(lat_str):
                lat = float(str(lat_str).replace(',', '.'))
            else:
                lat = gms_a_decimal(lat_str)
                if lat is None:
                    return None, None
            
            if ValidadorCoordenadas.es_decimal(lon_str):
                lon = float(str(lon_str).replace(',', '.'))
            else:
                lon = gms_a_decimal(lon_str)
                if lon is None:
                    return None, None
            
            return lat, lon
        
        except:
            return None, None
    
    @staticmethod
    def validar_rango_global(lat, lon):
        """Valida si coordenadas están en rango global válido."""
        try:
            lat = float(lat)
            lon = float(lon)
            return -90 <= lat <= 90 and -180 <= lon <= 180
        except:
            return False
    
    @staticmethod
    def en_chile_continental(lat, lon):
        """Verifica si punto está en Chile continental."""
        try:
            lat = float(lat)
            lon = float(lon)
            
            chile = CHILE_CONTINENTAL
            return (
                chile['lat_min'] <= lat <= chile['lat_max'] and
                chile['lon_min'] <= lon <= chile['lon_max']
            )
        except:
            return False
    
    @staticmethod
    def en_rapa_nui(lat, lon):
        """Verifica si punto está cerca de Rapa Nui."""
        try:
            lat = float(lat)
            lon = float(lon)
            
            rn = RAPA_NUI
            dist = np.sqrt(
                (lat - rn['lat'])**2 + (lon - rn['lon'])**2
            )
            return dist <= rn['tolerancia']
        except:
            return False
    
    @staticmethod
    def en_juan_fernandez(lat, lon):
        """Verifica si punto está cerca de Juan Fernández."""
        try:
            lat = float(lat)
            lon = float(lon)
            
            jf = JUAN_FERNANDEZ
            dist = np.sqrt(
                (lat - jf['lat'])**2 + (lon - jf['lon'])**2
            )
            return dist <= jf['tolerancia']
        except:
            return False
    
    @staticmethod
    def validar_chile(lat, lon):
        """Verifica si punto está en territorio chileno."""
        return (
            ValidadorCoordenadas.en_chile_continental(lat, lon) or
            ValidadorCoordenadas.en_rapa_nui(lat, lon) or
            ValidadorCoordenadas.en_juan_fernandez(lat, lon)
        )
    
    @staticmethod
    def validar_coordinate_chile(lat, lon):
        """Valida coordenadas y retorna estado geográfico con diccionario."""
        estado = ValidadorCoordenadas.obtener_estado_geografico(lat, lon)
        
        # Determinar ubicación
        if estado == "CHILE_CONTINENTAL":
            ubicacion = "Chile Continental"
        elif estado == "RAPA_NUI":
            ubicacion = "Rapa Nui"
        elif estado == "JUAN_FERNANDEZ":
            ubicacion = "Juan Fernández"
        elif estado == "FUERA_CHILE":
            ubicacion = "Fuera de Chile"
        else:
            ubicacion = "Inválido"
        
        return {
            'estado': estado,
            'ubicacion': ubicacion,
            'valido': estado != "FUERA_RANGO_GLOBAL" and estado != "FUERA_CHILE"
        }
    
    @staticmethod
    def obtener_estado_geografico(lat, lon):
        """Obtiene estado geográfico del punto."""
        if not ValidadorCoordenadas.validar_rango_global(lat, lon):
            return "FUERA_RANGO_GLOBAL"
        
        if ValidadorCoordenadas.en_chile_continental(lat, lon):
            return "CHILE_CONTINENTAL"
        elif ValidadorCoordenadas.en_rapa_nui(lat, lon):
            return "RAPA_NUI"
        elif ValidadorCoordenadas.en_juan_fernandez(lat, lon):
            return "JUAN_FERNANDEZ"
        else:
            return "FUERA_CHILE"


# Instancia global
validador = ValidadorCoordenadas()
