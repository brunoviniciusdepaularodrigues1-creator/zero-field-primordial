"""
run_zero_field.py: Integração numérica de Klein-Gordon + Friedmann para Zero Field Primordial

Equações:
  φ̈ + 3H φ̇ + m²φ = 0  (Klein-Gordon)
  H² = (8πG/3)(ρ_m + ρ_r + ρ_φ)  (Friedmann)

Onde:
  ρ_φ = (1/2)φ̇² + (1/2)m²φ²
  p_φ = (1/2)φ̇² - (1/2)m²φ²
"""

import numpy as np
from scipy.integrate import odeint
import pandas as pd


# ============================================================================
# CONSTANTES FÍSICAS
# ============================================================================

# Constantes fundamentais (unidades naturais, c=1)
c_kms = 299792.458  # velocidade da luz em km/s
H0_fiducial = 67.4  # H0 em km/s/Mpc (Planck 2018)
rd_fiducial = 147.0  # horizonte sonoro em Mpc (Planck 2018)

# Parâmetros cosmológicos padrão (ΛCDM)
Omega_m0 = 0.315  # densidade relativa de matéria hoje
Omega_r0 = 9.5e-5  # densidade relativa de radiação hoje
Omega_k = 0.0  # plano

# Massa do campo escalar (GeV)
# Nota: será explorada parametricamente; valor típico ~10^-42 GeV
M_Pl = 1.221e19  # Massa de Planck em GeV


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def get_cosmological_params(H0=H0_fiducial, Omega_m=Omega_m0):
    """
    Retorna parâmetros cosmológicos derivados.
    
    Args:
        H0: parâmetro de Hubble hoje em km/s/Mpc
        Omega_m: densidade relativa de matéria (incluindo DM)
    
    Returns:
        dict com parâmetros derivados
    """
    Omega_Lambda = 1.0 - Omega_m - Omega_r0 - Omega_k
    
    return {
        'H0': H0,
        'Omega_m': Omega_m,
        'Omega_r': Omega_r0,
        'Omega_Lambda': Omega_Lambda,
        'Omega_k': Omega_k,
    }


def rho_matter(z, Omega_m0, H0):
    """Densidade de matéria em função de z"""
    return Omega_m0 * (H0 ** 2) * (1 + z) ** 3


def rho_radiation(z, Omega_r0, H0):
    """Densidade de radiação em função de z"""
    return Omega_r0 * (H0 ** 2) * (1 + z) ** 4


def rho_scalar_field(phi, phi_dot, m):
    """
    Densidade de energia do campo escalar.
    
    ρ_φ = (1/2)φ̇² + (1/2)m²φ²
    """
    kinetic = 0.5 * phi_dot ** 2
    potential = 0.5 * m ** 2 * phi ** 2
    return kinetic + potential


def pressure_scalar_field(phi, phi_dot, m):
    """
    Pressão do campo escalar.
    
    p_φ = (1/2)φ̇² - (1/2)m²φ²
    """
    kinetic = 0.5 * phi_dot ** 2
    potential = 0.5 * m ** 2 * phi ** 2
    return kinetic - potential


def equation_of_state(phi, phi_dot, m):
    """
    Equação de estado do campo escalar.
    
    w_φ = p_φ / ρ_φ
    """
    rho = rho_scalar_field(phi, phi_dot, m)
    if np.abs(rho) < 1e-30:
        return 0.0
    p = pressure_scalar_field(phi, phi_dot, m)
    return p / rho


# ============================================================================
# SOLVER ODE: KLEIN-GORDON + FRIEDMANN
# ============================================================================

def hubble_friedmann(y, z, m, H0, Omega_m0, Omega_r0):
    """
    Sistema de EDOs em tempo conforme (em função de z).
    
    Estado: y = [φ, φ', H]
    onde φ' = dφ/dz (não dφ/dt)
    
    Friedmann: H(z) é determinado algebricamente por
      H² = (8πG/3)(ρ_m + ρ_r + ρ_φ)
    
    Klein-Gordon é derivada de segunda ordem → sistema de 1a ordem.
    
    Args:
        y: [phi, dphi_dz, H]
        z: redshift
        m: massa do campo (GeV)
        H0: Hubble hoje (km/s/Mpc)
        Omega_m0: Omega_m hoje
        Omega_r0: Omega_r hoje
    
    Returns:
        dy/dz
    """
    phi, dphi_dz, H = y
    
    # Densidades (em unidades de H0²)
    rho_m = rho_matter(z, Omega_m0, H0)
    rho_r = rho_radiation(z, Omega_r0, H0)
    
    # Campo escalar: φ̇ em termos de dφ/dz
    # Relação: dφ/dt = (dφ/dz)(dz/dt) = (dφ/dz) * (-H(1+z))
    # Logo: dφ/dz = -φ̇ / (H(1+z))
    # Portanto: φ̇ = -H(1+z) * dφ/dz
    
    if H <= 0:
        raise ValueError(f"H negativo em z={z}: H={H}")
    
    phi_dot = -H * (1 + z) * dphi_dz
    
    # Densidade e pressão do campo escalar
    rho_phi = rho_scalar_field(phi, phi_dot, m)
    
    # Friedmann (algébrica): H² = (8πG/3)(ρ_total)
    # Em unidades onde H0 em km/s/Mpc:
    H_squared = rho_m + rho_r + rho_phi
    H_new = np.sqrt(np.abs(H_squared))  # Proteção contra negativos
    
    # Klein-Gordon em termos de z:
    # φ̈ + 3H φ̇ + m²φ = 0
    # 
    # d/dz(φ̇) = (φ̈) / (dz/dt) = (φ̈) / (-H(1+z))
    # Logo: d/dz(dφ/dz) = -φ̈ / (H(1+z))²
    #
    # φ̈ = -3H φ̇ - m²φ
    # d/dz(dφ/dz) = -(-3H φ̇ - m²φ) / (H(1+z))²
    #             = (3H φ̇ + m²φ) / (H(1+z))²
    
    if (1 + z) == 0:
        raise ValueError("1+z = 0")
    
    d2phi_dz2 = (3 * H_new * phi_dot + m ** 2 * phi) / (H_new * (1 + z) ** 2)
    
    return np.array([dphi_dz, d2phi_dz2, 0.0])


def solve_zero_field(
    z_array,
    m=1e-42,
    phi_i=0.1,
    H0=H0_fiducial,
    Omega_m=Omega_m0,
    Omega_r=Omega_r0,
    z_i=1000,
    verbose=True
):
    """
    Integra Klein-Gordon + Friedmann de z_i até z_f.
    
    Args:
        z_array: array de redshifts para calcular solução
        m: massa do campo (GeV), default 1e-42
        phi_i: valor inicial de φ em z_i (em unidades de M_Pl)
        H0: Hubble hoje (km/s/Mpc)
        Omega_m: Omega_m hoje
        Omega_r: Omega_r hoje
        z_i: redshift inicial para integração
        verbose: imprimir logs
    
    Returns:
        dict com 'z', 'phi', 'phi_dot', 'H', 'rho_phi', 'w_phi'
    """
    
    if verbose:
        print(f"[Zero Field Solver]")
        print(f"  m = {m:.2e} GeV")
        print(f"  φ_i = {phi_i:.3f} M_Pl")
        print(f"  z_i = {z_i}")
        print(f"  H0 = {H0:.1f} km/s/Mpc")
        print(f"  Ω_m = {Omega_m:.4f}")
    
    # Condição inicial em z_i
    # φ̇_i = 0 (estado relaxado)
    # dφ/dz|_z_i = 0 (equivalente)
    params = get_cosmological_params(H0, Omega_m)
    H_i = H0 * np.sqrt(
        params['Omega_m'] * (1 + z_i) ** 3 +
        params['Omega_r'] * (1 + z_i) ** 4 +
        params['Omega_Lambda']
    )
    
    y_i = np.array([phi_i, 0.0, H_i])
    
    # Integrar de z_i descendente até z_f = 0
    z_sort = np.sort(z_array)[::-1]  # Descendente
    
    try:
        # odeint integra do primeiro ao último ponto
        solution = odeint(
            hubble_friedmann,
            y_i,
            z_sort,
            args=(m, H0, Omega_m, Omega_r),
            rtol=1e-8,
            atol=1e-10,
        )
    except Exception as e:
        print(f"ERRO na integração: {e}")
        return None
    
    phi_sol = solution[:, 0]
    dphi_dz_sol = solution[:, 1]
    H_sol = solution[:, 2]
    
    # Recalcular φ̇ em função de z
    phi_dot_sol = -H_sol * (1 + z_sort) * dphi_dz_sol
    
    # Densidades e equação de estado
    rho_phi_sol = np.array([
        rho_scalar_field(phi_sol[i], phi_dot_sol[i], m)
        for i in range(len(z_sort))
    ])
    
    w_phi_sol = np.array([
        equation_of_state(phi_sol[i], phi_dot_sol[i], m)
        for i in range(len(z_sort))
    ])
    
    # Reorganizar em ordem de z crescente (para saída)
    idx = np.argsort(z_sort)
    
    results = {
        'z': z_sort[idx],
        'phi': phi_sol[idx],
        'phi_dot': phi_dot_sol[idx],
        'H': H_sol[idx],
        'rho_phi': rho_phi_sol[idx],
        'w_phi': w_phi_sol[idx],
    }
    
    if verbose:
        print(f"  ✓ Integração concluída")
        print(f"  φ(z=0) = {results['phi'][-1]:.4e} M_Pl")
        print(f"  H(z=0) = {results['H'][-1]:.2f} km/s/Mpc")
        print(f"  w_φ(z=0) = {results['w_phi'][-1]:.3f}")
    
    return results


def compute_DV(H_of_z, z_values, rd_fid=rd_fiducial):
    """
    Calcula D_V / r_d a partir de H(z).
    
    D_V(z) = [(c/H0)² * z * ∫₀^z dz'/H(z')]^(1/3)
    D_V / r_d = D_V(z) / r_d_fiducial
    
    Args:
        H_of_z: função H(z) (ou array de valores)
        z_values: array de redshifts
        rd_fid: horizonte sonoro fiducial em Mpc
    
    Returns:
        array de D_V / r_d
    """
    
    if isinstance(H_of_z, np.ndarray):
        # Interpolar H(z) se for array
        from scipy.interpolate import interp1d
        H_interp = interp1d(z_values, H_of_z, kind='cubic', fill_value='extrapolate')
        H_func = H_interp
    else:
        H_func = H_of_z
    
    DV_over_rd = []
    
    for z in z_values:
        # Integral ∫₀^z dz'/H(z')
        from scipy.integrate import quad
        integral, _ = quad(lambda zp: 1.0 / H_func(zp), 0, z)
        
        # D_V(z) = [(c/H0)² * z * integral]^(1/3)
        # Em unidades onde H0 = 1:
        comoving_distance = (c_kms / H0_fiducial) * integral
        DV = (z * comoving_distance ** 2) ** (1.0 / 3.0)
        
        DV_over_rd.append(DV / rd_fid)
    
    return np.array(DV_over_rd)


# ============================================================================
# MAIN: Teste do solver
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Zero Field Primordial: Teste do Solver ODE")
    print("=" * 70)
    
    # Parâmetros do modelo
    m_phi = 1e-42  # GeV
    phi_initial = 0.1  # M_Pl
    z_initial = 1000
    
    # Redshifts para cálculo
    z_eval = np.array([0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0])
    
    # Resolver
    sol = solve_zero_field(
        z_eval,
        m=m_phi,
        phi_i=phi_initial,
        z_i=z_initial,
        verbose=True
    )
    
    if sol is not None:
        print("\n" + "=" * 70)
        print("Resultados:")
        print("=" * 70)
        
        df_results = pd.DataFrame({
            'z': sol['z'],
            'H(z) [km/s/Mpc]': sol['H'],
            'phi(z) [M_Pl]': sol['phi'],
            'rho_phi(z) [H0²]': sol['rho_phi'],
            'w_phi(z)': sol['w_phi'],
        })
        
        print(df_results.to_string(index=False))
        
        # Salvar
        df_results.to_csv('zero_field_evolution.csv', index=False)
        print("\n✓ Resultados salvos em zero_field_evolution.csv")
