# ============================================================================ #
#          DarwinCheck Vol.1 - Auditoría Taxonómica y Geográfica             #
#                         MÓDULO: TAXONOMÍA                                  #
# ============================================================================ #

import requests
import json
import pandas as pd
from typing import Optional, Dict, List
import streamlit as st
from functools import lru_cache
from modules.config import GBIF_API_URL, GBIF_TIMEOUT, SIMBIO_FILE
from modules.utils import safe_val, clean_text

class TaxonomyManager:
    """
    Gestor de taxonomía con SIMBIO (nacional) y GBIF (global)
    """
    
    def __init__(self):
        self.simbio_df = None
        self.valid_orders = []
        self._load_simbio()
    
    def _load_simbio(self):
        """Carga base de datos SIMBIO"""
        try:
            if SIMBIO_FILE.exists():
                simbio_raw = pd.read_excel(
                    SIMBIO_FILE,
                    sheet_name="Especies",
                    dtype=str
                )
                
                # Limpiar nombres de columnas
                simbio_raw.columns = [col.strip() for col in simbio_raw.columns]
                
                # Construir dataframe
                self.simbio_df = pd.DataFrame({
                    'Nombre_Cientifico': (
                        simbio_raw.get('Género', '').fillna('').astype(str) + ' ' +
                        simbio_raw.get('Epíteto específico', '').fillna('').astype(str)
                    ).str.strip(),
                    'Estado_Conservacion': simbio_raw.get('Estado de Conservación vigente', '').fillna(''),
                    'Nombre_Comun': simbio_raw.get('Nombre común', '').fillna(''),
                    'reino': simbio_raw.get('Reino', '').fillna(''),
                    'filo': simbio_raw.get('Filo o división', '').fillna(''),
                    'clase': simbio_raw.get('Clase', '').fillna(''),
                    'orden': simbio_raw.get('Orden', '').fillna(''),
                    'familia': simbio_raw.get('Familia', '').fillna(''),
                    'genero': simbio_raw.get('Género', '').fillna('').str.upper(),
                    'epiteto': simbio_raw.get('Epíteto específico', '').fillna('').str.lower(),
                })
                
                # Limpiar y filtrar
                self.simbio_df = self.simbio_df[
                    (self.simbio_df['genero'].str.strip() != '') &
                    (self.simbio_df['genero'] != 'NA')
                ].reset_index(drop=True)
                
                self.simbio_df['nombre_busqueda'] = (
                    self.simbio_df['Nombre_Cientifico'].str.lower().str.strip()
                )
                
                self.valid_orders = sorted(
                    self.simbio_df['orden'].unique().tolist()
                )
                
                st.success(f"✅ SIMBIO cargado: {len(self.simbio_df)} especies")
                
        except Exception as e:
            st.warning(f"⚠️ Error cargando SIMBIO: {str(e)}")
            self.simbio_df = pd.DataFrame()
    
    @lru_cache(maxsize=1000)
    def consultar_gbif(self, genero: str, epiteto: str) -> Optional[Dict]:
        """
        Consulta GBIF API por especie
        
        Args:
            genero: Género (mayúscula)
            epiteto: Epíteto específico (minúscula)
            
        Returns:
            Dict con información taxonómica o None
        """
        genero = safe_val(genero)
        epiteto = safe_val(epiteto)
        
        if not genero or not epiteto:
            return None
        
        try:
            nombre = f"{genero.strip()} {epiteto.strip()}"
            params = {'name': nombre}
            
            response = requests.get(
                GBIF_API_URL,
                params=params,
                timeout=GBIF_TIMEOUT
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            if not data.get('usageKey'):
                return None
            
            return {
                'usageKey': data.get('usageKey'),
                'reino': safe_val(data.get('kingdom', '')),
                'filo': safe_val(data.get('phylum', '')),
                'clase': safe_val(data.get('class', '')),
                'orden': safe_val(data.get('order', '')),
                'familia': safe_val(data.get('family', '')),
                'genero': safe_val(data.get('genus', '')),
                'epiteto': safe_val(data.get('specificEpithet', '')),
                'status': safe_val(data.get('status', '')),
                'fuente': 'GBIF'
            }
        
        except Exception as e:
            return None
    
    def buscar_en_simbio(self, genero: str, epiteto: str) -> tuple:
        """
        Busca especie en SIMBIO (nacional)
        
        Returns:
            (opciones_df, tipo_coincidencia)
            - tipo_coincidencia: 'exacto', 'genero', 'epiteto', 'ninguno'
        """
        if self.simbio_df is None or len(self.simbio_df) == 0:
            return None, 'ninguno'
        
        genero = safe_val(genero).lower()
        epiteto = safe_val(epiteto).lower()
        
        if not genero and not epiteto:
            return None, 'ninguno'
        
        # Búsqueda exacta
        nombre_busqueda = f"{genero} {epiteto}".strip()
        exactas = self.simbio_df[
            self.simbio_df['nombre_busqueda'] == nombre_busqueda
        ]
        
        if len(exactas) > 0:
            return exactas, 'exacto'
        
        # Por género
        if genero:
            por_genero = self.simbio_df[
                self.simbio_df['genero'].str.lower() == genero
            ]
            if len(por_genero) > 0:
                return por_genero, 'genero'
        
        # Por epíteto
        if epiteto:
            por_epiteto = self.simbio_df[
                self.simbio_df['epiteto'].str.lower() == epiteto
            ]
            if len(por_epiteto) > 0:
                return por_epiteto, 'epiteto'
        
        return None, 'ninguno'
    
    def corregir_taxonomia(self, genero: str, epiteto: str, archivo_pequeno: bool = True) -> Dict:
        """
        Realiza corrección taxonómica completa
        
        Precedencia: SIMBIO exacto > SIMBIO aproximado > GBIF
        
        Returns:
            Dict con información corregida y fuente
        """
        resultado = {
            'genero': genero,
            'epiteto': epiteto,
            'reino': '',
            'filo': '',
            'clase': '',
            'orden': '',
            'familia': '',
            'fuente': 'Original',
            'necesita_revision': False,
            'opciones': None
        }
        
        # 1. Búsqueda en SIMBIO
        opciones, tipo = self.buscar_en_simbio(genero, epiteto)
        
        if opciones is not None:
            if len(opciones) == 1:
                # Una sola coincidencia
                row = opciones.iloc[0]
                resultado.update({
                    'genero': row['genero'],
                    'epiteto': row['epiteto'],
                    'reino': row['reino'],
                    'filo': row['filo'],
                    'clase': row['clase'],
                    'orden': row['orden'],
                    'familia': row['familia'],
                    'fuente': f"✅ SIMBIO ({tipo.upper()})"
                })
                return resultado
            
            else:
                # Múltiples coincidencias
                resultado.update({
                    'necesita_revision': True,
                    'opciones': opciones[['genero', 'epiteto', 'reino', 'filo', 
                                          'clase', 'orden', 'familia']].to_dict('records'),
                    'fuente': f"⚠️ SIMBIO ({tipo.upper()}, {len(opciones)} opciones)"
                })
                return resultado
        
        # 2. Consulta GBIF (solo archivos pequeños)
        if archivo_pequeno:
            gbif_result = self.consultar_gbif(genero, epiteto)
            if gbif_result:
                resultado.update(gbif_result)
                return resultado
        
        return resultado
