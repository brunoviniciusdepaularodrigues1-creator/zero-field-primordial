#!/usr/bin/env python3
"""
Analysis: Chi-squared for Zero Field Primordial vs Lambda-CDM using SNe Ia

Comparison of Zero Field Primordial (scalar field model) with LCDM
against Type Ia Supernovae distance modulus data.
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize

def load_sn_data(filepath='data/sn_data.csv'):
    """Load Supernovae Type Ia data."""
    data = pd.read_csv(filepath)
    return data['z'].values, data['mu_obs'].values, data['mu_err'].values

def mu_lcdm(z, H0=70.0, Om=0.3):
    """Distance modulus for LCDM."""
    c = 3e5  # speed of light (km/s)
    DH = c / H0
    OL = 1.0 - Om
    
    def integrand(z_prime):
        return 1.0 / np.sqrt(Om * (1 + z_prime)**3 + OL)
    
    z_arr = np.linspace(0, z, 100)
    comoving_dist = DH * np.trapz(1.0 / np.sqrt(Om * (1 + z_arr)**3 + OL), z_arr)
    luminosity_dist = comoving_dist * (1 + z)
    
    return 5 * np.log10(luminosity_dist) + 25

def mu_zfp(z, H0=70.0, Om=0.3, m_phi=1e-42):
    """Distance modulus for Zero Field Primordial (approx)."""
    # For now, use a scalar correction to LCDM
    # In reality, would solve Klein-Gordon in FRW
    correction = 0.02 * np.log(1 + z)  # Small correction
    return mu_lcdm(z, H0, Om) + correction

def chi2_model(mu_theory, mu_obs, mu_err):
    """Compute chi-squared."""
    return np.sum(((mu_obs - mu_theory) / mu_err)**2)

if __name__ == '__main__':
    z, mu_obs, mu_err = load_sn_data()
    
    # LCDM
    mu_lcdm_vals = np.array([mu_lcdm(zi) for zi in z])
    chi2_lcdm = chi2_model(mu_lcdm_vals, mu_obs, mu_err)
    
    # Zero Field Primordial
    mu_zfp_vals = np.array([mu_zfp(zi) for zi in z])
    chi2_zfp = chi2_model(mu_zfp_vals, mu_obs, mu_err)
    
    print(f"SNe Ia Analysis Results:")
    print(f"  chi2(LCDM): {chi2_lcdm:.4f}")
    print(f"  chi2(ZFP):  {chi2_zfp:.4f}")
    print(f"  Delta chi2: {chi2_zfp - chi2_lcdm:.4f}")
    print(f"  N points: {len(z)}")
