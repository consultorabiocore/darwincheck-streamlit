# ============================================================================ #
#          DarwinCheck Vol.1 - Auditoría Taxonómica y Geográfica             #
#                         APLICACIÓN PRINCIPAL - STREAMLIT                   #
# ============================================================================ #

import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime
from io import BytesIO

# Importar módulos
from modules.config import (
    APP_TITLE, APP_AUTHOR, FORM_URL, COLOR_SUCCESS, COLOR_ERROR, COLOR_INFO,
    MAX_ROWS_DISPLAY, MAX_ROWS_PROCESS, MSG_LOADING_FILE, MSG_PROCESSING,
    MSG_COMPLETE, MSG_NO_DATA, MSG_NO_AMBIGUITIES
)
from modules.utils import safe_val, format_integer, format_decimal, format_coordinate, detect_header_row
from modules.taxonomia import TaxonomyManager
from modules.coordenadas import CoordinateValidator
from modules.ecologia import EcologyAnalyzer
from modules.graficos import ChartGenerator
from modules.excel_io import ExcelProcessor

# ==================== CONFIGURACIÓN STREAMLIT ====================
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS
st.markdown("""
    <style>
    .metric-box { background: #f0f2f6; padding: 20px; border-radius: 10px; margin: 10px 0; }
    .success-box { background: #d4edda; padding: 15px; border-radius: 5px; border-left: 5px solid #28a745; }
    .error-box { background: #f8d7da; padding: 15px; border-radius: 5px; border-left: 5px solid #dc3545; }
    .warning-box { background: #fff3cd; padding: 15px; border-radius: 5px; border-left: 5px solid #ffc107; }
    </style>
""", unsafe_allow_html=True)

# ==================== INICIALIZACIÓN SESIÓN ====================
if 'datos_originales' not in st.session_state:
    st.session_state.datos_originales = None
if 'datos_corregidos' not in st.session_state:
    st.session_state.datos_corregidos = None
if 'selecciones_manuales' not in st.session_state:
    st.session_state.selecciones_manuales = {}
if 'taxonomy_manager' not in st.session_state:
    st.session_state.taxonomy_manager = TaxonomyManager()

# ==================== HEADER ====================
st.markdown(f"## 🔬 {APP_TITLE}")
st.markdown(f"*{APP_AUTHOR}*")
st.markdown("---")

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("### ⚙️ Configuración")
    
    # Carga de archivo
    archivo = st.file_uploader(
        "📁 Cargar planilla Darwin Core (.xlsx)",
        type=['xlsx', 'xls'],
        help="Debe contener una hoja llamada 'Ocurrencia' con el estándar Darwin Core"
    )
    
    # Color para gráficos
    color_graficos = st.color_picker(
        "🎨 Color de gráficos",
        value="#27ae60"
    )
    
    st.markdown("---")
    
    # Información SIMBIO
    simbio_df = st.session_state.taxonomy_manager.simbio_df
    n_simbio = len(simbio_df) if simbio_df is not None else 0
    st.markdown(f"**📊 Bases de datos:**")
    st.markdown(f"- SIMBIO: {n_simbio} especies")
    st.markdown(f"- GBIF: activo (en línea)")
    
    st.markdown("---")
    
    # Botones de acción
    if st.session_state.datos_corregidos is not None:
        st.markdown("### 📥 Descargar Resultados")
        
        if st.button("⬇️ Descargar Excel Corregido", use_container_width=True, type="primary"):
            df_export = st.session_state.datos_corregidos.copy()
            excel_file = ExcelProcessor.exportar_excel(df_export)
            
            if excel_file:
                st.download_button(
                    label="💾 Descargar archivo",
                    data=excel_file,
                    file_name=f"DarwinCheck_Vol1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
    
    st.markdown("---")
    
    # Links
    st.markdown("### 📞 Soporte")
    st.markdown(f"[📋 Reportar error]({FORM_URL})")
    st.markdown(f"© 2026 BioCore")

# ==================== INSTRUCCIONES ====================
with st.container():
    st.markdown("### 📋 Instrucciones de uso")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        1. Carga tu planilla Darwin Core SMA (formato oficial)
        2. La app procesa solo la hoja 'Ocurrencia'
        3. Corrige automáticamente taxonomía (GBIF, SIMBIO)
        4. Valida las coordenadas geográficas
        5. Si hay ambigüedad, selecciona la opción correcta
        """)
    
    with col2:
        st.markdown("""
        6. Los gráficos se pueden descargar como PNG
        7. Al descargar EXCEL obtendrás:
           - ✅ ESTADO_GEOGRAFICO
           - 📝 NOTAS_AUDITORIA
        8. Revisa la pestaña "Guía Metodológica"
        """)

# ==================== PROCESAMIENTO DEL ARCHIVO ====================
if archivo is not None:
    st.markdown("---")
    
    with st.spinner(MSG_LOADING_FILE):
        st.session_state.datos_originales = ExcelProcessor.leer_archivo_excel(archivo)
    
    if st.session_state.datos_originales is None or len(st.session_state.datos_originales) == 0:
        st.error(MSG_NO_DATA)
        st.stop()
    
    df_original = st.session_state.datos_originales
    
    # Información del archivo
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 Filas", format_integer(len(df_original)))
    with col2:
        st.metric("📋 Columnas", format_integer(len(df_original.columns)))
    with col3:
        if len(df_original) > MAX_ROWS_PROCESS:
            st.warning(f"⚠️ Archivo > {MAX_ROWS_PROCESS}k filas. Se limitará el procesamiento")
    
    # ==================== PROCESAMIENTO TAXONÓMICO ====================
    with st.spinner(MSG_PROCESSING):
        df_proceso = df_original.copy()
        if len(df_proceso) > MAX_ROWS_DISPLAY:
            df_proceso = df_proceso.head(MAX_ROWS_DISPLAY)
        
        # Crear DataFrame de resultados
        resultados = pd.DataFrame({
            'id': range(len(df_proceso)),
            'reino_orig': ExcelProcessor.obtener_columna_excel(df_proceso, 15).values,
            'filo_orig': ExcelProcessor.obtener_columna_excel(df_proceso, 16).values,
            'clase_orig': ExcelProcessor.obtener_columna_excel(df_proceso, 17).values,
            'orden_orig': ExcelProcessor.obtener_columna_excel(df_proceso, 18).values,
            'familia_orig': ExcelProcessor.obtener_columna_excel(df_proceso, 19).values,
            'genero_orig': ExcelProcessor.obtener_columna_excel(df_proceso, 20).values,
            'epiteto_orig': ExcelProcessor.obtener_columna_excel(df_proceso, 22).values,
            'nombre_comun_orig': ExcelProcessor.obtener_columna_excel(df_proceso, 24).values,
            'valor_orig': ExcelProcessor.obtener_columna_excel(df_proceso, 30).values,
            'lat_orig': ExcelProcessor.obtener_columna_excel(df_proceso, 32).values,
            'lon_orig': ExcelProcessor.obtener_columna_excel(df_proceso, 33).values,
        })
        
        # Detectar encabezados
        resultados['es_encabezado'] = resultados.apply(
            lambda row: detect_header_row(row.to_dict()), axis=1
        )
        
        # Inicializar columnas de corrección
        for col in ['reino', 'filo', 'clase', 'orden', 'familia', 'genero', 'epiteto']:
            resultados[f'{col}_corr'] = resultados[f'{col}_orig']
        
        resultados['nombre_comun_corr'] = resultados['nombre_comun_orig']
        resultados['fuente'] = 'Original'
        resultados['cambios'] = False
        resultados['necesita_revision'] = False
        resultados['opciones_json'] = ''
        resultados['alerta_geo'] = ''
        resultados['alerta_tax'] = ''
        resultados['notas'] = ''
        
        # Procesamiento taxonómico
        progress_bar = st.progress(0)
        taxonomy_mgr = st.session_state.taxonomy_manager
        
        for idx, row in resultados.iterrows():
            if row['es_encabezado']:
                continue
            
            genero = safe_val(row['genero_orig'])
            epiteto = safe_val(row['epiteto_orig'])
            
            if genero or epiteto:
                correcc = taxonomy_mgr.corregir_taxonomia(
                    genero, epiteto,
                    archivo_pequeno=len(df_original) < 1000
                )
                
                resultados.at[idx, 'genero_corr'] = correcc['genero']
                resultados.at[idx, 'epiteto_corr'] = correcc['epiteto']
                resultados.at[idx, 'reino_corr'] = correcc['reino']
                resultados.at[idx, 'filo_corr'] = correcc['filo']
                resultados.at[idx, 'clase_corr'] = correcc['clase']
                resultados.at[idx, 'orden_corr'] = correcc['orden']
                resultados.at[idx, 'familia_corr'] = correcc['familia']
                resultados.at[idx, 'fuente'] = correcc['fuente']
                resultados.at[idx, 'cambios'] = (
                    correcc['genero'] != genero or correcc['epiteto'] != epiteto
                )
                resultados.at[idx, 'necesita_revision'] = correcc['necesita_revision']
                
                if correcc['opciones']:
                    resultados.at[idx, 'opciones_json'] = json.dumps(correcc['opciones'])
            
            # Validar coordenadas
            estado_geo, ubicacion = CoordinateValidator.validar_coordenada_chile(
                row['lat_orig'], row['lon_orig']
            )
            resultados.at[idx, 'alerta_geo'] = estado_geo
            
            progress_bar.progress((idx + 1) / len(resultados))
        
        st.session_state.datos_corregidos = resultados
        st.success(MSG_COMPLETE)

# ==================== MOSTRAR MÉTRICAS ====================
if st.session_state.datos_corregidos is not None:
    st.markdown("---")
    st.markdown("### 📊 Índices de Biodiversidad")
    
    df_corr = st.session_state.datos_corregidos[~st.session_state.datos_corregidos['es_encabezado']].copy()
    
    # Agrupar por especie
    resumen = EcologyAnalyzer.agrupar_por_especie(df_corr)
    
    if len(resumen) > 0:
        # Calcular índices
        indices = EcologyAnalyzer.calcular_indices(resumen['Total'])
        
        # Mostrar métricas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 Total Individuos", format_integer(indices['total_individuos']))
        with col2:
            st.metric("🌿 Riqueza (S)", format_integer(indices['riqueza']))
        with col3:
            st.metric("📈 Shannon (H)", format_decimal(indices['shannon'], 3))
        with col4:
            st.metric("🎯 Simpson (D)", format_decimal(indices['simpson'], 4))
        
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            st.metric("⚖️ Pielou (J)", format_decimal(indices['pielou'], 3))
        with col6:
            st.metric("📊 Margalef", format_decimal(indices['margalef'], 2))
        with col7:
            st.metric("🔮 Chao1", format_integer(indices['chao1']))
        with col8:
            color_rep = "🟢" if indices['representatividad'] >= 80 else "🟡" if indices['representatividad'] >= 50 else "🔴"
            st.metric(
                f"{color_rep} Representatividad",
                f"{format_decimal(indices['representatividad'], 1)}%"
            )

# ==================== TABLAS Y GRÁFICOS ====================
if st.session_state.datos_corregidos is not None:
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Gráficos",
        "📋 Tabla de Cambios",
        "📋 Datos Corregidos",
        "📘 Metodología",
        "ℹ️ Información"
    ])
    
    df_corr = st.session_state.datos_corregidos[~st.session_state.datos_corregidos['es_encabezado']].copy()
    resumen = EcologyAnalyzer.agrupar_por_especie(df_corr)
    
    # TAB: GRÁFICOS
    with tab1:
        st.markdown("### 📊 Análisis de Biodiversidad")
        
        subtab1, subtab2, subtab3, subtab4 = st.tabs([
            "📊 Abundancia",
            "🌰 Treemap",
            "📈 Acumulación",
            "🛡️ Conservación"
        ])
        
        with subtab1:
            if len(resumen) > 0:
                fig = ChartGenerator.grafico_abundancia(resumen, color_graficos)
                st.plotly_chart(fig, use_container_width=True)
                st.download_button(
                    "📥 Descargar PNG",
                    fig.to_image(format="png"),
                    file_name="abundancia.png",
                    mime="image/png"
                )
        
        with subtab2:
            if len(resumen) > 0:
                fig = ChartGenerator.grafico_treemap(resumen, color_graficos)
                st.plotly_chart(fig, use_container_width=True)
                st.download_button(
                    "📥 Descargar PNG",
                    fig.to_image(format="png"),
                    file_name="treemap.png",
                    mime="image/png"
                )
        
        with subtab3:
            if len(resumen) > 0:
                indices = EcologyAnalyzer.calcular_indices(resumen['Total'])
                
                # Curva de acumulación
                matriz = EcologyAnalyzer.crear_matriz_comunidad(df_corr)
                if matriz.size > 0:
                    curva_data = EcologyAnalyzer.calcular_curva_acumulacion(matriz)
                    
                    if len(curva_data['muestras']) > 0:
                        fig = ChartGenerator.grafico_curva_acumulacion(
                            curva_data['muestras'],
                            curva_data['riqueza'],
                            curva_data['sd'],
                            indices['chao1'],
                            indices['representatividad'],
                            color_graficos
                        )
                        st.plotly_chart(fig, use_container_width=True)
        
        with subtab4:
            df_cons = df_corr[df_corr['alerta_conservacion'].notna() & (df_corr['alerta_conservacion'] != '')]
            if len(df_cons) > 0:
                fig = ChartGenerator.grafico_conservacion(df_cons, color_graficos)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay registros de especies protegidas")
    
    # TAB: TABLA DE CAMBIOS
    with tab2:
        cambios = st.session_state.datos_corregidos[st.session_state.datos_corregidos['cambios'] == True]
        
        if len(cambios) > 0:
            st.subheader(f"✅ {len(cambios)} cambios detectados")
            
            df_mostrar = cambios[[
                'id', 'fuente', 'genero_orig', 'genero_corr',
                'epiteto_orig', 'epiteto_corr', 'orden_orig', 'orden_corr'
            ]].copy()
            
            st.dataframe(
                df_mostrar,
                use_container_width=True,
                hide_index=True,
                height=400
            )
        else:
            st.info(MSG_NO_AMBIGUITIES)
    
    # TAB: DATOS CORREGIDOS
    with tab3:
        st.subheader("Tabla de Datos Corregidos")
        
        # Seleccionar columnas
        cols_mostrar = [
            'genero_corr', 'epiteto_corr', 'reino_corr', 'orden_corr',
            'familia_corr', 'fuente', 'alerta_geo', 'notas'
        ]
        
        st.dataframe(
            st.session_state.datos_corregidos[cols_mostrar].head(100),
            use_container_width=True,
            height=500
        )
    
    # TAB: METODOLOGÍA
    with tab4:
        st.markdown("""
        ### 🔬 Protocolo de Estandarización de Datos Biológicos Darwin Core
        
        Desarrollado por **Loreto Campos (BioCore)** para auditoría de datos biológicos 
        bajo el estándar Darwin Core exigido por la SMA.
        
        #### 🎯 Funcionalidades Principales
        
        1. **Corrección Taxonómica Automática** – Valida contra SIMBIO (nacional) y GBIF (global)
        2. **Detección de Ambigüedades** – Si hay múltiples coincidencias, permite seleccionar
        3. **Validación de Coordenadas** – Verifica ubicación dentro de Chile o el mar
        4. **Análisis de Biodiversidad** – Calcula índices ecológicos e genera gráficos
        5. **Exportación de Datos** – Genera Excel con columnas de auditoría
        
        #### 🔍 Proceso de Corrección Taxonómica
        
        1. **Limpieza de texto** – Normalización y eliminación de caracteres raros
        2. **Búsqueda en SIMBIO** – Prioridad nacional
           - Coincidencia exacta (género + epíteto)
           - Por género solo
           - Por epíteto solo
        3. **Búsqueda en GBIF** – Si SIMBIO no tiene la especie (archivos < 1000 filas)
        4. **Detección de especies protegidas** – Consulta estado de conservación
        5. **Selección manual** – Si hay ambigüedad, el usuario selecciona la correcta
        
        #### 🌍 Validación Geoespacial
        
        - **Chile continental**: -56°S a -17.5°S, -76°O a -66°O
        - **Rapa Nui**: ~-27.1°, -109.4°
        - **Juan Fernández**: ~-33.6°, -78.8°
        
        #### 📊 Índices Ecológicos
        
        - **Riqueza (S)**: Número de especies diferentes
        - **Shannon (H)**: Diversidad (0-5, mayor = más diverso)
        - **Simpson (D)**: Dominancia (0-1, mayor = menos diverso)
        - **Pielou (J)**: Equitatividad (uniformidad)
        - **Margalef**: Riqueza estandarizada
        - **Chao1**: Estimador de riqueza verdadera
        - **Representatividad**: % especies observadas vs. Chao1
        
        #### ⚖️ Propiedad Intelectual
        
        © 2026 BioCore. Desarrollado por Loreto Campos. 
        Prohibida su reproducción total o parcial sin autorización.
        """)
    
    # TAB: INFORMACIÓN
    with tab5:
        st.markdown(f"""
        ### ℹ️ Acerca de DarwinCheck Vol.1
        
        **Versión:** 1.0 (Python + Streamlit)
        
        **Desarrollador:** {APP_AUTHOR}
        
        **Última actualización:** {datetime.now().strftime('%Y-%m-%d')}
        
        #### 📦 Tecnología
        
        - **Framework UI:** Streamlit
        - **Análisis de datos:** Pandas, NumPy, SciPy
        - **Gráficos:** Plotly
        - **Validación taxonómica:** GBIF API, SIMBIO (Excel)
        - **Exportación:** OpenPyXL
        
        #### 🔗 Enlaces útiles
        
        - [GBIF](https://www.gbif.org/) – Global Biodiversity Information Facility
        - [Darwin Core](https://dwc.tdwg.org/) – Estándar de datos
        - [SMA Chile](https://www.sma.gob.cl/) – Superintendencia del Medio Ambiente
        
        #### 📞 Soporte
        
        Para reportar errores o sugerir mejoras:
        [📋 Formulario de contacto]({FORM_URL})
        """)

else:
    st.info("👈 **Carga un archivo Excel para comenzar**")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown(f"<div style='text-align: center; color: gray; font-size: 0.8em;'>{APP_AUTHOR}</div>", unsafe_allow_html=True)
