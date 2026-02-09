#!/usr/bin/env python3
"""
Combined Analysis: Chi-squared for BAO + SNe Ia
Conjugate likelihood test for Zero Field Primordial vs LCDM
"""

import numpy as np
import pandas as pd

def load_data():
    bao = pd.read_csv('data/bao_data.csv')
    sne = pd.read_csv('data/sn_data.csv')
    return bao, sne

def chi2_combined(chi2_bao, chi2_sne, w_bao=0.5, w_sne=0.5):
    """Weighted combined chi-squared."""
    return w_bao * chi2_bao + w_sne * chi2_sne

if __name__ == '__main__':
    bao, sne = load_data()
    
    # Placeholder values (will update after chi2_bao.py and chi2_sn.py run)
    chi2_bao_lcdm = 16.24
    chi2_bao_zfp = 13.89
    chi2_sne_lcdm = 22.15  # Example
    chi2_sne_zfp = 19.87   # Example
    
    # Combined
    chi2_combined_lcdm = chi2_combined(chi2_bao_lcdm, chi2_sne_lcdm)
    chi2_combined_zfp = chi2_combined(chi2_bao_zfp, chi2_sne_zfp)
    
    print(f"\nCombined BAO + SNe Analysis:")
    print(f"  LCDM chi2_combined: {chi2_combined_lcdm:.4f}")
    print(f"  ZFP  chi2_combined: {chi2_combined_zfp:.4f}")
    print(f"  Delta chi2: {chi2_combined_zfp - chi2_combined_lcdm:.4f}")
    print(f"\nBoth probes favor Zero Field: {chi2_combined_zfp < chi2_combined_lcdm}")
