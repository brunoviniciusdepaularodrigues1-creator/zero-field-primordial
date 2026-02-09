"""chi2_bao.py: Comparação χ² BAO entre Zero Field Primordial e ΛCDM"""

import numpy as np
import pandas as pd

# Carregar dados BAO
data = pd.read_csv('../data/bao_data.csv')
z_obs = data['z'].values
DV_obs = data['DV_over_rd'].values
sigma_DV = data['sigma_DV_over_rd'].values

# Parâmetros cosmológicos base
H0 = 70.0  # km/s/Mpc
Omega_m = 0.3

def H_lcdm(z):
    """Hubble parameter para ΛCDM (plano, sem Λ explícito)"""
    Omega_Lambda = 1.0 - Omega_m
    return H0 * np.sqrt(Omega_m * (1 + z)**3 + Omega_Lambda)

def DV_lcdm(z):
    """D_V / r_s para ΛCDM (mock simplificado)"""
    return 0.35 * (1.0 + 0.05 * z)  # Aproximação simples

def DV_zero_field(z, m_phi=1e-42):
    """D_V para Zero Field (mock: assume evolução ligeiramente diferente)"""
    # Aqui entraria o solver ODE completo
    # Por enquanto, mock com parâmetro m_phi
    return DV_lcdm(z) * (1.0 + 0.02 * m_phi * 1e42)

def chi2(DV_model, DV_obs, sigma):
    """Calcula χ² simples"""
    return np.sum(((DV_obs - DV_model) / sigma)**2)

# Computar χ²
DV_lcdm_pred = np.array([DV_lcdm(z) for z in z_obs])
DV_zfp_pred = np.array([DV_zero_field(z) for z in z_obs])

chi2_lcdm = chi2(DV_lcdm_pred, DV_obs, sigma_DV)
chi2_zfp = chi2(DV_zfp_pred, DV_obs, sigma_DV)

print(f"[FASE 6] Análise χ² BAO")
print(f"  χ² ΛCDM: {chi2_lcdm:.3f}")
print(f"  χ² Zero Field: {chi2_zfp:.3f}")
print(f"  Dados: {len(z_obs)} pontos")

if chi2_zfp < chi2_lcdm + 5:  # Threshold simples
    veredito = "PASSA"
else:
    veredito = "FALHA"

print(f"\n[FASE 7] Veredito: {veredito}")

# Salvar resultados
results = pd.DataFrame({
    'z': z_obs,
    'DV_obs': DV_obs,
    'DV_lcdm': DV_lcdm_pred,
    'DV_zfp': DV_zfp_pred
})
results.to_csv('results.csv', index=False)
print(f"\nResultados salvos em results.csv")
