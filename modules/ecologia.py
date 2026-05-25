# ============================================================================ #
#                 DarwinCheck - Cálculos Ecológicos                            #
# ============================================================================ #

import pandas as pd
import numpy as np
from scipy.special import comb

class CalculadoraEcologica:
    """Calcula índices ecológicos de biodiversidad."""
    
    @staticmethod
    def abundancia_relativa(abundancia_especies):
        """Calcula abundancia relativa (proporciones)."""
        total = np.sum(abundancia_especies)
        if total == 0:
            return np.zeros_like(abundancia_especies, dtype=float)
        return abundancia_especies / total
    
    @staticmethod
    def shannon(abundancia_especies):
        """Calcula índice de Shannon (H)."""
        pi = CalculadoraEcologica.abundancia_relativa(abundancia_especies)
        pi = pi[pi > 0]  # Solo valores positivos
        H = -np.sum(pi * np.log(pi))
        return H
    
    @staticmethod
    def simpson(abundancia_especies):
        """Calcula índice de Simpson (D)."""
        pi = CalculadoraEcologica.abundancia_relativa(abundancia_especies)
        D = np.sum(pi ** 2)
        return D
    
    @staticmethod
    def pielou(abundancia_especies):
        """Calcula índice de equitabilidad de Pielou (J)."""
        S = np.sum(abundancia_especies > 0)  # Riqueza
        if S <= 1:
            return 0
        
        H = CalculadoraEcologica.shannon(abundancia_especies)
        J = H / np.log(S)
        return J
    
    @staticmethod
    def margalef(abundancia_especies):
        """Calcula índice de Margalef."""
        S = np.sum(abundancia_especies > 0)  # Riqueza
        N = np.sum(abundancia_especies)  # Abundancia total
        
        if N <= 1:
            return 0
        
        Mg = (S - 1) / np.log(N)
        return Mg
    
    @staticmethod
    def chao1(abundancia_especies):
        """Estima riqueza usando Chao1."""
        abundancia_no_cero = abundancia_especies[abundancia_especies > 0]
        S = len(abundancia_no_cero)
        
        # Contar singletons (f1) y doubletons (f2)
        f1 = np.sum(abundancia_no_cero == 1)
        f2 = np.sum(abundancia_no_cero == 2)
        
        if f2 > 0:
            chao = S + (f1**2) / (2 * f2)
        else:
            chao = S + (f1 * (f1 - 1)) / 2
        
        return chao
    
    @staticmethod
    def calcular_rarefaccion(abundancia_especies, tamano_muestra=None):
        """Calcula curva de rarefacción."""
        N = np.sum(abundancia_especies)
        abundancia_no_cero = abundancia_especies[abundancia_especies > 0]
        
        if tamano_muestra is None:
            # Usar tamaños de 1 a N
            tamanos = np.arange(1, N + 1)
        else:
            tamanos = np.array(tamanos)
        
        rarefaccion = []
        
        for n in tamanos:
            if n > N:
                continue
            
            riqueza_esperada = 0
            for abundancia in abundancia_no_cero:
                if abundancia >= n:
                    # Probabilidad de que la especie esté en la muestra
                    try:
                        prob = 1 - (comb(N - abundancia, n) / comb(N, n))
                        riqueza_esperada += prob
                    except:
                        riqueza_esperada += 1
            
            rarefaccion.append(riqueza_esperada)
        
        return tamanos, np.array(rarefaccion)
    
    @staticmethod
    def calcular_todos_indices(abundancia_especies):
        """Calcula todos los índices ecológicos."""
        return {
            'riqueza': np.sum(abundancia_especies > 0),
            'abundancia_total': np.sum(abundancia_especies),
            'shannon': CalculadoraEcologica.shannon(abundancia_especies),
            'simpson': CalculadoraEcologica.simpson(abundancia_especies),
            'pielou': CalculadoraEcologica.pielou(abundancia_especies),
            'margalef': CalculadoraEcologica.margalef(abundancia_especies),
            'chao1': CalculadoraEcologica.chao1(abundancia_especies),
        }


# Instancia global
calc_ecologico = CalculadoraEcologica()
