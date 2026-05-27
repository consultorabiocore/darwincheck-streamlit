else '',
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
        st.metric("🦊 Especie Dominante", "Ver gráficos")
    
    st.divider()
    
    # Tabs de análisis
    tab_abundancia, tab_dominancia, tab_riqueza, tab_curva, tab_conservacion, tab_tabla, tab_metodologia = st.tabs(
        ["📊 Abundancia", "🌰 Dominancia", "📈 Riqueza", "📉 Curva", "🛡️ Conservación", "📋 Datos", "📘 Metodología"]
    )
    
    with tab_abundancia:
        st.markdown("### Top 20 Especies Más Abundantes")
        resumen = df_biodiv.groupby('especie')['valor'].sum().reset_index()
        fig = gen_graficos.abundancia_top_especies(resumen, col_especie='especie', col_valor='valor')
        st.plotly_chart(fig, use_container_width=True)
        st.download_button(
            "⬇️ Descargar PNG",
            key="download_abundancia",
            file_name=f"abundancia_{datetime.now().strftime('%Y%m%d')}.png",
            use_container_width=True
        )
    
    with tab_dominancia:
        st.markdown("### Treemap: Distribución de Abundancia")
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
    
    with tab_conservacion:
        st.markdown("### Estados de Conservación")
        if any(corr['estado_conservacion'] != ''):
            conserv = corr[corr['estado_conservacion'] != ''].groupby('estado_conservacion').size().reset_index(name='count')
            fig = gen_graficos.conservacion_barras(conserv, col_categoria='estado_conservacion', col_count='count')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin registros de conservación")
    
    with tab_tabla:
        st.markdown("### Planilla Corregida")
        st.dataframe(st.session_state.datos_corregidos, use_container_width=True, height=600)
    
    with tab_metodologia:
        st.markdown("""
        ## 🔬 Protocolo de Estandarización Darwin Core
        
        ### Funcionalidades
        - ✅ Corrección taxonómica automática (SIMBIO + GBIF)
        - ✅ Validación de coordenadas (Chile)
        - ✅ Índices ecológicos completos
        - ✅ Exportación con auditoría
        
        ### Proceso
        1. **Limpieza** - Normalización de texto
        2. **SIMBIO** - Búsqueda nacional
        3. **GBIF** - Búsqueda global
        4. **Validación** - Coordenadas y conservación
        5. **Auditoría** - Columnas de trazabilidad
        
        © 2026 BioCore - Loreto Campos
        """)

else:
    st.info("👈 Carga un archivo Excel en el panel lateral para comenzar")

