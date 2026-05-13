# ============================================================================ #
#          DarwinCheck Vol.1 - Auditoría Taxonómica y Geográfica             #
#                    MÓDULO: PROCESAMIENTO DE EXCEL                          #
# ============================================================================ #

import pandas as pd
import numpy as np
from io import BytesIO
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
import streamlit as st
from modules.config import DARWIN_CORE_COLUMNS, MAX_ROWS_DISPLAY
from modules.utils import safe_val

class ExcelProcessor:
    """
    Procesador de archivos Excel Darwin Core
    """
    
    @staticmethod
    def leer_archivo_excel(archivo_subido) -> pd.DataFrame:
        """
        Lee archivo Excel y extrae hoja 'Ocurrencia'
        
        Args:
            archivo_subido: UploadedFile de Streamlit
            
        Returns:
            DataFrame con datos
        """
        try:
            df = pd.read_excel(
                archivo_subido,
                sheet_name='Ocurrencia',
                dtype=str
            )
            
            # Limpiar columnas
            df.columns = [col.strip() for col in df.columns]
            
            # Limpiar datos
            for col in df.columns:
                df[col] = df[col].fillna('').astype(str)
                df[col] = df[col].apply(
                    lambda x: '' if x.lower() in ['na', 'null', 'n/a', 'nan'] else x.strip()
                )
            
            return df
        
        except Exception as e:
            st.error(f"❌ Error al leer archivo: {str(e)}")
            return pd.DataFrame()
    
    @staticmethod
    def exportar_excel(df_corregido: pd.DataFrame, df_original: pd.DataFrame = None) -> BytesIO:
        """
        Exporta DataFrame corregido a Excel
        
        Args:
            df_corregido: DataFrame con datos corregidos
            df_original: DataFrame original (para conservar otras hojas)
            
        Returns:
            BytesIO con archivo Excel
        """
        
        try:
            output = BytesIO()
            
            # Crear writer
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Escribir hoja corregida
                df_corregido.to_excel(
                    writer,
                    sheet_name='Ocurrencia',
                    index=False
                )
                
                # Ajustar ancho de columnas
                worksheet = writer.sheets['Ocurrencia']
                for idx, col in enumerate(df_corregido.columns, 1):
                    col_letter = get_column_letter(idx)
                    max_length = max(
                        df_corregido[col].astype(str).apply(len).max(),
                        len(col)
                    )
                    worksheet.column_dimensions[col_letter].width = min(max_length + 2, 50)
            
            output.seek(0)
            return output
        
        except Exception as e:
            st.error(f"❌ Error exportando Excel: {str(e)}")
            return None
    
    @staticmethod
    def obtener_columna_excel(df: pd.DataFrame, indice: int) -> pd.Series:
        """
        Obtiene columna por índice (1-basado como en Darwin Core)
        
        Args:
            df: DataFrame
            indice: Índice de columna (1-basado)
            
        Returns:
            Series o Series vacía
        """
        
        indice_0 = indice - 1
        if indice_0 < 0 or indice_0 >= len(df.columns):
            return pd.Series([''] * len(df))
        
        return df.iloc[:, indice_0]
    
    @staticmethod
    def asignar_columna_excel(df: pd.DataFrame, indice: int, valores: list) -> pd.DataFrame:
        """
        Asigna valores a columna por índice
        
        Args:
            df: DataFrame
            indice: Índice de columna (1-basado)
            valores: Lista de valores
            
        Returns:
            DataFrame modificado
        """
        
        indice_0 = indice - 1
        if indice_0 < 0 or indice_0 >= len(df.columns):
            return df
        
        # Asegurar que valores tiene la misma longitud
        valores = (valores + [''] * len(df))[:len(df)]
        
        df.iloc[:, indice_0] = valores
        return df
