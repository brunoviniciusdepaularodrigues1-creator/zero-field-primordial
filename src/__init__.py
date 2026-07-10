"""
Zero Field Primordial — Pacote de análise cosmológica

Módulo principal para testes de um campo escalar massivo como componente
de "escuridão" em cosmologia FRW plana.

Imports principais:
- Solver ODE: run_zero_field.solve_zero_field()
- Análise χ²: chi2_bao, parameter_sweep, validation_notebook
- Utilidades: utils (constantes, funções)

Exemplo de uso:
    >>> from src.run_zero_field import solve_zero_field
    >>> sol = solve_zero_field(z_array, m=1e-42, phi_i=0.1, z_i=1000)
    >>> print(f"H(z=0) = {sol['H'][-1]:.1f} km/s/Mpc")

Referência:
    - Lagrangiana: ℒ = ½∂φ∂φ - ½m²φ²
    - Klein-Gordon: φ̈ + 3Hφ̇ + m²φ = 0
    - Friedmann: H² = (8πG/3)(ρ_m + ρ_r + ρ_φ)

Status:
    - Fase 6: ✅ Análise χ² BAO completa
    - Fase 7: ⏳ Testes SNe (em desenvolvimento)
    - Fase 8: ⏳ Testes CMB (em desenvolvimento)
    - Fase 9: ⏳ MCMC (em desenvolvimento)

Princípios operacionais:
    - CHAVE: Coerência, definições claras, sem evasão
    - 0: Honestidade com falhas, refutabilidade explícita

Autor: Bruno Vinicius de Paulo Rodrigues
Licença: MIT (2026)
"""

__version__ = "1.0.0"
__author__ = "Bruno Vinicius de Paulo Rodrigues"
__license__ = "MIT"

# Importar módulos principais
try:
    from .run_zero_field import (
        solve_zero_field,
        compute_DV,
        H_lcdm,
        get_cosmological_params,
        rho_scalar_field,
        pressure_scalar_field,
        equation_of_state,
        H0_fiducial,
        Omega_m0,
        Omega_r0,
        c_kms,
        rd_fiducial,
        M_Pl,
    )
    print("✓ run_zero_field importado com sucesso")
except ImportError as e:
    print(f"⚠️ Erro ao importar run_zero_field: {e}")

try:
    from . import utils
    print("✓ utils importado com sucesso")
except ImportError as e:
    print(f"⚠️ Erro ao importar utils: {e}")

# Metadata
__all__ = [
    'solve_zero_field',
    'compute_DV',
    'H_lcdm',
    'get_cosmological_params',
    'rho_scalar_field',
    'pressure_scalar_field',
    'equation_of_state',
    'utils',
]
