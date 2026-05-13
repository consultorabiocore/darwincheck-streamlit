# ============================================================================ #
#          DarwinCheck Vol.1 - Auditoría Taxonómica y Geográfica             #
#                         MÓDULO: ECOLOGÍA                                   #
# ============================================================================ #

import numpy as np
import pandas as pd
from typing import Dict, Tuple
from scipy.special import gammaln
import warnings

warnings.filterwarnings('ignore')

class EcologyAnalyzer:
    """
    Calculador de índices ecológicos y análisis de biodiversidad
    
    Índices implementados:
    - Riqueza (S)
    - Shannon (H)
    - Simpson (D)
    - Pielou (J)
    - Margalef
    - Chao1
    - Curva de acumulación
    """
    
    @staticmethod
    def calcular_indices(abundancias: pd.Series) -> Dict[str, float]:
        """
        Calcula todos los índices ecológicos
        
        Args:
            abundancias: Series con abundancias de especies
            
        Returns:
            Dict con todos los índices calculados
        """
        
        # Convertir a array numérico
        try:
            abundancias = pd.to_numeric(abundancias, errors='coerce')
            abundancias = abundancias[abundancias.notna()].values
            abundancias = abundancias[abundancias > 0]
        except:
            abundancias = np.array([])
        
        if len(abundancias) == 0:
            return {
                'riqueza': 0,
                'total_individuos': 0,
                'shannon': 0,
                'shannon_max': 0,
                'simpson': 0,
                'pielou': 0,
                'margalef': 0,
                'chao1': 0,
                'representatividad': 0
            }
        
        total = np.sum(abundancias)
        riqueza = len(abundancias)
        
        # Proporciones
        proporciones = abundancias / total
        
        # Shannon
        shannon = -np.sum(proporciones * np.log(proporciones))
        shannon_max = np.log(riqueza)
        
        # Simpson
        simpson = np.sum(proporciones ** 2)
        
        # Pielou (Equitatividad)
        pielou = shannon / shannon_max if shannon_max > 0 else 0
        
        # Margalef
        margalef = (riqueza - 1) / np.log(total) if total > 1 else 0
        
        # Chao1
        singletons = np.sum(abundancias == 1)
        doubletons = np.sum(abundancias == 2)
        
        if doubletons > 0:
            chao1 = riqueza + (singletons ** 2) / (2 * doubletons)
        else:
            chao1 = riqueza
        
        # Representatividad
        representatividad = min((riqueza / chao1) * 100, 100)
        
        return {
            'riqueza': int(riqueza),
            'total_individuos': int(total),
            'shannon': float(shannon),
            'shannon_max': float(shannon_max),
            'simpson': float(simpson),
            'pielou': float(pielou),
            'margalef': float(margalef),
            'chao1': float(chao1),
            'representatividad': float(representatividad)
        }
    
    @staticmethod
    def calcular_curva_acumulacion(matriz_comunidad: np.ndarray, permutaciones: int = 100) -> Dict:
        """
        Calcula curva de acumulación de especies (rarefacción)
        
        Args:
            matriz_comunidad: Matriz muestras x especies
            permutaciones: Número de aleatorios
            
        Returns:
            Dict con puntos de la curva
        """
        
        if matriz_comunidad.size == 0 or matriz_comunidad.shape[0] == 0:
            return {'muestras': [], 'riqueza': [], 'sd': []}
        
        n_muestras = matriz_comunidad.shape[0]
        
        # Limitar para rendimiento
        if n_muestras > 500:
            indices = np.random.choice(n_muestras, 500, replace=False)
            matriz_comunidad = matriz_comunidad[indices, :]
            n_muestras = 500
        
        riqueza_acum = []
        sd_acum = []
        
        for i in range(1, n_muestras + 1):
            riquezas_perm = []
            
            for _ in range(permutaciones):
                indices_perm = np.random.choice(n_muestras, i, replace=False)
                sub_matriz = matriz_comunidad[indices_perm, :]
                riqueza = np.sum(np.sum(sub_matriz, axis=0) > 0)
                riquezas_perm.append(riqueza)
            
            riqueza_acum.append(np.mean(riquezas_perm))
            sd_acum.append(np.std(riquezas_perm))
        
        return {
            'muestras': list(range(1, n_muestras + 1)),
            'riqueza': riqueza_acum,
            'sd': sd_acum
        }
    
    @staticmethod
    def agrupar_por_especie(df: pd.DataFrame) -> pd.DataFrame:
        """
        Agrupa datos por especie y suma abundancias
        
        Args:
            df: DataFrame con columnas 'genero_corr', 'epiteto_corr', 'valor_orig'
            
        Returns:
            DataFrame agrupado con columnas: nombre, Total
        """
        
        # Crear nombre científico
        df_copy = df.copy()
        df_copy['nombre'] = (
            df_copy['genero_corr'].astype(str) + ' ' + 
            df_copy['epiteto_corr'].astype(str)
        ).str.strip()
        
        # Convertir valores a numéricos
        df_copy['valor'] = pd.to_numeric(
            df_copy['valor_orig'].astype(str).str.replace(',', '.'),
            errors='coerce'
        ).fillna(1)
        
        # Agrupar
        agrupado = df_copy.groupby('nombre')['valor'].sum().reset_index()
        agrupado.columns = ['nombre', 'Total']
        agrupado = agrupado.sort_values('Total', ascending=False)
        
        return agrupado
    
    @staticmethod
    def crear_matriz_comunidad(df: pd.DataFrame) -> np.ndarray:
        """
        Crea matriz muestras x especies (filas x columnas)
        
        Args:
            df: DataFrame con columnas 'genero_corr', 'epiteto_corr', 'valor_orig'
            
        Returns:
            Matriz numpy (n_muestras x n_especies)
        """
        
        df_copy = df.copy()
        df_copy['especie'] = (
            df_copy['genero_corr'].astype(str) + ' ' + 
            df_copy['epiteto_corr'].astype(str)
        ).str.strip()
        
        # Convertir valores
        df_copy['valor'] = pd.to_numeric(
            df_copy['valor_orig'].astype(str).str.replace(',', '.'),
            errors='coerce'
        ).fillna(1)
        
        # Crear tabla pivote
        matriz = df_copy.pivot_table(
            index=df_copy.index,
            columns='especie',
            values='valor',
            fill_value=0,
            aggfunc='sum'
        )
        
        return matriz.values
