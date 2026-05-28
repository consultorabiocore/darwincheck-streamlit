# ============================================================================ #
#              DarwinCheck - Lectura/Escritura de Excel                        #
# ============================================================================ #

import pandas as pd
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment
from io import BytesIO
import warnings

warnings.filterwarnings('ignore')

class GestorExcel:
    """Gestiona lectura y escritura de archivos Excel."""
    
    @staticmethod
    def leer_archivo(archivo_subido):
        """Lee archivo Excel subido."""
        try:
            # Leer la hoja "Ocurrencia"
            df = pd.read_excel(
                archivo_subido,
                sheet_name='Ocurrencia',
                dtype=str
            )
            
            # Limpiar nombres de columnas
            df.columns = df.columns.str.strip()
            
            return df
        
        except Exception as e:
            print(f"Error leyendo Excel: {e}")
            return None
    
    @staticmethod
    def leer_darwin_core(archivo_subido):
        """Lee archivo Darwin Core (alias de leer_archivo con manejo de errores)."""
        try:
            df = GestorExcel.leer_archivo(archivo_subido)
            if df is None:
                return None, "Error al leer el archivo Excel"
            
            # Validar que tenga mínimo 34 columnas
            if len(df.columns) < 34:
                return None, f"El archivo debe tener al menos 34 columnas. Tiene {len(df.columns)}"
            
            return df, None
        
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def guardar_archivo(df, nombre_archivo, datos_auditoria=None):
        """Guarda DataFrame a archivo Excel con formato."""
        try:
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Escribir datos principales
                df.to_excel(writer, sheet_name='Ocurrencia', index=False)
                
                # Si hay datos de auditoría, crear hoja adicional
                if datos_auditoria is not None:
                    datos_auditoria.to_excel(
                        writer,
                        sheet_name='Auditoría',
                        index=False
                    )
                
                # Formatear
                workbook = writer.book
                worksheet = writer.sheets['Ocurrencia']
                
                # Ancho de columnas
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
                
                # Encabezados
                header_fill = PatternFill(
                    start_color="27AE60",
                    end_color="27AE60",
                    fill_type="solid"
                )
                header_font = Font(bold=True, color="FFFFFF")
                
                for cell in worksheet[1]:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal='center', vertical='center')
            
            output.seek(0)
            return output.getvalue()
        
        except Exception as e:
            print(f"Error guardando Excel: {e}")
            return None


# Instancia global
gestor_excel = GestorExcel()
