# Zero Field Primordial

## Visão geral

Este repositório testa uma hipótese física específca: um campo escalar real mínimo como componente cosmológica em um universo FRW plano, avaliado contra dados observacionais BAO.

**Herança conceitual**: Herda de [Ponte Zafira](https://github.com/brunoviniciusdepaularodrigues1-creator/ponte-zafira) apenas os princípios operacionais (Chave e 0), não conclusões filosóficas ou proteção simbólica.

**Status**: Hipótese descartável. Tratada como teste científico rigoroso, do zero ao veredito, sem ajuste fino para salvar resultado.

---

## Princípios operacionais: Chave e 0

### Chave (Coerência)
- Definição clara do modelo: Lagrangiana, assunções, condições iniciais explícitas.
- Dados observacionais selecionados sem critério subjetivo (BOSS/eBOSS BAO, z ≈ 0.1–2.4).
- Métodos de comparação definidos a priori (χ² BAO, sem prior subjetivo).
- Linguagem direta: "passa", "falha", "parcial"—sem evasão.

### 0 (Honestidade com falhas)
- Possibilidade real de descartar o modelo sem ajuste.
- Logs de todas as falhas e decisões (veja `ZERO_LOGS/`).
- Se não passar em BAO, documentar por quê; não tentar "salvar" ajustando parâmetros.
- Se passar em BAO, testar antes contra SN/CMB antes de falar em "extensões".

---

## Estrutura do repositório

```
zero-field-primordial/
├── README.md                    (este arquivo)
├── RESULTADO.md                 (veredito final: PASSA / FALHA / PARCIAL)
├── DISCUSSÃO.md                 (análise pós-veredito, próximos passos)
│
├── model/
│   ├── lagrangiana.md           (definição matemática: φ, ℒ, assunções)
│   ├── equacoes.md              (Klein–Gordon, ρ_φ, p_φ em FRW)
│   ├── equacao_estado.md        (w_φ(z) analítico e numérico)
│   └── condicoes_iniciais.md    (φ_i, φ̇_i, justificativa física)
│
├── src/
│   ├── run_zero_field.py        (solver ODE: evolução de φ(z), H(z), Ω_φ(z))
│   ├── bao_likelihood.py         (cálculo de χ² BAO)
│   └── utils.py                 (funções auxiliares)
│
├── data/
│   ├── bao_data.csv             (dados observacionais BOSS/eBOSS)
│   └── README.md                (proveniência dos dados)
│
├── analysis/
│   ├── chi2_bao.py              (comparação χ² com ΛCDM)
│   ├── plots/                   (gráficos: φ(z), ρ_φ(z), χ²)
│   └── results.csv              (resultados numéricos)
│
├── ZERO_LOGS/
│   ├── fase_0.txt               (escopo: confirmado)
│   ├── fase_1.txt               (lagrangiana: validado)
│   ├── fase_2.txt               (equações: validado)
│   ├── fase_3.txt               (CI: confirmado)
│   ├── fase_4.txt               (evolução numérica: log)
│   ├── fase_5.txt               (BAO: dados carregados)
│   ├── fase_6.txt               (χ² BAO: resultado)
│   └── fase_7.txt               (veredito: PASSA / FALHA / PARCIAL)
│
└── .gitignore
```

---

## Pipeline: Do zero ao veredito

- [ ] FASE 0: Escopo travado
- [ ] FASE 1: Definição mínima do modelo
- [ ] FASE 2: Equações cosmológicas
- [ ] FASE 3: Condições iniciais honestas
- [ ] FASE 4: Evolução numérica
- [ ] FASE 5: Observáveis BAO
- [ ] FASE 6: Estatística (sem piedade)
- [ ] FASE 7: Veredito explícito
- [ ] FASE 8: Pós-veredito (só depois)

---

## Reproduzindo o resultado BAO

Para executar a análise e obter os resultados:

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Executar análise de chi-quadrado BAO
python analysis/chi2_bao.py
```

**Saída esperada:**
- Cálculo de $\chi^2$ para Zero Field Primordial contra dados BAO
- Comparação com ΛCDM baseline
- Resultado final em `RESULTADO.md`

**Dados utilizados:** `data/bao_data.csv` (17 pontos de redshift)

## Referência

- **Ponte Zafira** (base conceitual): [github.com/brunoviniciusdepaularodrigues1-creator/ponte-zafira](https://github.com/brunoviniciusdepaularodrigues1-creator/ponte-zafira)
- **BAO data** (BOSS/eBOSS): Veja `data/README.md`.
