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
                        'Nombre_Cientifico': (
                            simbio_raw.get('Género', '') + ' ' + 
                            simbio_raw.get('Epíteto específico', '')
                        ),
                        'Estado_Conservacion': simbio_raw.get('Estado de Conservación vigente', ''),
                        'Nombre_Comun': simbio_raw.get('Nombre común', ''),
                        'reino': simbio_raw.get('Reino', ''),
                        'filo': simbio_raw.get('Filo o División', ''),
                        'clase': simbio_raw.get('Clase', ''),
                        'orden': simbio_raw.get('Orden', ''),
                        'familia': simbio_raw.get('Familia', ''),
                        'genero': simbio_raw.get('Género', ''),
                        'epiteto': simbio_raw.get('Epíteto específico', ''),
                    })
                    
                    # Normalizar para búsqueda
                    self.simbio_df['nombre_busqueda'] = (
                        self.simbio_df['Nombre_Cientifico'].apply(
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
                        'fuente': '✅ GBIF'
                    }
        
        except Exception as e:
            print(f"⚠️ Error en GBIF: {e}")
        
        return None
    
    def buscar_simbio_exacta(self, genero, epiteto):
        """PASO 1: Búsqueda exacta nombre completo (género + epíteto)."""
        if es_vacio(genero) or es_vacio(epiteto) or len(self.simbio_df) == 0:
            return None
        
        nombre = normalizar_texto(f"{genero} {epiteto}")
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
                'epiteto': safe_val(fila['epiteto']),
                'nombre_comun': safe_val(fila['Nombre_Comun']),
                'fuente': '✅ SIMBIO (EXACTO)'
            }
        
        return None
    
    def buscar_por_epiteto(self, epiteto):
        """PASO 2A: Búsqueda por epíteto específico (si género vacío)."""
        if es_vacio(epiteto) or len(self.simbio_df) == 0:
            return []
        
        epi_norm = normalizar_texto(epiteto)
        resultados = self.simbio_df[
            self.simbio_df['epiteto'].apply(lambda x: normalizar_texto(x)) == epi_norm
        ]
        
        return resultados.to_dict('records') if len(resultados) > 0 else []
    
    def buscar_por_genero(self, genero):
        """PASO 2B: Búsqueda por género (si epíteto vacío o no coincide)."""
        if es_vacio(genero) or len(self.simbio_df) == 0:
            return []
        
        gen_norm = normalizar_texto(genero)
        resultados = self.simbio_df[
            self.simbio_df['genero'].apply(lambda x: normalizar_texto(x)) == gen_norm
        ]
        
        return resultados.to_dict('records') if len(resultados) > 0 else []
    
    def completar_con_gbif(self, resultado_simbio, genero, epiteto):
        """Completa campos vacíos desde GBIF."""
        if not resultado_simbio or resultado_simbio.get('fuente', '').startswith('GBIF'):
            return resultado_simbio
        
        # Si hay campos vacíos en SIMBIO, intentar llenarlos con GBIF
        campos_vacios = [
            key for key in ['reino', 'filo', 'clase', 'orden', 'familia']
            if es_vacio(resultado_simbio.get(key, ''))
        ]
        
        if campos_vacios:
            gbif_data = self.consultar_gbif(genero, epiteto)
            if gbif_data:
                for campo in campos_vacios:
                    resultado_simbio[campo] = gbif_data.get(campo, '')
                resultado_simbio['fuente'] = resultado_simbio.get('fuente', '') + ' + GBIF'
        
        return resultado_simbio
    
    def obtener_opciones_taxonomia(self, genero, epiteto):
        """Retorna lista de opciones de corrección para selector interactivo."""
        if not self.simbio_cargado:
            self.cargar_simbio()
        
        opciones = []
        
        # PASO 1: Búsqueda exacta
        exacta = self.buscar_simbio_exacta(genero, epiteto)
        if exacta:
            opciones.append({
                'nombre': f"{exacta['genero']} {exacta['epiteto']} | {exacta['orden']} (SIMBIO - EXACTO)",
                'datos': exacta
            })
            return opciones  # Si hay exacta, retornar solo esa
        
        # PASO 2: Búsquedas parciales
        # 2A: Por epíteto si género vacío
        if es_vacio(genero) and not es_vacio(epiteto):
            por_epiteto = self.buscar_por_epiteto(epiteto)
            for rec in por_epiteto[:5]:  # Máximo 5 opciones
                opciones.append({
                    'nombre': f"{rec['genero']} {rec['epiteto']} | {rec['orden']} (SIMBIO - EPÍTETO)",
                    'datos': {
                        'reino': rec['reino'],
                        'filo': rec['filo'],
                        'clase': rec['clase'],
                        'orden': rec['orden'],
                        'familia': rec['familia'],
                        'genero': rec['genero'],
                        'epiteto': rec['epiteto'],
                        'nombre_comun': rec['Nombre_Comun'],
                        'fuente': '✅ SIMBIO (EPÍTETO)'
                    }
                })
        
        # 2B: Por género si no hay coincidencia exacta
        if not es_vacio(genero):
            por_genero = self.buscar_por_genero(genero)
            for rec in por_genero[:5]:  # Máximo 5 opciones
                opciones.append({
                    'nombre': f"{rec['genero']} {rec['epiteto']} | {rec['orden']} (SIMBIO - GÉNERO)",
                    'datos': {
                        'reino': rec['reino'],
                        'filo': rec['filo'],
                        'clase': rec['clase'],
                        'orden': rec['orden'],
                        'familia': rec['familia'],
                        'genero': rec['genero'],
                        'epiteto': rec['epiteto'],
                        'nombre_comun': rec['Nombre_Comun'],
                        'fuente': '✅ SIMBIO (GÉNERO)'
                    }
                })
        
        # PASO 3: GBIF (solo si no hay muchas opciones de SIMBIO)
        if len(opciones) < 3:
            gbif = self.consultar_gbif(genero, epiteto)
            if gbif:
                opciones.append({
                    'nombre': f"{gbif['genero']} {gbif['epiteto']} (GBIF)",
                    'datos': gbif
                })
        
        # Opción: Sin corregir
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
                'nombre_comun': '',
                'fuente': 'NO_CORREGIDO'
            }
        })
        
        return opciones if opciones else []
    
    def resolver_taxonomia(self, genero, epiteto):
        """Resuelve taxonomía: SIMBIO exacta → por epíteto → por género → GBIF → original."""
        if not self.simbio_cargado:
            self.cargar_simbio()
        
        # PASO 1: Búsqueda exacta en SIMBIO
        resultado = self.buscar_simbio_exacta(genero, epiteto)
        if resultado:
            # Completar campos vacíos con GBIF
            resultado = self.completar_con_gbif(resultado, genero, epiteto)
            return resultado
        
        # PASO 2A: Si género vacío, buscar por epíteto
        if es_vacio(genero) and not es_vacio(epiteto):
            por_epiteto = self.buscar_por_epiteto(epiteto)
            if len(por_epiteto) == 1:
                rec = por_epiteto[0]
                resultado = {
                    'reino': rec['reino'],
                    'filo': rec['filo'],
                    'clase': rec['clase'],
                    'orden': rec['orden'],
                    'familia': rec['familia'],
                    'genero': rec['genero'],
                    'epiteto': rec['epiteto'],
                    'nombre_comun': rec['Nombre_Comun'],
                    'fuente': '✅ SIMBIO (EPÍTETO)'
                }
                resultado = self.completar_con_gbif(resultado, rec['genero'], rec['epiteto'])
                return resultado
            elif len(por_epiteto) > 1:
                # Múltiples opciones - marca para revisión manual
                return {
                    'genero': safe_val(genero),
                    'epiteto': safe_val(epiteto),
                    'reino': '',
                    'filo': '',
                    'clase': '',
                    'orden': '',
                    'familia': '',
                    'nombre_comun': '',
                    'fuente': f'⚠️ SIMBIO EPÍTETO ({len(por_epiteto)} opciones)',
                    'necesita_revision': True,
                    'opciones': por_epiteto
                }
        
        # PASO 2B: Búsqueda por género
        if not es_vacio(genero):
            por_genero = self.buscar_por_genero(genero)
            if len(por_genero) == 1:
                rec = por_genero[0]
                resultado = {
                    'reino': rec['reino'],
                    'filo': rec['filo'],
                    'clase': rec['clase'],
                    'orden': rec['orden'],
                    'familia': rec['familia'],
                    'genero': rec['genero'],
                    'epiteto': rec['epiteto'],
                    'nombre_comun': rec['Nombre_Comun'],
                    'fuente': '✅ SIMBIO (GÉNERO)'
                }
                resultado = self.completar_con_gbif(resultado, genero, epiteto)
                return resultado
            elif len(por_genero) > 1:
                # Múltiples opciones - marca para revisión manual
                return {
                    'genero': safe_val(genero),
                    'epiteto': safe_val(epiteto),
                    'reino': '',
                    'filo': '',
                    'clase': '',
                    'orden': '',
                    'familia': '',
                    'nombre_comun': '',
                    'fuente': f'⚠️ SIMBIO GÉNERO ({len(por_genero)} opciones)',
                    'necesita_revision': True,
                    'opciones': por_genero
                }
        
        # PASO 3: Fallback a GBIF
        resultado = self.consultar_gbif(genero, epiteto)
        if resultado:
            return resultado
        
        # No encontrado - retornar original
        return {
            'reino': '',
            'filo': '',
            'clase': '',
            'orden': '',
            'familia': '',
            'genero': safe_val(genero),
            'epiteto': safe_val(epiteto),
            'nombre_comun': '',
            'fuente': 'NO_ENCONTRADO'
        }


# Instancia global (sin cargar SIMBIO en import)
gestor_taxonomia = GestorTaxonomia()
