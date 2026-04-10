# Graph Report - .  (2026-04-10)

## Corpus Check
- 5 files · ~11,400 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 69 nodes · 110 edges · 7 communities detected
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 10 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `FairnessEngine` - 13 edges
2. `ReportGenerator` - 8 edges
3. `main()` - 8 edges
4. `ProposalPDF` - 6 edges
5. `upload_page()` - 5 edges
6. `multi_audit_page()` - 5 edges
7. `main()` - 5 edges
8. `_render_detailed_charts()` - 4 edges
9. `report_page()` - 4 edges
10. `detect_demographic_cols()` - 4 edges

## Surprising Connections (you probably didn't know these)
- `MatadorAudit — AI-Powered Fairness Auditing Dashboard.` --uses--> `FairnessEngine`  [INFERRED]
  src/app.py → src/fairness_engine.py
- `Grid of cards showing risk level and key stat for each audit.` --uses--> `FairnessEngine`  [INFERRED]
  src/app.py → src/fairness_engine.py
- `Full charts for each audit.` --uses--> `FairnessEngine`  [INFERRED]
  src/app.py → src/fairness_engine.py
- `Side-by-side comparison table of all audits.` --uses--> `FairnessEngine`  [INFERRED]
  src/app.py → src/fairness_engine.py
- `Generate a PDF fairness report.` --uses--> `FairnessEngine`  [INFERRED]
  src/app.py → src/fairness_engine.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.15
Nodes (12): multi_audit_page(), MatadorAudit — AI-Powered Fairness Auditing Dashboard., Grid of cards showing risk level and key stat for each audit., Full charts for each audit., Side-by-side comparison table of all audits., Generate a PDF fairness report., _render_comparison_table(), _render_detailed_charts() (+4 more)

### Community 1 - "Community 1"
Cohesion: 0.19
Nodes (11): FPDF, main(), make_title_page(), parse_and_render(), ProposalPDF, Render a markdown table., Replace Unicode chars unsupported by latin-1 with ASCII equivalents., Write a line with bold spans handled via multi_cell fragments. (+3 more)

### Community 2 - "Community 2"
Cohesion: 0.22
Nodes (6): FairnessEngine, Return outcome rates per demographic group., Compute all fairness metrics., Max difference in positive outcome rate across groups., Gap in true positive rates across groups (simplified)., Ratio of lowest group rate to highest (four-fifths rule).

### Community 3 - "Community 3"
Cohesion: 0.35
Nodes (12): about_page(), detect_demographic_cols(), detect_outcome_cols(), export_page(), generate_pdf_report(), generate_template_report(), main(), proxy_page() (+4 more)

### Community 4 - "Community 4"
Cohesion: 0.43
Nodes (6): generate_student(), main(), pick_zip(), print_bias_summary(), Generate synthetic CSUN-like university data with known biases baked in., Print bias summary for ALL outcome columns.

### Community 5 - "Community 5"
Cohesion: 0.5
Nodes (4): _point_biserial(), proxy_detection(), Core fairness metrics engine.  Metrics implemented are based on established fair, Point-biserial correlation (pure numpy, no scipy needed).

### Community 6 - "Community 6"
Cohesion: 1.0
Nodes (1): Detect proxy variables correlated with a protected attribute.          For categ

## Knowledge Gaps
- **15 isolated node(s):** `Generate plain-English fairness reports using Claude API.`, `Generate a narrative fairness report from engine results.`, `Core fairness metrics engine.  Metrics implemented are based on established fair`, `Point-biserial correlation (pure numpy, no scipy needed).`, `Compute all fairness metrics.` (+10 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 6`** (1 nodes): `Detect proxy variables correlated with a protected attribute.          For categ`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `FairnessEngine` connect `Community 2` to `Community 0`, `Community 5`?**
  _High betweenness centrality (0.206) - this node is a cross-community bridge._
- **Why does `MatadorAudit — AI-Powered Fairness Auditing Dashboard.` connect `Community 0` to `Community 2`, `Community 3`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `FairnessEngine` (e.g. with `MatadorAudit — AI-Powered Fairness Auditing Dashboard.` and `Grid of cards showing risk level and key stat for each audit.`) actually correct?**
  _`FairnessEngine` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `ReportGenerator` (e.g. with `MatadorAudit — AI-Powered Fairness Auditing Dashboard.` and `Grid of cards showing risk level and key stat for each audit.`) actually correct?**
  _`ReportGenerator` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Generate plain-English fairness reports using Claude API.`, `Generate a narrative fairness report from engine results.`, `Core fairness metrics engine.  Metrics implemented are based on established fair` to the rest of the system?**
  _15 weakly-connected nodes found - possible documentation gaps or missing edges._