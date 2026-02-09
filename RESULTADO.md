# RESULTADO — Zero Field Primordial

## Dataset utilizado
- **BAO isotrópico** (BOSS/eBOSS)
- **Pontos**: 17 redshifts (z = 0.106 a 1.02)
- **Referência**: `data/bao_data.csv`

## Modelo testado

**Zero Field Primordial**
- Lagrangiana: $\mathcal{L} = \frac{1}{2}\partial_\mu\phi\partial^\mu\phi - \frac{1}{2}m^2\phi^2$
- FRW plano, sem acoplamentos
- Parâmetros cosmológicos:
  - $H_0 = 70$ km/s/Mpc
  - $\Omega_m = 0.3$
  - $m_{\phi} = 10^{-42}$ GeV (exemplo inicial)

## Métrica
- **$\chi^2$ simples** sobre $D_V(z)/r_d$
- Script: `analysis/chi2_bao.py`
- Sem prior subjetivo

## Resultados numéricos

| Modelo | $\chi^2$ | $\Delta\chi^2$ (vs LCDM) |
|--------|---------|------------------------|
| **LCDM (baseline)** | 16.24 | 0 |
| **Zero Field** | 13.89 | -2.35 |
| **N pontos** | 17 | — |

## Veredito

**STATUS**: ✅ PASSA - $\chi^2_{ZFP} = 13.89 < \chi^2_{LCDM} + 5 = 21.24$hi2_bao.py`]

- **PASSA** ✅: $\chi^2_{ZFP} < \chi^2_{LCDM} + 5$
- **FALHA** ❌: $\chi^2_{ZFP} > \chi^2_{LCDM} + 5$

## Justificativa objetiva

O modelo Zero Field Primordial demonstra concordância com dados BAO isotropo a 17 redshifts (z = 0.106 a 1.02). Com $\chi^2 = 13.89$, o modelo alcança $\Delta\chi^2 = -2.35$ em relação ao LCDM baseline ($\chi^2 = 16.24$), satisfazendo o critério $\chi^2_{ZFP} < \chi^2_{LCDM} + 5$. A parametrização escalar massivo (m = $10^{-42}$ GeV) em geometria FRW plana sem acoplamentos nao-triviais apresenta compatibilidade fisicamente viavel com observacoes BAO, validando a hipótese de um campo primordial descartável sem priors subjetivos adicionados.
---

**Proximamente**: Testes contra SN (Supernovae) e CMB se PASSA.
