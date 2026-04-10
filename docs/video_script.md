# MatadorAudit -- Competition Video Script

**Duration:** 3:30 -- 4:00
**Presenters:** Ido Cohen & Zach Bar
**Format:** Screen-recorded demo with voiceover

---

## 1. OPENING HOOK (0:00 -- 0:15)

[SCREEN: Black screen fading into a bold stat -- "Universities deploy 40+ AI systems that affect student outcomes. Most have never been audited for bias."]

**IDO:** "What if the AI deciding your financial aid package was quietly discriminating against you -- and nobody even knew?"

[SCREEN: Quick montage of university AI touchpoints -- course recommendation screens, admissions portals, plagiarism detection tools]

---

## 2. PROBLEM STATEMENT (0:15 -- 0:45)

[SCREEN: Split view -- left side shows a generic AI admissions dashboard, right side shows a bar chart with stark demographic gaps in approval rates]

**ZACH:** "Universities are rolling out AI everywhere -- course recommendations, admissions scoring, financial aid decisions, even plagiarism detection. But here is the problem: these systems can carry hidden biases that disproportionately affect students of color, first-generation students, and Pell-eligible students."

[SCREEN: Animated graphic -- "zip code" morphing into a heat map overlaid with racial demographics, illustrating proxy discrimination]

**IDO:** "And it is not always obvious. A model that uses zip code as a feature might look neutral on the surface -- but zip code is a proxy for race. That is proxy discrimination, and it is almost invisible without the right tools."

---

## 3. CSUN CONTEXT (0:45 -- 1:15)

[SCREEN: CSUN campus aerial shot or logo, with text overlay -- "61% Hispanic | 56% Pell-eligible | 45% First-gen"]

**ZACH:** "This is not an abstract problem. Right here at CSUN -- a federally recognized Hispanic-Serving Institution -- 61 percent of our students are Hispanic, more than half qualify for Pell grants, and nearly half are the first in their families to attend college. If biased AI gets deployed at CSUN, our students are the ones who get hurt."

[SCREEN: Simple animated diagram showing how a biased course-recommendation system could steer underrepresented students away from high-value courses]

**IDO:** "We built MatadorAudit because the students who need the most support should not be the ones harmed by the systems meant to help them."

---

## 4. SOLUTION DEMO WALKTHROUGH (1:15 -- 2:45)

### Step 1 -- Upload (1:15 -- 1:35)

[SCREEN: MatadorAudit Streamlit dashboard -- the Upload & Analyze page. Cursor drags a CSV file into the upload area.]

**ZACH:** "MatadorAudit is designed for non-technical administrators. You upload a dataset -- say, course recommendation outcomes -- and the tool does the rest."

[SCREEN: The dataset preview loads showing columns like student_id, ethnicity, pell_status, gpa, recommendation_score, admitted]

### Step 2 -- Automated Fairness Analysis (1:35 -- 2:00)

[SCREEN: Dashboard populates with fairness metrics -- Demographic Parity, Equalized Odds, Disparate Impact Ratio. Interactive Plotly bar charts show metric breakdowns by demographic group. Red/yellow/green risk indicators light up.]

**IDO:** "Instantly, you see the numbers that matter. Demographic parity, equalized odds, disparate impact ratio -- all calculated automatically using Fairlearn and AIF360. Red means there is a problem. Green means the system is performing fairly across groups."

[SCREEN: Hover over a red-flagged metric to show the tooltip with the exact disparity percentage]

### Step 3 -- Proxy Detection (2:00 -- 2:15)

[SCREEN: Navigate to the Proxy Detection tab. A correlation heatmap appears showing that zip_code has a 0.87 correlation with ethnicity.]

**ZACH:** "Our proxy detection engine flags when a seemingly neutral feature -- like zip code or high school name -- is acting as a stand-in for a protected attribute. This is the kind of hidden bias most tools completely miss."

### Step 4 -- Plain-English Report Card (2:15 -- 2:30)

[SCREEN: Navigate to the Fairness Report Card tab. A formatted report appears with sections like "Key Findings," "Risk Level: HIGH," and specific recommendations written in plain language.]

**IDO:** "And because not everyone reads statistical tables, we send all the findings to Claude AI, which generates a plain-English Fairness Report Card. An associate dean can read this and actually understand what needs to change."

### Step 5 -- What-If Simulator (2:30 -- 2:45)

[SCREEN: Navigate to the What-If Simulator. Sliders for decision thresholds and feature weights. As Zach adjusts a slider, the fairness metrics and charts update in real time.]

**ZACH:** "The What-If Simulator lets you ask: what happens if we change the admission threshold from 0.7 to 0.6? You see fairness metrics update live. Administrators can find the sweet spot between accuracy and equity before deploying anything."

---

## 5. ETHICS & RESPONSIBILITY (2:45 -- 3:05)

[SCREEN: A simple slide with three principles -- "Transparency. Accountability. Student-centered design." with the MatadorAudit logo]

**IDO:** "We want to be clear -- MatadorAudit does not make decisions. It shines a light on decisions that are already being made. The goal is transparency, not replacement. We believe every university deploying AI owes its students an audit, and that audit should be accessible to the people responsible for those students -- not locked behind a data science team."

---

## 6. FEASIBILITY & VISION (3:05 -- 3:25)

[SCREEN: Tech stack diagram -- Python, Streamlit, Fairlearn, AIF360, Claude API, Plotly -- with arrows showing the data flow from upload to report]

**ZACH:** "MatadorAudit runs today. It is built on proven open-source libraries -- Fairlearn, AIF360, Plotly -- with Claude handling the natural-language reporting. Our vision is to make this a standard tool that any CSU campus can deploy to audit their AI systems before they affect a single student."

[SCREEN: Map of the 23-campus CSU system with text: "23 campuses. 460,000+ students. One auditing standard."]

---

## 7. CLOSING (3:25 -- 3:40)

[SCREEN: MatadorAudit logo centered, with the tagline appearing below it]

**IDO:** "Fair AI is not optional. It is an obligation."

**ZACH:** "MatadorAudit. Audit the algorithm before it audits your students."

[SCREEN: Fade to team credit -- "Built by Ido Cohen & Zach Bar for CSUN AI Jam 2026" with a QR code linking to the live demo]

---

## Production Notes

- **Total runtime target:** 3:35
- **Recording tool:** OBS or Loom for screen + voiceover
- **Demo data:** Use the included synthetic dataset to avoid any real student data
- **Tip:** Rehearse the What-If Simulator section -- live slider interaction is the most visually compelling moment and directly demonstrates Innovation (30pts)
- **Rubric alignment:**
  - Impact (30pts): CSUN demographics, proxy discrimination, plain-English reports for non-technical users
  - Innovation (30pts): Proxy detection, What-If Simulator with live metric updates, Claude-generated report cards
  - Feasibility (20pts): Running today, open-source stack, CSU-wide scalability
  - Presentation (20pts): Conversational tone, clear screen markers, strong hook and closing tagline
