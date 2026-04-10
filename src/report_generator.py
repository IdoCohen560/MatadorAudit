"""Generate plain-English fairness reports using Claude API."""
import anthropic


class ReportGenerator:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate(self, engine) -> str:
        """Generate a narrative fairness report from engine results."""
        results = engine.results
        rates = engine.group_rates()

        prompt = f"""You are a fairness auditing expert writing a report for a non-technical university administrator at CSUN (California State University, Northridge), a Hispanic-Serving Institution.

Analyze these fairness audit results and write a clear, actionable Fairness Report Card in HTML format.

**Audit context:**
- Demographic dimension: {engine.demo_col}
- Outcome being audited: {engine.outcome_col}
- Total records analyzed: {len(engine.df)}

**Fairness Metrics:**
- Demographic Parity Gap: {results['demographic_parity']['disparity']:.4f}
  - Highest rate group: {results['demographic_parity']['max_group']}
  - Lowest rate group: {results['demographic_parity']['min_group']}
- Equalized Odds Gap: {results['equalized_odds']['gap']:.4f}
- Disparate Impact Ratio: {results['disparate_impact']['ratio']:.4f}
  - Passes four-fifths rule: {results['disparate_impact'].get('passes_four_fifths', 'N/A')}

**Group outcome rates:**
{rates.to_string(index=False)}

Write the report with these sections:
1. **Executive Summary** (2-3 sentences, plain English)
2. **Key Findings** (bullet points, specific numbers, name the groups affected)
3. **Risk Assessment** (HIGH/MEDIUM/LOW for each metric with brief explanation)
4. **Root Cause Hypotheses** (what might be causing the disparities)
5. **Recommended Actions** (specific, actionable steps the administrator can take)

Use HTML formatting. Be direct, specific, and avoid jargon. This report will be read by a financial aid director or department chair, not a data scientist."""

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        return message.content[0].text
