# MatadorAudit -- Competition Video Script

**Duration:** 4:30 -- 5:00
**Presenters:** Ido Cohen & Zach Bar
**Format:** Screen-recorded demo with voiceover
**Track:** AI and Ethics

---

## 1. INTRODUCTION AND TRACK (0:00 -- 0:50)

[SCREEN: Black screen fading into the MatadorAudit logo, then the CSUN campus or CSUN seal]

**IDO:** "Hi, I am Ido Cohen, a Computer Science student here at CSUN."

**ZACH:** "And I am Zach Bar, also studying Computer Science at CSUN. Together, we built MatadorAudit."

**IDO:** "Our project falls under the AI and Ethics track. We are tackling a question that affects every student on this campus: are the AI systems CSUN uses treating all of us fairly?"

[SCREEN: Bold text on dark background -- "Universities deploy AI across admissions, financial aid, course recommendations, and plagiarism detection. Most have never been audited for bias."]

**ZACH:** "Right now, AI tools are making decisions about financial aid, admissions, course recommendations, plagiarism detection, scholarship allocation, academic advising, and more. These systems affect who gets funded, who gets admitted, and who gets flagged. But nobody is systematically checking whether those decisions are equitable across demographics."

[SCREEN: Quick montage -- Canvas dashboard, a PeopleSoft financial aid screen, Turnitin interface]

**IDO:** "As students at CSUN, we have seen firsthand how much these systems shape our experience. And as a federally recognized Hispanic-Serving Institution with 56.2 percent Hispanic and Latino students, 58 percent Pell-eligible, and 47 percent first-generation -- the stakes here are not theoretical. If AI bias exists in these systems, our classmates are the ones being harmed."

[SCREEN: CSUN campus photo with text overlay -- "56.2% Hispanic/Latino | 58% Pell-Eligible | 47% First-Generation | 38,000 Students"]

---

## 2. CONCEPT AND USE OF AI (0:50 -- 2:00)

[SCREEN: MatadorAudit Netlify landing page at matadoraudit.netlify.app]

**ZACH:** "MatadorAudit is an AI-powered fairness auditing toolkit designed for non-technical university administrators. A financial aid director or department chair can upload a dataset and get a complete fairness audit without writing a single line of code. Our landing page lives at matadoraudit.netlify.app, and the live interactive tool runs at matadoraudit.streamlit.app."

[SCREEN: Scroll through feature cards on the Netlify site, then open Streamlit app]

**IDO:** "The tool audits eight different scenarios across campus AI systems: financial aid allocation, STEM course recommendations, plagiarism detection, admissions screening, at-risk student flagging, scholarship allocation, academic advising quality, and gender parity. For each one, MatadorAudit computes established fairness metrics including demographic parity, equalized odds, and the disparate impact ratio based on the EEOC four-fifths rule."

[SCREEN: Navigate to the Methodology section, expand the Disparate Impact accordion]

**ZACH:** "A key feature is Proxy Discrimination Detection. Many AI systems do not use race directly, but they use zip code, high school ranking, or a predicted persistence score that correlates strongly with race. Our tool uses point-biserial correlation to flag these hidden proxies. In our synthetic CSUN data, the predicted persistence variable correlates 0.25 with race -- meaning the model effectively knows a student's ethnicity through a supposedly neutral variable."

[SCREEN: Show the proxy detection tab in the dashboard with correlation bars]

**IDO:** "We also built an AI Q&A Assistant directly into the tool. After running any audit, users can ask follow-up questions in plain English -- like 'Why is the gap so large for Hispanic students?' or 'What should I do next?' The assistant is powered by Groq, which is completely free with no setup required. Users can also connect Claude, ChatGPT, Gemini, or Ollama if they prefer."

[SCREEN: Show the AI Q&A chat panel with a sample question and response]

**ZACH:** "What makes this responsible is what it does not do. MatadorAudit does not make decisions. It does not automatically debias anything. It provides transparency and lets humans decide what trade-offs are acceptable. We also never send raw student data to any external API -- AI models receive only statistical summaries."

---

## 3. VISUAL REPRESENTATION (2:00 -- 3:10)

[SCREEN: Open the live Streamlit app at matadoraudit.streamlit.app]

**ZACH:** "Let me walk you through the actual tool. Here is our live Streamlit dashboard."

### Step 1 -- Upload

[SCREEN: Click "Load CSUN Demo Data" button. Dataset loads with 5,000 records.]

**ZACH:** "An administrator clicks Load CSUN Demo Data -- or uploads their own CSV. The tool instantly detects 7 demographic columns and 8 outcome columns."

### Step 2 -- Run Analysis

[SCREEN: Select race_ethnicity as demographic, financial_aid_approved as outcome, click Run Fairness Analysis. Metrics populate.]

**IDO:** "Select the demographic dimension and outcome to audit, then hit Run Fairness Analysis. In seconds, you see the demographic parity gap, equalized odds gap, and disparate impact ratio -- all color-coded by risk level. Every chart includes a plain-English explanation so non-technical users understand exactly what they are looking at."

[SCREEN: Show the bar chart of approval rates by race/ethnicity with plain-English caption beneath it]

### Step 3 -- Multi-Audit Dashboard

[SCREEN: Navigate to the Multi-Audit Dashboard, click "Run All 8 Audits"]

**ZACH:** "Our Multi-Audit Dashboard lets administrators run all eight audit scenarios at once. You can view results three ways: Summary Cards for a quick overview, Detailed Charts for deep analysis, or Comparison Table to see all metrics side by side. This is the fastest way to spot where bias lives across your institution."

[SCREEN: Toggle between Summary Cards, Detailed Charts, and Comparison Table views]

### Step 4 -- What-If Simulator

[SCREEN: Navigate to What-If Simulator, drag the threshold slider from 0.55 down to 0.40. Show metrics updating.]

**IDO:** "In the What-If Simulator, watch what happens when we lower the persistence threshold from 0.55 to 0.40. The approval rate increases, the parity gap shrinks, and the disparate impact ratio crosses above the 0.80 four-fifths rule line. Administrators can see exactly what fixing the bias would look like before making any changes."

### Step 5 -- AI Q&A and Next Steps

[SCREEN: Show AI Q&A Assistant with Groq selected, ask a follow-up question]

**ZACH:** "After any audit, the AI Q&A Assistant provides instant answers. And every page includes detailed next steps -- who to contact, what actions to take, and recommended timelines. This turns data into action."

[SCREEN: Show the Next Steps section with contact recommendations and timeline]

---

## 4. IMPLEMENTATION CONSIDERATIONS (3:10 -- 4:10)

[SCREEN: Show the Netlify site About section with the implementation timeline]

**IDO:** "MatadorAudit is built on proven open-source tools: Python, Streamlit, Plotly for the dashboard, and multiple AI providers for the Q&A assistant -- with Groq as the free default. The total annual cost is under 500 dollars."

[SCREEN: Show the feasibility section -- tech stack table and cost breakdown]

**ZACH:** "For integration with existing CSUN systems, administrators would export data from Canvas LMS or PeopleSoft as CSV files and upload them directly. No IT infrastructure changes needed. In a future phase, we envision direct API connectors to these systems for automated scheduled audits."

[SCREEN: Simple flow diagram -- "Canvas/PeopleSoft Export -> CSV Upload -> MatadorAudit Analysis -> Fairness Report -> Admin Action"]

**IDO:** "Our implementation timeline has four phases. Pilot with the CSUN Financial Aid Office in Summer 2026. Expand to Admissions and Academic Advising in Fall 2026. Integrate into the annual equity review process by Spring 2027. And ultimately, package this as an open-source tool for all 23 CSU campuses serving 460,000 students."

[SCREEN: Map of CSU system with "23 campuses. 460,000+ students. One auditing standard."]

**ZACH:** "The challenges we anticipate are institutional resistance from departments whose tools show bias, and the mathematical reality that fairness metrics can conflict with each other -- you cannot satisfy all definitions simultaneously. We address this by framing audits as improvement opportunities, not blame, and by presenting multiple metrics so humans choose the right trade-offs."

**IDO:** "To keep the tool responsible and adaptable over time, we designed it with modular fairness metrics that can be updated as the field evolves, WCAG 2.1 AA accessibility compliance, and clear labeling that the What-If Simulator is exploratory -- all changes require institutional review before implementation."

---

## 5. CLOSING (4:10 -- 4:35)

[SCREEN: MatadorAudit logo centered on dark background]

**IDO:** "All data used in this demo is synthetic. No real CSUN student data was accessed, uploaded, or shared with any AI platform. Our synthetic dataset is modeled on publicly available institutional data from CSUN Institutional Research, the CSUN Fact Sheet, IPEDS, and the US Department of Education College Scorecard."

[SCREEN: Data Sources section from the Netlify site]

**ZACH:** "We used AI to assist with generating natural-language fairness reports, powering the Q&A assistant, and helping structure our analysis framework. The fairness metrics themselves are computed using our own implementation based on established research by Dwork 2012, the EEOC 1978, Hardt 2016, Datta 2015, and Chouldechova 2017."

[SCREEN: Tagline fades in -- "Every Matador Deserves a Fair Shot"]

**IDO:** "Fair AI is not optional. It is an obligation."

**ZACH:** "MatadorAudit. Because every Matador deserves a fair shot."

[SCREEN: Fade to team credit -- "Built by Ido Cohen & Zach Bar | CSUN AI Jam 2026 | AI and Ethics Track" with URLs: matadoraudit.netlify.app | matadoraudit.streamlit.app]

---

## Production Notes

- **Total runtime target:** 4:35
- **Recording tool:** OBS or Loom for screen + voiceover
- **Demo data:** Use the included synthetic dataset -- no real student data
- **Key moments to rehearse:**
  - The Multi-Audit Dashboard running all 8 audits at once (most impressive feature)
  - The What-If Simulator slider interaction (most visually compelling)
  - The AI Q&A Assistant with Groq (demonstrates free, no-setup AI)
  - The proxy detection reveal (most intellectually striking)
- **Submission:** Upload final video through the designated Canvas assignment
- **Rubric alignment:**
  - Impact & Relevance (30pts): CSUN demographics (56.2%, 58%, 47%), 8 audit scenarios, lived experience framing, CSU-wide scalability
  - Innovation & Responsible AI (30pts): Multi-Audit Dashboard, AI Q&A with Groq, proxy detection, What-If Simulator, ethics-first design, no automated debiasing
  - Feasibility (20pts): Running today at matadoraudit.streamlit.app and matadoraudit.netlify.app, open-source stack, <$500/yr, phased rollout
  - Presentation (20pts): Individual intros, clear track statement, live demo walkthrough, data source disclosure, methodology citations, strong tagline
- **All four required sections covered:**
  1. Introduction and Track -- 0:00-0:50
  2. Concept and Use of AI -- 0:50-2:00
  3. Visual Representation -- 2:00-3:10
  4. Implementation Considerations -- 3:10-4:10
  5. Closing + disclosures -- 4:10-4:35
- **Data ethics compliance:**
  - No real CSUN data used
  - No copyrighted data
  - No data involving minors
  - No commercial promotion
  - Synthetic data disclosure stated in video
  - AI usage disclosure stated in video
