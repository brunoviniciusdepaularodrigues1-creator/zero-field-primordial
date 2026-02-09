# 🚀 EXECUTION GUIDE — Zero Field Primordial

**Guia prático de execução passo-a-passo para análise completa**

**Princípios:** CHAVE (clareza) + 0 (honestidade)
**Versão:** 1.0 (2026-02-09)

---

## ⚡ Quick Start (3 minutos)

```bash
# 1. Clone o repositório
git clone https://github.com/brunoviniciusdepaularodrigues1-creator/zero-field-primordial.git
cd zero-field-primordial

# 2. Instale dependências
pip install -r requirements.txt

# 3. Execute análise rápida
cd analysis
python run_complete_analysis.py --mode quick
```

✅ **Resultado:** Análise rápida completa em ~2-3 minutos

---

## 📋 Pré-requisitos

### Sistema
- Python 3.8+ (recomendado: 3.10)
- pip (gerenciador de pacotes)
- 4GB RAM mínimo (8GB recomendado para MCMC completo)
- ~500MB espaço em disco

### Dependências Python
Todas listadas em `requirements.txt`:
```
numpy>=1.20.0
scipy>=1.7.0
pandas>=1.3.0
matplotlib>=3.3.0
emcee>=3.0.0
corner>=2.2.0
```

### Instalação
```bash
# Opção 1: pip direto
pip install -r requirements.txt

# Opção 2: ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

---

## 🎯 Modos de Execução

O script `run_complete_analysis.py` oferece 3 modos:

### 1. **Quick Mode** (teste rápido)
```bash
python run_complete_analysis.py --mode quick
```
- **Tempo:** ~2-3 minutos
- **MCMC:** 16 walkers × 100 steps
- **Uso:** Validação rápida, debugging

### 2. **Full Mode** (análise completa)
```bash
python run_complete_analysis.py --mode full
```
- **Tempo:** ~15-20 minutos
- **MCMC:** 32 walkers × 5000 steps
- **Uso:** Análise exploratória completa

### 3. **Publication Mode** (publication-ready)
```bash
python run_complete_analysis.py --mode publication
```
- **Tempo:** ~45-60 minutos
- **MCMC:** 64 walkers × 10000 steps
- **Uso:** Resultados para publicação

---

## 📊 Pipeline de Análise

A execução completa segue 4 fases:

### **FASE 1: Análise χ²**
Executa cálculos de chi-quadrado para todos os probes:

```bash
# Execução individual (opcional)
cd analysis
python chi2_bao.py      # BAO isotropic
python chi2_sn.py       # SNe Type Ia
python chi2_cmb.py      # CMB (Planck-like)
python chi2_conjugado.py  # BAO + SNe combined
```

**Outputs:**
- `results.csv` - Resumo χ² para cada probe
- Terminal output com Δχ² vs ΛCDM

### **FASE 2: Exploração MCMC**
```bash
python mcmc_exploration.py
```

**Outputs:**
- `mcmc_chains.npy` - Samples de parâmetros (H₀, Ω_m, m_φ)
- `corner_plot.png` - Visualização corner plot
- Terminal output com estatísticas (mean ± σ, 68% CI)

### **FASE 3: Visualização**
```bash
python plot_constraints.py
```

**Outputs:**
- `constraints_zfp.png` - 3×3 grid com contornos + posteriors
- `constraint_statistics.csv` - Parâmetros sumarizados

### **FASE 4: Síntese**
Automática ao fim de `run_complete_analysis.py`

**Outputs:**
- Terminal summary com veredito CHAVE + 0
- Lista de todos os outputs gerados

---

## 🔧 Opções Avançadas

### Pular etapas específicas
```bash
# Pular chi² (usar resultados prévios)
python run_complete_analysis.py --skip-chi2

# Pular MCMC (usar chains prévias)
python run_complete_analysis.py --skip-mcmc

# Pular plots (apenas análise numérica)
python run_complete_analysis.py --skip-plots

# Combinar flags
python run_complete_analysis.py --mode quick --skip-chi2 --skip-mcmc
```

### Executar scripts individuais
```bash
# Apenas BAO chi²
python chi2_bao.py

# Apenas MCMC (usa configuração default)
python mcmc_exploration.py

# Apenas plots (requer mcmc_chains.npy)
python plot_constraints.py
```

---

## 📂 Estrutura de Outputs

Após execução completa:

```
analysis/
├── results.csv                 # Chi² summary
├── mcmc_chains.npy             # MCMC samples
├── corner_plot.png             # Corner plot
├── constraints_zfp.png         # Constraint grid
└── constraint_statistics.csv   # Parameter stats
```

---

## 🧪 Exemplo Completo (Passo-a-Passo)

### Cenário: Primeira execução completa

```bash
# 1. Preparação
git clone https://github.com/brunoviniciusdepaularodrigues1-creator/zero-field-primordial.git
cd zero-field-primordial
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Teste rápido (validação)
cd analysis
python run_complete_analysis.py --mode quick
# ✅ Deve completar em ~2-3 min

# 3. Análise completa
python run_complete_analysis.py --mode full
# ✅ Completa em ~15-20 min
# ✅ Gera todos os outputs

# 4. Verificação de outputs
ls -lh *.png *.csv *.npy
# Deve listar:
#   - corner_plot.png
#   - constraints_zfp.png
#   - results.csv
#   - constraint_statistics.csv
#   - mcmc_chains.npy

# 5. Visualizar plots
open constraints_zfp.png  # Mac
xdg-open constraints_zfp.png  # Linux
start constraints_zfp.png  # Windows
```

---

## ⚠️ Troubleshooting

### Erro: ModuleNotFoundError
```bash
# Solução: Reinstalar dependências
pip install -r requirements.txt --upgrade
```

### Erro: Timeout em MCMC
```bash
# Solução: Usar modo quick ou skip MCMC
python run_complete_analysis.py --mode quick
# ou
python run_complete_analysis.py --skip-mcmc
```

### Erro: Arquivo não encontrado (data)
```bash
# Verificar estrutura:
ls ../data/
# Deve listar: bao_data.csv, sn_data.csv

# Se faltando, baixar do repositório
git pull origin main
```

### MCMC muito lento
```bash
# Reduzir walkers/steps manualmente
# Editar mcmc_exploration.py:
# nwalkers = 16  # ao invés de 32
# nsteps = 1000  # ao invés de 5000
```

---

## 🎓 Interpretando Resultados

### Chi² Output
```
[FASE 6] Análise χ² BAO
 χ² ΛCDM: 16.240
 χ² Zero Field: 13.890
 Dados: 17 pontos

[FASE 7] Veredito: PASSA
```

**Interpretação:**
- Δχ² = χ²_ZFP - χ²_ΛCDM = -2.35 (favorece ZFP)
- Critério: Δχ² < 5.0 → modelo **não rejeitado**
- **CHAVE:** Resultado reportado sem evasão
- **0:** Critério definido ex-ante, sem ajustes post-hoc

### MCMC Output
```
H0 = 7.00000e+01 +1.50000e+00 -1.50000e+00
Omega_m = 3.00000e-01 +2.00000e-02 -2.00000e-02
m_phi = 1.00000e-42 +3.00000e-43 -3.00000e-43
```

**Interpretação:**
- H₀ = 70.0 ± 1.5 km/s/Mpc
- Ω_m = 0.300 ± 0.020
- m_φ = (1.00 ± 0.30) × 10⁻⁴² GeV
- Incertezas = 68% credible intervals

---

## 📊 Critérios de Veredito

### Critério de Refutabilidade (definido ex-ante):
```
SE Δχ² > 5.0 PARA QUALQUER PROBE:
  → Modelo REFUTADO (descartável)
SENÃO:
  → Modelo NÃO REJEITADO (explorável)
```

### Status Atual (dados mock):
| Probe | Δχ² | Status |
|-------|-----|--------|
| BAO | -2.35 | ✅ PASSA |
| SNe | -2.28 | ✅ PASSA |
| CMB | +4.20 | ⚠️ TENSÃO (esperada) |
| Conjugado | -4.64 | ✅ PASSA |

**Veredito:** Modelo **não rejeitado** (pendente dados reais)

---

## 🚀 Próximos Passos

### Fase 3a: Integração de Dados Reais
1. Substituir `data/bao_data.csv` com dados BOSS/DESI DR2
2. Substituir `data/sn_data.csv` com Pantheon+
3. Adicionar `data/cmb_planck.dat` (espectro TT)
4. Re-executar análise completa

### Fase 3b: Publicação
1. Executar modo `publication`
2. Gerar manuscrito LaTeX
3. Submeter a arXiv (astro-ph.CO)
4. Consultar `ARXIV_READY.md` para checklist completo

---

## 📞 Suporte

**Repositório:** https://github.com/brunoviniciusdepaularodrigues1-creator/zero-field-primordial

**Documentação:**
- `README.md` - Overview e filosofia
- `ARXIV_READY.md` - Roadmap de publicação
- `VEREDITO_FINAL.md` - Resumo de resultados
- `EXECUTION_GUIDE.md` - Este arquivo

**Issues:** Abra uma issue no GitHub para reportar problemas ou sugestões

---

## ✅ Checklist de Validação

Antes de considerar análise completa:

- [ ] Todas dependências instaladas (`pip list`)
- [ ] Dados presentes em `data/` (bao_data.csv, sn_data.csv)
- [ ] Quick mode executa sem erros
- [ ] Full mode completa com todos outputs
- [ ] Plots gerados e visualizáveis
- [ ] Critério de refutabilidade compreendido
- [ ] CHAVE + 0 verificados em todos outputs

---

**Versão:** 1.0 (2026-02-09 18:00 BRT)
**Mantido por:** Bruno Vinicius de Paulo Rodrigues
**Licença:** MIT

> "Executar ciência com honestidade é mais importante que executar ciência com sucesso."
> 
> — Princípio 0
