# ============================================================================ #
#          DarwinCheck Vol.1 - Auditoría Taxonómica y Geográfica             #
#                         MÓDULO: GRÁFICOS                                   #
# ============================================================================ #

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Optional

class ChartGenerator:
    """
    Generador de gráficos interactivos con Plotly
    """
    
    @staticmethod
    def grafico_abundancia(resumen: pd.DataFrame, color: str, n_top: int = 20) -> go.Figure:
        """
        Gráfico de barras: Top especies más abundantes
        
        Args:
            resumen: DataFrame con columnas 'nombre', 'Total'
            color: Color hex
            n_top: Número de especies a mostrar
            
        Returns:
            Figura Plotly
        """
        
        top_especies = resumen.head(n_top)
        
        fig = px.bar(
            top_especies,
            x='Total',
            y='nombre',
            orientation='h',
            title=f'Top {n_top} especies más abundantes',
            labels={'Total': 'Individuos', 'nombre': 'Especie'},
            color='Total',
            color_continuous_scale=[[0, 'lightgray'], [1, color]]
        )
        
        fig.update_layout(
            hovermode='closest',
            height=600,
            yaxis={'categoryorder': 'total ascending'},
            font=dict(size=12),
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def grafico_riqueza(df: pd.DataFrame, color: str, n_top: int = 20) -> go.Figure:
        """
        Gráfico de puntos (lollipop): Riqueza de especies
        
        Args:
            df: DataFrame con todas las ocurrencias
            color: Color hex
            n_top: Número de especies a mostrar
            
        Returns:
            Figura Plotly
        """
        
        # Agrupar
        df_copy = df.copy()
        df_copy['especie'] = (
            df_copy['genero_corr'].astype(str) + ' ' + 
            df_copy['epiteto_corr'].astype(str)
        ).str.strip()
        
        riqueza = df_copy.groupby('especie').size().reset_index(name='Registros')
        riqueza = riqueza.sort_values('Registros', ascending=False).head(n_top)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=riqueza['Registros'],
            y=riqueza['especie'],
            mode='markers',
            marker=dict(size=12, color=color),
            name='Registros'
        ))
        
        fig.add_trace(go.Scatter(
            x=riqueza['Registros'],
            y=riqueza['especie'],
            mode='lines',
            line=dict(color=color, width=2),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        fig.update_layout(
            title=f'Riqueza de especies (Top {n_top})',
            xaxis_title='Registros',
            yaxis_title='Especie',
            height=600,
            hovermode='closest',
            font=dict(size=12),
            yaxis={'categoryorder': 'total ascending'}
        )
        
        return fig
    
    @staticmethod
    def grafico_treemap(resumen: pd.DataFrame, color: str, n_top: int = 30) -> go.Figure:
        """
        Treemap: Distribución de abundancia
        
        Args:
            resumen: DataFrame con columnas 'nombre', 'Total'
            color: Color hex
            n_top: Número de especies a mostrar
            
        Returns:
            Figura Plotly
        """
        
        datos = resumen.head(n_top)
        
        fig = px.treemap(
            datos,
            labels='nombre',
            values='Total',
            title=f'Distribución de abundancia ({n_top} especies)',
            color='Total',
            color_continuous_scale=[[0, 'lightgray'], [1, color]],
            hover_data={'Total': ':,.0f', 'nombre': False}
        )
        
        fig.update_traces(
            textposition='middle center',
            textfont=dict(size=12),
            hovertemplate='<b>%{label}</b><br>Individuos: %{value:,.0f}<extra></extra>'
        )
        
        fig.update_layout(height=600, font=dict(size=11))
        
        return fig
    
    @staticmethod
    def grafico_curva_acumulacion(
        muestras: list,
        riqueza: list,
        sd: list,
        chao1: float,
        representatividad: float,
        color: str
    ) -> go.Figure:
        """
        Gráfico: Curva de acumulación de especies
        
        Args:
            muestras: Lista de números de muestras
            riqueza: Lista de riqueza acumulada
            sd: Lista de desviaciones estándar
            chao1: Valor de Chao1
            representatividad: Porcentaje de representatividad
            color: Color hex
            
        Returns:
            Figura Plotly
        """
        
        fig = go.Figure()
        
        # Banda de incertidumbre
        fig.add_trace(go.Scatter(
            x=muestras + muestras[::-1],
            y=[r + s for r, s in zip(riqueza, sd)] + [r - s for r, s in zip(riqueza[::-1], sd[::-1])],
            fill='toself',
            fillcolor=f'rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.2)',
            line=dict(color='rgba(0,0,0,0)'),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Línea principal
        fig.add_trace(go.Scatter(
            x=muestras,
            y=riqueza,
            mode='lines',
            line=dict(color=color, width=3),
            name='Riqueza acumulada',
            hovertemplate='<b>Muestra:</b> %{x}<br><b>Riqueza:</b> %{y:.0f}<extra></extra>'
        ))
        
        # Chao1
        fig.add_hline(
            y=chao1,
            line_dash='dash',
            line_color='red',
            annotation_text=f'Chao1: {chao1:.0f}',
            annotation_position='right',
            opacity=0.5
        )
        
        fig.update_layout(
            title=f'Curva de acumulación de especies (Representatividad: {representatividad:.1f}%)',
            xaxis_title='Número de muestras',
            yaxis_title='Riqueza acumulada',
            height=600,
            hovermode='x unified',
            font=dict(size=12),
            template='plotly_white'
        )
        
        return fig
    
    @staticmethod
    def grafico_conservacion(df: pd.DataFrame, color: str) -> go.Figure:
        """
        Gráfico: Categorías de conservación
        
        Args:
            df: DataFrame filtrado con columna 'alerta_conservacion'
            color: Color hex
            
        Returns:
            Figura Plotly
        """
        
        # Extraer categorías
        df_copy = df.copy()
        df_copy['categoria'] = df_copy['alerta_conservacion'].str.extract(
            r'Conservación: ([^;]+)', expand=False
        )
        df_copy = df_copy[df_copy['categoria'].notna()]
        
        if len(df_copy) == 0:
            fig = go.Figure()
            fig.add_annotation(text="Sin datos de conservación")
            return fig
        
        conteos = df_copy['categoria'].value_counts().reset_index()
        conteos.columns = ['Categoría', 'Registros']
        
        fig = px.bar(
            conteos,
            x='Categoría',
            y='Registros',
            title='Estados de Conservación',
            color='Registros',
            color_continuous_scale=[[0, 'lightgray'], [1, color]],
            labels={'Registros': 'Número de registros'}
        )
        
        fig.update_layout(
            height=500,
            xaxis_tickangle=-45,
            hovermode='closest',
            font=dict(size=12)
        )
        
        return fig
