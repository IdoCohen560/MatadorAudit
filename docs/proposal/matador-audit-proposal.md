# MatadorAudit: AI-Powered Fairness Auditing for University Systems

**CSUN AI Jam 2026 — Competition Proposal**

**Team Members:**
- Ido Cohen (ID: 203866929)
- Zach Bar (ID: 202478542)

**Track:** AI & Ethics

---

## Executive Summary

California State University, Northridge is one of the most diverse universities in the nation. With a student body that is 61% Hispanic/Latino, 56% Pell Grant-eligible, and representative of over 100 languages spoken at home, CSUN holds the designation of a Hispanic-Serving Institution (HSI) — a responsibility, not just a label.

As CSUN and universities nationwide adopt AI-driven systems for course recommendations, admissions screening, financial aid allocation, and plagiarism detection, a critical question goes unanswered: **Are these systems treating all students fairly?**

MatadorAudit is an AI-powered fairness auditing toolkit that empowers non-technical university administrators to answer that question. Users upload a dataset or connect to an AI system's output, and MatadorAudit automatically detects demographic disparities, tests for proxy discrimination, and generates a plain-English **Fairness Report Card** with actionable recommendations. An interactive **What-If Simulator** lets users adjust decision thresholds and watch fairness metrics update in real time — turning opaque algorithmic decisions into transparent, accountable processes.

We are not theorizing about bias. We are building the tool to detect and measure it.

---

## 1. Problem Statement

### The Invisible Risk

Universities are rapidly deploying AI systems across critical decision points:

| System | Decision | Stakes |
|--------|----------|--------|
| **Course recommendation engines** | Which classes students see first | Shapes academic trajectories and time-to-degree |
| **Admissions screening tools** | Which applicants advance to review | Determines who gets access to education |
| **Financial aid allocation models** | How limited funds are distributed | Affects whether students can afford to stay enrolled |
| **Plagiarism detection (e.g., Turnitin)** | Who gets flagged for academic dishonesty | Disproportionate false positives harm non-native English speakers |

These systems are typically evaluated on **accuracy** — do they make correct predictions on average? But accuracy can mask severe disparities. A course recommendation engine that is 85% accurate overall might be 92% accurate for white students and only 71% accurate for Hispanic students. A financial aid model that optimizes for "predicted graduation rate" may systematically disadvantage first-generation college students whose data patterns differ from the training population.

### Why CSUN Specifically

CSUN's demographics make fairness auditing not optional but essential:

- **61% Hispanic/Latino** — the largest demographic group, yet historically underrepresented in the training data that commercial AI tools are built on
- **56% Pell Grant-eligible** — socioeconomic status is one of the strongest proxy variables for race, meaning income-based filtering can replicate racial discrimination
- **12% students with disabilities** — disability status intersects with every other demographic dimension
- **45% first-generation college students** — these students have thinner institutional data trails, which can bias predictive models against them

Without proactive auditing, CSUN risks allowing AI systems to quietly undermine the equity mission that defines the institution.

### The Gap

Existing fairness tools (Microsoft Fairlearn, IBM AIF360) are powerful but require Python programming expertise, statistical knowledge, and familiarity with fairness metrics like demographic parity, equalized odds, and disparate impact ratios. The people who need fairness auditing most — department chairs, financial aid directors, admissions officers — cannot use these tools.

**MatadorAudit bridges this gap.**

---

## 2. Solution Overview

### What MatadorAudit Does

MatadorAudit is a web-based dashboard that provides four core capabilities:

#### 2.1 Automated Fairness Analysis
Users upload a CSV dataset or connect to a system's output. MatadorAudit automatically:
- Detects demographic columns (race, gender, income bracket, disability status, etc.)
- Identifies the decision/outcome column
- Computes a comprehensive suite of fairness metrics across all demographic groups
- Flags statistically significant disparities

#### 2.2 Proxy Discrimination Detection
Many AI systems don't use race directly — but they use zip code, high school GPA weighting, or SAT scores that **correlate strongly with race**. MatadorAudit runs correlation analysis to detect when supposedly neutral variables are acting as proxies for protected characteristics. This is one of the most insidious forms of algorithmic bias and one of the hardest to detect without specialized tools.

#### 2.3 Plain-English Fairness Report Card
Powered by the Claude AI API, MatadorAudit transforms raw statistical output into a narrative report that any administrator can understand:

> **Finding:** Hispanic/Latino students are 2.3x more likely to be denied financial aid renewal than white students with equivalent GPAs. This disparity persists after controlling for credit hours and enrollment status.
>
> **Risk Level:** HIGH
>
> **Recommended Action:** Review the "predicted persistence" variable in the aid allocation model. Our proxy analysis shows this variable correlates 0.78 with zip code, which in turn correlates 0.71 with race/ethnicity in the CSUN student population.

No statistics PhD required.

#### 2.4 What-If Simulator
An interactive tool where administrators can:
- Adjust decision thresholds (e.g., "what if we lower the GPA cutoff from 3.0 to 2.8?")
- Toggle demographic weighting
- Watch fairness metrics update in real time across all groups
- Find the optimal balance point between accuracy and equity

This transforms fairness from a one-time audit into an ongoing design tool.

### Technical Architecture

```
┌─────────────────────────────────────────────────────┐
│                   MatadorAudit                       │
│                  Web Dashboard                       │
│              (Streamlit + Plotly)                     │
├─────────────┬──────────────┬────────────────────────┤
│  Upload &   │   Fairness   │    What-If             │
│  Connect    │   Engine     │    Simulator            │
│  Module     │              │                         │
├─────────────┼──────────────┼────────────────────────┤
│             │  Fairlearn   │    Claude API           │
│   CSV/API   │  + AIF360    │  (Report Generation)   │
│   Ingest    │  (Metrics &  │                         │
│             │  Mitigation) │  Microsoft Copilot     │
│             │              │  (Accessible Interface) │
├─────────────┴──────────────┴────────────────────────┤
│          Synthetic / Real University Data             │
└─────────────────────────────────────────────────────┘
```

### AI Integration Strategy

| AI Tool | Role | Why This Tool |
|---------|------|---------------|
| **Anthropic Claude API** | Core intelligence — generates plain-English fairness reports from statistical output | Best-in-class at translating technical data into clear, nuanced narrative; handles sensitive topics with appropriate care |
| **Microsoft Copilot** | Secondary interface — administrators can ask follow-up questions about their report in natural language | Accessible via CSUN Microsoft 365 licenses; familiar interface for staff |
| **Google Gemini** | Alternative report generation pathway; data analysis assistance | Available to all CSUN users; strong at structured data interpretation |
| **Microsoft Fairlearn** | Fairness metric computation engine | Industry-standard open-source library; actively maintained by Microsoft Research |
| **IBM AIF360** | Bias mitigation algorithms and additional metrics | Complementary to Fairlearn; includes mitigation strategies not available elsewhere |

---

## 3. Impact Analysis

### Direct Impact at CSUN

**Immediate beneficiaries:**
- ~38,000 enrolled students whose outcomes are shaped by AI-driven systems
- Administrative staff in Admissions, Financial Aid, Academic Advising, and Student Affairs
- CSUN's Office of Equity and Diversity — gains a quantitative tool to complement qualitative equity work

**Specific use cases at CSUN:**
1. **Financial Aid Office** — Audit the predictive models used to allocate limited scholarship and aid funds. Ensure that "predicted persistence" scores don't penalize first-generation students.
2. **Admissions** — Test whether supplemental application screening tools produce equitable outcomes across racial, income, and disability demographics.
3. **Academic Advising** — Verify that course recommendation algorithms don't channel students of color away from STEM or high-demand majors.
4. **Academic Integrity** — Analyze Turnitin/plagiarism detection outputs for disparate false-positive rates among non-native English speakers and international students.

### Reach and Depth

MatadorAudit doesn't just identify problems — it provides a structured framework for remediation:

1. **Detection** → What disparities exist?
2. **Diagnosis** → Why do they exist? (proxy analysis)
3. **Simulation** → What happens if we change the thresholds?
4. **Documentation** → Generate an auditable fairness report for compliance and accreditation

This four-step framework makes fairness auditing a repeatable, institutionalized process rather than a one-off investigation.

### Long-Term Potential

- **CSU System-wide adoption:** 23 campuses, 460,000+ students. MatadorAudit could become the standard fairness auditing tool across the system.
- **Accreditation value:** WASC/WSCUC accreditation increasingly expects evidence of equity in institutional processes. MatadorAudit generates exactly this evidence.
- **Policy impact:** Audit results can inform university policy decisions about which AI tools to adopt, continue, or retire.
- **Open-source model:** Release MatadorAudit as open-source software so any university can deploy it, creating a national standard for AI fairness auditing in higher education.

---

## 4. Ethics & Responsible AI

### What We've Considered

**Data Privacy:**
- MatadorAudit can operate entirely on synthetic or de-identified data
- No student PII is required for the auditing process — only aggregate demographic categories and outcomes
- All data processing happens locally or in CSUN-controlled infrastructure; no student data is sent to external AI APIs
- The Claude API receives only statistical summaries, never raw student records

**Limitations We Acknowledge:**
- Fairness metrics can conflict with each other — it is mathematically impossible to satisfy all fairness definitions simultaneously (Chouldechova, 2017). MatadorAudit presents multiple metrics and lets humans decide which trade-offs are acceptable.
- Intersectionality is hard to measure with small sample sizes. A Hispanic female student with a disability may face compounding biases that group-level metrics miss. We flag when subgroup sizes are too small for reliable analysis.
- A fairness audit is not a fairness guarantee. MatadorAudit detects measurable disparities but cannot catch all forms of bias, especially those embedded in the choice of what to measure.

**Avoiding Harm:**
- We do not recommend automated "debiasing" without human oversight. Every recommendation includes context about trade-offs.
- The What-If Simulator is explicitly labeled as exploratory — changes must go through institutional review before implementation.
- We include a "Confidence Level" indicator on all findings to prevent over-reliance on uncertain results.

**Inclusive Design:**
- Dashboard designed for accessibility (WCAG 2.1 AA compliance)
- Reports generated in plain English, not statistical jargon
- Supports multiple export formats for different stakeholder audiences

---

## 5. Feasibility & Implementation

### Technical Feasibility

All core components are mature, open-source, and free:

| Component | Status | Cost |
|-----------|--------|------|
| Python + Streamlit | Production-ready | Free |
| Microsoft Fairlearn | v0.10+, actively maintained | Free (MIT License) |
| IBM AIF360 | v0.6+, IBM-supported | Free (Apache 2.0) |
| Claude API | Production API | ~$0.01 per report (affordable at scale) |
| Plotly | Production-ready | Free |

**We have a working prototype.** The demo accompanying this proposal is functional — it processes real (synthetic) data and generates real fairness reports. This is not a concept; it is software.

### Implementation Timeline

| Phase | Timeline | Deliverable |
|-------|----------|-------------|
| **Phase 1: Pilot** | Summer 2026 | Deploy with CSUN Financial Aid Office for one audit cycle |
| **Phase 2: Expand** | Fall 2026 | Add Admissions and Academic Advising; refine based on Phase 1 feedback |
| **Phase 3: Institutionalize** | Spring 2027 | Integrate into CSUN's annual equity review process |
| **Phase 4: Scale** | 2027-2028 | Package for other CSU campuses; publish as open-source |

### Resource Requirements

- **Computing:** Runs on any standard university workstation or CSUN cloud infrastructure
- **Personnel:** One technical administrator for deployment and maintenance (could be a student worker or IT staff)
- **Budget:** < $500/year for Claude API usage at typical audit volumes
- **Training:** 30-minute onboarding session for administrators — the tool is designed to be self-explanatory

### Risks and Adaptability

| Risk | Mitigation |
|------|------------|
| AI API pricing changes | Core fairness metrics work without any API; Claude is only for report generation |
| Resistance from departments whose tools show bias | Frame as improvement opportunity, not blame; reports include positive findings too |
| Evolving fairness definitions | Modular metric system allows adding new fairness measures as the field advances |
| Data quality issues | Built-in data validation and quality checks before analysis begins |

---

## 6. Data Disclosure

All data used in this proposal and demonstration is **synthetic**. No real CSUN student data was accessed, uploaded, or shared with any AI platform. Our synthetic dataset is modeled on publicly available institutional data from:

- CSUN Institutional Research (csun.edu/counts/demographic.php)
- CSUN Fact Sheet (csun.edu/about/facts)
- IPEDS / NCES (nces.ed.gov/ipeds/)
- US Department of Education College Scorecard (collegescorecard.ed.gov)

Claude AI was used to assist with generating natural-language fairness reports. All fairness metrics are computed using our own implementation based on established fairness research.

---

## 7. Conclusion

CSUN has the most diverse student body in the CSU system. That diversity is a strength — but only if the AI systems CSUN deploys serve all students equitably. Right now, there is no systematic way to verify that they do.

MatadorAudit changes that. It takes the powerful but inaccessible tools of algorithmic fairness research and puts them in the hands of the administrators who make decisions every day. It doesn't just detect bias — it explains it in plain English, shows what's causing it, and lets users explore what fixing it would look like.

We built this because we believe fairness shouldn't require a computer science degree to verify. And because at a university that serves the students CSUN serves, getting this right isn't optional.

**MatadorAudit: Because every Matador deserves a fair shot.**

---

## References

- Chouldechova, A. (2017). Fair prediction with disparate impact: A study of bias in recidivism prediction instruments. *Big Data, 5*(2), 153-163.
- Bellamy, R.K.E., et al. (2019). AI Fairness 360: An extensible toolkit for detecting and mitigating algorithmic bias. *IBM Journal of Research and Development, 63*(4/5).
- Bird, S., et al. (2020). Fairlearn: A toolkit for assessing and improving fairness in AI. *Microsoft Research Technical Report MSR-TR-2020-32*.
- CSUN Office of Institutional Research (2025). CSUN Student Demographics Dashboard.
- U.S. Department of Education (2024). Hispanic-Serving Institutions Program.
