"""MatadorAudit — AI-Powered Fairness Auditing Dashboard."""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fairness_engine import FairnessEngine
from report_generator import ReportGenerator

st.set_page_config(
    page_title="MatadorAudit",
    page_icon="🎯",
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
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/b/b2/CSUN_Seal.svg/150px-CSUN_Seal.svg.png", width=80)
    st.sidebar.title("MatadorAudit")
    st.sidebar.markdown("AI-Powered Fairness Auditing")

    page = st.sidebar.radio("Navigate", [
        "📊 Upload & Analyze",
        "📋 Fairness Report Card",
        "🔗 Proxy Detection",
        "🎛️ What-If Simulator",
    ])

    # Data loading
    if 'df' not in st.session_state:
        st.session_state.df = None
        st.session_state.engine = None
        st.session_state.report = None

    if page == "📊 Upload & Analyze":
        upload_page()
    elif page == "📋 Fairness Report Card":
        report_page()
    elif page == "🔗 Proxy Detection":
        proxy_page()
    elif page == "🎛️ What-If Simulator":
        simulator_page()


def upload_page():
    st.title("📊 Upload & Analyze")
    st.markdown("Upload a dataset or use our synthetic CSUN demo data to begin a fairness audit.")

    col1, col2 = st.columns(2)

    with col1:
        uploaded = st.file_uploader("Upload CSV", type=['csv'])
        if uploaded:
            st.session_state.df = pd.read_csv(uploaded)
            st.success(f"Loaded {len(st.session_state.df)} records")

    with col2:
        if st.button("🎓 Load CSUN Demo Data", use_container_width=True):
            st.session_state.df = pd.read_csv("data/csun_synthetic_students.csv")
            st.success(f"Loaded {len(st.session_state.df)} synthetic CSUN student records")

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

        if st.button("🔍 Run Fairness Analysis", type="primary", use_container_width=True):
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


def report_page():
    st.title("📋 Fairness Report Card")

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

    with c2:
        risk = risk_level(eo['gap'])
        st.markdown(f"### Equalized Odds Gap")
        st.markdown(f"## {eo['gap']:.3f}")
        st.markdown(f"**{risk} RISK**")

    with c3:
        di_risk = "LOW" if di['ratio'] >= 0.8 else ("MEDIUM" if di['ratio'] >= 0.6 else "HIGH")
        st.markdown(f"### Disparate Impact Ratio")
        st.markdown(f"## {di['ratio']:.3f}")
        st.markdown(f"**{di_risk} RISK**")

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
    st.title("🔗 Proxy Discrimination Detection")

    if st.session_state.df is None:
        st.warning("Load data first from the Upload & Analyze tab.")
        return

    df = st.session_state.df
    st.markdown("Detecting variables that correlate with protected demographics — potential proxy discrimination.")

    demo_cols = detect_demographic_cols(df)
    selected = st.selectbox("Check proxies for:", demo_cols, index=0)

    if st.button("🔍 Run Proxy Analysis", type="primary"):
        with st.spinner("Analyzing correlations..."):
            from fairness_engine import FairnessEngine
            correlations = FairnessEngine.proxy_detection(df, selected)

        if correlations:
            st.markdown("### Proxy Correlation Results")

            for item in correlations:
                col = item['column']
                corr = item['correlation']
                risk = "HIGH" if abs(corr) > 0.65 else ("MEDIUM" if abs(corr) > 0.45 else "LOW")
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
    st.title("🎛️ What-If Simulator")

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
    rates = engine.group_rates()

    best = rates.loc[rates['rate'].idxmax()]
    worst = rates.loc[rates['rate'].idxmin()]

    gap = best['rate'] - worst['rate']
    ratio = worst['rate'] / best['rate'] if best['rate'] > 0 else 0

    report = f"""
    <h3>Fairness Report Card</h3>
    <p><strong>Audit:</strong> {engine.outcome_col} by {engine.demo_col}</p>

    <h4>Key Finding</h4>
    <p><strong>{worst['group']}</strong> students have the lowest positive outcome rate at
    <strong>{worst['rate']:.1%}</strong>, compared to <strong>{best['rate']:.1%}</strong> for
    <strong>{best['group']}</strong> students — a gap of <strong>{gap:.1%}</strong>.</p>

    <h4>Disparate Impact Analysis</h4>
    <p>The disparate impact ratio is <strong>{di['ratio']:.3f}</strong>.
    {"This is below the 0.80 threshold established by the EEOC four-fifths rule, indicating potential discrimination." if di['ratio'] < 0.8 else "This meets the EEOC four-fifths rule threshold."}
    </p>

    <h4>Demographic Parity</h4>
    <p>The demographic parity gap is <strong>{dp['disparity']:.3f}</strong>.
    {"This indicates a significant disparity in outcomes across groups." if abs(dp['disparity']) > 0.1 else "This is within acceptable bounds."}</p>

    <h4>Recommendation</h4>
    <p>{"⚠️ <strong>Immediate review recommended.</strong> The disparity levels detected suggest systemic bias in this decision process. Use the What-If Simulator to explore threshold adjustments that could reduce the gap while maintaining decision quality." if di['ratio'] < 0.8 or abs(dp['disparity']) > 0.1 else "✅ Fairness metrics are within acceptable ranges. Continue monitoring on a regular schedule."}
    </p>
    """
    return report


if __name__ == '__main__':
    main()
