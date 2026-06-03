# ============================================================================ #
#          DarwinCheck Vol.1 - Auditoría Taxonómica y Geográfica             #
#               Versión Python/Streamlit (MIGRACIÓN DESDE R)                 #
# ============================================================================ #

import streamlit as st
from pathlib import Path
import sys
import traceback

# ==================== MOSTRAR ESTADO EN PANTALLA ====================
status_placeholder = st.empty()

def mostrar_estado(mensaje, tipo="info"):
    """Muestra estado en tiempo real en la pantalla."""
    if tipo == "error":
        status_placeholder.error(f"❌ {mensaje}")
    elif tipo == "success":
        status_placeholder.success(f"✅ {mensaje}")
    else:
        status_placeholder.info(f"⏳ {mensaje}")

# ==================== CONFIGURAR RUTA ====================
try:
    mostrar_estado("Configurando rutas...")
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    CACHE_DIR = BASE_DIR / "cache"
    TEMP_DIR = BASE_DIR / "temp"
    LOGO_FILE = BASE_DIR / "logo.png"
    
    sys.path.insert(0, str(BASE_DIR))
    
    for dir_path in [DATA_DIR, LOGS_DIR, CACHE_DIR, TEMP_DIR]:
        dir_path.mkdir(exist_ok=True)
    
    mostrar_estado("Rutas configuradas", "success")
except Exception as e:
    mostrar_estado(f"Error configurando rutas: {str(e)}", "error")
    st.stop()

# ==================== IMPORTS BÁSICOS ====================
try:
    mostrar_estado("Importando librerías básicas...")
    import pandas as pd
    import numpy as np
    from datetime import datetime
    from io import BytesIO
    import warnings
    warnings.filterwarnings('ignore')
    mostrar_estado("Librerías básicas importadas", "success")
except Exception as e:
    mostrar_estado(f"Error en librerías básicas: {str(e)}", "error")
    st.error(traceback.format_exc())
    st.stop()

# ==================== IMPORTAR MÓDULOS (SIN LAZY LOADING) ====================
try:
    mostrar_estado("Importando modules.utils...")
    from modules.utils import (
        safe_val, normalizar_texto, limpiar_dataframe, fmt_entero, fmt_decimal,
        fmt_coordenada, detectar_encabezado, formatar_hora, gms_a_decimal,
        registrar_log, es_vacio
    )
    mostrar_estado("modules.utils importado", "success")
except Exception as e:
    mostrar_estado(f"Error en modules.utils: {str(e)}", "error")
    st.error(traceback.format_exc())
    st.stop()

try:
    mostrar_estado("Importando modules.config...")
    from modules.config import (
        SIMBIO_FILE, GBIF_API_BASE, GBIF_TIMEOUT,
        CHILE_CONTINENTAL, RAPA_NUI, JUAN_FERNANDEZ
    )
    mostrar_estado("modules.config importado", "success")
except Exception as e:
    mostrar_estado(f"Error en modules.config: {str(e)}", "error")
    st.error(traceback.format_exc())
    st.stop()

try:
    mostrar_estado("Importando modules.coordenadas...")
    from modules.coordenadas import validador
    mostrar_estado("modules.coordenadas importado", "success")
except Exception as e:
    mostrar_estado(f"Error en modules.coordenadas: {str(e)}", "error")
    st.error(traceback.format_exc())
    st.stop()

try:
    mostrar_estado("Importando modules.ecologia...")
    from modules.ecologia import calc_ecologico
    mostrar_estado("modules.ecologia importado", "success")
except Exception as e:
    mostrar_estado(f"Error en modules.ecologia: {str(e)}", "error")
    st.error(traceback.format_exc())
    st.stop()

try:
    mostrar_estado("Importando modules.graficos...")
    from modules.graficos import gen_graficos
    mostrar_estado("modules.graficos importado", "success")
except Exception as e:
    mostrar_estado(f"Error en modules.graficos: {str(e)}", "error")
    st.error(traceback.format_exc())
    st.stop()

try:
    mostrar_estado("Importando modules.excel_io...")
    from modules.excel_io import gestor_excel
    mostrar_estado("modules.excel_io importado", "success")
except Exception as e:
    mostrar_estado(f"Error en modules.excel_io: {str(e)}", "error")
    st.error(traceback.format_exc())
    st.stop()

try:
    mostrar_estado("Importando modules.taxonomia (esto puede tardar)...")
    from modules.taxonomia import gestor_taxonomia
    mostrar_estado("modules.taxonomia importado", "success")
except Exception as e:
    mostrar_estado(f"Error en modules.taxonomia: {str(e)}", "error")
    st.error(f"**Traceback completo:**\n```\n{traceback.format_exc()}\n```")
    st.stop()

mostrar_estado("✅ TODOS LOS MÓDULOS CARGADOS CORRECTAMENTE", "success")

# ==================== CARGAR SIMBIO AL INICIO ====================
try:
    mostrar_estado("Cargando SIMBIO (base de datos nacional)...")
    gestor_taxonomia.cargar_simbio()
    num_simbio = len(gestor_taxonomia.simbio_df) if gestor_taxonomia.simbio_df is not None else 0
    mostrar_estado(f"✅ SIMBIO cargado: {num_simbio} especies", "success")
except Exception as e:
    mostrar_estado(f"⚠️ Error cargando SIMBIO: {str(e)}", "info")

# ==================== CONFIGURACIÓN STREAMLIT ====================
st.set_page_config(
    page_title="DarwinCheck Vol.1",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS
st.markdown("""
    <style>
    .metric-card { background: linear-gradient(135deg, #27ae60 0%, #1e8449 100%);
                   color: white; padding: 20px; border-radius: 10px; 
                   text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .error-row { background-color: #ffcccc; }
    .success-row { background-color: #d4edda; }
    .warning-row { background-color: #fff3cd; }
    h1 { color: #27ae60; text-align: center; font-weight: bold; }
    h2 { color: #2c3e50; border-bottom: 3px solid #27ae60; padding-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# ==================== INICIALIZAR SESSION STATE ====================
if 'datos_originales' not in st.session_state:
    st.session_state.datos_originales = None
    st.session_state.datos_corregidos = None
    st.session_state.selecciones_manuales = {}
    st.session_state.color_grafico = "#27ae60"
    st.session_state.opciones_taxonomia = {}

# ==================== HEADER ====================
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<h1>🔬 DarwinCheck Vol.1</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:#7f8c8d;'>Auditoría Taxonómica y Geográfica</h3>", 
               unsafe_allow_html=True)

st.divider()

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("## 📁 Configuración")
    
    # Logo
    if LOGO_FILE.exists():
        st.image(str(LOGO_FILE), use_column_width=True)
    
    st.divider()
    
    # Carga archivo
    archivo_cargado = st.file_uploader(
        "1️⃣ Cargar Planilla Darwin Core (SMA)",
        type=['xlsx', 'xls'],
        accept_multiple_files=False,
        help="Archivo Excel con hoja 'Ocurrencia' y mínimo 34 columnas"
    )
    
    # Selector de color
    col_grafico = st.color_picker(
        "2️⃣ Color de Gráficos",
        value="#27ae60",
        help="Selecciona color para visualizaciones"
    )
    st.session_state.color_grafico = col_grafico
    gen_graficos.actualizar_color(col_grafico)
    
    st.divider()
    
    # Información SIMBIO
    st.markdown("### 📊 Bases de Datos")
    col_stats1, col_stats2 = st.columns(2)
    
    with col_stats1:
        try:
            num_simbio = len(gestor_taxonomia.simbio_df) if gestor_taxonomia.simbio_df is not None and len(gestor_taxonomia.simbio_df) > 0 else 0
            st.metric("SIMBIO", f"{num_simbio} sp.", delta="Nacional", delta_color="off")
        except:
            st.metric("SIMBIO", "Error", delta_color="off")
    
    with col_stats2:
        st.metric("GBIF", "Activo", delta="Global", delta_color="off")
    
    st.divider()
    st.markdown("""
        <small>© 2026 BioCore | Loreto Campos</small>
    """, unsafe_allow_html=True)

# ==================== FUNCIONES PRINCIPALES ====================

def generar_excel_descarga():
    """Genera archivo Excel descargable con correcciones."""
    try:
        df_export = st.session_state.datos_originales.copy()
        corr = st.session_state.datos_corregidos
        
        # Actualizar columnas taxonómicas
        if ncol := df_export.shape[1]:
            if ncol >= 15: df_export.iloc[:, 14] = corr['reino_corr'].values
            if ncol >= 16: df_export.iloc[:, 15] = corr['filo_corr'].values
            if ncol >= 17: df_export.iloc[:, 16] = corr['clase_corr'].values
            if ncol >= 18: df_export.iloc[:, 17] = corr['orden_corr'].values
            if ncol >= 19: df_export.iloc[:, 18] = corr['familia_corr'].values
            if ncol >= 20: df_export.iloc[:, 19] = corr['genero_corr'].values
            if ncol >= 22: df_export.iloc[:, 21] = corr['epiteto_corr'].values
            if ncol >= 24: df_export.iloc[:, 23] = corr['nombre_comun_corr'].values
            if ncol >= 8: df_export.iloc[:, 7] = corr['hora_inicio_corr'].values
            if ncol >= 32: df_export.iloc[:, 31] = corr['lat_corr'].values
            if ncol >= 33: df_export.iloc[:, 32] = corr['lon_corr'].values
            if ncol >= 34: df_export.iloc[:, 33] = corr['hora_registro_corr'].values
        
        # Agregar columnas auditoría
        df_export['ESTADO_GEOGRAFICO'] = corr['estado_geografico'].values
        df_export['NOTAS_AUDITORIA'] = corr['fuente'].values
        
        # Escribir a BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_export.to_excel(writer, sheet_name='Ocurrencia', index=False)
        
        return output.getvalue()
    
    except Exception as e:
        st.error(f"Error generando descarga: {str(e)}")
        return None


def procesar_archivo(df_raw):
    """Procesa archivo y ejecuta correcciones taxonómicas."""
    
    # Asegurarse de que SIMBIO esté cargado
    if not gestor_taxonomia.simbio_cargado:
        with st.spinner("⏳ Cargando SIMBIO..."):
            gestor_taxonomia.cargar_simbio()
    
    with st.spinner("⏳ Procesando archivo..."):
        # Inicializar dataframe de resultados
        datos_corr = pd.DataFrame({
            'id': range(len(df_raw)),
            'es_encabezado': [detectar_encabezado(
                df_raw.iloc[i, 14] if df_raw.shape[1] > 14 else '',
                df_raw.iloc[i, 15] if df_raw.shape[1] > 15 else '',
                df_raw.iloc[i, 16] if df_raw.shape[1] > 16 else '',
                df_raw.iloc[i, 17] if df_raw.shape[1] > 17 else '',
                df_raw.iloc[i, 18] if df_raw.shape[1] > 18 else '',
                df_raw.iloc[i, 19] if df_raw.shape[1] > 19 else ''
            ) for i in range(len(df_raw))],
            'genero_orig': df_raw.iloc[:, 19].values if df_raw.shape[1] > 19 else '',
            'epiteto_orig': df_raw.iloc[:, 21].values if df_raw.shape[1] > 21 else '',
            'reino_orig': df_raw.iloc[:, 14].values if df_raw.shape[1] > 14 else '',
            'filo_orig': df_raw.iloc[:, 15].values if df_raw.shape[1] > 15 else '',
            'clase_orig': df_raw.iloc[:, 16].values if df_raw.shape[1] > 16 else '',
            'orden_orig': df_raw.iloc[:, 17].values if df_raw.shape[1] > 17 else '',
            'familia_orig': df_raw.iloc[:, 18].values if df_raw.shape[1] > 18 else '',
            'nombre_comun_orig': df_raw.iloc[:, 23].values if df_raw.shape[1] > 23 else '',
            'valor_orig': df_raw.iloc[:, 29].values if df_raw.shape[1] > 29 else '1',
            'lat_orig': df_raw.iloc[:, 31].values if df_raw.shape[1] > 31 else '',
            'lon_orig': df_raw.iloc[:, 32].values if df_raw.shape[1] > 32 else '',
            'hora_inicio_orig': df_raw.iloc[:, 7].values if df_raw.shape[1] > 7 else '',
            'hora_registro_orig': df_raw.iloc[:, 33].values if df_raw.shape[1] > 33 else '',
        })
        
        # Copiar columnas originales a corregidas
        for col in ['genero', 'epiteto', 'reino', 'filo', 'clase', 'orden', 'familia', 'nombre_comun']:
            datos_corr[f'{col}_corr'] = datos_corr[f'{col}_orig']
        
        # Procesar coordenadas
        datos_corr['lat_corr'] = [
            fmt_coordenada(gms_a_decimal(datos_corr.loc[i, 'lat_orig']))
            for i in range(len(datos_corr))
        ]
        datos_corr['lon_corr'] = [
            fmt_coordenada(gms_a_decimal(datos_corr.loc[i, 'lon_orig']))
            for i in range(len(datos_corr))
        ]
        
        # Formatear horas
        datos_corr['hora_inicio_corr'] = [
            formatar_hora(datos_corr.loc[i, 'hora_inicio_orig'])
            for i in range(len(datos_corr))
        ]
        datos_corr['hora_registro_corr'] = [
            formatar_hora(datos_corr.loc[i, 'hora_registro_orig'])
            for i in range(len(datos_corr))
        ]
        
        # TAXONOMÍA - PASO 1: SIMBIO EXACTA
        progress_bar = st.progress(0)
        status_text = st.empty()
        opciones_para_revision = {}
        
        for idx, row in datos_corr.iterrows():
            if row['es_encabezado']:
                continue
            
            genero = safe_val(row['genero_orig'])
            epiteto = safe_val(row['epiteto_orig'])
            
            if es_vacio(genero) and es_vacio(epiteto):
                progress_bar.progress((idx + 1) / len(datos_corr))
                continue
            
            # Resolver taxonomía
            resultado = gestor_taxonomia.resolver_taxonomia(genero, epiteto)
            
            # Aplicar corrección
            for col in ['reino', 'filo', 'clase', 'orden', 'familia', 'genero', 'epiteto']:
                valor = resultado.get(col, '')
                datos_corr.at[idx, f'{col}_corr'] = safe_val(valor) if valor else ''
            
            # Guardar fuente
            datos_corr.at[idx, 'fuente'] = resultado.get('fuente', 'NO_ENCONTRADO')
            
            # Si necesita revisión manual
            if resultado.get('necesita_revision', False):
                opciones_para_revision[idx] = resultado
            
            status_text.text(f"Procesando fila {idx + 1} de {len(datos_corr)}...")
            progress_bar.progress((idx + 1) / len(datos_corr))
        
        status_text.empty()
        
        # VALIDACIÓN GEOGRÁFICA
        validaciones_geo = []
        for idx, row in datos_corr.iterrows():
            val = validador.validar_coordinate_chile(row['lat_orig'], row['lon_orig'])
            validaciones_geo.append(val)
        
        geo_df = pd.DataFrame(validaciones_geo)
        datos_corr['estado_geografico'] = geo_df['estado']
        datos_corr['ubicacion_geografica'] = geo_df['ubicacion']
        
        # Guardar opciones en session state
        st.session_state.opciones_taxonomia = opciones_para_revision
        
        return datos_corr


# ==================== FLUJO PRINCIPAL ====================

# Instrucciones
with st.expander("📋 Instrucciones de uso", expanded=True):
    st.markdown("""
    ### 📖 ¿Cómo usar DarwinCheck Vol.1?

    **DarwinCheck** es una herramienta de auditoría taxonómica y geográfica para datos Darwin Core.

    #### 🎯 Pasos principales:

    1. **Cargar archivo Excel** con estructura Darwin Core (mínimo 34 columnas)
    2. **Seleccionar color** para los gráficos (opcional)
    3. El sistema automáticamente:
        - ✅ Normaliza datos taxonómicos
        - ✅ Valida coordenadas dentro de Chile
        - ✅ Calcula índices ecológicos
        - ✅ Genera reportes de auditoría

    #### 📊 Visualizaciones disponibles:
    - **Abundancia**: Especies más representadas
    - **Dominancia**: Distribución con Treemap
    - **Riqueza**: Número de especies (Lollipop)
    - **Curva de acumulación**: Rarefacción de especies
    - **Datos**: Tabla completa con correcciones
    """)

# Cargar archivo
if archivo_cargado:
    try:
        with st.spinner("📂 Leyendo archivo..."):
            df_raw, error = gestor_excel.leer_darwin_core(archivo_cargado)
            
            if error:
                st.error(f"❌ {error}")
            else:
                st.session_state.datos_originales = df_raw
                st.success(f"✅ Cargado: {df_raw.shape[0]} filas × {df_raw.shape[1]} columnas")
                
                # Procesar
                st.session_state.datos_corregidos = procesar_archivo(df_raw)
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.error(traceback.format_exc())

# Mostrar métricas
if st.session_state.datos_corregidos is not None:
    corr = st.session_state.datos_corregidos[~st.session_state.datos_corregidos['es_encabezado']]
    
    # Crear dataframe para cálculos
    df_biodiv = pd.DataFrame({
        'especie': corr['genero_corr'] + ' ' + corr['epiteto_corr'],
        'valor': corr['valor_orig'].apply(lambda x: pd.to_numeric(x, errors='coerce')).fillna(1)
    })
    
    indices = calc_ecologico.resumen_completo(df_biodiv)
    
    # Mostrar métricas en columnas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🦗 Total Individuos", fmt_entero(indices['total_individuos']))
    with col2:
        st.metric("🌿 Riqueza", fmt_entero(indices['riqueza']))
    with col3:
        st.metric("📊 Shannon (H)", fmt_decimal(indices['shannon'], 2))
    
    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric("🎲 Simpson (D)", fmt_decimal(indices['simpson'], 4))
    with col5:
        st.metric("⚖️ Pielou (J)", fmt_decimal(indices['pielou'], 2))
    with col6:
        st.metric("🌳 Margalef", fmt_decimal(indices['margalef'], 2))
    
    col7, col8, col9 = st.columns(3)
    with col7:
        st.metric("🔮 Chao1", fmt_decimal(indices['chao1'], 0))
    with col8:
        color_rep = "normal" if indices['representatividad'] >= 80 else "off"
        st.metric("✓ Representatividad", 
                 f"{fmt_decimal(indices['representatividad'], 1)}%",
                 delta_color=color_rep)
    with col9:
        if len(df_biodiv) > 0:
            especie_dominante = df_biodiv.groupby('especie')['valor'].sum().idxmax()
            st.metric("🦊 Especie Dominante", especie_dominante.split()[-1])
        else:
            st.metric("🦊 Especie Dominante", "Sin datos")
    
    st.divider()
    
    # Mostrar correcciones aplicadas
    correcciones_aplicadas = st.session_state.datos_corregidos[
        st.session_state.datos_corregidos['fuente'].str.contains('SIMBIO|GBIF', na=False)
    ]
    
    if len(correcciones_aplicadas) > 0:
        st.markdown(f"### ✅ Correcciones Aplicadas ({len(correcciones_aplicadas)} registros)")
        st.info(f"Se aplicaron correcciones taxonómicas a **{len(correcciones_aplicadas)}** registros")
        
        # Mostrar tabla resumen de correcciones
        resumen_correcciones = correcciones_aplicadas[['genero_orig', 'epiteto_orig', 'genero_corr', 'epiteto_corr', 'fuente']].head(10)
        st.dataframe(resumen_correcciones, use_container_width=True)
    
    st.divider()
    
    # Selector de correcciones taxonómicas si hay ambigüedades
    if st.session_state.opciones_taxonomia:
        st.markdown("### 🔧 Correcciones Taxonómicas que Requieren Revisión Manual")
        st.warning(f"Se encontraron {len(st.session_state.opciones_taxonomia)} registros con múltiples opciones de corrección.")
        
        with st.form("form_taxonomia"):
            for idx, opts in st.session_state.opciones_taxonomia.items():
                genero_orig = st.session_state.datos_corregidos.at[idx, 'genero_orig']
                epiteto_orig = st.session_state.datos_corregidos.at[idx, 'epiteto_orig']
                
                opciones = gestor_taxonomia.obtener_opciones_taxonomia(genero_orig, epiteto_orig)
                nombres_opciones = [o['nombre'] for o in opciones]
                
                selected = st.selectbox(
                    f"Fila {idx+1}: {genero_orig} {epiteto_orig}",
                    nombres_opciones,
                    key=f"taxonomia_{idx}"
                )
                
                # Guardar selección
                idx_seleccionado = nombres_opciones.index(selected)
                st.session_state.selecciones_manuales[idx] = opciones[idx_seleccionado]['datos']
            
            if st.form_submit_button("✅ Aplicar Correcciones Manuales"):
                # Aplicar correcciones seleccionadas
                for idx, datos in st.session_state.selecciones_manuales.items():
                    for col in ['reino', 'filo', 'clase', 'orden', 'familia', 'genero', 'epiteto']:
                        st.session_state.datos_corregidos.at[idx, f'{col}_corr'] = datos.get(col, '')
                st.success("✅ Correcciones manuales aplicadas")
                st.rerun()
    
    st.divider()
    
    # Tabs de análisis
    tab_abundancia, tab_dominancia, tab_riqueza, tab_curva, tab_tabla = st.tabs(
        ["📊 Abundancia", "🌰 Dominancia", "📈 Riqueza", "📉 Curva", "📋 Datos"]
    )
    
    with tab_abundancia:
        st.markdown("### Top 20 Especies Más Abundantes")
        resumen = df_biodiv.groupby('especie')['valor'].sum().reset_index()
        fig = gen_graficos.abundancia_top_especies(resumen, col_especie='especie', col_valor='valor')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab_dominancia:
        st.markdown("### Treemap: Distribución de Abundancia")
        resumen = df_biodiv.groupby('especie')['valor'].sum().reset_index()
        fig = gen_graficos.dominancia_treemap(resumen, col_especie='especie', col_valor='valor')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab_riqueza:
        st.markdown("### Riqueza de Especies (Lollipop)")
        fig = gen_graficos.riqueza_lollipop(df_biodiv, col_especie='especie')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab_curva:
        st.markdown("### Curva de Acumulación de Especies")
        abundancias = calc_ecologico.crear_matriz_abundancia(df_biodiv)
        rarefac = calc_ecologico.rarefaccion(abundancias, permutaciones=50)
        fig = gen_graficos.curva_acumulacion(
            abundancias,
            rarefac['muestras'],
            rarefac['riqueza'],
            rarefac['sd'],
            indices['chao1']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab_tabla:
        st.markdown("### Planilla Corregida")
        st.dataframe(st.session_state.datos_corregidos, use_container_width=True, height=600)
    
    # Botón descarga
    st.download_button(
        label="⬇️ DESCARGAR EXCEL",
        data=generar_excel_descarga(),
        file_name=f"DarwinCheck_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

else:
    st.info("👈 Carga un archivo Excel en el panel lateral para comenzar")
