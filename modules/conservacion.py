# ============================================================================ #
#          DarwinCheck - Gestión de Estados de Conservación                    #
# ============================================================================ #

import pandas as pd
import numpy as np
from modules.utils import safe_val, normalizar_texto, es_vacio

class GestorConservacion:
    """Gestiona datos de estados de conservación de especies."""
    
    def __init__(self):
        self.estados_conocidos = {
            'EN': 'En Peligro (EN)',
            'VU': 'Vulnerable (VU)',
            'CR': 'En Peligro Crítico (CR)',
            'NT': 'Casi Amenazado (NT)',
            'LC': 'Preocupación Menor (LC)',
            'DD': 'Datos Insuficientes (DD)',
            'EX': 'Extinto (EX)',
            'EW': 'Extinto en Estado Silvestre (EW)',
        }
        # Mapeo de categorías en español a códigos IUCN
        self.mapeo_conservacion = {
            'en peligro': 'EN',
            'vulnerable': 'VU',
            'peligro crítico': 'CR',
            'casi amenazado': 'NT',
            'preocupación menor': 'LC',
            'datos insuficientes': 'DD',
            'extinto': 'EX',
            'extinto en estado silvestre': 'EW',
            'amenazado': 'VU',
            'protegida': 'VU',
            'endangered': 'EN',
            'vulnerable': 'VU',
            'critically endangered': 'CR',
            'near threatened': 'NT',
            'least concern': 'LC',
            'data deficient': 'DD',
        }
    
    def obtener_estado_desde_simbio(self, estado_texto):
        """Obtiene estado de conservación desde SIMBIO."""
        if es_vacio(estado_texto):
            return ''
        
        estado_norm = normalizar_texto(str(estado_texto))
        
        # Buscar coincidencia exacta
        for texto, codigo in self.mapeo_conservacion.items():
            if texto in estado_norm:
                return codigo
        
        # Retornar tal cual si tiene valor
        return safe_val(estado_texto)
    
    def obtener_categoria_completa(self, codigo):
        """Obtiene la categoría completa desde el código."""
        return self.estados_conocidos.get(codigo, codigo)
    
    def tiene_conservacion(self, estado):
        """Verifica si tiene información de conservación."""
        return not es_vacio(estado)
    
    def clasificar_por_estado(self, df, col_estado='estado_conservacion'):
        """Clasifica un dataframe por estado de conservación."""
        if col_estado not in df.columns:
            return {}
        
        grupos = {}
        for idx, row in df.iterrows():
            estado = safe_val(row[col_estado])
            if not es_vacio(estado):
                if estado not in grupos:
                    grupos[estado] = []
                grupos[estado].append(idx)
        
        return grupos
    
    def generar_resumen(self, df, col_especie='especie', col_estado='estado_conservacion'):
        """Genera resumen de conservación por especies."""
        if col_estado not in df.columns:
            return pd.DataFrame()
        
        # Filtrar filas con conservación
        df_con = df[df[col_estado].notna() & (df[col_estado] != '')]
        
        if df_con.empty:
            return pd.DataFrame()
        
        # Agrupar por estado
        resumen = df_con.groupby(col_estado).size().reset_index(name='cantidad')
        
        # Mapear a categorías completas
        resumen['categoria'] = resumen[col_estado].apply(self.obtener_categoria_completa)
        
        return resumen.sort_values('cantidad', ascending=False)


# Instancia global
gestor_conservacion = GestorConservacion()
