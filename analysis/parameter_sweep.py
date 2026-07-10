"""
parameter_sweep.py: Exploração sistemática do espaço de parâmetros

Varre os parâmetros do modelo Zero Field Primordial:
- m_phi: massa do campo (GeV)
- phi_i: valor inicial do campo (M_Pl)
- z_i: redshift inicial

Computa χ² BAO para cada combinação e encontra o melhor ajuste.
"""

import sys
import os
import numpy as np
import pandas as pd
from scipy.optimize import minimize, differential_evolution
from scipy.integrate import quad
from scipy.interpolate import interp1d
import warnings

warnings.filterwarnings('ignore')

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from run_zero_field import (
    solve_zero_field,
    H0_fiducial,
    Omega_m0,
    Omega_r0,
    c_kms,
    rd_fiducial,
    H_lcdm,
)


# ============================================================================
# CONSTANTES
# ============================================================================

H0_DEFAULT = 67.4
OMEGA_M_DEFAULT = 0.315


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def load_bao_data():
    """Carrega dados BAO do CSV"""
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'bao_data.csv')
    data = pd.read_csv(data_path)
    return data['z'].values, data['DV_over_rd'].values, data['sigma_DV_over_rd'].values


def compute_chi2_zfp(params, z_obs, DV_obs, sigma_obs):
    """
    Computa χ² para Zero Field com parâmetros dados.
    
    Args:
        params: [m_phi, phi_i, z_i]
        z_obs, DV_obs, sigma_obs: dados BAO
    
    Returns:
        χ² (ou np.inf se houver erro)
    """
    m_phi, phi_i, z_i = params
    
    # Proteções contra parâmetros inválidos
    if m_phi <= 0 or phi_i <= 0 or z_i < 100:
        return np.inf
    
    try:
        # Resolver ODE
        z_max = np.max(z_obs) + 0.1
        z_eval = np.linspace(0, z_max, 150)
        
        sol = solve_zero_field(
            z_eval,
            m=m_phi,
            phi_i=phi_i,
            z_i=z_i,
            verbose=False
        )
        
        if sol is None:
            return np.inf
        
        # Interpolar H(z)
        H_interp = interp1d(sol['z'], sol['H'], kind='cubic', fill_value='extrapolate')
        
        # Calcular D_V/r_d em z_obs
        DV_pred = []
        for z in z_obs:
            try:
                integral, _ = quad(lambda zp: 1.0 / H_interp(zp), 0, z, limit=50)
                comoving_dist = (c_kms / H0_fiducial) * integral
                DV = (z * comoving_dist ** 2) ** (1.0 / 3.0)
                DV_pred.append(DV / rd_fiducial)
            except:
                return np.inf
        
        DV_pred = np.array(DV_pred)
        
        # χ²
        chi2 = np.sum(((DV_obs - DV_pred) / sigma_obs) ** 2)
        
        return chi2 if np.isfinite(chi2) else np.inf
    
    except Exception as e:
        return np.inf


def chi2_lcdm_fixed(z_obs, DV_obs, sigma_obs):
    """Computa χ² para ΛCDM (fixo, sem parâmetros livres)"""
    DV_lcdm = np.array([
        (z * (c_kms / H0_DEFAULT) ** 2 * 
         quad(lambda zp: 1.0 / H_lcdm(zp, H0_DEFAULT, OMEGA_M_DEFAULT), 0, z)[0]) 
        ** (1.0 / 3.0) / rd_fiducial
        for z in z_obs
    ])
    
    chi2 = np.sum(((DV_obs - DV_lcdm) / sigma_obs) ** 2)
    return chi2


# ============================================================================
# OTIMIZAÇÃO
# ============================================================================

def optimize_parameters(z_obs, DV_obs, sigma_obs, method='differential_evolution'):
    """
    Encontra os melhores parâmetros para Zero Field.
    
    Args:
        method: 'differential_evolution' ou 'minimize'
    
    Returns:
        dict com resultado da otimização
    """
    
    print("\n[Parameter Optimization]")
    print(f"Método: {method}")
    
    # Definir bounds (espaço de parâmetros)
    bounds = [
        (1e-44, 1e-40),  # m_phi em GeV
        (0.01, 1.0),     # phi_i em M_Pl
        (100, 2000),     # z_i
    ]
    
    print(f"Bounds:")
    print(f"  m_phi: {bounds[0]}")
    print(f"  phi_i: {bounds[1]}")
    print(f"  z_i: {bounds[2]}")
    
    if method == 'differential_evolution':
        result = differential_evolution(
            lambda p: compute_chi2_zfp(p, z_obs, DV_obs, sigma_obs),
            bounds,
            seed=42,
            maxiter=500,
            popsize=30,
            atol=0.1,
            tol=0.01,
            workers=1,
        )
    else:
        # Usar minimize (menos robusto, mas mais rápido)
        x0 = [1e-42, 0.1, 1000]
        result = minimize(
            lambda p: compute_chi2_zfp(p, z_obs, DV_obs, sigma_obs),
            x0,
            method='Nelder-Mead',
            options={'maxiter': 1000, 'xatol': 1e-6}
        )
    
    return result


def grid_search(z_obs, DV_obs, sigma_obs):
    """
    Varredura em grid para exploração qualitativa.
    """
    
    print("\n[Grid Search]")
    
    m_phi_vals = np.logspace(-44, -40, 10)
    phi_i_vals = np.linspace(0.01, 1.0, 10)
    z_i_vals = np.array([100, 500, 1000, 2000])
    
    results = []
    
    total = len(m_phi_vals) * len(phi_i_vals) * len(z_i_vals)
    count = 0
    
    for m in m_phi_vals:
        for p in phi_i_vals:
            for z in z_i_vals:
                chi2 = compute_chi2_zfp([m, p, z], z_obs, DV_obs, sigma_obs)
                results.append({
                    'm_phi': m,
                    'phi_i': p,
                    'z_i': z,
                    'chi2': chi2,
                })
                count += 1
                if count % 50 == 0:
                    print(f"  {count}/{total} combinações testadas...")
    
    df = pd.DataFrame(results)
    return df.sort_values('chi2').reset_index(drop=True)


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 80)
    print("PASSO 3: EXPLORAÇÃO DE PARÂMETROS")
    print("Zero Field Primordial — Espaço de Parâmetros")
    print("=" * 80)
    
    # Carregar dados
    z_obs, DV_obs, sigma_obs = load_bao_data()
    print(f"\n✓ {len(z_obs)} pontos BAO carregados")
    
    # χ² ΛCDM (referência)
    chi2_lcdm = chi2_lcdm_fixed(z_obs, DV_obs, sigma_obs)
    print(f"\nΛCDM χ² = {chi2_lcdm:.3f}")
    
    # ========================================================================
    # Grid Search (exploração rápida)
    # ========================================================================
    
    print("\n" + "-" * 80)
    print("ETAPA 1: Grid Search")
    print("-" * 80)
    
    df_grid = grid_search(z_obs, DV_obs, sigma_obs)
    
    print(f"\n✓ Grid search completo")
    print(f"\nMelhores 10 combinações:")
    print(df_grid.head(10).to_string(index=False))
    
    # Salvar grid
    grid_path = os.path.join(os.path.dirname(__file__), 'parameter_grid.csv')
    df_grid.to_csv(grid_path, index=False)
    print(f"\n✓ Resultados do grid salvos em: {grid_path}")
    
    # ========================================================================
    # Otimização (refinamento fino)
    # ========================================================================
    
    print("\n" + "-" * 80)
    print("ETAPA 2: Otimização Fina (Differential Evolution)")
    print("-" * 80)
    
    result = optimize_parameters(z_obs, DV_obs, sigma_obs, method='differential_evolution')
    
    m_best, phi_best, z_best = result.x
    chi2_best = result.fun
    
    print(f"\n✓ Otimização concluída")
    print(f"\nMelhores parâmetros encontrados:")
    print(f"  m_phi = {m_best:.4e} GeV")
    print(f"  phi_i = {phi_best:.4f} M_Pl")
    print(f"  z_i = {z_best:.1f}")
    print(f"  χ² = {chi2_best:.3f}")
    print(f"  Δχ² vs ΛCDM = {chi2_best - chi2_lcdm:.3f}")
    
    # ========================================================================
    # Análise de sensibilidade
    # ========================================================================
    
    print("\n" + "-" * 80)
    print("ETAPA 3: Análise de Sensibilidade")
    print("-" * 80)
    
    # Variar m_phi mantendo outros fixos
    m_test = np.logspace(-44, -40, 20)
    chi2_m = [
        compute_chi2_zfp([m, phi_best, z_best], z_obs, DV_obs, sigma_obs)
        for m in m_test
    ]
    
    # Variar phi_i mantendo outros fixos
    phi_test = np.linspace(0.01, 1.0, 20)
    chi2_phi = [
        compute_chi2_zfp([m_best, p, z_best], z_obs, DV_obs, sigma_obs)
        for p in phi_test
    ]
    
    print(f"\nSensibilidade a m_phi:")
    print(f"  Range: [{m_test.min():.2e}, {m_test.max():.2e}]")
    print(f"  χ² min: {np.min(chi2_m):.3f}")
    print(f"  χ² max: {np.max(chi2_m):.3f}")
    
    print(f"\nSensibilidade a phi_i:")
    print(f"  Range: [{phi_test.min():.3f}, {phi_test.max():.3f}]")
    print(f"  χ² min: {np.min(chi2_phi):.3f}")
    print(f"  χ² max: {np.max(chi2_phi):.3f}")
    
    # ========================================================================
    # Salvar resultados finais
    # ========================================================================
    
    print("\n" + "-" * 80)
    print("ETAPA 4: Salvar Resultados")
    print("-" * 80)
    
    summary = {
        'optimization_method': 'differential_evolution',
        'chi2_lcdm': chi2_lcdm,
        'chi2_best_zfp': chi2_best,
        'delta_chi2': chi2_best - chi2_lcdm,
        'm_phi_best': m_best,
        'phi_i_best': phi_best,
        'z_i_best': z_best,
        'n_bao_points': len(z_obs),
    }
    
    summary_df = pd.DataFrame([summary])
    summary_path = os.path.join(os.path.dirname(__file__), 'optimization_summary.csv')
    summary_df.to_csv(summary_path, index=False)
    print(f"\n✓ Resumo salvo em: {summary_path}")
    
    # Salvar sensibilidade
    sensitivity_df = pd.DataFrame({
        'm_phi': m_test,
        'chi2_vs_m': chi2_m,
        'phi_i': phi_test,
        'chi2_vs_phi': [np.nan] * len(m_test),
    })
    sensitivity_df.loc[:len(phi_test)-1, 'chi2_vs_phi'] = chi2_phi
    
    sens_path = os.path.join(os.path.dirname(__file__), 'sensitivity_analysis.csv')
    sensitivity_df.to_csv(sens_path, index=False)
    print(f"✓ Análise de sensibilidade salva em: {sens_path}")
    
    # ========================================================================
    # Conclusão
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("CONCLUSÃO — PASSO 3")
    print("=" * 80)
    
    if chi2_best < chi2_lcdm + 5:
        status = "✅ COMPATÍVEL com BAO"
    else:
        status = "❌ EXCLUÍDO por BAO"
    
    print(f"\nEstado: {status}")
    print(f"Melhores parâmetros: m={m_best:.2e}, φ_i={phi_best:.3f}, z_i={z_best:.0f}")
    print(f"χ² = {chi2_best:.3f} (ΛCDM: {chi2_lcdm:.3f}, Δχ² = {chi2_best - chi2_lcdm:.3f})")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
