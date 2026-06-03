# ============================================================================ #
#              DarwinCheck - Generador de Gráficos con Plotly                   #
# ============================================================================ #

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

class GeneradorGraficos:
    """Genera gráficos interactivos con Plotly para visualizaciones."""
    
    def __init__(self, color_defecto="#27ae60"):
        self.color = color_defecto
    
    def actualizar_color(self, color):
        """Actualiza color de gráficos."""
        self.color = color
    
    def abundancia_top_especies(self, df, col_especie='especie', col_valor='valor', top=20):
        """Crea gráfico de barras horizontal de top especies abundantes."""
        try:
            df_top = df.nlargest(top, col_valor)
            
            fig = go.Figure(data=[
                go.Bar(
                    y=df_top[col_especie],
                    x=df_top[col_valor],
                    orientation='h',
                    marker=dict(color=self.color, opacity=0.8),
                    text=df_top[col_valor],
                    textposition='auto'
                )
            ])
            
            fig.update_layout(
                title="Top 20 Especies Más Abundantes",
                xaxis_title="Número de Individuos",
                yaxis_title="Especie",
                height=600,
                showlegend=False,
                hovermode='closest',
                margin=dict(l=200)
            )
            
            return fig
        except Exception as e:
            print(f"Error en abundancia_top_especies: {e}")
            return go.Figure()
    
    def dominancia_treemap(self, df, col_especie='especie', col_valor='valor'):
        """Crea treemap de distribución de abundancia."""
        try:
            # Limpiar datos
            df_clean = df.copy()
            df_clean = df_clean[df_clean[col_valor] > 0]
            
            # Calcular porcentajes
            total = df_clean[col_valor].sum()
            df_clean['porcentaje'] = (df_clean[col_valor] / total * 100).round(1)
            
            # Crear etiquetas con porcentajes
            df_clean['etiqueta'] = df_clean.apply(
                lambda row: f"{row[col_especie]}<br>{row[col_valor]} individuos<br>({row['porcentaje']}%)",
                axis=1
            )
            
            fig = go.Figure(go.Treemap(
                labels=df_clean['etiqueta'],
                parents=[''] * len(df_clean),
                values=df_clean[col_valor],
                marker=dict(
                    colors=df_clean[col_valor],
                    colorscale='Viridis',
                    cmid=df_clean[col_valor].median(),
                    colorbar=dict(title="Abundancia")
                ),
                textposition='middle center',
                hovertemplate='<b>%{label}</b><extra></extra>'
            ))
            
            fig.update_layout(
                title="Treemap: Distribución de Abundancia por Especie",
                height=600,
                margin=dict(t=50, l=0, r=0, b=0)
            )
            
            return fig
        except Exception as e:
            print(f"Error en dominancia_treemap: {e}")
            return go.Figure()
    
    def riqueza_lollipop(self, df, col_especie='especie', top=20):
        """Crea gráfico lollipop de riqueza de especies."""
        try:
            # Contar ocurrencias de cada especie
            riqueza = df[col_especie].value_counts().head(top).reset_index()
            riqueza.columns = [col_especie, 'count']
            riqueza = riqueza.sort_values('count', ascending=True)
            
            fig = go.Figure()
            
            # Líneas (stems)
            fig.add_trace(go.Scatter(
                x=riqueza['count'],
                y=riqueza[col_especie],
                mode='lines',
                line=dict(color=self.color, width=2),
                hoverinfo='skip',
                showlegend=False
            ))
            
            # Puntos (heads)
            fig.add_trace(go.Scatter(
                x=riqueza['count'],
                y=riqueza[col_especie],
                mode='markers',
                marker=dict(size=10, color=self.color),
                text=riqueza['count'],
                textposition='middle right',
                hovertemplate='<b>%{y}</b><br>Frecuencia: %{x}<extra></extra>'
            ))
            
            fig.update_layout(
                title="Riqueza de Especies (Top 20 - Lollipop)",
                xaxis_title="Frecuencia",
                yaxis_title="Especie",
                height=600,
                showlegend=False,
                hovermode='closest',
                margin=dict(l=200)
            )
            
            return fig
        except Exception as e:
            print(f"Error en riqueza_lollipop: {e}")
            return go.Figure()
    
    def curva_acumulacion(self, abundancias, muestras, riqueza, sd, chao1):
        """Crea gráfico de curva de acumulación de especies."""
        try:
            # Convertir a array si es necesario
            muestras = np.array(muestras)
            riqueza = np.array(riqueza)
            sd = np.array(sd)
            
            fig = go.Figure()
            
            # Línea de rarefacción
            fig.add_trace(go.Scatter(
                x=muestras,
                y=riqueza,
                mode='lines+markers',
                name='Rarefacción',
                line=dict(color=self.color, width=2),
                marker=dict(size=5)
            ))
            
            # Banda de confianza (±SD)
            upper_bound = riqueza + sd
            lower_bound = riqueza - sd
            
            fig.add_trace(go.Scatter(
                x=np.concatenate([muestras, muestras[::-1]]),
                y=np.concatenate([upper_bound, lower_bound[::-1]]),
                fill='toself',
                fillcolor='rgba(39, 174, 96, 0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                showlegend=True,
                name='±SD'
            ))
            
            # Línea Chao1
            fig.add_hline(y=chao1, line_dash="dash", line_color="red", 
                         annotation_text=f"Chao1: {chao1:.0f}", annotation_position="right")
            
            fig.update_layout(
                title="Curva de Acumulación de Especies",
                xaxis_title="Número de Muestras",
                yaxis_title="Riqueza Esperada",
                height=500,
                hovermode='closest'
            )
            
            return fig
        except Exception as e:
            print(f"Error en curva_acumulacion: {e}")
            return go.Figure()
    
    def conservacion_barras(self, df, col_categoria='estado_conservacion', col_count='count'):
        """Crea gráfico de barras de estados de conservación."""
        try:
            fig = go.Figure(data=[
                go.Bar(
                    x=df[col_categoria],
                    y=df[col_count],
                    marker=dict(color=self.color, opacity=0.8),
                    text=df[col_count],
                    textposition='auto'
                )
            ])
            
            fig.update_layout(
                title="Estados de Conservación",
                xaxis_title="Estado",
                yaxis_title="Número de Especies",
                height=500,
                showlegend=False,
                hovermode='closest'
            )
            
            return fig
        except Exception as e:
            print(f"Error en conservacion_barras: {e}")
            return go.Figure()


# Instancia global
gen_graficos = GeneradorGraficos()
