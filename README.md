# MatadorAudit

**AI-Powered Fairness Auditing for University Systems**

CSUN AI Jam 2026 | Ido Cohen & Zach Bar

---

MatadorAudit lets non-technical university administrators audit AI-driven systems for demographic fairness. Upload a dataset, get instant disparity detection, plain-English reports, and an interactive What-If Simulator.

## Why

CSUN is a Hispanic-Serving Institution — 61% Hispanic/Latino, 56% Pell-eligible, 45% first-generation. AI tools used in admissions, financial aid, course recommendations, and plagiarism detection must serve all students equitably. MatadorAudit makes that verifiable.

## Features

- **Automated Fairness Analysis** — demographic parity, equalized odds, disparate impact
- **Proxy Discrimination Detection** — catches hidden correlations (zip code → race)
- **AI-Generated Report Card** — Claude API translates stats into plain English
- **What-If Simulator** — adjust thresholds, watch fairness metrics update live
- **PDF Export** — downloadable reports for stakeholders

## Quick Start

```bash
pip install -r requirements.txt
streamlit run src/app.py
```

## Tech Stack

| Component | Role |
|-----------|------|
| Python + Streamlit | Dashboard |
| Microsoft Fairlearn | Fairness metrics |
| IBM AIF360 | Bias mitigation |
| Anthropic Claude API | Report generation |
| Plotly | Visualizations |

## Project Structure

```
MatadorAudit/
├── src/
│   ├── app.py                 # Streamlit dashboard
│   ├── fairness_engine.py     # Core fairness metrics
│   └── report_generator.py    # Claude API reports
├── data/
│   └── csun_synthetic_students.csv
├── docs/
│   ├── proposal/              # Competition proposal
│   └── visuals/               # Slide deck
├── scripts/
│   └── generate_synthetic_data.py
└── requirements.txt
```

## License

MIT
