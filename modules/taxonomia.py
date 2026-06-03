# ============================================================================ #
#              DarwinCheck - Gestión Taxonómica (GBIF + SIMBIO)                #
# ============================================================================ #

import pandas as pd
import numpy as np
import requests
import json
from functools import lru_cache
from difflib import SequenceMatcher
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
    
    def similitud(self, texto1, texto2):
        """Calcula similitud entre dos textos (0-1)."""
        return SequenceMatcher(None, texto1, texto2).ratio()
    
    def buscar_simbio_exacta(self, genero, epiteto):
        """Busca especie exacta en SIMBIO."""
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
                'fuente': 'SIMBIO',
                'exacta': True
            }
        
        return None
    
    def buscar_simbio_difusa(self, genero, epiteto, umbral=0.7):
        """Busca especie con similitud difusa (fuzzy matching)."""
        if es_vacio(genero) or es_vacio(epiteto) or len(self.simbio_df) == 0:
            return []
        
        nombre_objetivo = normalizar_texto(f"{genero} {epiteto}")
        coincidencias = []
        
        for idx, row in self.simbio_df.iterrows():
            nombre_simbio = row['nombre_busqueda']
            similitud_score = self.similitud(nombre_objetivo, nombre_simbio)
            
            if similitud_score >= umbral:
                coincidencias.append({
                    'score': similitud_score,
                    'nombre': row['nombre_cientifico'],
                    'reino': safe_val(row['reino']),
                    'filo': safe_val(row['filo']),
                    'clase': safe_val(row['clase']),
                    'orden': safe_val(row['orden']),
                    'familia': safe_val(row['familia']),
                    'genero': safe_val(row['genero']),
                    'epiteto': safe_val(row['nombre_cientifico'].split()[-1]),
                    'nombre_comun': safe_val(row['nombre_comun']),
                    'fuente': 'SIMBIO'
                })
        
        # Ordenar por similitud descendente
        coincidencias = sorted(coincidencias, key=lambda x: x['score'], reverse=True)
        return coincidencias[:5]  # Retornar máximo 5 opciones
    
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
                        'fuente': 'GBIF',
                        'exacta': True
                    }
        
        except Exception as e:
            print(f"⚠️ Error en GBIF: {e}")
        
        return None
    
    def resolver_taxonomia(self, genero, epiteto):
        """Resuelve taxonomía: primero SIMBIO exacta, luego GBIF, luego SIMBIO difusa."""
        # Cargar SIMBIO si es necesario
        if not self.simbio_cargado:
            self.cargar_simbio()
        
        # 1. Intentar búsqueda exacta en SIMBIO
        resultado = self.buscar_simbio_exacta(genero, epiteto)
        if resultado:
            return resultado
        
        # 2. Fallback a GBIF
        resultado = self.consultar_gbif(genero, epiteto)
        if resultado:
            return resultado
        
        # 3. Búsqueda difusa en SIMBIO (si no encontró exacta)
        coincidencias = self.buscar_simbio_difusa(genero, epiteto, umbral=0.65)
        if coincidencias:
            # Retornar la mejor coincidencia
            mejor = coincidencias[0]
            return {
                'reino': mejor['reino'],
                'filo': mejor['filo'],
                'clase': mejor['clase'],
                'orden': mejor['orden'],
                'familia': mejor['familia'],
                'genero': mejor['genero'],
                'epiteto': mejor['epiteto'],
                'nombre_comun': mejor['nombre_comun'],
                'fuente': 'SIMBIO_DIFUSA',
                'exacta': False,
                'coincidencias': coincidencias  # Pasar opciones para selector
            }
        
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
            'fuente': 'NO_ENCONTRADO',
            'exacta': False,
            'coincidencias': []
        }
    
    def obtener_opciones_taxonomia(self, genero, epiteto):
        """Obtiene opciones de corrección para selector interactivo."""
        if not self.simbio_cargado:
            self.cargar_simbio()
        
        opciones = []
        
        # Búsqueda exacta
        exacta = self.buscar_simbio_exacta(genero, epiteto)
        if exacta:
            opciones.append({
                'nombre': f"{exacta['genero']} {exacta['epiteto']} (SIMBIO - EXACTA)",
                'datos': exacta
            })
        
        # Búsqueda difusa
        difusas = self.buscar_simbio_difusa(genero, epiteto, umbral=0.65)
        for coinc in difusas:
            if coinc['nombre'] not in [o['nombre'] for o in opciones]:
                opciones.append({
                    'nombre': f"{coinc['nombre']} (similitud: {coinc['score']:.0%})",
                    'datos': coinc
                })
        
        # GBIF
        gbif = self.consultar_gbif(genero, epiteto)
        if gbif:
            opciones.append({
                'nombre': f"{gbif['genero']} {gbif['epiteto']} (GBIF)",
                'datos': gbif
            })
        
        # Opción de dejar original
        opciones.append({
            'nombre': f"{safe_val(genero)} {safe_val(epiteto)} (SIN CORREGIR)",
            'datos': {
                'genero': safe_val(genero),
                'epiteto': safe_val(epiteto),
                'reino': '',
                'filo': '',
                'clase': '',
                'orden': '',
                'familia': '',
                'fuente': 'NO_CORREGIDO'
            }
        })
        
        return opciones if opciones else []


# Instancia global (sin cargar SIMBIO en import)
gestor_taxonomia = GestorTaxonomia()
