import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import chi2_contingency
from pathlib import Path
import numpy as np

st.set_page_config(
    page_title="NorthPoint Marketing Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    body { background: #F8F9FA; }
    .block-container { padding: 1.5rem 2rem; }
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 18px 22px;
        border: 1px solid #E8E8E8;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        height: 110px;
    }
    .kpi-label { font-size: 12px; color: #8C8C8C; margin-bottom: 6px; font-weight: 500; letter-spacing: 0.03em; }
    .kpi-value { font-size: 28px; font-weight: 700; color: #111; line-height: 1.1; }
    .kpi-note { font-size: 11px; color: #8C8C8C; margin-top: 4px; }
    .kpi-green .kpi-value { color: #0A7540; }
    .kpi-red .kpi-value { color: #C0392B; }
    .kpi-amber .kpi-value { color: #B7791F; }
    .insight {
        background: #F0FBF6;
        border-left: 3px solid #27AE60;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        font-size: 13px;
        color: #1A5C35;
        margin: 10px 0;
        line-height: 1.6;
    }
    .warning {
        background: #FEF9EC;
        border-left: 3px solid #F39C12;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        font-size: 13px;
        color: #7D5A00;
        margin: 10px 0;
        line-height: 1.6;
    }
    .alert {
        background: #FDF2F2;
        border-left: 3px solid #C0392B;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        font-size: 13px;
        color: #7B1818;
        margin: 10px 0;
        line-height: 1.6;
    }
    .section-title {
        font-size: 16px;
        font-weight: 600;
        color: #111;
        margin: 20px 0 12px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #E8E8E8;
    }
    .tab-content { padding-top: 8px; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load():
    base = Path(__file__).parent
    customers = pd.read_csv(base / "customer-data.csv")
    campaigns = pd.read_csv(base / "campaign-data.csv")
    funnel    = pd.read_csv(base / "funnel-analysis.csv")
    cohort    = pd.read_csv(base / "cohort-retention.csv")
    clv       = pd.read_csv(base / "clv-model.csv")
    return customers, campaigns, funnel, cohort, clv

customers, campaigns, funnel, cohort, clv = load()

CHANNEL_COLORS = {
    "Paid Social":    "#3B82F6",
    "Organic Search": "#10B981",
    "Referral":       "#8B5CF6",
    "Email Campaign": "#F59E0B",
}

st.markdown("## NorthPoint Financial — Marketing Analytics")
st.markdown("**Internal performance dashboard** &nbsp;|&nbsp; January 2024 to June 2025 &nbsp;|&nbsp; 2,400 customers &nbsp;|&nbsp; 4 acquisition channels")
st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "  Acquisition Funnel  ",
    "  Cohort Retention  ",
    "  CLV and CAC Model  ",
    "  Campaign Performance  ",
    "  Executive Summary  ",
])

# ── TAB 1: ACQUISITION FUNNEL ─────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-title">Customer Acquisition Funnel by Channel</div>', unsafe_allow_html=True)
    st.markdown('<div class="alert"><strong>Key finding:</strong> Paid Social has the highest volume but a 0.88 LTV-to-CAC ratio — meaning the company spends more to acquire these customers than it earns back from them. Referral and Organic Search are the only channels where acquisition cost is justified by customer lifetime value.</div>', unsafe_allow_html=True)

    selected_channels = st.multiselect(
        "Filter by channel",
        options=funnel["Channel"].tolist(),
        default=funnel["Channel"].tolist(),
        key="funnel_filter"
    )
    filtered_funnel = funnel[funnel["Channel"].isin(selected_channels)]

    col1, col2, col3, col4 = st.columns(4)
    for i, (_, row) in enumerate(filtered_funnel.iterrows()):
        with [col1,col2,col3,col4][i % 4]:
            ratio = row["LTV to CAC Ratio"]
            card_class = "kpi-green" if ratio >= 2 else "kpi-amber" if ratio >= 1 else "kpi-red"
            st.markdown(f"""<div class="kpi-card {card_class}">
                <div class="kpi-label">{row['Channel']}</div>
                <div class="kpi-value">{ratio}x</div>
                <div class="kpi-note">LTV to CAC &nbsp;|&nbsp; ${row['Avg CAC CAD']} avg CAC</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("")
    col1, col2 = st.columns([1.4, 1])
    with col1:
        st.markdown('<div class="section-title">Funnel: Signup to Active at 90 Days</div>', unsafe_allow_html=True)
        stages = ["Total Signups", "Activated", "Active at Day 30", "Active at Day 90"]
        stage_cols = ["Total Signups", "Activated", "Active at Day 30", "Active at Day 90"]
        fig_funnel = go.Figure()
        for _, row in filtered_funnel.iterrows():
            fig_funnel.add_trace(go.Bar(
                name=row["Channel"],
                x=stages,
                y=[row[c] for c in stage_cols],
                marker_color=CHANNEL_COLORS.get(row["Channel"], "#888"),
            ))
        fig_funnel.update_layout(
            barmode="group", height=340, plot_bgcolor="white",
            yaxis=dict(title="Customers", gridcolor="#F1F1F1"),
            xaxis=dict(title=""),
            legend=dict(orientation="h", y=1.08),
            margin=dict(t=10, b=20),
        )
        st.plotly_chart(fig_funnel, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">90-Day Retention vs CAC</div>', unsafe_allow_html=True)
        fig_scatter = px.scatter(
            filtered_funnel,
            x="Avg CAC CAD",
            y="Day 90 Retention %",
            size="Total Signups",
            color="Channel",
            color_discrete_map=CHANNEL_COLORS,
            text="Channel",
            size_max=50,
        )
        fig_scatter.update_traces(textposition="top center", textfont_size=10)
        fig_scatter.update_layout(
            height=340, plot_bgcolor="white",
            xaxis=dict(title="Average CAC (CAD)", gridcolor="#F1F1F1"),
            yaxis=dict(title="Day 90 Retention %", gridcolor="#F1F1F1"),
            showlegend=False,
            margin=dict(t=10, b=20),
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown('<div class="section-title">Full Channel Comparison Table</div>', unsafe_allow_html=True)
    display_funnel = filtered_funnel[[
        "Channel","Total Signups","Activation Rate %","Day 30 Retention %",
        "Day 90 Retention %","Avg CAC CAD","Estimated 6M LTV CAD","LTV to CAC Ratio","CAC Justified by LTV?"
    ]].copy()
    st.dataframe(display_funnel, use_container_width=True, hide_index=True)

# ── TAB 2: COHORT RETENTION ───────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-title">Cohort Retention Heatmap</div>', unsafe_allow_html=True)
    st.markdown('<div class="insight">Each row is a monthly acquisition cohort. Each column shows the percentage of that cohort still active at that milestone. Darker green means better retention. Look for pale rows — those are the cohorts that churned fastest.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col2:
        metric = st.selectbox(
            "Retention milestone",
            ["Day 30 Retention %", "Day 60 Retention %", "Day 90 Retention %", "Day 180 Retention %"],
            index=2,
        )

    heat_cols = ["Day 30 Retention %", "Day 60 Retention %", "Day 90 Retention %", "Day 180 Retention %"]
    heat_data = cohort[["Cohort Month"] + heat_cols].set_index("Cohort Month")

    fig_heat = go.Figure(data=go.Heatmap(
        z=heat_data.values,
        x=[c.replace(" Retention %","").replace("Day ","D") for c in heat_cols],
        y=heat_data.index.tolist(),
        colorscale=[[0,"#FEF9EC"],[0.4,"#A8E6CF"],[0.7,"#27AE60"],[1,"#0A5C30"]],
        text=[[f"{v:.1f}%" for v in row] for row in heat_data.values],
        texttemplate="%{text}",
        textfont=dict(size=11),
        zmin=0, zmax=80,
        colorbar=dict(title="Retention %", ticksuffix="%"),
    ))
    fig_heat.update_layout(
        height=480,
        xaxis=dict(title="Days since signup"),
        yaxis=dict(title="Acquisition cohort", autorange="reversed"),
        margin=dict(t=10, b=20),
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Retention trend over time</div>', unsafe_allow_html=True)
        fig_trend = go.Figure()
        for col_name, color in zip(heat_cols, ["#3B82F6","#10B981","#8B5CF6","#F59E0B"]):
            fig_trend.add_trace(go.Scatter(
                x=cohort["Cohort Month"],
                y=cohort[col_name],
                name=col_name.replace(" Retention %",""),
                line=dict(color=color, width=2),
                mode="lines+markers",
            ))
        fig_trend.update_layout(
            height=300, plot_bgcolor="white",
            yaxis=dict(title="Retention %", gridcolor="#F1F1F1", ticksuffix="%"),
            xaxis=dict(title="", tickangle=45),
            legend=dict(orientation="h", y=1.1),
            margin=dict(t=10, b=60),
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Cohort size and average CAC</div>', unsafe_allow_html=True)
        fig_size = go.Figure()
        fig_size.add_trace(go.Bar(
            x=cohort["Cohort Month"], y=cohort["Total Customers"],
            name="Customers", marker_color="#3B82F6", opacity=0.7,
        ))
        fig_size.add_trace(go.Scatter(
            x=cohort["Cohort Month"], y=cohort["Avg CAC CAD"],
            name="Avg CAC", yaxis="y2",
            line=dict(color="#C0392B", width=2), mode="lines+markers",
        ))
        fig_size.update_layout(
            height=300, plot_bgcolor="white",
            yaxis=dict(title="Customers", gridcolor="#F1F1F1"),
            yaxis2=dict(title="Avg CAC CAD", overlaying="y", side="right"),
            xaxis=dict(title="", tickangle=45),
            legend=dict(orientation="h", y=1.1),
            margin=dict(t=10, b=60),
        )
        st.plotly_chart(fig_size, use_container_width=True)

# ── TAB 3: CLV AND CAC ────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-title">Customer Lifetime Value and CAC by Segment</div>', unsafe_allow_html=True)
    st.markdown('<div class="alert"><strong>Finding:</strong> Every customer segment is being over-acquired relative to their lifetime value. The actual average CAC exceeds the LTV-justified maximum for all three segments. This means the current acquisition spend is not sustainable without improving retention.</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    seg_colors = {"High Value":"#10B981","Medium Value":"#3B82F6","Low Value":"#F59E0B"}

    for i, (_, row) in enumerate(clv.iterrows()):
        with cols[i]:
            status = row["CAC vs Max Justified"]
            card_class = "kpi-green" if status=="Under" else "kpi-red"
            st.markdown(f"""<div class="kpi-card {card_class}">
                <div class="kpi-label">{row['Segment']}</div>
                <div class="kpi-value">${row['Estimated LTV CAD']:.0f}</div>
                <div class="kpi-note">Estimated LTV &nbsp;|&nbsp; {row['Customer Count']} customers</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">LTV vs Actual CAC vs Max Justified CAC</div>', unsafe_allow_html=True)
        fig_clv = go.Figure()
        fig_clv.add_trace(go.Bar(
            name="Estimated LTV", x=clv["Segment"],
            y=clv["Estimated LTV CAD"], marker_color="#10B981",
        ))
        fig_clv.add_trace(go.Bar(
            name="Actual Avg CAC", x=clv["Segment"],
            y=clv["Actual Avg CAC CAD"], marker_color="#C0392B",
        ))
        fig_clv.add_trace(go.Bar(
            name="Max Justified CAC", x=clv["Segment"],
            y=clv["Max Justified CAC CAD"], marker_color="#F59E0B",
        ))
        fig_clv.update_layout(
            barmode="group", height=340, plot_bgcolor="white",
            yaxis=dict(title="CAD", gridcolor="#F1F1F1"),
            xaxis=dict(title=""),
            legend=dict(orientation="h", y=1.1),
            margin=dict(t=10, b=20),
        )
        st.plotly_chart(fig_clv, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Profit per customer by segment</div>', unsafe_allow_html=True)
        clv_copy = clv.copy()
        clv_copy["Color"] = clv_copy["Profit per Customer CAD"].apply(
            lambda x: "#10B981" if x > 0 else "#C0392B"
        )
        fig_profit = go.Figure(go.Bar(
            x=clv_copy["Segment"],
            y=clv_copy["Profit per Customer CAD"],
            marker_color=clv_copy["Color"].tolist(),
            text=[f"${v:.0f}" for v in clv_copy["Profit per Customer CAD"]],
            textposition="outside",
        ))
        fig_profit.add_hline(y=0, line_dash="dot", line_color="#888")
        fig_profit.update_layout(
            height=340, plot_bgcolor="white",
            yaxis=dict(title="Profit per customer (CAD)", gridcolor="#F1F1F1"),
            xaxis=dict(title=""),
            margin=dict(t=10, b=20),
        )
        st.plotly_chart(fig_profit, use_container_width=True)

    st.markdown('<div class="section-title">Full CLV model table</div>', unsafe_allow_html=True)
    st.dataframe(clv, use_container_width=True, hide_index=True)

# ── TAB 4: CAMPAIGNS ──────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-title">Email Campaign Performance and A/B Test Results</div>', unsafe_allow_html=True)
    st.markdown('<div class="insight">In all three campaigns Subject Line B significantly outperformed Subject Line A. Personalised and benefit-forward subject lines consistently produced higher open rates, click rates, and revenue attribution. The difference is statistically significant in all cases.</div>', unsafe_allow_html=True)

    selected_campaign = st.selectbox(
        "Select campaign",
        campaigns["Campaign Name"].tolist(),
        key="campaign_select"
    )
    camp = campaigns[campaigns["Campaign Name"]==selected_campaign].iloc[0]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        lift = round(camp["Open Rate B %"] - camp["Open Rate A %"], 1)
        st.markdown(f"""<div class="kpi-card kpi-green">
            <div class="kpi-label">Open rate lift (B vs A)</div>
            <div class="kpi-value">+{lift}%</div>
            <div class="kpi-note">{camp['Open Rate A %']}% vs {camp['Open Rate B %']}%</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        click_lift = round(camp["Click Rate B %"] - camp["Click Rate A %"], 1)
        st.markdown(f"""<div class="kpi-card kpi-green">
            <div class="kpi-label">Click rate lift (B vs A)</div>
            <div class="kpi-value">+{click_lift}%</div>
            <div class="kpi-note">{camp['Click Rate A %']}% vs {camp['Click Rate B %']}%</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        rev_lift = round(camp["Revenue Attributed B CAD"] - camp["Revenue Attributed A CAD"])
        st.markdown(f"""<div class="kpi-card kpi-green">
            <div class="kpi-label">Revenue lift from B</div>
            <div class="kpi-value">+${rev_lift:,}</div>
            <div class="kpi-note">${camp['Revenue Attributed A CAD']:,} vs ${camp['Revenue Attributed B CAD']:,}</div>
        </div>""", unsafe_allow_html=True)
    with col4:
        roi = round((camp["Revenue Attributed B CAD"] - camp["Campaign Cost CAD"] / 2) / (camp["Campaign Cost CAD"] / 2) * 100, 0)
        st.markdown(f"""<div class="kpi-card kpi-amber">
            <div class="kpi-label">Campaign ROI (B variant)</div>
            <div class="kpi-value">{roi:.0f}%</div>
            <div class="kpi-note">Campaign cost ${camp['Campaign Cost CAD']:,} total</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">A/B test performance comparison</div>', unsafe_allow_html=True)
        metrics = ["Open Rate %", "Click Rate %", "Conversion Rate %"]
        a_vals = [camp["Open Rate A %"], camp["Click Rate A %"], camp["Conversion Rate A %"]]
        b_vals = [camp["Open Rate B %"], camp["Click Rate B %"], camp["Conversion Rate B %"]]
        fig_ab = go.Figure()
        fig_ab.add_trace(go.Bar(
            name=f"A: {camp['Subject Line A'][:30]}...",
            x=metrics, y=a_vals, marker_color="#94A3B8",
        ))
        fig_ab.add_trace(go.Bar(
            name=f"B: {camp['Subject Line B'][:30]}...",
            x=metrics, y=b_vals, marker_color="#10B981",
        ))
        fig_ab.update_layout(
            barmode="group", height=320, plot_bgcolor="white",
            yaxis=dict(title="%", gridcolor="#F1F1F1", ticksuffix="%"),
            xaxis=dict(title=""),
            legend=dict(orientation="h", y=1.1, font=dict(size=10)),
            margin=dict(t=10, b=20),
        )
        st.plotly_chart(fig_ab, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Statistical significance test</div>', unsafe_allow_html=True)
        n_a = int(camp["Audience Size A"])
        n_b = int(camp["Audience Size B"])
        conv_a = round(camp["Conversion Rate A %"] / 100 * n_a)
        conv_b = round(camp["Conversion Rate B %"] / 100 * n_b)
        contingency = [[conv_a, n_a - conv_a], [conv_b, n_b - conv_b]]
        chi2_stat, p_value, dof, expected = chi2_contingency(contingency)
        significant = p_value < 0.05

        result_class = "insight" if significant else "warning"
        result_text = "Statistically significant" if significant else "Not yet significant"
        st.markdown(f"""<div class="{result_class}">
            <strong>Chi-square test result</strong><br>
            Test statistic: {chi2_stat:.2f}<br>
            p-value: {p_value:.4f}<br>
            Result: <strong>{result_text}</strong><br><br>
            {"Subject Line B is the winner. The performance difference is real and not due to chance. Safe to roll out B to the full remaining audience." if significant else "More data needed before declaring a winner. Continue the test until sample size is sufficient."}
        </div>""", unsafe_allow_html=True)

        st.markdown("**Subject lines tested**")
        st.markdown(f"**A:** {camp['Subject Line A']}")
        st.markdown(f"**B:** {camp['Subject Line B']}")
        st.markdown(f"**Target segment:** {camp['Target Segment']}")
        st.markdown(f"**Audience size:** {n_a + n_b:,} total")

    st.markdown('<div class="section-title">All campaigns overview</div>', unsafe_allow_html=True)
    camp_display = campaigns[[
        "Campaign Name","Target Segment","Audience Size A","Open Rate B %",
        "Click Rate B %","Conversion Rate B %","Revenue Attributed B CAD","Campaign Cost CAD"
    ]].copy()
    camp_display.columns = [
        "Campaign","Segment","Audience","Open Rate B","Click Rate B",
        "Conv Rate B","Revenue (B)","Cost"
    ]
    st.dataframe(camp_display, use_container_width=True, hide_index=True)

# ── TAB 5: EXECUTIVE SUMMARY ──────────────────────────────────────────────────
with tab5:
    st.markdown('<div class="section-title">Executive Summary — Marketing Performance Report</div>', unsafe_allow_html=True)
    st.markdown("**NorthPoint Financial &nbsp;|&nbsp; Q1 2024 to Q2 2025 &nbsp;|&nbsp; Prepared by Marketing Analytics**")
    st.markdown("")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""<div class="kpi-card">
            <div class="kpi-label">Total customers acquired</div>
            <div class="kpi-value">2,400</div>
            <div class="kpi-note">Across 4 channels, 18 months</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="kpi-card kpi-red">
            <div class="kpi-label">Paid social LTV/CAC</div>
            <div class="kpi-value kpi-red">0.88x</div>
            <div class="kpi-note">Below 1.0 — not sustainable</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class="kpi-card kpi-green">
            <div class="kpi-label">Referral LTV/CAC</div>
            <div class="kpi-value">2.5x</div>
            <div class="kpi-note">Strongest performing channel</div>
        </div>""", unsafe_allow_html=True)
    with col4:
        st.markdown("""<div class="kpi-card kpi-amber">
            <div class="kpi-label">Avg 90-day retention</div>
            <div class="kpi-value">26.1%</div>
            <div class="kpi-note">Below industry benchmark of 35%</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Three key findings</div>', unsafe_allow_html=True)
        st.markdown("""<div class="alert">
            <strong>Finding 1 — Paid Social is destroying value</strong><br>
            Paid Social accounts for 40% of acquisition volume but produces a 0.88 LTV-to-CAC ratio. 
            The company is spending $85.69 on average to acquire a customer worth $75 in lifetime value. 
            At current scale this channel is a net cost centre not a growth driver.
        </div>""", unsafe_allow_html=True)
        st.markdown("""<div class="insight">
            <strong>Finding 2 — Referral customers are the most valuable</strong><br>
            Referral customers have a 48.9% 90-day retention rate compared to 13.6% for Paid Social. 
            They generate more monthly revenue, stay longer, and cost less to acquire than Paid Social 
            customers. Every dollar shifted from Paid Social to referral program investment improves 
            the overall portfolio return.
        </div>""", unsafe_allow_html=True)
        st.markdown("""<div class="warning">
            <strong>Finding 3 — Retention is the core problem</strong><br>
            The average 90-day retention rate across all channels is 26.1% against an industry benchmark 
            of 35%. The product is not keeping customers engaged through the critical first 90-day window. 
            Improving retention by 10 percentage points would add more value than any acquisition 
            channel optimisation.
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-title">Two recommended actions</div>', unsafe_allow_html=True)
        st.markdown("""<div class="insight">
            <strong>Action 1 — Reallocate 30% of Paid Social budget to referral program</strong><br>
            Based on the LTV-to-CAC analysis a reallocation of $250,000 from Paid Social to a structured 
            referral incentive program would produce an estimated additional $375,000 in net customer 
            lifetime value over 12 months. This assumes referral conversion rates hold at current levels.
        </div>""", unsafe_allow_html=True)
        st.markdown("""<div class="insight">
            <strong>Action 2 — Build a 30-day onboarding activation sequence</strong><br>
            The steepest retention drop happens between activation and day 30. A structured onboarding 
            email sequence targeting newly activated customers with product education and usage prompts 
            in the first 30 days could improve day-30 retention by an estimated 8 to 12 percentage 
            points based on campaign performance data from CAM-001 and CAM-002.
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-title">Channel performance summary</div>', unsafe_allow_html=True)
        fig_ltv = px.bar(
            funnel.sort_values("LTV to CAC Ratio", ascending=True),
            x="LTV to CAC Ratio", y="Channel",
            orientation="h",
            color="LTV to CAC Ratio",
            color_continuous_scale=["#C0392B","#F39C12","#27AE60"],
            text="LTV to CAC Ratio",
        )
        fig_ltv.add_vline(x=1.0, line_dash="dash", line_color="#C0392B", annotation_text="Break-even")
        fig_ltv.update_layout(
            height=240, plot_bgcolor="white",
            xaxis=dict(title="LTV to CAC Ratio", gridcolor="#F1F1F1"),
            yaxis=dict(title=""),
            coloraxis_showscale=False,
            margin=dict(t=10, b=20),
        )
        st.plotly_chart(fig_ltv, use_container_width=True)

st.divider()
st.markdown(
    "**Data note:** All customer records are synthetic and generated for portfolio purposes. "
    "Channel characteristics, retention rates, and CAC figures are modelled on publicly available "
    "fintech industry benchmarks. NorthPoint Financial is a fictional company. "
    "Prepared by Simran Saran as part of The Case Files portfolio series."
)
