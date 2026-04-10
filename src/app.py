"""MatadorAudit — AI-Powered Fairness Auditing Dashboard."""
import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Ensure src/ is on the path for imports
sys.path.insert(0, os.path.dirname(__file__))

from fairness_engine import FairnessEngine
from report_generator import ReportGenerator

# Resolve paths relative to the repo root (works locally and on Streamlit Cloud)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(ROOT_DIR, 'data')
LOGO_PATH = os.path.join(ROOT_DIR, 'site', 'assets', 'csun-matador-audit-logo.png')

st.set_page_config(
    page_title="MatadorAudit",
    page_icon=LOGO_PATH if os.path.isfile(LOGO_PATH) else "🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .metric-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .risk-high { color: #ef4444; font-weight: 900; }
    .risk-medium { color: #f59e0b; font-weight: 700; }
    .risk-low { color: #22c55e; font-weight: 600; }
    .report-box {
        background: rgba(255,255,255,0.03);
        border-left: 4px solid #CF0A2C;
        padding: 20px;
        border-radius: 0 8px 8px 0;
        margin: 12px 0;
    }
</style>
""", unsafe_allow_html=True)


def main():
    if os.path.isfile(LOGO_PATH):
        st.sidebar.image(LOGO_PATH, use_container_width=True)
    else:
        st.sidebar.title("MatadorAudit")
    st.sidebar.markdown("AI-Powered Fairness Auditing")

    page = st.sidebar.radio("Navigate", [
        "Upload & Analyze",
        "Multi-Audit Dashboard",
        "Fairness Report Card",
        "Proxy Detection",
        "What-If Simulator",
        "Export Report",
        "About",
    ])

    # Data loading
    if 'df' not in st.session_state:
        st.session_state.df = None
        st.session_state.engine = None
        st.session_state.report = None

    if page == "Upload & Analyze":
        upload_page()
    elif page == "Multi-Audit Dashboard":
        multi_audit_page()
    elif page == "Fairness Report Card":
        report_page()
    elif page == "Proxy Detection":
        proxy_page()
    elif page == "What-If Simulator":
        simulator_page()
    elif page == "Export Report":
        export_page()
    elif page == "About":
        about_page()


def upload_page():
    st.title("Upload & Analyze")
    st.markdown("Upload a dataset or use our synthetic CSUN demo data to begin a fairness audit.")

    col1, col2 = st.columns(2)

    with col1:
        uploaded = st.file_uploader("Upload CSV", type=['csv'])
        if uploaded:
            st.session_state.df = pd.read_csv(uploaded)
            st.success(f"Loaded {len(st.session_state.df)} records")

    with col2:
        if st.button("Load CSUN Demo Data", use_container_width=True):
            st.session_state.df = pd.read_csv(os.path.join(DATA_DIR, "csun_synthetic_students.csv"))
            st.success(f"Loaded {len(st.session_state.df)} synthetic CSUN student records")
        st.caption("Synthetic data modeled on publicly available CSUN institutional data. See About page for sources.")

    if st.session_state.df is not None:
        df = st.session_state.df
        st.markdown("---")
        st.subheader("Dataset Overview")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Records", f"{len(df):,}")
        c2.metric("Features", len(df.columns))
        c3.metric("Demographic Cols", len(detect_demographic_cols(df)))
        c4.metric("Outcome Cols", len(detect_outcome_cols(df)))

        # Auto-detect demographics
        demo_cols = detect_demographic_cols(df)
        outcome_cols = detect_outcome_cols(df)

        st.markdown("#### Detected Columns")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Demographic columns:**")
            for c in demo_cols:
                st.markdown(f"- `{c}`")
        with col_b:
            st.markdown("**Outcome/decision columns:**")
            for c in outcome_cols:
                st.markdown(f"- `{c}`")

        # Configure analysis
        st.markdown("---")
        st.subheader("Configure Analysis")

        selected_demo = st.selectbox("Primary demographic column", demo_cols, index=0)
        selected_outcome = st.selectbox("Outcome column to audit", outcome_cols, index=0)

        if st.button("Run Fairness Analysis", type="primary", use_container_width=True):
            with st.spinner("Computing fairness metrics..."):
                engine = FairnessEngine(df, selected_demo, selected_outcome)
                engine.compute_all()
                st.session_state.engine = engine
                st.session_state.selected_demo = selected_demo
                st.session_state.selected_outcome = selected_outcome

            st.success("Analysis complete! Navigate to the Report Card tab.")

            # Preview
            results = engine.results
            st.markdown("#### Quick Results")

            metric_cols = st.columns(3)
            dp = results['demographic_parity']
            eo = results['equalized_odds']
            di = results['disparate_impact']

            with metric_cols[0]:
                risk = risk_level(dp['disparity'])
                st.metric("Demographic Parity Gap", f"{dp['disparity']:.3f}")
                st.markdown(f"Risk: <span class='risk-{risk.lower()}'>{risk}</span>", unsafe_allow_html=True)

            with metric_cols[1]:
                risk = risk_level(eo['gap'])
                st.metric("Equalized Odds Gap", f"{eo['gap']:.3f}")
                st.markdown(f"Risk: <span class='risk-{risk.lower()}'>{risk}</span>", unsafe_allow_html=True)

            with metric_cols[2]:
                di_risk = "LOW" if di['ratio'] >= 0.8 else ("MEDIUM" if di['ratio'] >= 0.6 else "HIGH")
                st.metric("Disparate Impact Ratio", f"{di['ratio']:.3f}")
                st.markdown(f"Risk: <span class='risk-{di_risk.lower()}'>{di_risk}</span>", unsafe_allow_html=True)

            # Group breakdown chart
            st.markdown("#### Outcome Rates by Group")
            rates = engine.group_rates()
            fig = px.bar(
                rates, x='group', y='rate',
                color='rate',
                color_continuous_scale=['#ef4444', '#f59e0b', '#22c55e'],
                labels={'group': selected_demo, 'rate': 'Positive Outcome Rate'},
            )
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        with st.expander("Preview raw data"):
            st.dataframe(df.head(50))


def multi_audit_page():
    st.title("Multi-Audit Dashboard")
    st.markdown("Run all pre-configured fairness audits at once across multiple university systems.")

    if st.session_state.df is None:
        st.info("Load data first from the Upload & Analyze tab, or click below to use demo data.")
        if st.button("Load CSUN Demo Data and Run All Audits", type="primary"):
            st.session_state.df = pd.read_csv(os.path.join(DATA_DIR, "csun_synthetic_students.csv"))
        else:
            return

    df = st.session_state.df

    # Define all audit scenarios
    AUDITS = {}

    # Only add audits for columns that exist in the dataset
    if 'financial_aid_approved' in df.columns:
        AUDITS['Financial Aid Approval'] = {
            'demo': 'race_ethnicity', 'outcome': 'financial_aid_approved',
            'desc': 'Are students from all racial/ethnic backgrounds approved for financial aid at equal rates?',
            'color': '#CF0A2C',
        }
    if 'stem_rec_quality' in df.columns:
        df['_stem_good'] = df['stem_rec_quality'] >= 0.75
        AUDITS['STEM Recommendation Quality'] = {
            'demo': 'race_ethnicity', 'outcome': '_stem_good',
            'desc': 'Do all students receive equally high-quality STEM course recommendations?',
            'color': '#3b82f6',
        }
    if 'plagiarism_flagged' in df.columns:
        AUDITS['Plagiarism Detection'] = {
            'demo': 'race_ethnicity', 'outcome': 'plagiarism_flagged',
            'desc': 'Are some groups flagged for plagiarism at disproportionately higher rates?',
            'color': '#8b5cf6',
        }
    if 'admitted' in df.columns:
        AUDITS['Admissions Screening'] = {
            'demo': 'race_ethnicity', 'outcome': 'admitted',
            'desc': 'Do admissions screening tools produce equitable outcomes across demographics?',
            'color': '#22c55e',
        }
    if 'at_risk_flag' in df.columns:
        AUDITS['At-Risk Flagging'] = {
            'demo': 'race_ethnicity', 'outcome': 'at_risk_flag',
            'desc': 'Are "at-risk" prediction flags disproportionately applied to certain groups?',
            'color': '#f59e0b',
        }
    if 'scholarship_awarded' in df.columns:
        AUDITS['Scholarship Allocation'] = {
            'demo': 'race_ethnicity', 'outcome': 'scholarship_awarded',
            'desc': 'Is scholarship funding distributed equitably across racial/ethnic groups?',
            'color': '#06b6d4',
        }
    if 'competitive_program_rec' in df.columns:
        df['_comp_good'] = df['competitive_program_rec'] >= 0.70
        AUDITS['Advising: Competitive Programs'] = {
            'demo': 'race_ethnicity', 'outcome': '_comp_good',
            'desc': 'Are students from all backgrounds equally recommended for competitive programs?',
            'color': '#ec4899',
        }
    if 'financial_aid_approved' in df.columns and 'gender' in df.columns:
        AUDITS['Financial Aid by Gender'] = {
            'demo': 'gender', 'outcome': 'financial_aid_approved',
            'desc': 'Is financial aid approval equitable across gender identities?',
            'color': '#a855f7',
        }

    if not AUDITS:
        st.warning("No auditable outcome columns detected in this dataset.")
        return

    # View mode selector
    view = st.radio("View mode", ["Summary Cards", "Detailed Charts", "Comparison Table"],
                     horizontal=True)

    # Run all audits
    with st.spinner("Running all audits..."):
        audit_results = {}
        for name, config in AUDITS.items():
            engine = FairnessEngine(df, config['demo'], config['outcome'])
            engine.compute_all()
            audit_results[name] = {
                'engine': engine,
                'config': config,
                'dp': engine.results['demographic_parity']['disparity'],
                'di': engine.results['disparate_impact']['ratio'],
                'eo': engine.results['equalized_odds']['gap'],
                'worst': engine.group_rates().iloc[-1],
                'best': engine.group_rates().iloc[0],
            }

    if view == "Summary Cards":
        _render_summary_cards(audit_results)
    elif view == "Detailed Charts":
        _render_detailed_charts(audit_results)
    elif view == "Comparison Table":
        _render_comparison_table(audit_results)


def _render_summary_cards(audit_results):
    """Grid of cards showing risk level and key stat for each audit."""
    cols = st.columns(2)
    for i, (name, data) in enumerate(audit_results.items()):
        with cols[i % 2]:
            di = data['di']
            dp = data['dp']
            if di < 0.6 or dp > 0.15:
                risk, risk_color = "HIGH RISK", "#ef4444"
            elif di < 0.8 or dp > 0.08:
                risk, risk_color = "MEDIUM", "#f59e0b"
            else:
                risk, risk_color = "LOW RISK", "#22c55e"

            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);
                        border-left:4px solid {data['config']['color']};border-radius:12px;
                        padding:20px;margin-bottom:16px">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                    <strong style="font-size:16px">{name}</strong>
                    <span style="background:{risk_color}22;color:{risk_color};padding:3px 10px;
                                 border-radius:6px;font-size:12px;font-weight:800">{risk}</span>
                </div>
                <p style="color:#71717a;font-size:13px;margin-bottom:12px">{data['config']['desc']}</p>
                <div style="display:flex;gap:24px">
                    <div><span style="font-size:24px;font-weight:900;color:{risk_color}">{di:.3f}</span>
                         <br><span style="font-size:11px;color:#71717a">Disparate Impact</span></div>
                    <div><span style="font-size:24px;font-weight:900">{dp:.3f}</span>
                         <br><span style="font-size:11px;color:#71717a">Parity Gap</span></div>
                    <div><span style="font-size:14px;color:#71717a">Lowest: <strong style="color:#e4e4e7">{data['worst']['group']}</strong>
                         at {data['worst']['rate']:.1%}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)


def _render_detailed_charts(audit_results):
    """Full charts for each audit."""
    selected = st.selectbox("Select audit to view in detail",
                             list(audit_results.keys()))
    data = audit_results[selected]
    engine = data['engine']
    config = data['config']

    st.markdown(f"**{config['desc']}**")
    st.caption(f"Demographic dimension: `{config['demo']}` | Outcome: `{config['outcome']}`")

    # Metrics row
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Demographic Parity Gap", f"{data['dp']:.4f}")
        st.caption("Difference between highest and lowest group rates. >0.10 = concern.")
    with c2:
        st.metric("Equalized Odds Gap", f"{data['eo']:.4f}")
        st.caption("Gap in true positive rates across groups.")
    with c3:
        di_pass = "PASS" if data['di'] >= 0.8 else "FAIL"
        st.metric("Disparate Impact Ratio", f"{data['di']:.4f}")
        st.caption(f"EEOC four-fifths rule: {'Passing' if data['di'] >= 0.8 else 'Below 0.80 threshold'}.")

    # Bar chart
    rates = engine.group_rates()
    fig = px.bar(
        rates, x='group', y='rate',
        color='rate',
        color_continuous_scale=['#ef4444', '#f59e0b', '#22c55e'],
        labels={'group': config['demo'], 'rate': 'Positive Outcome Rate'},
        title=f'{selected} — Outcome Rate by {config["demo"]}'
    )
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        yaxis_tickformat='.0%',
        dragmode=False,
        xaxis=dict(fixedrange=True),
        yaxis=dict(fixedrange=True),
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # Report
    report = generate_template_report(engine)
    st.markdown(f"<div class='report-box'>{report}</div>", unsafe_allow_html=True)


def _render_comparison_table(audit_results):
    """Side-by-side comparison table of all audits."""
    rows = []
    for name, data in audit_results.items():
        di = data['di']
        dp = data['dp']
        if di < 0.6 or dp > 0.15:
            risk = "HIGH"
        elif di < 0.8 or dp > 0.08:
            risk = "MEDIUM"
        else:
            risk = "LOW"
        rows.append({
            'Audit': name,
            'Risk Level': risk,
            'Disparate Impact': f"{di:.4f}",
            '4/5 Rule': 'PASS' if di >= 0.8 else 'FAIL',
            'Parity Gap': f"{dp:.4f}",
            'Eq. Odds Gap': f"{data['eo']:.4f}",
            'Lowest Group': data['worst']['group'],
            'Lowest Rate': f"{data['worst']['rate']:.1%}",
            'Highest Rate': f"{data['best']['rate']:.1%}",
        })

    table_df = pd.DataFrame(rows)
    st.dataframe(table_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("**How to read this table:**")
    st.markdown("""
    - **Disparate Impact** below 0.80 fails the EEOC four-fifths rule
    - **Parity Gap** above 0.10 indicates significant disparity
    - **Risk Level** combines both metrics: HIGH = immediate review needed
    - **Lowest Group** shows which demographic group is most disadvantaged
    """)


def report_page():
    st.title("Fairness Report Card")

    if st.session_state.engine is None:
        st.warning("Run an analysis first from the Upload & Analyze tab.")
        return

    engine = st.session_state.engine
    results = engine.results

    # Header metrics
    c1, c2, c3 = st.columns(3)
    dp = results['demographic_parity']
    eo = results['equalized_odds']
    di = results['disparate_impact']

    with c1:
        risk = risk_level(dp['disparity'])
        st.markdown(f"### Demographic Parity")
        st.markdown(f"## {dp['disparity']:.3f}")
        st.markdown(f"**{risk} RISK**")
        st.caption("Gap between highest and lowest group outcome rates. >0.10 = concern.")

    with c2:
        risk = risk_level(eo['gap'])
        st.markdown(f"### Equalized Odds Gap")
        st.markdown(f"## {eo['gap']:.3f}")
        st.markdown(f"**{risk} RISK**")
        st.caption("Difference in true positive rates across groups.")

    with c3:
        di_risk = "LOW" if di['ratio'] >= 0.8 else ("MEDIUM" if di['ratio'] >= 0.6 else "HIGH")
        st.markdown(f"### Disparate Impact Ratio")
        st.markdown(f"## {di['ratio']:.3f}")
        st.markdown(f"**{di_risk} RISK**")
        st.caption("Ratio of lowest to highest group rate. <0.80 fails the EEOC four-fifths rule.")

    st.markdown("---")

    # AI Report
    st.subheader("AI-Generated Narrative Report")

    use_ai = st.checkbox("Generate AI report with Claude", value=False)
    if use_ai:
        api_key = st.text_input("Anthropic API Key", type="password")
        if api_key and st.button("Generate Report"):
            with st.spinner("Claude is analyzing your fairness data..."):
                gen = ReportGenerator(api_key)
                report = gen.generate(engine)
                st.session_state.report = report
            st.markdown(f"<div class='report-box'>{report}</div>", unsafe_allow_html=True)
    else:
        # Fallback: template-based report
        report = generate_template_report(engine)
        st.session_state.report = report
        st.markdown(f"<div class='report-box'>{report}</div>", unsafe_allow_html=True)

    # Group comparison chart
    st.markdown("---")
    st.subheader("Group Comparison")
    rates = engine.group_rates()
    fig = px.bar(
        rates, x='group', y='rate',
        color='rate',
        color_continuous_scale=['#ef4444', '#f59e0b', '#22c55e'],
        labels={'group': st.session_state.selected_demo, 'rate': 'Positive Outcome Rate'},
        title=f"Outcome rates by {st.session_state.selected_demo}"
    )
    fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)


def proxy_page():
    st.title("Proxy Discrimination Detection")

    if st.session_state.df is None:
        st.warning("Load data first from the Upload & Analyze tab.")
        return

    df = st.session_state.df
    st.markdown("Detecting variables that correlate with protected demographics — potential proxy discrimination.")

    demo_cols = detect_demographic_cols(df)
    selected = st.selectbox("Check proxies for:", demo_cols, index=0)

    if st.button("Run Proxy Analysis", type="primary"):
        with st.spinner("Analyzing correlations..."):
            from fairness_engine import FairnessEngine
            correlations = FairnessEngine.proxy_detection(df, selected)

        if correlations:
            st.markdown("### Proxy Correlation Results")

            for item in correlations:
                col = item['column']
                corr = item['correlation']
                risk = item.get('risk', "HIGH" if abs(corr) > 0.25 else ("MEDIUM" if abs(corr) > 0.15 else "LOW"))
                color = '#ef4444' if risk == 'HIGH' else ('#f59e0b' if risk == 'MEDIUM' else '#22c55e')

                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:16px;padding:12px;margin:8px 0;
                            background:rgba(255,255,255,0.03);border-radius:8px;
                            border-left:4px solid {color}">
                    <div style="min-width:200px;font-weight:600">{col}</div>
                    <div style="flex:1">
                        <div style="height:20px;background:rgba(255,255,255,0.05);border-radius:4px;overflow:hidden">
                            <div style="height:100%;width:{abs(corr)*100}%;background:{color};border-radius:4px"></div>
                        </div>
                    </div>
                    <div style="min-width:60px;text-align:right;font-weight:700;color:{color}">{corr:.3f}</div>
                    <div style="min-width:80px;text-align:center;font-size:12px;padding:2px 8px;
                                background:{color}22;color:{color};border-radius:4px;font-weight:700">{risk}</div>
                </div>
                """, unsafe_allow_html=True)

            # Next steps for proxy findings
            high_proxies = [c for c in correlations if c.get('risk') == 'HIGH']
            if high_proxies:
                st.markdown("---")
                st.markdown("### What to do about proxy variables")
                st.markdown(f"""
                **{len(high_proxies)} high-risk proxy variable(s) detected.** These variables
                strongly correlate with the protected attribute `{selected}`, meaning any AI system
                using them as inputs may be indirectly discriminating based on {selected}.

                **Recommended actions:**
                1. **Audit downstream systems** -- check if the flagged variables are used as inputs
                   in any AI model or decision rule. If so, those systems likely have disparate impact.
                2. **Test with and without** -- re-run the fairness analysis after removing each proxy
                   variable to measure its contribution to the overall disparity.
                3. **Consult Institutional Research** -- verify whether the correlations reflect real
                   structural factors (e.g., geographic segregation) or data artifacts.
                4. **Report to the Office of Equity and Diversity** -- proxy discrimination findings
                   should be shared with equity officers, especially for variables used in financial
                   aid, admissions, or academic integrity systems.
                """)

            # Heatmap
            st.markdown("### Correlation Heatmap")
            numeric_df = df.select_dtypes(include=['number', 'bool']).copy()
            # Encode the selected demographic
            if df[selected].dtype == 'object':
                numeric_df[selected + '_encoded'] = pd.Categorical(df[selected]).codes

            corr_matrix = numeric_df.corr()
            fig = px.imshow(
                corr_matrix,
                color_continuous_scale='RdBu_r',
                zmin=-1, zmax=1,
                title="Feature Correlation Matrix"
            )
            fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', height=500)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No significant proxy correlations detected.")


def simulator_page():
    st.title("What-If Simulator")

    if st.session_state.df is None or st.session_state.engine is None:
        st.warning("Run an analysis first from the Upload & Analyze tab.")
        return

    df = st.session_state.df
    engine = st.session_state.engine

    st.markdown("Adjust decision thresholds and watch fairness metrics update in real time.")

    # Only works for numeric outcome columns with a threshold
    outcome = st.session_state.selected_outcome
    demo = st.session_state.selected_demo

    # Find a numeric column that could serve as a threshold basis
    numeric_cols = [c for c in df.select_dtypes(include=['number']).columns
                    if c not in detect_demographic_cols(df)]

    if not numeric_cols:
        st.warning("No numeric columns available for threshold simulation.")
        return

    threshold_col = st.selectbox("Variable to threshold on:", numeric_cols,
                                  index=numeric_cols.index('predicted_persistence')
                                  if 'predicted_persistence' in numeric_cols else 0)

    col_min = float(df[threshold_col].min())
    col_max = float(df[threshold_col].max())
    col_mean = float(df[threshold_col].mean())

    threshold = st.slider(
        f"Decision threshold for `{threshold_col}`",
        min_value=col_min,
        max_value=col_max,
        value=col_mean,
        step=(col_max - col_min) / 100,
    )

    # Recompute with new threshold
    simulated_outcome = df[threshold_col] >= threshold
    sim_engine = FairnessEngine(df, demo, outcome)
    sim_engine.df['__sim_outcome'] = simulated_outcome
    sim_engine.outcome_col = '__sim_outcome'
    sim_engine.compute_all()

    orig = engine.results
    sim = sim_engine.results

    st.markdown("### Metric Comparison")
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        orig_rate = df[outcome].mean() if df[outcome].dtype == bool else (df[outcome] == True).mean()
        sim_rate = simulated_outcome.mean()
        delta = sim_rate - orig_rate
        st.metric("Approval Rate", f"{sim_rate:.1%}", f"{delta:+.1%}")

    with c2:
        orig_dp = orig['demographic_parity']['disparity']
        sim_dp = sim['demographic_parity']['disparity']
        st.metric("Dem. Parity Gap", f"{sim_dp:.3f}", f"{sim_dp - orig_dp:+.3f}",
                  delta_color="inverse")

    with c3:
        orig_eo = orig['equalized_odds']['gap']
        sim_eo = sim['equalized_odds']['gap']
        st.metric("Eq. Odds Gap", f"{sim_eo:.3f}", f"{sim_eo - orig_eo:+.3f}",
                  delta_color="inverse")

    with c4:
        orig_di = orig['disparate_impact']['ratio']
        sim_di = sim['disparate_impact']['ratio']
        st.metric("Disparate Impact", f"{sim_di:.3f}", f"{sim_di - orig_di:+.3f}")

    # Side-by-side group rates
    st.markdown("### Group Outcome Rates — Before vs After")
    orig_rates = engine.group_rates()
    sim_rates = sim_engine.group_rates()

    orig_rates['scenario'] = 'Original'
    sim_rates['scenario'] = f'Threshold = {threshold:.3f}'
    combined = pd.concat([orig_rates, sim_rates])

    fig = px.bar(
        combined, x='group', y='rate', color='scenario',
        barmode='group',
        color_discrete_sequence=['#666', '#CF0A2C'],
        labels={'group': demo, 'rate': 'Positive Outcome Rate'},
    )
    fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)


# --- Helpers ---

def detect_demographic_cols(df):
    demo_keywords = ['race', 'ethnicity', 'gender', 'sex', 'disability', 'first_gen',
                     'pell', 'income', 'age_group', 'veteran']
    return [c for c in df.columns if any(k in c.lower() for k in demo_keywords)]


def detect_outcome_cols(df):
    outcome_keywords = ['approved', 'admitted', 'flagged', 'decision', 'outcome',
                        'accepted', 'denied', 'selected', 'recommended', 'score', 'quality']
    return [c for c in df.columns if any(k in c.lower() for k in outcome_keywords)]


def risk_level(disparity):
    if abs(disparity) > 0.15:
        return "HIGH"
    elif abs(disparity) > 0.08:
        return "MEDIUM"
    return "LOW"


def generate_template_report(engine):
    r = engine.results
    dp = r['demographic_parity']
    di = r['disparate_impact']
    eo = r['equalized_odds']
    rates = engine.group_rates()

    best = rates.loc[rates['rate'].idxmax()]
    worst = rates.loc[rates['rate'].idxmin()]

    gap = best['rate'] - worst['rate']
    is_high_risk = di['ratio'] < 0.8 or abs(dp['disparity']) > 0.1

    # Determine overall risk
    if di['ratio'] < 0.6 or abs(dp['disparity']) > 0.2:
        overall_risk = "CRITICAL"
        risk_color = "#ef4444"
    elif is_high_risk:
        overall_risk = "HIGH"
        risk_color = "#ef4444"
    elif di['ratio'] < 0.9 or abs(dp['disparity']) > 0.05:
        overall_risk = "MEDIUM"
        risk_color = "#f59e0b"
    else:
        overall_risk = "LOW"
        risk_color = "#22c55e"

    report = f"""
    <h3>Fairness Report Card</h3>
    <p><strong>Audit:</strong> {engine.outcome_col} by {engine.demo_col}<br>
    <strong>Records analyzed:</strong> {len(engine.df):,}<br>
    <strong>Overall risk level:</strong> <span style="color:{risk_color};font-weight:900">{overall_risk}</span></p>

    <hr style="border-color:rgba(255,255,255,0.1);margin:16px 0">

    <h4>What the numbers mean</h4>

    <p><strong>Demographic Parity Gap: {dp['disparity']:.3f}</strong><br>
    This measures the difference in positive outcome rates between the best- and worst-performing
    demographic groups. A gap of 0 means all groups have identical rates.
    {"Your gap of " + f"{dp['disparity']:.3f}" + " exceeds the 0.10 threshold, meaning there is a statistically meaningful difference in how groups are treated." if abs(dp['disparity']) > 0.1 else "Your gap is within acceptable bounds."}</p>

    <p><strong>Disparate Impact Ratio: {di['ratio']:.3f}</strong><br>
    This is the ratio of the lowest group's rate to the highest group's rate, based on the
    EEOC "four-fifths rule" (Uniform Guidelines on Employee Selection Procedures, 1978).
    Under Title VII of the Civil Rights Act, a ratio below 0.80 is considered evidence of
    potential adverse impact.
    {"<strong style='color:#ef4444'>Your ratio of " + f"{di['ratio']:.3f}" + " is below the 0.80 threshold.</strong>" if di['ratio'] < 0.8 else "<strong style='color:#22c55e'>Your ratio meets the legal threshold.</strong>"}</p>

    <p><strong>Equalized Odds Gap: {eo['gap']:.3f}</strong><br>
    This measures whether the system performs equally well across groups, not just on average.
    A system can be accurate overall but still have very different error rates for different
    demographics.</p>

    <hr style="border-color:rgba(255,255,255,0.1);margin:16px 0">

    <h4>Key Finding</h4>
    <p><strong>{worst['group']}</strong> students have the lowest positive outcome rate at
    <strong>{worst['rate']:.1%}</strong>, compared to <strong>{best['rate']:.1%}</strong> for
    <strong>{best['group']}</strong> students — a gap of <strong>{gap:.1%}</strong>.</p>
    """

    if is_high_risk:
        report += f"""
    <hr style="border-color:rgba(255,255,255,0.1);margin:16px 0">

    <h4 style="color:#ef4444">Recommended Next Steps</h4>

    <p><strong>1. Escalate to the appropriate office</strong><br>
    Share this report with the department head or director responsible for the system being audited.
    If this involves financial aid, contact the <strong>Financial Aid Director</strong>.
    For admissions, contact the <strong>Director of Admissions</strong>.
    For academic systems, contact the <strong>Associate Dean</strong> of the relevant college.
    Include the specific metrics and group disparities documented above.</p>

    <p><strong>2. Convene a review committee</strong><br>
    Form a cross-functional team including:
    representatives from the <strong>Office of Equity and Diversity</strong>,
    the <strong>department that owns the system</strong>,
    <strong>Institutional Research</strong> for data validation,
    and <strong>IT/data science staff</strong> who maintain the system.
    Schedule a review meeting within 30 days.</p>

    <p><strong>3. Investigate root causes</strong><br>
    Use the <strong>Proxy Detection</strong> tab to identify which input variables may be
    driving the disparity. Common causes include:
    zip code or geographic data correlating with race,
    historical data reflecting past discrimination,
    and "predicted success" scores trained on biased outcomes.</p>

    <p><strong>4. Test alternative thresholds</strong><br>
    Use the <strong>What-If Simulator</strong> to explore whether adjusting decision thresholds
    can reduce the disparity while maintaining acceptable accuracy. Document the trade-offs
    between fairness and accuracy for each threshold setting.</p>

    <p><strong>5. Document and monitor</strong><br>
    Export this report as a PDF (use the Export Report tab) and file it as part of the
    department's equity review documentation. Schedule a follow-up audit in 90 days to
    measure whether interventions have improved outcomes. This documentation also supports
    WASC/WSCUC accreditation requirements around equity.</p>

    <p><strong>6. Consider external review</strong><br>
    For disparate impact ratios below 0.60, consider engaging the university's
    <strong>Office of General Counsel</strong> or an external fairness auditor to assess
    legal compliance under Title VII and applicable state regulations.</p>
    """
    else:
        report += f"""
    <hr style="border-color:rgba(255,255,255,0.1);margin:16px 0">

    <h4 style="color:#22c55e">Status: Within Acceptable Bounds</h4>

    <p><strong>Recommended next steps:</strong></p>

    <p><strong>1. Continue regular monitoring</strong><br>
    Schedule quarterly fairness audits to ensure metrics remain within acceptable ranges.
    Disparities can emerge gradually as student populations shift or systems are updated.</p>

    <p><strong>2. Document this baseline</strong><br>
    Export this report as a PDF and file it as your baseline measurement. Future audits
    should be compared against this baseline to detect any regression.</p>

    <p><strong>3. Expand audit coverage</strong><br>
    If this system passes, audit other university AI systems using the Multi-Audit Dashboard.
    A passing result here does not guarantee fairness in other systems.</p>
    """

    return report


def export_page():
    st.title("Export Fairness Report")

    if st.session_state.engine is None:
        st.warning("Run an analysis first from the Upload & Analyze tab.")
        return

    engine = st.session_state.engine
    results = engine.results
    rates = engine.group_rates()

    st.markdown("Download a PDF or CSV summary of your fairness audit.")

    # CSV export
    st.subheader("Group Rates (CSV)")
    csv_data = rates.to_csv(index=False)
    st.download_button("Download Group Rates CSV", csv_data, "fairness_group_rates.csv", "text/csv")

    # Full metrics summary
    st.subheader("Metrics Summary")
    summary = {
        'Metric': ['Demographic Parity Gap', 'Equalized Odds Gap', 'Disparate Impact Ratio',
                    'Passes Four-Fifths Rule', 'Highest Rate Group', 'Lowest Rate Group'],
        'Value': [
            f"{results['demographic_parity']['disparity']:.4f}",
            f"{results['equalized_odds']['gap']:.4f}",
            f"{results['disparate_impact']['ratio']:.4f}",
            str(results['disparate_impact'].get('passes_four_fifths', 'N/A')),
            results['demographic_parity']['max_group'],
            results['demographic_parity']['min_group'],
        ]
    }
    summary_df = pd.DataFrame(summary)
    st.dataframe(summary_df, use_container_width=True)
    st.download_button("Download Metrics CSV", summary_df.to_csv(index=False),
                       "fairness_metrics.csv", "text/csv")

    # PDF export
    st.subheader("PDF Report")
    if st.button("Generate PDF Report", type="primary"):
        with st.spinner("Generating PDF..."):
            pdf_bytes = generate_pdf_report(engine)
        st.download_button("Download PDF", pdf_bytes, "MatadorAudit_Report.pdf", "application/pdf")


def generate_pdf_report(engine):
    """Generate a PDF fairness report."""
    from fpdf import FPDF

    results = engine.results
    rates = engine.group_rates()
    best = rates.loc[rates['rate'].idxmax()]
    worst = rates.loc[rates['rate'].idxmin()]

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)

    # Title page
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 28)
    pdf.ln(60)
    pdf.cell(0, 15, 'MatadorAudit', ln=True, align='C')
    pdf.set_font('Helvetica', '', 16)
    pdf.cell(0, 10, 'Fairness Report Card', ln=True, align='C')
    pdf.ln(20)
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(0, 8, f'Audit: {engine.outcome_col} by {engine.demo_col}', ln=True, align='C')
    pdf.cell(0, 8, f'Records analyzed: {len(engine.df):,}', ln=True, align='C')
    pdf.cell(0, 8, 'Generated by MatadorAudit - CSUN AI Jam 2026', ln=True, align='C')

    # Metrics page
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 18)
    pdf.cell(0, 12, 'Fairness Metrics', ln=True)
    pdf.ln(5)
    pdf.set_font('Helvetica', '', 12)

    dp = results['demographic_parity']['disparity']
    eo = results['equalized_odds']['gap']
    di = results['disparate_impact']['ratio']

    metrics = [
        ('Demographic Parity Gap', f'{dp:.4f}', risk_level(dp)),
        ('Equalized Odds Gap', f'{eo:.4f}', risk_level(eo)),
        ('Disparate Impact Ratio', f'{di:.4f}',
         'LOW' if di >= 0.8 else ('MEDIUM' if di >= 0.6 else 'HIGH')),
    ]

    for name, val, risk in metrics:
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(90, 8, name)
        pdf.set_font('Helvetica', '', 12)
        pdf.cell(30, 8, val)
        pdf.cell(30, 8, f'[{risk} RISK]', ln=True)

    # Group rates
    pdf.ln(10)
    pdf.set_font('Helvetica', 'B', 18)
    pdf.cell(0, 12, 'Group Outcome Rates', ln=True)
    pdf.ln(5)

    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(80, 8, 'Group', border=1)
    pdf.cell(40, 8, 'Rate', border=1, ln=True)

    pdf.set_font('Helvetica', '', 11)
    for _, row in rates.iterrows():
        pdf.cell(80, 8, str(row['group']), border=1)
        pdf.cell(40, 8, f"{row['rate']:.1%}", border=1, ln=True)

    # Key finding
    pdf.ln(10)
    pdf.set_font('Helvetica', 'B', 18)
    pdf.cell(0, 12, 'Key Finding', ln=True)
    pdf.ln(5)
    pdf.set_font('Helvetica', '', 12)
    gap = best['rate'] - worst['rate']
    finding = (f"{worst['group']} students have the lowest positive outcome rate at "
               f"{worst['rate']:.1%}, compared to {best['rate']:.1%} for {best['group']} "
               f"students - a gap of {gap:.1%}.")
    pdf.multi_cell(0, 7, finding)

    if di < 0.8:
        pdf.ln(5)
        pdf.set_font('Helvetica', 'B', 12)
        pdf.multi_cell(0, 7, "WARNING: Disparate impact ratio is below the 0.80 threshold "
                       "established by the EEOC four-fifths rule. Immediate review recommended.")

    return bytes(pdf.output())


def about_page():
    st.title("About MatadorAudit")

    st.markdown("""
    ### AI-Powered Fairness Auditing for University Systems

    **MatadorAudit** empowers non-technical university administrators to audit AI-driven
    systems for demographic fairness — no coding or statistics expertise required.

    ---

    **Built for CSUN AI Jam 2026**

    | | |
    |---|---|
    | **Team** | Ido Cohen & Zach Bar |
    | **University** | California State University, Northridge |
    | **Track** | AI & Ethics |

    ---

    ### How It Works

    1. **Upload** a dataset or connect to a system's output
    2. **Analyze** — MatadorAudit auto-detects demographics and computes fairness metrics
    3. **Read** the plain-English Fairness Report Card
    4. **Explore** the What-If Simulator to find fairer thresholds
    5. **Export** a PDF report for stakeholders

    ### Technology

    | Component | Purpose |
    |-----------|---------|
    | **Microsoft Fairlearn** | Fairness metric computation |
    | **IBM AIF360** | Bias mitigation algorithms |
    | **Anthropic Claude API** | Plain-English report generation |
    | **Streamlit + Plotly** | Interactive dashboard |
    | **Microsoft Copilot / Google Gemini** | Follow-up Q&A for administrators |

    ### Data Sources

    | Source | Description |
    |--------|-------------|
    | [CSUN Institutional Research](https://www.csun.edu/counts/demographic.php) | Official student demographic breakdowns |
    | [CSUN Fact Sheet](https://www.csun.edu/about/facts) | Enrollment, HSI designation, Pell and first-gen rates |
    | [CSU System Data Center](https://www.calstate.edu/data-center) | CSU-wide graduation and retention data |
    | [US Dept of Education College Scorecard](https://collegescorecard.ed.gov/) | Federal completion, earnings, financial aid data |
    | [IPEDS (NCES)](https://nces.ed.gov/ipeds/) | National enrollment and graduation data |

    ### Methodology References

    Our fairness metrics are based on established academic research and legal standards:

    | Metric | Source |
    |--------|--------|
    | **Demographic Parity** | Dwork et al., "Fairness through Awareness," ITCS 2012 |
    | **Disparate Impact (Four-Fifths Rule)** | EEOC Uniform Guidelines, 29 C.F.R. Part 1607 (1978); *Griggs v. Duke Power Co.*, 401 U.S. 424 (1971) |
    | **Equalized Odds** | Hardt, Price & Srebro, "Equality of Opportunity in Supervised Learning," NeurIPS 2016 |
    | **Proxy Discrimination** | Datta, Tschantz & Datta, "Automated Experiments on Ad Privacy Settings," PoPETs 2015 |
    | **Impossibility Theorem** | Chouldechova, "Fair Prediction with Disparate Impact," *Big Data* 5(2), 2017 |

    ### Data Disclosure

    All data used in this tool is **synthetic**. No real CSUN student data was
    accessed, uploaded, or shared with any AI platform. Our synthetic dataset is
    modeled on publicly available institutional data from the sources listed above.

    Claude AI is used solely for generating natural-language fairness reports.
    No student records or personally identifiable information are sent to any
    external API. Only aggregate statistical summaries are transmitted.

    ### Why CSUN

    CSUN is a **Hispanic-Serving Institution** with one of the most diverse student
    bodies in the CSU system. With 56.2% Hispanic/Latino students, 58% Pell-eligible,
    and 47% first-generation, we have a responsibility to ensure AI tools serve
    all students equitably.

    ---

    *MatadorAudit: Because every Matador deserves a fair shot.*
    """)


if __name__ == '__main__':
    main()
