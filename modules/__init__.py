# ============================================================================ #
#                      DarwinCheck - Paquete de Módulos                        #
# ============================================================================ #
"""
DarwinCheck Vol.1 - Auditoría Taxonómica y Geográfica
Módulos principales para procesamiento de datos Darwin Core
"""

from modules.config import *
from modules.utils import *
from modules.taxonomia import gestor_taxonomia
from modules.coordenadas import validador
from modules.ecologia import calc_ecologico
from modules.graficos import gen_graficos
from modules.excel_io import gestor_excel

__version__ = "1.0.0"
__author__ = "BioCore - Loreto Campos"

__all__ = [
    'gestor_taxonomia',
    'validador',
    'calc_ecologico',
    'gen_graficos',
    'gestor_excel',
]
