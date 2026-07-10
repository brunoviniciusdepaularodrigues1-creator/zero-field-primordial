"""
validation_notebook.py: Notebook de validação integrado

Este script executa a pipeline completa:
1. Carrega dados BAO
2. Resolve Zero Field Primordial
3. Calcula χ² BAO para ambos os modelos
4. Gera visualizações
5. Produz relatório final
"""

import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.integrate import quad
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
)


# ============================================================================
# CONSTANTES E CONFIGURAÇÕES
# ============================================================================

H0_DEFAULT = 67.4
OMEGA_M_DEFAULT = 0.315
FIGURE_DPI = 100
FIGURE_SIZE = (12, 8)


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def load_bao_data():
    """Carrega dados BAO"""
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'bao_data.csv')
    try:
        data = pd.read_csv(data_path)
        return data['z'].values, data['DV_over_rd'].values, data['sigma_DV_over_rd'].values
    except FileNotFoundError:
        print(f"ERRO: Arquivo não encontrado: {data_path}")
        return None, None, None


def H_lcdm(z, H0=H0_DEFAULT, Omega_m=OMEGA_M_DEFAULT):
    """Parâmetro de Hubble para ΛCDM"""
    Omega_Lambda = 1.0 - Omega_m
    return H0 * np.sqrt(Omega_m * (1 + z) ** 3 + Omega_Lambda)


def DV_lcdm(z, H0=H0_DEFAULT, Omega_m=OMEGA_M_DEFAULT, rd_fid=rd_fiducial):
    """D_V / r_d para ΛCDM"""
    try:
        integral, _ = quad(lambda zp: 1.0 / H_lcdm(zp, H0, Omega_m), 0, z, limit=50)
        comoving_dist = (c_kms / H0) * integral
        DV = (z * comoving_dist ** 2) ** (1.0 / 3.0)
        return DV / rd_fid
    except:
        return np.nan


def DV_zero_field(z_array, m_phi=1e-42, phi_i=0.1, z_i=1000):
    """D_V / r_d para Zero Field via solver ODE"""
    print(f"\n[Validation] Resolvendo Zero Field Primordial...")
    print(f"  m = {m_phi:.2e} GeV")
    print(f"  φ_i = {phi_i:.3f} M_Pl")
    print(f"  z_i = {z_i:.0f}")
    
    # Resolver
    z_max = np.max(z_array) + 0.1
    z_eval = np.linspace(0, z_max, 200)
    
    sol = solve_zero_field(
        z_eval,
        m=m_phi,
        phi_i=phi_i,
        z_i=z_i,
        verbose=False
    )
    
    if sol is None:
        print("  ERRO: Solver falhou!")
        return None, None
    
    # Interpolar H(z)
    H_interp = interp1d(sol['z'], sol['H'], kind='cubic', fill_value='extrapolate')
    
    # Calcular D_V/r_d
    DV_results = []
    for z in z_array:
        try:
            integral, _ = quad(lambda zp: 1.0 / H_interp(zp), 0, z, limit=50)
            comoving_dist = (c_kms / H0_fiducial) * integral
            DV = (z * comoving_dist ** 2) ** (1.0 / 3.0)
            DV_results.append(DV / rd_fiducial)
        except:
            DV_results.append(np.nan)
    
    print(f"  ✓ Solução obtida")
    return np.array(DV_results), sol


def compute_chi2(DV_model, DV_obs, sigma_obs):
    """Computa χ²"""
    valid = ~(np.isnan(DV_model) | np.isnan(DV_obs))
    if not np.any(valid):
        return np.inf, 0
    
    chi2 = np.sum(((DV_obs[valid] - DV_model[valid]) / sigma_obs[valid]) ** 2)
    dof = np.sum(valid)
    
    return chi2, dof


# ============================================================================
# PIPELINE PRINCIPAL
# ============================================================================

def run_validation():
    """Executa pipeline de validação completo"""
    
    print("\n" + "=" * 100)
    print("VALIDAÇÃO INTEGRADA: Zero Field Primordial vs ΛCDM")
    print("=" * 100)
    
    # ========================================================================
    # ETAPA 1: Carregar dados
    # ========================================================================
    
    print("\n[ETAPA 1] Carregando dados BAO...")
    z_obs, DV_obs, sigma_obs = load_bao_data()
    
    if z_obs is None:
        print("ERRO: Falha ao carregar dados")
        return False
    
    print(f"✓ {len(z_obs)} pontos carregados")
    print(f"  z ∈ [{z_obs.min():.3f}, {z_obs.max():.3f}]")
    print(f"  σ(D_V/r_d) médio: {sigma_obs.mean():.4f}")
    
    # ========================================================================
    # ETAPA 2: Calcular ΛCDM
    # ========================================================================
    
    print("\n[ETAPA 2] Calculando ΛCDM...")
    DV_lcdm_pred = np.array([DV_lcdm(z) for z in z_obs])
    chi2_lcdm, dof_lcdm = compute_chi2(DV_lcdm_pred, DV_obs, sigma_obs)
    chi2_red_lcdm = chi2_lcdm / (dof_lcdm - 0)  # 0 parâmetros livres
    
    print(f"✓ ΛCDM calculado")
    print(f"  χ² = {chi2_lcdm:.3f}")
    print(f"  χ²_red = {chi2_red_lcdm:.3f}")
    print(f"  DoF = {dof_lcdm}")
    
    # ========================================================================
    # ETAPA 3: Calcular Zero Field
    # ========================================================================
    
    print("\n[ETAPA 3] Calculando Zero Field Primordial...")
    
    m_phi = 1e-42
    phi_i = 0.1
    z_i = 1000
    
    DV_zfp_pred, sol_zfp = DV_zero_field(z_obs, m_phi=m_phi, phi_i=phi_i, z_i=z_i)
    
    if DV_zfp_pred is None:
        print("ERRO: Falha no cálculo de Zero Field")
        return False
    
    chi2_zfp, dof_zfp = compute_chi2(DV_zfp_pred, DV_obs, sigma_obs)
    chi2_red_zfp = chi2_zfp / (dof_zfp - 1)  # 1 parâmetro livre (m_phi)
    
    print(f"✓ Zero Field calculado")
    print(f"  χ² = {chi2_zfp:.3f}")
    print(f"  χ²_red = {chi2_red_zfp:.3f}")
    print(f"  DoF = {dof_zfp}")
    
    # ========================================================================
    # ETAPA 4: Análise comparativa
    # ========================================================================
    
    print("\n[ETAPA 4] Análise Comparativa...")
    
    delta_chi2 = chi2_zfp - chi2_lcdm
    delta_chi2_red = chi2_red_zfp - chi2_red_lcdm
    
    print(f"  Δχ² = {delta_chi2:.3f}")
    print(f"  Δχ²_red = {delta_chi2_red:.3f}")
    
    # Veredito
    threshold = 5.0
    if delta_chi2 < threshold:
        veredito = "✅ COMPATÍVEL"
        if delta_chi2 < 0:
            favored = "(favorecido)"
        else:
            favored = "(compatível)"
    else:
        veredito = "❌ EXCLUÍDO"
        favored = ""
    
    print(f"\n  Veredito: {veredito} {favored}")
    print(f"  (Critério: Δχ² < {threshold})")
    
    # ========================================================================
    # ETAPA 5: Visualizações
    # ========================================================================
    
    print("\n[ETAPA 5] Gerando visualizações...")
    
    fig, axes = plt.subplots(2, 2, figsize=FIGURE_SIZE, dpi=FIGURE_DPI)
    fig.suptitle('Validação: Zero Field Primordial vs ΛCDM', fontsize=14, fontweight='bold')
    
    # Gráfico 1: D_V/r_d vs z
    ax = axes[0, 0]
    ax.errorbar(z_obs, DV_obs, yerr=sigma_obs, fmt='ko', label='Observações BAO', markersize=6)
    ax.plot(z_obs, DV_lcdm_pred, 'b-', label='ΛCDM', linewidth=2)
    ax.plot(z_obs, DV_zfp_pred, 'r--', label='Zero Field', linewidth=2)
    ax.set_xlabel('Redshift z', fontsize=11)
    ax.set_ylabel('$D_V / r_d$', fontsize=11)
    ax.set_title('D_V/r_d: Dados vs Modelos', fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Gráfico 2: Resíduos χ²
    ax = axes[0, 1]
    residual_lcdm = (DV_obs - DV_lcdm_pred) / sigma_obs
    residual_zfp = (DV_obs - DV_zfp_pred) / sigma_obs
    
    x_pos = np.arange(len(z_obs))
    width = 0.35
    ax.bar(x_pos - width/2, residual_lcdm, width, label='ΛCDM', alpha=0.7)
    ax.bar(x_pos + width/2, residual_zfp, width, label='Zero Field', alpha=0.7)
    ax.axhline(0, color='k', linestyle='-', linewidth=0.5)
    ax.set_xlabel('Índice do ponto', fontsize=11)
    ax.set_ylabel('Resíduo (σ)', fontsize=11)
    ax.set_title('Resíduos Normalizados', fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Gráfico 3: Evolução de φ(z)
    ax = axes[1, 0]
    if sol_zfp is not None:
        ax.plot(sol_zfp['z'], sol_zfp['phi'], 'g-', linewidth=2)
        ax.set_xlabel('Redshift z', fontsize=11)
        ax.set_ylabel('$\\phi(z)$ [$M_{Pl}$]', fontsize=11)
        ax.set_title('Evolução do Campo Escalar', fontsize=12)
        ax.grid(True, alpha=0.3)
    
    # Gráfico 4: Equação de estado
    ax = axes[1, 1]
    if sol_zfp is not None:
        ax.plot(sol_zfp['z'], sol_zfp['w_phi'], 'purple', linewidth=2, label='Zero Field')
        ax.axhline(0, color='k', linestyle='--', linewidth=1, label='w=0 (matéria)')
        ax.axhline(-1, color='r', linestyle='--', linewidth=1, label='w=-1 (Λ)')
        ax.set_xlabel('Redshift z', fontsize=11)
        ax.set_ylabel('$w_\\phi(z)$', fontsize=11)
        ax.set_title('Equação de Estado do Campo', fontsize=12)
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_ylim([-1.5, 0.5])
    
    plt.tight_layout()
    
    # Salvar figura
    fig_path = os.path.join(os.path.dirname(__file__), 'validation_plot.png')
    plt.savefig(fig_path, dpi=FIGURE_DPI, bbox_inches='tight')
    print(f"  ✓ Gráfico salvo: {fig_path}")
    plt.close()
    
    # ========================================================================
    # ETAPA 6: Gerar relatório
    # ========================================================================
    
    print("\n[ETAPA 6] Gerando relatório...")
    
    # DataFrame de resultados
    results_df = pd.DataFrame({
        'z': z_obs,
        'DV_obs': DV_obs,
        'sigma_DV': sigma_obs,
        'DV_lcdm': DV_lcdm_pred,
        'DV_zfp': DV_zfp_pred,
        'residual_lcdm': (DV_obs - DV_lcdm_pred) / sigma_obs,
        'residual_zfp': (DV_obs - DV_zfp_pred) / sigma_obs,
    })
    
    results_csv = os.path.join(os.path.dirname(__file__), 'validation_results.csv')
    results_df.to_csv(results_csv, index=False)
    print(f"  ✓ Resultados salvos: {results_csv}")
    
    # Arquivo de resumo
    summary_path = os.path.join(os.path.dirname(__file__), '..', 'RESULTADO.md')
    
    with open(summary_path, 'w') as f:
        f.write("# RESULTADO — Validação Integrada\n\n")
        f.write(f"**Data:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## Veredito: {veredito}\n\n")
        
        f.write("## Estatística χ² BAO\n\n")
        f.write("| Modelo | χ² | χ²_red | n_params |\n")
        f.write("|--------|-----|--------|----------|\n")
        f.write(f"| ΛCDM | {chi2_lcdm:.3f} | {chi2_red_lcdm:.3f} | 0 |\n")
        f.write(f"| Zero Field | {chi2_zfp:.3f} | {chi2_red_zfp:.3f} | 1 |\n\n")
        
        f.write(f"## Comparação\n\n")
        f.write(f"- Δχ² = {delta_chi2:.3f}\n")
        f.write(f"- Δχ²_red = {delta_chi2_red:.3f}\n")
        f.write(f"- Critério: Δχ² < 5.0\n")
        f.write(f"- Status: **{veredito}**\n\n")
        
        f.write(f"## Parâmetros do Modelo\n\n")
        f.write(f"- m_φ = {m_phi:.2e} GeV\n")
        f.write(f"- φ_i = {phi_i:.3f} M_Pl\n")
        f.write(f"- z_i = {z_i:.0f}\n\n")
        
        f.write(f"## Próximos Passos\n\n")
        f.write(f"1. Testar contra dados de Supernovas Type Ia (SNe)\n")
        f.write(f"2. Testar contra dados de CMB\n")
        f.write(f"3. Exploração completa do espaço de parâmetros (MCMC)\n")
        f.write(f"4. Publicação em arXiv (se favorável)\n\n")
        
        f.write(f"---\n")
        f.write(f"*Gerado automaticamente por validation_notebook.py*\n")
    
    print(f"  ✓ Relatório salvo: {summary_path}")
    
    # ========================================================================
    # ETAPA 7: Resumo final
    # ========================================================================
    
    print("\n" + "=" * 100)
    print("RESUMO FINAL")
    print("=" * 100)
    
    print(f"\nModelo ΛCDM:")
    print(f"  χ² = {chi2_lcdm:.3f} (DoF={dof_lcdm})")
    
    print(f"\nModelo Zero Field Primordial:")
    print(f"  χ² = {chi2_zfp:.3f} (DoF={dof_zfp})")
    print(f"  Parâmetros: m={m_phi:.2e} GeV, φ_i={phi_i:.3f} M_Pl")
    
    print(f"\nComparação:")
    print(f"  Δχ² = {delta_chi2:.3f}")
    print(f"  Resultado: {veredito}")
    
    if delta_chi2 < 0:
        print(f"\n⭐ Zero Field é FAVORECIDO por BAO!")
    elif delta_chi2 < threshold:
        print(f"\n✓ Zero Field é compatível com BAO")
    else:
        print(f"\n✗ Zero Field é excluído por BAO")
    
    print("\n" + "=" * 100)
    
    return True


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    try:
        success = run_validation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
