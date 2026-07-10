# GUIA DE EXECUÇÃO — Zero Field Primordial

## 🚀 Quick Start

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Executar validação integrada (RECOMENDADO)
python analysis/validation_notebook.py

# 3. Ou executar análises individuais
python analysis/chi2_bao.py              # Análise χ² BAO
python analysis/parameter_sweep.py       # Exploração de parâmetros
```

---

## 📋 O que cada script faz

### `src/run_zero_field.py`
**Solver ODE para Klein-Gordon + Friedmann**

Integra numericamente:
- Equação de Klein-Gordon: $\ddot{\phi} + 3H\dot{\phi} + m^2\phi = 0$
- Friedmann: $H^2 = \frac{8\pi G}{3}(\rho_m + \rho_r + \rho_\phi)$

**Uso:**
```python
from src.run_zero_field import solve_zero_field

sol = solve_zero_field(
    z_array=np.linspace(0, 2, 100),
    m=1e-42,        # massa do campo (GeV)
    phi_i=0.1,      # valor inicial (M_Pl)
    z_i=1000,       # redshift inicial
    verbose=True
)

# Retorna dict com: z, phi, phi_dot, H, rho_phi, w_phi
```

**Saída:**
- `H(z)`: evolução do parâmetro de Hubble
- `φ(z)`: evolução do campo escalar
- `w_φ(z)`: equação de estado do campo

---

### `analysis/chi2_bao.py`
**Comparação χ² BAO entre Zero Field e ΛCDM**

Executa:
1. Carrega dados observacionais BAO (17 pontos, z=0.1–2.3)
2. Calcula $D_V/r_d$ para ΛCDM (analítico)
3. Calcula $D_V/r_d$ para Zero Field (numérico via solver)
4. Computa $\chi^2$ para ambos
5. Gera veredito (PASSA/FALHA)

**Saída:**
- `analysis/results_chi2_bao.csv`: tabela com predições
- `RESULTADO.md`: resumo do veredito
- Console: prints com χ², Δχ², status

**Critério ex-ante:** Δχ² < 5 → **PASSA**

---

### `analysis/parameter_sweep.py`
**Exploração sistemática do espaço de parâmetros**

Executa 3 etapas:

#### Etapa 1: Grid Search
- Varre combinações de $(m_\phi, \phi_i, z_i)$
- Rápido, exploração qualitativa
- Salva: `parameter_grid.csv`

#### Etapa 2: Otimização Fina
- Usa Differential Evolution
- Encontra melhores parâmetros
- Minimiza χ² BAO

#### Etapa 3: Análise de Sensibilidade
- Varia $m_\phi$ isoladamente
- Varia $\phi_i$ isoladamente
- Mostra como χ² responde

**Saída:**
- `optimization_summary.csv`: parâmetros ótimos
- `sensitivity_analysis.csv`: resposta de χ²
- Console: prints com gráficos de convergência

---

### `analysis/validation_notebook.py` ⭐ **PRINCIPAL**
**Pipeline integrado de validação**

Executa tudo em sequência:

1. **Carrega dados BAO** (17 pontos)
2. **Calcula ΛCDM** (referência)
3. **Resolve Zero Field** (solver ODE)
4. **Computa χ²** para ambos
5. **Gera visualizações** (4 gráficos)
6. **Produz relatório** (RESULTADO.md)

**Saída:**
- `analysis/validation_plot.png`: 4 gráficos
  - D_V/r_d vs z (dados + predições)
  - Resíduos normalizados
  - Evolução de φ(z)
  - Equação de estado w_φ(z)
- `analysis/validation_results.csv`: tabela completa
- `RESULTADO.md`: relatório final com veredito

**Tempo de execução:** ~2-3 minutos

---

## 📊 Estrutura de Saída

Após executar `validation_notebook.py`, você terá:

```
zero-field-primordial/
├── RESULTADO.md                     ← Veredito final
├── analysis/
│   ├── validation_plot.png          ← 4 gráficos principais
│   ├── validation_results.csv       ← Tabela de resultados
│   ├── results_chi2_bao.csv         ← Detalhes χ²
│   ├── optimization_summary.csv     ← Parâmetros ótimos
│   └── sensitivity_analysis.csv     ← Análise de sensibilidade
└── src/
    └── zero_field_evolution.csv     ← Evolução numérica
```

---

## 🔍 Interpretando os Resultados

### Veredito no RESULTADO.md

```markdown
## Veredito: ✅ PASSA

| Modelo | χ² | χ²_red |
|--------|-----|--------|
| ΛCDM | 16.24 | 1.51 |
| Zero Field | 13.89 | 1.27 |

Δχ² = -2.35 (favorável para Zero Field)
```

**O que significa:**
- **Δχ² < 0**: Zero Field é **favorecido** por BAO
- **0 < Δχ² < 5**: Zero Field é **compatível** com BAO
- **Δχ² > 5**: Zero Field é **excluído** por BAO

---

## 🛠️ Customizando Parâmetros

### Variar massa do campo (m_φ)

```python
# Em validation_notebook.py, altere:
m_phi = 1e-42  # ← Mude aqui (GeV)

# Valores típicos:
# 1e-44: campo muito leve, comportamento próximo a Λ
# 1e-42: intermediário (padrão)
# 1e-40: campo mais pesado, mais "matéria-like"
```

### Variar condição inicial (φ_i)

```python
phi_i = 0.1  # ← Mude aqui (em unidades de M_Pl)

# 0.01 - 0.1: regime sub-Planckiano
# 0.1 - 1.0: regime Planckiano
```

### Variar redshift inicial (z_i)

```python
z_i = 1000  # ← Mude aqui

# > 500: permite evolução longa
# ~1000: padrão (era radiação-dominada)
```

---

## ⚠️ Troubleshooting

### "ERRO: Arquivo não encontrado"
```bash
# Certifique-se de estar no diretório raiz
cd zero-field-primordial/
python analysis/validation_notebook.py
```

### "ModuleNotFoundError: No module named 'run_zero_field'"
```bash
# Re-instale dependências
pip install -r requirements.txt

# Ou adicione manualmente ao path:
export PYTHONPATH="${PYTHONPATH}:/caminho/para/zero-field-primordial/src"
```

### Integração ODE muito lenta
```python
# Em run_zero_field.py, reduza precisão temporariamente:
solution = odeint(
    ...,
    rtol=1e-6,  # ← Reduzir de 1e-8
    atol=1e-8,  # ← Reduzir de 1e-10
)
```

### χ² do Zero Field é NaN
```
→ Geralmente significa erro na integração numérica
→ Tente com z_i maior (ex: 2000) e φ_i menor (ex: 0.01)
```

---

## 📈 Próximos Passos (Fases 7-8)

Após validar BAO com sucesso:

### Fase 7: Testar contra SNe (Supernovas Type Ia)
```bash
python analysis/chi2_sne.py  # (a implementar)
```

### Fase 8: Testar contra CMB
```bash
python analysis/chi2_cmb.py  # (a implementar)
```

### Fase 9: MCMC completo
```bash
python analysis/mcmc_exploration.py  # (a implementar)
```

---

## 📝 Documentação de Referência

- **Modelo**: `model/lagrangiana.md`, `model/equacoes.md`
- **Dados BAO**: `data/bao_data.csv`, `data/README.md`
- **Status do projeto**: `ARXIV_READY.md`, `VEREDITO_FINAL.md`

---

## ✅ Checklist de Execução

- [ ] Instalar dependências: `pip install -r requirements.txt`
- [ ] Testar solver ODE: `python src/run_zero_field.py`
- [ ] Executar validação: `python analysis/validation_notebook.py`
- [ ] Verificar RESULTADO.md gerado
- [ ] Inspecionar validation_plot.png
- [ ] Revisar validation_results.csv

---

## 🎯 Resumo

| Script | Função | Tempo | Saída |
|--------|--------|-------|-------|
| `run_zero_field.py` | Solver ODE | ~10s | H(z), φ(z), w_φ(z) |
| `chi2_bao.py` | Análise χ² BAO | ~30s | χ², veredito |
| `parameter_sweep.py` | Otimização parâmetros | ~5min | Parâmetros ótimos |
| `validation_notebook.py` | **Pipeline completo** | ~3min | Plots + relatório |

**Recomendação:** Execute `validation_notebook.py` para visualizar tudo de uma vez.

---

**Última atualização:** 2026-07-10  
**Status:** ✅ Operacional  
**Próxima etapa:** Fase 7 (SNe)
