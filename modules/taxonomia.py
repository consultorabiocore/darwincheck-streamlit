# ============================================================================ #
#              DarwinCheck - Gestión Taxonómica (GBIF + SIMBIO)                #
# ============================================================================ #

import pandas as pd
import numpy as np
import requests
import json
from functools import lru_cache
from modules.config import SIMBIO_FILE, GBIF_API_BASE, GBIF_TIMEOUT
from modules.utils import safe_val, normalizar_texto, es_vacio

class GestorTaxonomia:
    """Gestiona consultas taxonómicas contra GBIF y SIMBIO."""
    
    def __init__(self):
        self.simbio_df = None  # Lazy loading
        self.simbio_cargado = False
        self.cache_gbif = {}
    
    def cargar_simbio(self):
        """Carga base de datos SIMBIO desde Excel (lazy loading)."""
        if self.simbio_cargado:
            return
        
        self.simbio_cargado = True
        self.simbio_df = pd.DataFrame()
        
        try:
            if SIMBIO_FILE.exists():
                try:
                    print(f"📂 Cargando SIMBIO desde {SIMBIO_FILE}...")
                    simbio_raw = pd.read_excel(
                        SIMBIO_FILE,
                        sheet_name='Especies',
                        dtype=str
                    )
                    
                    # Limpiar nombres de columnas
                    simbio_raw.columns = simbio_raw.columns.str.strip()
                    
                    # Crear dataframe procesado
                    self.simbio_df = pd.DataFrame({
                        'nombre_cientifico': (
                            simbio_raw.get('Género', '') + ' ' + 
                            simbio_raw.get('Epíteto específico', '')
                        ),
                        'estado_conservacion': simbio_raw.get('Estado de Conservación vigente', ''),
                        'nombre_comun': simbio_raw.get('Nombre común', ''),
                        'reino': simbio_raw.get('Reino', ''),
                        'filo': simbio_raw.get('Filo o División', ''),
                        'clase': simbio_raw.get('Clase', ''),
                        'orden': simbio_raw.get('Orden', ''),
                        'familia': simbio_raw.get('Familia', ''),
                        'genero': simbio_raw.get('Género', ''),
                    })
                    
                    # Normalizar para búsqueda
                    self.simbio_df['nombre_busqueda'] = (
                        self.simbio_df['nombre_cientifico'].apply(
                            lambda x: normalizar_texto(x)
                        )
                    )
                    
                    # Limpiar valores
                    for col in self.simbio_df.columns:
                        self.simbio_df[col] = self.simbio_df[col].apply(safe_val)
                    
                    # Filtrar filas sin género
                    self.simbio_df = self.simbio_df[
                        self.simbio_df['genero'].apply(lambda x: not es_vacio(x))
                    ]
                    
                    print(f"✅ SIMBIO cargado: {len(self.simbio_df)} especies")
                
                except Exception as e:
                    print(f"⚠️ Error leyendo SIMBIO Excel: {e}")
                    self.simbio_df = pd.DataFrame()
            else:
                print(f"⚠️ Archivo SIMBIO no encontrado: {SIMBIO_FILE}")
                self.simbio_df = pd.DataFrame()
        
        except Exception as e:
            print(f"⚠️ Error inicializando SIMBIO: {e}")
            self.simbio_df = pd.DataFrame()
    
    def buscar_simbio(self, genero, epiteto):
        """Busca especie en SIMBIO por género + epíteto."""
        # Cargar SIMBIO si es necesario
        if not self.simbio_cargado:
            self.cargar_simbio()
        
        if es_vacio(genero) or es_vacio(epiteto) or len(self.simbio_df) == 0:
            return None
        
        nombre = normalizar_texto(f"{genero} {epiteto}")
        
        # Búsqueda exacta
        resultados = self.simbio_df[
            self.simbio_df['nombre_busqueda'] == nombre
        ]
        
        if len(resultados) > 0:
            fila = resultados.iloc[0]
            return {
                'reino': safe_val(fila['reino']),
                'filo': safe_val(fila['filo']),
                'clase': safe_val(fila['clase']),
                'orden': safe_val(fila['orden']),
                'familia': safe_val(fila['familia']),
                'genero': safe_val(fila['genero']),
                'epiteto': safe_val(epiteto),
                'nombre_comun': safe_val(fila['nombre_comun']),
                'estado_conservacion': safe_val(fila['estado_conservacion']),
                'fuente': 'SIMBIO'
            }
        
        return None
    
    @lru_cache(maxsize=1000)
    def consultar_gbif(self, genero, epiteto):
        """Consulta GBIF por nombre científico."""
        if es_vacio(genero) or es_vacio(epiteto):
            return None
        
        nombre = f"{genero.strip()} {epiteto.strip()}"
        
        try:
            url = f"{GBIF_API_BASE}/species/match"
            params = {'name': nombre}
            
            resp = requests.get(url, params=params, timeout=GBIF_TIMEOUT)
            
            if resp.status_code == 200:
                data = resp.json()
                
                if data.get('usageKey'):
                    return {
                        'reino': safe_val(data.get('kingdom')),
                        'filo': safe_val(data.get('phylum')),
                        'clase': safe_val(data.get('class')),
                        'orden': safe_val(data.get('order')),
                        'familia': safe_val(data.get('family')),
                        'genero': safe_val(data.get('genus')),
                        'epiteto': safe_val(data.get('specificEpithet')),
                        'nombre_comun': '',
                        'estado_conservacion': '',
                        'fuente': 'GBIF'
                    }
        
        except Exception as e:
            print(f"⚠️ Error en GBIF: {e}")
        
        return None
    
    def resolver_taxonomia(self, genero, epiteto):
        """Resuelve taxonomía: primero SIMBIO, luego GBIF."""
        # Intentar SIMBIO
        resultado = self.buscar_simbio(genero, epiteto)
        if resultado:
            return resultado
        
        # Fallback a GBIF
        resultado = self.consultar_gbif(genero, epiteto)
        if resultado:
            return resultado
        
        # No encontrado
        return {
            'reino': '',
            'filo': '',
            'clase': '',
            'orden': '',
            'familia': '',
            'genero': safe_val(genero),
            'epiteto': safe_val(epiteto),
            'nombre_comun': '',
            'estado_conservacion': '',
            'fuente': 'NO_ENCONTRADO'
        }
    
    def obtener_taxonomia(self, genero, epiteto):
        """Alias para resolver_taxonomia (compatibilidad)."""
        return self.resolver_taxonomia(genero, epiteto)


# Instancia global (sin cargar SIMBIO en import)
gestor_taxonomia = GestorTaxonomia()
