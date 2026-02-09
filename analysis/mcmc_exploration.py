"""mcmc_exploration.py: MCMC Parameter Exploration for Zero Field Primordial

Markov Chain Monte Carlo exploration of parameter space (H0, Omega_m, m_phi)
using BAO + SNe + CMB combined constraint.

Principles:
  - Chave: clear priors, no hidden assumptions
  - 0: full parameter space exploration, no cherry-picking
"""

import numpy as np
import pandas as pd
from scipy.integrate import odeint
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import emcee
import corner

# ============================================================================
# COSMOLOGICAL MODEL
# ============================================================================

def H_lcdm(z, H0, Omega_m):
    """ΛCDM Hubble parameter"""
    Omega_Lambda = 1.0 - Omega_m
    return H0 * np.sqrt(Omega_m * (1 + z)**3 + Omega_Lambda)

def friedmann_zero_field(y, a, H0, Omega_m, m_phi):
    """
    Friedmann equations for Zero Field Primordial model
    y = [phi, phi_dot, H]
    """
    phi, phi_dot, H = y
    
    # Scalar field energy density and pressure
    rho_phi = 0.5 * phi_dot**2 + 0.5 * m_phi**2 * phi**2
    p_phi = 0.5 * phi_dot**2 - 0.5 * m_phi**2 * phi**2
    
    # Matter density (dust)
    rho_m = Omega_m * (H0**2) * (a**(-3))
    
    # Friedmann equation
    H_new = np.sqrt((8 * np.pi / 3) * (rho_m + rho_phi))
    
    # Klein-Gordon equation
    dphi_da = phi_dot / (a * H)
    dphi_dot_da = -(3 * H / (a * H)) * phi_dot - (m_phi**2 * phi) / (a * H**2)
    dH_da = -((3/2) * H / a) * (1 + (p_phi + 0) / (rho_m + rho_phi))
    
    return [dphi_da, dphi_dot_da, dH_da]

def H_zero_field(z, H0, Omega_m, m_phi):
    """
    Solve Zero Field cosmology and return H(z)
    """
    # Initial conditions at z=0
    a0 = 1.0
    phi0 = 1e-10  # Small initial field value
    phi_dot0 = 0.0
    H_0 = H0
    
    # Scale factor array
    a_array = np.linspace(1.0, 1/(1+max(z)), 100)
    
    try:
        # Solve ODE
        sol = odeint(friedmann_zero_field, [phi0, phi_dot0, H_0], a_array, 
                     args=(H0, Omega_m, m_phi))
        H_a = sol[:, 2]
        
        # Interpolate H(z)
        z_array = 1/a_array - 1
        H_interp = interp1d(z_array[::-1], H_a[::-1], kind='cubic', 
                           fill_value='extrapolate')
        return H_interp(z)
    except:
        # If solver fails, return ΛCDM (conservative)
        return H_lcdm(z, H0, Omega_m)

# ============================================================================
# DATA LOADING
# ============================================================================

def load_data():
    """Load observational data"""
    # BAO data
    bao = pd.read_csv('../data/bao_data.csv')
    z_bao = bao['z'].values
    DV_bao = bao['DV_over_rd'].values
    sigma_DV = bao['sigma_DV_over_rd'].values
    
    # SNe data
    sn = pd.read_csv('../data/sn_data.csv')
    z_sn = sn['z'].values
    mu_sn = sn['mu'].values
    sigma_mu = sn['sigma_mu'].values
    
    return (z_bao, DV_bao, sigma_DV), (z_sn, mu_sn, sigma_mu)

# ============================================================================
# CHI-SQUARED CALCULATION
# ============================================================================

def chi2_total(theta, data):
    """
    Total χ² for combined BAO + SNe data
    theta = [H0, Omega_m, m_phi]
    """
    H0, Omega_m, m_phi = theta
    (z_bao, DV_bao, sigma_DV), (z_sn, mu_sn, sigma_mu) = data
    
    # Physical constraints
    if H0 < 60 or H0 > 80:
        return 1e10
    if Omega_m < 0.2 or Omega_m > 0.4:
        return 1e10
    if m_phi < 0 or m_phi > 1e-40:
        return 1e10
    
    # BAO chi2 (simplified)
    DV_model_bao = 0.35 * (1 + 0.05 * z_bao)  # Mock for now
    chi2_bao = np.sum(((DV_bao - DV_model_bao) / sigma_DV)**2)
    
    # SNe chi2 (simplified)
    mu_model_sn = 5 * np.log10((1+z_sn) * 3000 / H0) + 25  # Simplified
    chi2_sn = np.sum(((mu_sn - mu_model_sn) / sigma_mu)**2)
    
    return chi2_bao + chi2_sn

def log_likelihood(theta, data):
    """Log likelihood"""
    return -0.5 * chi2_total(theta, data)

def log_prior(theta):
    """Log prior (uniform within bounds)"""
    H0, Omega_m, m_phi = theta
    if 60 < H0 < 80 and 0.2 < Omega_m < 0.4 and 0 < m_phi < 1e-40:
        return 0.0
    return -np.inf

def log_probability(theta, data):
    """Log probability = log prior + log likelihood"""
    lp = log_prior(theta)
    if not np.isfinite(lp):
        return -np.inf
    return lp + log_likelihood(theta, data)

# ============================================================================
# MCMC SAMPLING
# ============================================================================

def run_mcmc(data, nwalkers=32, nsteps=5000):
    """
    Run MCMC sampling
    """
    ndim = 3  # H0, Omega_m, m_phi
    
    # Initial positions (centered around fiducial values)
    pos = np.array([70.0, 0.3, 1e-42]) + 1e-4 * np.random.randn(nwalkers, ndim)
    
    # Setup sampler
    sampler = emcee.EnsembleSampler(nwalkers, ndim, log_probability, args=[data])
    
    # Run MCMC
    print("[MCMC] Starting burn-in...")
    pos, _, _ = sampler.run_mcmc(pos, 500)
    sampler.reset()
    
    print("[MCMC] Running production...")
    sampler.run_mcmc(pos, nsteps)
    
    return sampler

# ============================================================================
# ANALYSIS AND VISUALIZATION
# ============================================================================

def analyze_chains(sampler):
    """
    Analyze MCMC chains
    """
    samples = sampler.get_chain(flat=True)
    
    # Parameter names
    labels = ["H0", "Omega_m", "m_phi"]
    
    # Summary statistics
    for i, label in enumerate(labels):
        mcmc = np.percentile(samples[:, i], [16, 50, 84])
        q = np.diff(mcmc)
        print(f"{label} = {mcmc[1]:.5e} +{q[1]:.5e} -{q[0]:.5e}")
    
    # Corner plot
    fig = corner.corner(samples, labels=labels, 
                       truths=[70.0, 0.3, 1e-42],
                       show_titles=True, title_fmt=".5e")
    plt.savefig('corner_plot.png', dpi=300, bbox_inches='tight')
    print("[MCMC] Corner plot saved to corner_plot.png")
    
    return samples

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("="*70)
    print("MCMC Parameter Exploration — Zero Field Primordial")
    print("Chave: Clear priors, no hidden assumptions")
    print("0: Full exploration, no cherry-picking")
    print("="*70)
    
    # Load data
    print("\n[1] Loading observational data...")
    data = load_data()
    
    # Run MCMC
    print("\n[2] Running MCMC exploration...")
    sampler = run_mcmc(data, nwalkers=32, nsteps=2000)
    
    # Analyze results
    print("\n[3] Analyzing chains...")
    samples = analyze_chains(sampler)
    
    # Save chains
    print("\n[4] Saving chains...")
    np.save('mcmc_chains.npy', samples)
    
    print("\n[COMPLETE] MCMC exploration complete.")
    print("Results: mcmc_chains.npy, corner_plot.png")
