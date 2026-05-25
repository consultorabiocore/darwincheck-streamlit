# ============================================================================ #
#              DarwinCheck - Generador de Gráficos                             #
# ============================================================================ #

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

class GeneradorGraficos:
    """Genera gráficos para visualizaciones."""
    
    def __init__(self, color_defecto="#27ae60"):
        self.color = color_defecto
        sns.set_style("whitegrid")
    
    def actualizar_color(self, color):
        """Actualiza color de gráficos."""
        self.color = color
    
    def grafico_barras_abundancia(self, df_abundancia, titulo="Abundancia por Especie"):
        """Crea gráfico de barras de abundancia."""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        df_ordenado = df_abundancia.sort_values(ascending=False).head(20)
        
        ax.barh(range(len(df_ordenado)), df_ordenado.values, color=self.color, alpha=0.8)
        ax.set_yticks(range(len(df_ordenado)))
        ax.set_yticklabels(df_ordenado.index, fontsize=10)
        ax.set_xlabel("Número de Individuos", fontsize=11)
        ax.set_title(titulo, fontsize=13, fontweight='bold')
        
        # Agregar valores
        for i, v in enumerate(df_ordenado.values):
            ax.text(v, i, f' {int(v)}', va='center', fontsize=9)
        
        plt.tight_layout()
        return fig
    
    def grafico_pastel_composicion(self, df_composicion, titulo="Composición de Especies"):
        """Crea gráfico de pastel."""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Top 10, resto agrupado
        df_top = df_composicion.head(10)
        if len(df_composicion) > 10:
            resto = pd.Series({
                'Otros': df_composicion[10:].sum()
            })
            df_top = pd.concat([df_top, resto])
        
        colores = plt.cm.Set3(np.linspace(0, 1, len(df_top)))
        
        wedges, texts, autotexts = ax.pie(
            df_top.values,
            labels=df_top.index,
            autopct='%1.1f%%',
            colors=colores,
            startangle=90
        )
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
        
        ax.set_title(titulo, fontsize=13, fontweight='bold', pad=20)
        plt.tight_layout()
        return fig
    
    def grafico_dominancia(self, df_abundancia, titulo="Curva de Dominancia"):
        """Crea gráfico de dominancia acumulada."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        df_ordenado = df_abundancia.sort_values(ascending=False)
        abundancia_acumulada = np.cumsum(df_ordenado.values) / df_ordenado.sum() * 100
        
        ax.plot(
            range(1, len(abundancia_acumulada) + 1),
            abundancia_acumulada,
            'o-',
            color=self.color,
            linewidth=2,
            markersize=4
        )
        
        ax.set_xlabel("Número de Especies (ordenadas por abundancia)", fontsize=11)
        ax.set_ylabel("Abundancia Acumulada (%)", fontsize=11)
        ax.set_title(titulo, fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0, 105])
        
        plt.tight_layout()
        return fig
    
    def grafico_diversidad_shannon(self, valores_shannon):
        """Crea gráfico de índice Shannon."""
        fig, ax = plt.subplots(figsize=(8, 6))
        
        if isinstance(valores_shannon, (list, np.ndarray)):
            ax.bar(range(len(valores_shannon)), valores_shannon, color=self.color, alpha=0.8)
            ax.set_xlabel("Muestreo", fontsize=11)
        else:
            ax.bar(['Shannon'], [valores_shannon], color=self.color, alpha=0.8)
        
        ax.set_ylabel("Índice de Shannon (H)", fontsize=11)
        ax.set_title("Diversidad - Índice de Shannon", fontsize=13, fontweight='bold')
        ax.set_ylim(0, max(8, (valores_shannon if isinstance(valores_shannon, (int, float)) else max(valores_shannon)) + 1))
        
        plt.tight_layout()
        return fig
    
    def fig_a_bytes(self, fig):
        """Convierte figura matplotlib a bytes PNG."""
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        return buf.getvalue()


# Instancia global
gen_graficos = GeneradorGraficos()
