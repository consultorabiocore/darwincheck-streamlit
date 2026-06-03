# ============================================================================ #
#          DarwinCheck - Gestión de Estados de Conservación                    #
# ============================================================================ #

import pandas as pd
import numpy as np
from modules.utils import safe_val, normalizar_texto, es_vacio

class GestorConservacion:
    """Gestiona datos de estados de conservación de especies."""
    
    def __init__(self):
        self.estados_iucn = {
            'EN': 'En Peligro (EN)',
            'VU': 'Vulnerable (VU)',
            'CR': 'En Peligro Crítico (CR)',
            'NT': 'Casi Amenazado (NT)',
            'LC': 'Preocupación Menor (LC)',
            'DD': 'Datos Insuficientes (DD)',
            'EX': 'Extinto (EX)',
            'EW': 'Extinto en Estado Silvestre (EW)',
        }
    
    def normalizar_estado(self, estado_texto):
        """Normaliza estado de conservación desde diferentes fuentes."""
        if es_vacio(estado_texto):
            return ''
        
        estado = normalizar_texto(str(estado_texto))
        
        # Mapeos comunes
        mapeos = {
            'en peligro': 'EN',
            'endangered': 'EN',
            'vulnerable': 'VU',
            'peligro critico': 'CR',
            'critically endangered': 'CR',
            'casi amenazado': 'NT',
            'near threatened': 'NT',
            'preocupacion menor': 'LC',
            'least concern': 'LC',
            'datos insuficientes': 'DD',
            'data deficient': 'DD',
            'extinto': 'EX',
            'extinct': 'EX',
            'amenazado': 'VU',
            'threatened': 'VU',
            'protegida': 'VU',
        }
        
        # Búsqueda por clave
        for clave, codigo in mapeos.items():
            if clave in estado:
                return codigo
        
        # Si es código IUCN válido, devolverlo
        if estado.upper() in self.estados_iucn:
            return estado.upper()
        
        # Retornar original si tiene valor
        return safe_val(estado_texto) if not es_vacio(estado_texto) else ''
    
    def obtener_categoria_completa(self, codigo):
        """Obtiene la categoría completa desde el código."""
        return self.estados_iucn.get(codigo if isinstance(codigo, str) else str(codigo), codigo)
    
    def es_amenazado(self, codigo):
        """Verifica si una especie está amenazada (EN, VU, CR)."""
        amenazados = {'EN', 'VU', 'CR'}
        return str(codigo).upper() in amenazados
    
    def tiene_conservacion(self, estado):
        """Verifica si tiene información de conservación."""
        return not es_vacio(estado)


# Instancia global
gestor_conservacion = GestorConservacion()
