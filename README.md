<div align="center">

<img src="site/assets/csun-matador-audit-logo-dark.png" alt="MatadorAudit" width="380">

# MatadorAudit

**Fairness auditing that a non-technical university administrator can actually run** — upload a dataset, detect demographic disparities in AI-driven decisions, and read the results in plain English.

### [▶ Launch the full tool → matadoraudit.streamlit.app](https://matadoraudit.streamlit.app)

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat-square&logo=plotly&logoColor=white)
![Anthropic Claude](https://img.shields.io/badge/Claude-D97757?style=flat-square&logo=anthropic&logoColor=white)
![CSUN AI Jam 2026](https://img.shields.io/badge/CSUN%20AI%20Jam-2026-C8102E?style=flat-square)

</div>

---

MatadorAudit checks whether AI-driven university systems — admissions screening, financial aid, course recommendations, plagiarism detection — produce equitable outcomes across demographic groups. You upload a CSV (or pick a demo dataset), and the app computes established fairness metrics, flags where a group is disadvantaged, explains what each number means, and lets you simulate a policy change before you make it.

It was built for the **CSUN AI Jam 2026** by Ido Cohen & Zach Bar. The context is specific: CSUN is a Hispanic-Serving Institution — 56.2% Hispanic/Latino, 58% Pell-eligible, 47% first-generation — so any automated decision system used there has to be checked against those populations, not assumed fair.

## Live sites

- **Full tool** — [matadoraudit.streamlit.app](https://matadoraudit.streamlit.app) — the complete auditing platform
- **Landing page & chatbot** — [matadoraudit.netlify.app](https://matadoraudit.netlify.app) — overview dashboard with an embedded AI Q&A widget

## Features

- **Upload & analyze** — three demo datasets (Standard, High Bias, Fair) plus custom CSV upload
- **Multi-audit dashboard** — 8 scenarios (financial aid, STEM recommendations, plagiarism detection, admissions screening, at-risk flagging, scholarship allocation, academic advising, gender parity) across 3 view modes (summary cards, detailed charts, comparison table)
- **Fairness report card** — expandable metric explanations with academic/legal citations, risk levels, and a 6-step action plan
- **Proxy discrimination detection** — correlation analysis that surfaces neutral variables acting as stand-ins for protected attributes
- **What-If Simulator** — adjust a decision threshold and see the before/after fairness impact
- **AI Q&A assistant** — OpenRouter (free, built-in key) by default; optionally Claude, ChatGPT, Gemini, or Copilot with your own key
- **Export** — PDF and CSV report downloads

## How it works

The fairness math lives in [`src/fairness_engine.py`](src/fairness_engine.py) and is implemented in pure NumPy/pandas — no scipy, Fairlearn, or AIF360 dependency. The metrics map to published research and legal standards:

| Metric | Grounded in |
|--------|-------------|
| Demographic (statistical) parity | Dwork et al., *Fairness through Awareness*, ITCS 2012 |
| Disparate impact / four-fifths rule | EEOC Uniform Guidelines, 29 C.F.R. Part 1607; *Griggs v. Duke Power Co.* (1971) |
| Equalized odds | Hardt, Price & Srebro, *Equality of Opportunity in Supervised Learning*, NeurIPS 2016 |
| Proxy detection (point-biserial correlation) | Datta, Tschantz & Datta, PoPETs 2015 |

A disparate-impact ratio below 0.80 is flagged as prima facie adverse impact, matching the four-fifths rule.

## Quick start

```bash
pip install -r requirements.txt
streamlit run src/app.py
```

The AI Q&A assistant works out of the box via OpenRouter. Claude-generated reports are optional and require your own `ANTHROPIC_API_KEY`.

## Tech stack

| Component | Role |
|-----------|------|
| Python + Streamlit | Dashboard and interactions |
| NumPy / pandas fairness engine | Fairness metrics (no scipy / Fairlearn / AIF360) |
| Plotly | Charts and visualizations |
| OpenRouter (free tier) | Default AI Q&A (Nemotron, GPT-OSS, Gemma, Liquid) |
| Anthropic Claude | Optional AI report generation (user-provided key) |
| fpdf2 | PDF export |

## Project structure

```
MatadorAudit/
├── src/
│   ├── app.py                 # Streamlit dashboard
│   ├── fairness_engine.py     # Core fairness metrics (pure NumPy/pandas)
│   └── report_generator.py    # Optional Claude API reports
├── data/                      # Synthetic + fair + high-bias CSVs
├── site/                      # Netlify landing page & chatbot
├── docs/                      # Competition proposal + slide deck
├── scripts/                   # Synthetic data generation, PDF export
└── requirements.txt
```

## License

MIT.

<div align="center"><sub>CSUN AI Jam 2026 · Ido Cohen & Zach Bar</sub></div>
