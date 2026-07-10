"""
utils.py: Funções auxiliares para Zero Field Primordial

Contém:
- Constantes físicas
- Funções de conversão
- Utilitários de I/O
- Funções de visualização
"""

import numpy as np
import pandas as pd
from scipy.integrate import quad
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import os


# ============================================================================
# CONSTANTES FÍSICAS
# ============================================================================

# Velocidade da luz
c_light = 2.99792458e8  # m/s
c_kms = 299792.458     # km/s

# Constantes cosmológicas
H0_Planck = 67.4       # km/s/Mpc (Planck 2018)
h_Planck = 0.674       # H0 / 100
rd_Planck = 147.090    # r_d (horizonte sonoro) em Mpc

# Constantes fundamentais
M_Pl = 1.221e19        # Massa de Planck em GeV
M_sun = 1.989e30       # Massa solar em kg

# Constantes cosmológicas padrão (ΛCDM, Planck 2018)
Omega_m_Planck = 0.315
Omega_b_Planck = 0.049
Omega_dm_Planck = Omega_m_Planck - Omega_b_Planck
Omega_Lambda_Planck = 0.685
Omega_r_Planck = 9.5e-5


# ============================================================================
# FUNÇÕES DE CONVERSÃO
# ============================================================================

def redshift_to_scale_factor(z):
    """Converte redshift z para fator de escala a"""
    return 1.0 / (1.0 + z)


def scale_factor_to_redshift(a):
    """Converte fator de escala a para redshift z"""
    return (1.0 / a) - 1.0


def lookback_time(z, H0=H0_Planck, Omega_m=Omega_m_Planck):
    """
    Calcula tempo de lookback (em Gyr) até redshift z
    
    t_lookback = (1/H0) * ∫₀^z dz' / [(1+z') * E(z')]
    
    onde E(z) = √[Ω_m(1+z)³ + Ω_Λ]
    """
    Omega_Lambda = 1.0 - Omega_m
    
    def integrand(zp):
        E = np.sqrt(Omega_m * (1 + zp) ** 3 + Omega_Lambda)
        return 1.0 / ((1 + zp) * E)
    
    integral, _ = quad(integrand, 0, z, limit=100)
    
    # Converter para Gyr
    H0_Gyr = H0 / 1000.0  # Converter km/s/Mpc para (km/s/kpc) * 1000
    t_Gyr = integral * 1000.0 / H0_Planck * (3.086e19)  # Conversão para Gyr
    
    return t_Gyr


def comoving_distance(z, H0=H0_Planck, Omega_m=Omega_m_Planck):
    """
    Calcula distância de comoving (em Mpc)
    
    d_c = (c/H0) * ∫₀^z dz' / E(z')
    """
    Omega_Lambda = 1.0 - Omega_m
    
    def integrand(zp):
        E = np.sqrt(Omega_m * (1 + zp) ** 3 + Omega_Lambda)
        return 1.0 / E
    
    integral, _ = quad(integrand, 0, z, limit=100)
    d_c = (c_kms / H0) * integral
    
    return d_c


def luminosity_distance(z, H0=H0_Planck, Omega_m=Omega_m_Planck):
    """
    Calcula distância de luminosidade (em Mpc)
    
    d_L = (1+z) * d_c(z)
    """
    d_c = comoving_distance(z, H0, Omega_m)
    d_L = (1 + z) * d_c
    
    return d_L


def angular_diameter_distance(z, H0=H0_Planck, Omega_m=Omega_m_Planck):
    """
    Calcula distância de diâmetro angular (em Mpc)
    
    d_A = d_c(z) / (1+z)
    """
    d_c = comoving_distance(z, H0, Omega_m)
    d_A = d_c / (1 + z)
    
    return d_A


# ============================================================================
# FUNÇÕES DE ESTATÍSTICA
# ============================================================================

def chi2_reduced(chi2, dof, n_params=0):
    """Calcula χ² reduzido"""
    if dof <= n_params:
        return np.inf
    return chi2 / (dof - n_params)


def aic(chi2, n_params, n_data):
    """Critério de Informação de Akaike"""
    return chi2 + 2 * n_params


def bic(chi2, n_params, n_data):
    """Critério de Informação Bayesiano"""
    return chi2 + n_params * np.log(n_data)


def credible_interval(samples, credibility=0.68):
    """
    Calcula intervalo de credibilidade de amostras MCMC
    
    Args:
        samples: array 1D de amostras
        credibility: 0.68 (1σ), 0.95 (2σ), etc.
    
    Returns:
        (mean, lower, upper)
    """
    lower_percentile = (1 - credibility) / 2 * 100
    upper_percentile = (1 + credibility) / 2 * 100
    
    mean = np.mean(samples)
    lower = np.percentile(samples, lower_percentile)
    upper = np.percentile(samples, upper_percentile)
    
    return mean, lower, upper


# ============================================================================
# FUNÇÕES DE I/O
# ============================================================================

def load_csv(filename):
    """Carrega arquivo CSV de forma robusta"""
    try:
        df = pd.read_csv(filename)
        return df
    except FileNotFoundError:
        print(f"ERRO: Arquivo não encontrado: {filename}")
        return None
    except Exception as e:
        print(f"ERRO ao carregar {filename}: {e}")
        return None


def save_csv(df, filename):
    """Salva DataFrame em CSV"""
    try:
        df.to_csv(filename, index=False)
        print(f"✓ Arquivo salvo: {filename}")
        return True
    except Exception as e:
        print(f"ERRO ao salvar {filename}: {e}")
        return False


def save_numpy(data, filename):
    """Salva dados em formato NPY"""
    try:
        np.save(filename, data)
        print(f"✓ Arquivo salvo: {filename}")
        return True
    except Exception as e:
        print(f"ERRO ao salvar {filename}: {e}")
        return False


def load_numpy(filename):
    """Carrega dados em formato NPY"""
    try:
        data = np.load(filename)
        return data
    except FileNotFoundError:
        print(f"ERRO: Arquivo não encontrado: {filename}")
        return None
    except Exception as e:
        print(f"ERRO ao carregar {filename}: {e}")
        return None


# ============================================================================
# FUNÇÕES DE VALIDAÇÃO
# ============================================================================

def validate_parameters(params, bounds):
    """
    Valida se parâmetros estão dentro dos bounds
    
    Args:
        params: array de parâmetros
        bounds: list de (min, max) para cada parâmetro
    
    Returns:
        bool: True se válido
    """
    for p, (pmin, pmax) in zip(params, bounds):
        if p < pmin or p > pmax:
            return False
    return True


def check_nan_inf(data, name="data"):
    """Verifica presença de NaN ou Inf"""
    n_nan = np.sum(np.isnan(data))
    n_inf = np.sum(np.isinf(data))
    
    if n_nan > 0:
        print(f"⚠️ {name}: {n_nan} valores NaN encontrados")
    if n_inf > 0:
        print(f"⚠️ {name}: {n_inf} valores Inf encontrados")
    
    return n_nan == 0 and n_inf == 0


# ============================================================================
# FUNÇÕES DE VISUALIZAÇÃO
# ============================================================================

def plot_comparison_bars(names, values, errors=None, title="", xlabel="", ylabel=""):
    """
    Cria gráfico de barras comparativo
    
    Args:
        names: lista de nomes dos modelos
        values: lista de valores
        errors: lista de erros (opcional)
        title, xlabel, ylabel: labels
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x = np.arange(len(names))
    if errors is not None:
        ax.bar(x, values, yerr=errors, capsize=5, alpha=0.7)
    else:
        ax.bar(x, values, alpha=0.7)
    
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    return fig, ax


def plot_evolution(z, y, label="", title="", xlabel="z", ylabel=""):
    """
    Cria gráfico de evolução vs redshift
    
    Args:
        z: array de redshifts
        y: array de valores
        label, title, xlabel, ylabel: labels
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(z, y, 'b-', linewidth=2, label=label)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    if label:
        ax.legend()
    
    plt.tight_layout()
    return fig, ax


def plot_posterior(samples, param_name="", bins=50):
    """
    Cria histograma de posterior 1D
    
    Args:
        samples: array 1D de amostras
        param_name: nome do parâmetro
        bins: número de bins
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.hist(samples, bins=bins, alpha=0.7, edgecolor='black')
    ax.set_xlabel(param_name, fontsize=12)
    ax.set_ylabel('Frequência', fontsize=12)
    ax.set_title(f'Posterior: {param_name}', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Adicionar estatísticas
    mean, lower, upper = credible_interval(samples)
    ax.axvline(mean, color='r', linestyle='--', linewidth=2, label=f'Média: {mean:.3e}')
    ax.axvline(lower, color='g', linestyle=':', linewidth=1, alpha=0.7)
    ax.axvline(upper, color='g', linestyle=':', linewidth=1, alpha=0.7, label='68% CI')
    ax.legend()
    
    plt.tight_layout()
    return fig, ax


# ============================================================================
# FUNÇÕES DE FORMATAÇÃO
# ============================================================================

def format_scientific(value, decimals=2):
    """Formata número em notação científica"""
    if value == 0:
        return "0"
    return f"{value:.{decimals}e}"


def format_with_error(value, error, decimals=2):
    """Formata valor com erro"""
    return f"{value:.{decimals}f} ± {error:.{decimals}f}"


def print_section(title, level=1):
    """Imprime seção formatada"""
    if level == 1:
        print("\n" + "=" * 80)
        print(title)
        print("=" * 80)
    elif level == 2:
        print("\n" + "-" * 80)
        print(title)
        print("-" * 80)
    else:
        print(f"\n>>> {title}")


def print_key_value(key, value, decimals=3):
    """Imprime par chave-valor formatado"""
    if isinstance(value, (int, np.integer)):
        print(f"  {key}: {value}")
    elif isinstance(value, (float, np.floating)):
        if abs(value) < 1e-3 or abs(value) > 1e3:
            print(f"  {key}: {value:.{decimals}e}")
        else:
            print(f"  {key}: {value:.{decimals}f}")
    else:
        print(f"  {key}: {value}")


# ============================================================================
# MAIN (testes)
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("Testes de Funções Auxiliares")
    print("=" * 80)
    
    # Teste: conversões
    print("\n[1] Conversões")
    z_test = 0.5
    a = redshift_to_scale_factor(z_test)
    z_back = scale_factor_to_redshift(a)
    print(f"  z={z_test} → a={a:.4f} → z={z_back:.4f}")
    
    # Teste: distâncias
    print("\n[2] Distâncias")
    d_c = comoving_distance(0.5)
    d_L = luminosity_distance(0.5)
    d_A = angular_diameter_distance(0.5)
    print(f"  Comoving distance (z=0.5): {d_c:.1f} Mpc")
    print(f"  Luminosity distance (z=0.5): {d_L:.1f} Mpc")
    print(f"  Angular diameter distance (z=0.5): {d_A:.1f} Mpc")
    
    # Teste: estatística
    print("\n[3] Estatística")
    samples = np.random.normal(100, 10, 10000)
    mean, lower, upper = credible_interval(samples, 0.68)
    print(f"  Mean: {mean:.2f}")
    print(f"  68% CI: [{lower:.2f}, {upper:.2f}]")
    
    print("\n✓ Testes concluídos")
