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

**STATUS**: ⚠️ PROVISÓRIO — Valores ilustrativos para validação do pipeline
- **Veredito suspenso** até execução real de `analysis/chi2_bao.py`
- - **Pipeline**: Em desenvolvimento (estrutura validada, execução pendente)


## Justificativa objetiva

**Nota**: Os valores na tabela de "Resultados numéricos" são ilustrativos para validação do pipeline. O veredito final depende da execução real do script `analysis/chi2_bao.py` contra dados BAO. A estrutura teórica do Zero Field Primordial (campo escalar livre massivo em FRW plano) foi formulada corretamente e é fisicamente viável, mas aguarda constrangimento numérico conclusivo.---

**Proximamente**: Testes contra SN (Supernovae) e CMB se PASSA.
