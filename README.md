# Zero Field Primordial

## Visão geral

Este repositório testa uma hipótese física específica: um **campo escalar real mínimo** como componente cosmológica em um universo FRW plano, avaliado contra dados observacionais BAO (Baryon Acoustic Oscillations).

**Herança conceitual**: Herda de [Ponte Zafira](https://github.com/brunoviniciusdepaularodrigues1-creator/ponte-zafira) apenas os princípios operacionais (Chave e 0), não conclusões filosóficas.

**Status**: Hipótese descartável. Tratada como teste científico rigoroso, do zero ao veredito, sem ajuste fino para salvar resultado.

---

## 🎯 Princípios operacionais: Chave e 0

### ✅ Chave (Coerência)
- Definição clara do modelo: Lagrangiana, assunções, condições iniciais explícitas
- Dados observacionais selecionados sem critério subjetivo (BOSS/eBOSS BAO, z ≈ 0.1–2.4)
- Métodos de comparação definidos a priori (χ² BAO, sem prior subjetivo)
- Linguagem direta: "passa", "falha", "parcial"—sem evasão

### ✅ 0 (Honestidade com falhas)
- Possibilidade real de descartar o modelo sem ajuste
- Logs de todas as falhas e decisões (veja `RESULTADO.md`)
- Se não passar em BAO, documentar por quê; não tentar "salvar" ajustando parâmetros
- Se passar em BAO, testar antes contra SNe/CMB antes de falar em "extensões"

---

## 📊 Resultados Atuais

| Probe | χ²_ΛCDM | χ²_ZFP | Δχ² | Status |
|-------|---------|--------|-----|--------|
| **BAO** | 16.24 | 13.89 | -2.35 | ✅ **PASSA** (favorecido) |
| **SNe** | — | — | — | ⏳ Em desenvolvimento |
| **CMB** | — | — | — | ⏳ Em desenvolvimento |

**Veredito:** Zero Field é **compatível** com dados BAO (Δχ² < 5)

---

## 🚀 Quick Start

### Instalação (1 minuto)
```bash
git clone https://github.com/brunoviniciusdepaularodrigues1-creator/zero-field-primordial.git
cd zero-field-primordial
pip install -r requirements.txt
```

### Execução (3 minutos)
```bash
# Pipeline completo integrado
python analysis/validation_notebook.py
```

**Saída:**
- `RESULTADO.md` — Veredito final
- `analysis/validation_plot.png` — 4 gráficos principais
- `analysis/validation_results.csv` — Tabela de resultados

Veja [EXECUTION_GUIDE.md](EXECUTION_GUIDE.md) para detalhes completos.

---

## 📂 Estrutura do repositório

```
zero-field-primordial/
├── README.md                    ← Este arquivo
├── RESULTADO.md                 ← Veredito final
├── EXECUTION_GUIDE.md           ← Guia de execução
├── ARXIV_READY.md              ← Roadmap de publicação
├── VEREDITO_FINAL.md           ← Síntese dos resultados
│
├── model/                       ← Documentação teórica
│   ├── lagrangiana.md          # ℒ = ½∂φ∂φ - ½m²φ²
│   ├── equacoes.md             # Klein-Gordon + Friedmann
│   ├── equacao_estado.md       # w_φ(z)
│   └── condicoes_iniciais.md   # φ_i, φ̇_i, justificativa
│
├── src/                         ← Código computacional
│   ├── run_zero_field.py       # ⭐ Solver ODE (Klein-Gordon)
│   ├── chi2_bao.py             # Análise χ² BAO
│   └── utils.py                # Funções auxiliares
│
├── analysis/                    ← Scripts de análise
│   ├── validation_notebook.py   # ⭐ Pipeline integrado
│   ├── chi2_bao.py             # χ² BAO detalhado
│   ├── parameter_sweep.py      # Otimização de parâmetros
│   └── plots/                  # Gráficos gerados
│
├── data/                        ← Dados observacionais
│   ├── bao_data.csv            # BOSS/eBOSS BAO (17 pontos)
│   └── README.md               # Proveniência dos dados
│
├── requirements.txt             ← Dependências Python
├── LICENSE                      ← MIT License
└── .gitignore
```

---

## 🔬 Modelo Físico

### Lagrangiana
$$\mathcal{L} = \frac{1}{2}\partial_\mu\phi\partial^\mu\phi - \frac{1}{2}m^2\phi^2$$

Onde:
- φ: campo escalar real massivo
- m: massa (parâmetro livre, ~10⁻⁴² GeV)
- Métrica de fundo: FRW plano (k=0)

### Equações de movimento
**Klein-Gordon em FRW:**
$$\ddot{\phi} + 3H\dot{\phi} + m^2\phi = 0$$

**Friedmann (plano, sem Λ):**
$$H^2 = \frac{8\pi G}{3}(\rho_m + \rho_r + \rho_\phi)$$

Onde:
$$\rho_\phi = \frac{1}{2}\dot{\phi}^2 + \frac{1}{2}m^2\phi^2$$
$$p_\phi = \frac{1}{2}\dot{\phi}^2 - \frac{1}{2}m^2\phi^2$$

### Observável: D_V/r_d
$$D_V(z) = \left[z \int_0^z \frac{dz'}{H(z')}\right]^{1/3}$$

Comparado com dados BAO em 17 redshifts (z = 0.106–2.33).

---

## 📈 Pipeline de Análise

### Etapa 1: Solver ODE (`src/run_zero_field.py`)
Integra numericamente Klein-Gordon + Friedmann desde z_i até z=0

**Entrada:** (m, φ_i, z_i)  
**Saída:** H(z), φ(z), ρ_φ(z), w_φ(z)

### Etapa 2: Cálculo de χ² BAO (`analysis/chi2_bao.py`)
Compara D_V/r_d do modelo com observações

**Critério ex-ante:** Δχ² < 5.0 → **PASSA**

### Etapa 3: Otimização (`analysis/parameter_sweep.py`)
Explora espaço de parâmetros via:
- Grid search (qualitativo)
- Differential Evolution (ótimo global)
- Análise de sensibilidade

### Etapa 4: Validação Integrada (`analysis/validation_notebook.py`) ⭐
Executa pipeline completo + visualizações + relatório

---

## 📊 Interpretando os Resultados

### Arquivo RESULTADO.md

```markdown
## Veredito: ✅ PASSA

| Modelo | χ² | χ²_red |
|--------|-----|--------|
| ΛCDM | 16.24 | 1.51 |
| Zero Field | 13.89 | 1.27 |

Δχ² = -2.35
Critério: Δχ² < 5.0 ✓
Status: COMPATÍVEL (favorecido)
```

**O que significa:**
- **Δχ² < 0**: Zero Field é **favorecido** por BAO
- **0 < Δχ² < 5**: Zero Field é **compatível** com BAO
- **Δχ² > 5**: Zero Field é **excluído** por BAO

### Gráficos (validation_plot.png)

1. **D_V/r_d vs z**: Dados observacionais + predições dos dois modelos
2. **Resíduos**: (obs - modelo) / σ em unidades de sigma
3. **Evolução φ(z)**: Campo escalar ao longo do tempo cósmico
4. **Equação de estado w_φ(z)**: Comportamento dinâmico do campo

---

## 🛠️ Customização

### Variar parâmetros do modelo

```python
# Em analysis/validation_notebook.py:

m_phi = 1e-42    # ← massa do campo (GeV)
phi_i = 0.1      # ← valor inicial (M_Pl)
z_i = 1000       # ← redshift inicial
```

### Executar scripts individuais

```bash
# Apenas solver ODE
python src/run_zero_field.py

# Apenas χ² BAO
python analysis/chi2_bao.py

# Apenas otimização
python analysis/parameter_sweep.py
```

---

## 📚 Documentação

- **Modelo teórico**: Veja `model/`
- **Guia de execução**: Veja [EXECUTION_GUIDE.md](EXECUTION_GUIDE.md)
- **Roadmap de publicação**: Veja [ARXIV_READY.md](ARXIV_READY.md)
- **Síntese final**: Veja [VEREDITO_FINAL.md](VEREDITO_FINAL.md)

---

## ⚠️ Limitações Explícitas

1. **Modelo é efetivo, não fundamental**
   - Sem pretensão de UV completion
   - Válido apenas para baixo redshift

2. **CMB não foi testado** (esperamos tensão)
   - Previsto para Fase 8

3. **SNe Type Ia não testado**
   - Previsto para Fase 7

4. **Parâmetros não esgotados**
   - MCMC completo em desenvolvimento

---

## 🎓 Pedagogical Value

Este projeto demonstra:
1. **Model-building discipline**: Assunções claras, refutabilidade explícita
2. **Numerical cosmology**: Solver ODE para Friedmann + Klein-Gordon
3. **Statistical inference**: χ² analysis, model comparison
4. **Scientific communication**: Documentação transparente, reprodutibilidade
5. **Honest science**: Reportar tensões, não esconder falhas

---

## 🚀 Próximos Passos

- [ ] **Fase 7**: Teste contra SNe Type Ia
- [ ] **Fase 8**: Teste contra CMB (Planck TT spectrum)
- [ ] **Fase 9**: MCMC completo (5000+ steps)
- [ ] **Fase 10**: Publicação em arXiv

---

## 📞 Contato & Colaboração

**Repositório:** https://github.com/brunoviniciusdepaularodrigues1-creator/zero-field-primordial

**Mantido por:** Bruno Vinicius de Paulo Rodrigues

**Licença:** MIT (2026)

---

## 📖 Referências

- **Ponte Zafira** (framework conceitual): https://github.com/brunoviniciusdepaularodrigues1-creator/ponte-zafira
- **Dados BAO**: BOSS (Baryon Oscillation Spectroscopic Survey), eBOSS
- **Teoria**: Friedmann equations, Klein-Gordon field, effective dark energy

---

> "Science advances by building hypotheses that can fail. Zero Field Primordial is designed to fail—explicitly, measurably, and honestly."
> 
> — Princípio CHAVE + 0

**Última atualização:** 2026-07-10  
**Status:** ✅ Operacional (Fase 6 Completa)
