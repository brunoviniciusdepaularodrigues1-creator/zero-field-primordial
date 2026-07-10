"""
chi2_bao.py: Comparação χ² BAO entre Zero Field Primordial e ΛCDM

Este script:
1. Carrega dados observacionais BAO reais
2. Calcula D_V/r_d para Zero Field Primordial (via solver ODE)
3. Calcula D_V/r_d para ΛCDM (analítico)
4. Computa χ² para ambos os modelos
5. Compara e gera veredito
"""

import sys
import os
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from scipy.integrate import quad

# Adicionar diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from run_zero_field import (
    solve_zero_field,
    compute_DV,
    H0_fiducial,
    Omega_m0,
    Omega_r0,
    c_kms,
    rd_fiducial,
)


# ============================================================================
# CONSTANTES
# ============================================================================

H0_DEFAULT = 67.4  # km/s/Mpc (Planck 2018)
OMEGA_M_DEFAULT = 0.315


# ============================================================================
# MODELO ΛCDM (ANALÍTICO)
# ============================================================================

def H_lcdm(z, H0=H0_DEFAULT, Omega_m=OMEGA_M_DEFAULT):
    """
    Parâmetro de Hubble para ΛCDM.
    
    H(z) = H0 * √[Ω_m(1+z)³ + (1-Ω_m)]
    
    (assumindo Ω_r ≈ 0 e plano)
    """
    Omega_Lambda = 1.0 - Omega_m
    return H0 * np.sqrt(Omega_m * (1 + z) ** 3 + Omega_Lambda)


def DV_lcdm_analytic(z, H0=H0_DEFAULT, Omega_m=OMEGA_M_DEFAULT, rd_fid=rd_fiducial):
    """
    Calcula D_V / r_d para ΛCDM.
    
    D_V(z) = [(c/H0)² * z * ∫₀^z dz'/H(z')]^(1/3)
    """
    # Integral comoving
    integral, _ = quad(lambda zp: 1.0 / H_lcdm(zp, H0, Omega_m), 0, z)
    
    # Distância de comoving
    comoving_dist = (c_kms / H0) * integral
    
    # D_V
    DV = (z * comoving_dist ** 2) ** (1.0 / 3.0)
    
    return DV / rd_fid


# ============================================================================
# MODELO ZERO FIELD (NUMÉRICO)
# ============================================================================

def DV_zero_field_numeric(z_obs, m_phi=1e-42, phi_i=0.1, z_i=1000):
    """
    Calcula D_V / r_d para Zero Field Primordial via solver ODE.
    
    Args:
        z_obs: array de redshifts observacionais
        m_phi: massa do campo (GeV)
        phi_i: valor inicial de φ (M_Pl)
        z_i: redshift inicial
    
    Returns:
        array de D_V/r_d em z_obs
    """
    print(f"\n[Chi2 BAO] Resolvendo Zero Field...")
    print(f"  m = {m_phi:.2e} GeV")
    print(f"  φ_i = {phi_i:.3f} M_Pl")
    
    # Resolver até z_max (com margem)
    z_max = np.max(z_obs) + 0.1
    z_eval = np.linspace(0, z_max, 200)
    
    sol = solve_zero_field(
        z_eval,
        m=m_phi,
        phi_i=phi_i,
        z_i=z_i,
        verbose=False
    )
    
    if sol is None:
        print("  ✗ ERRO: Solver falhou!")
        return None
    
    # Interpolar H(z)
    H_interp = interp1d(sol['z'], sol['H'], kind='cubic', fill_value='extrapolate')
    
    # Calcular D_V/r_d em z_obs via integração numérica
    DV_results = []
    for z in z_obs:
        integral, _ = quad(lambda zp: 1.0 / H_interp(zp), 0, z, limit=50)
        comoving_dist = (c_kms / H0_fiducial) * integral
        DV = (z * comoving_dist ** 2) ** (1.0 / 3.0)
        DV_results.append(DV / rd_fiducial)
    
    print(f"  ✓ Solução obtida para {len(z_obs)} pontos")
    return np.array(DV_results)


# ============================================================================
# ANÁLISE χ²
# ============================================================================

def compute_chi2(DV_model, DV_obs, sigma_obs):
    """
    Computa χ² = Σ [(D_obs - D_model) / σ]²
    
    Args:
        DV_model: valores preditos pelo modelo
        DV_obs: valores observados
        sigma_obs: erros observacionais
    
    Returns:
        χ², graus de liberdade
    """
    if len(DV_model) != len(DV_obs):
        raise ValueError("Tamanhos diferentes!")
    
    chi2_vals = ((DV_obs - DV_model) / sigma_obs) ** 2
    chi2_total = np.sum(chi2_vals)
    dof = len(DV_obs)
    
    return chi2_total, dof


def reduced_chi2(chi2, dof, n_params=0):
    """Computa χ² reduzido = χ² / (dof - n_params)"""
    return chi2 / (dof - n_params)


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 80)
    print("FASE 6: ANÁLISE χ² BAO")
    print("Comparação: Zero Field Primordial vs ΛCDM")
    print("=" * 80)
    
    # ========================================================================
    # 1. Carregar dados BAO
    # ========================================================================
    
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'bao_data.csv')
    
    print(f"\n[1] Carregando dados BAO de: {data_path}")
    
    try:
        data = pd.read_csv(data_path)
    except FileNotFoundError:
        print(f"✗ ERRO: Arquivo não encontrado: {data_path}")
        return False
    
    z_obs = data['z'].values
    DV_obs = data['DV_over_rd'].values
    sigma_DV = data['sigma_DV_over_rd'].values
    
    print(f"✓ {len(z_obs)} pontos de redshift carregados")
    print(f"  z_min = {z_obs.min():.3f}, z_max = {z_obs.max():.3f}")
    print(f"  σ(D_V/r_d) médio = {sigma_DV.mean():.4f}")
    
    # ========================================================================
    # 2. Calcular D_V/r_d para ΛCDM
    # ========================================================================
    
    print(f"\n[2] Calculando D_V/r_d para ΛCDM...")
    
    DV_lcdm = np.array([
        DV_lcdm_analytic(z, H0=H0_DEFAULT, Omega_m=OMEGA_M_DEFAULT)
        for z in z_obs
    ])
    
    print(f"✓ ΛCDM calculado para {len(z_obs)} pontos")
    
    # ========================================================================
    # 3. Calcular D_V/r_d para Zero Field
    # ========================================================================
    
    print(f"\n[3] Calculando D_V/r_d para Zero Field Primordial...")
    
    DV_zfp = DV_zero_field_numeric(
        z_obs,
        m_phi=1e-42,
        phi_i=0.1,
        z_i=1000
    )
    
    if DV_zfp is None:
        print("✗ ERRO: Falha no cálculo de Zero Field")
        return False
    
    print(f"✓ Zero Field calculado")
    
    # ========================================================================
    # 4. Computar χ²
    # ========================================================================
    
    print(f"\n[4] Computando χ²...")
    
    chi2_lcdm, dof = compute_chi2(DV_lcdm, DV_obs, sigma_DV)
    chi2_zfp, _ = compute_chi2(DV_zfp, DV_obs, sigma_DV)
    
    reduced_chi2_lcdm = reduced_chi2(chi2_lcdm, dof, n_params=0)
    reduced_chi2_zfp = reduced_chi2(chi2_zfp, dof, n_params=1)  # m_phi é parâmetro
    
    delta_chi2 = chi2_zfp - chi2_lcdm
    
    print(f"\n{'='*80}")
    print(f"RESULTADOS χ² BAO")
    print(f"{'='*80}")
    print(f"\nΛCDM:")
    print(f"  χ² = {chi2_lcdm:.3f}")
    print(f"  χ²_red = {reduced_chi2_lcdm:.3f}")
    print(f"  DoF = {dof}")
    
    print(f"\nZero Field Primordial:")
    print(f"  χ² = {chi2_zfp:.3f}")
    print(f"  χ²_red = {reduced_chi2_zfp:.3f}")
    print(f"  DoF = {dof}")
    
    print(f"\nComparação:")
    print(f"  Δχ² = χ²_ZFP - χ²_ΛCDM = {delta_chi2:.3f}")
    print(f"  Δχ²_red = {reduced_chi2_zfp - reduced_chi2_lcdm:.3f}")
    
    # ========================================================================
    # 5. Veredito (critério ex-ante: Δχ² < 5 = PASSA)
    # ========================================================================
    
    print(f"\n{'='*80}")
    print(f"FASE 7: VEREDITO")
    print(f"{'='*80}")
    
    threshold = 5.0
    
    if delta_chi2 < threshold:
        veredito = "✅ PASSA"
        status = "favored" if delta_chi2 < 0 else "compatible"
    else:
        veredito = "❌ FALHA"
        status = "excluded"
    
    print(f"\nCritério ex-ante: Δχ² < {threshold}")
    print(f"Resultado: {veredito}")
    print(f"Status: {status}")
    
    if delta_chi2 < 0:
        print(f"\n⭐ Zero Field é FAVORECIDO por BAO (Δχ² = {delta_chi2:.3f})")
    elif delta_chi2 < threshold:
        print(f"\n✓ Zero Field é compatível com BAO dentro do limiar")
    else:
        print(f"\n✗ Zero Field é EXCLUÍDO por BAO (Δχ² = {delta_chi2:.3f})")
    
    # ========================================================================
    # 6. Salvar resultados
    # ========================================================================
    
    print(f"\n[5] Salvando resultados...")
    
    results_df = pd.DataFrame({
        'z': z_obs,
        'DV_obs': DV_obs,
        'sigma_DV': sigma_DV,
        'DV_lcdm': DV_lcdm,
        'DV_zfp': DV_zfp,
        'residual_lcdm': (DV_obs - DV_lcdm) / sigma_DV,
        'residual_zfp': (DV_obs - DV_zfp) / sigma_DV,
    })
    
    results_csv = os.path.join(os.path.dirname(__file__), 'results_chi2_bao.csv')
    results_df.to_csv(results_csv, index=False)
    print(f"✓ Resultados salvos em: {results_csv}")
    
    # Salvar resumo
    summary_path = os.path.join(os.path.dirname(__file__), '..', 'RESULTADO.md')
    
    with open(summary_path, 'w') as f:
        f.write("# RESULTADO — Fase 6: χ² BAO\n\n")
        f.write(f"**Veredito:** {veredito}\n\n")
        f.write(f"## Estatística\n\n")
        f.write(f"| Modelo | χ² | χ²_red | Δχ² |\n")
        f.write(f"|--------|-----|--------|-----|\n")
        f.write(f"| ΛCDM | {chi2_lcdm:.3f} | {reduced_chi2_lcdm:.3f} | — |\n")
        f.write(f"| Zero Field | {chi2_zfp:.3f} | {reduced_chi2_zfp:.3f} | {delta_chi2:.3f} |\n\n")
        f.write(f"## Interpretação\n\n")
        f.write(f"- Critério ex-ante: Δχ² < {threshold}\n")
        f.write(f"- Resultado: {veredito}\n")
        f.write(f"- Status: {status}\n\n")
        f.write(f"## Próximos passos\n\n")
        f.write(f"Testar contra dados SNe (Supernovas Type Ia) e CMB.\n")
    
    print(f"✓ Resumo salvo em: {summary_path}")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
