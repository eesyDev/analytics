import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="JMA Attachments — Site Audit",
    page_icon="🚨",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.block-container { padding-top: 2rem; padding-bottom: 2rem; }
.metric-card {
    background: #fff3cd;
    border-left: 4px solid #ff6b35;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.75rem;
}
.alert-red {
    background: #fdecea;
    border-left: 4px solid #d32f2f;
    border-radius: 6px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.6rem;
    font-size: 0.95rem;
}
.alert-amber {
    background: #fff8e1;
    border-left: 4px solid #f9a825;
    border-radius: 6px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.6rem;
    font-size: 0.95rem;
}
.alert-green {
    background: #e8f5e9;
    border-left: 4px solid #388e3c;
    border-radius: 6px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.6rem;
    font-size: 0.95rem;
}
.section-header {
    font-size: 1.1rem;
    font-weight: 600;
    color: #1a1a1a;
    margin-top: 2rem;
    margin-bottom: 0.5rem;
    border-bottom: 2px solid #ff6b35;
    padding-bottom: 0.3rem;
}
.hotjar-placeholder {
    background: #f5f5f5;
    border: 2px dashed #bbb;
    border-radius: 10px;
    padding: 2rem;
    text-align: center;
    color: #888;
    margin-top: 0.5rem;
}
</style>
""", unsafe_allow_html=True)


# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    queries   = pd.read_csv("data/Queries.csv")
    pages     = pd.read_csv("data/Pages.csv")
    devices   = pd.read_csv("data/Devices.csv")
    countries = pd.read_csv("data/Countries.csv")
    chart     = pd.read_csv("data/Chart.csv")

    # clean CTR / Position columns
    for df in [queries, pages, devices, countries]:
        df["CTR"]      = df["CTR"].str.replace("%", "").astype(float)
        df["Position"] = df["Position"].astype(float)

    chart["CTR"]  = chart["CTR"].str.replace("%", "").astype(float)
    chart["Date"] = pd.to_datetime(chart["Date"])

    queries.rename(columns={"Top queries": "Query"}, inplace=True)
    pages.rename(columns={"Top pages": "Page"}, inplace=True)

    return queries, pages, devices, countries, chart


queries, pages, devices, countries, chart = load_data()


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("## 🚨 JMA Attachments — Website Performance Audit")
st.markdown(
    "**Period:** Last 7 days &nbsp;|&nbsp; "
    "**Source:** Google Search Console &nbsp;|&nbsp; "
    "**Status:** <span style='color:red;font-weight:600'>Action Required</span>",
    unsafe_allow_html=True,
)
st.divider()


# ── KPI row ───────────────────────────────────────────────────────────────────
total_clicks      = int(chart["Clicks"].sum())
total_impressions = int(chart["Impressions"].sum())
avg_ctr           = chart["CTR"].mean()
avg_pos           = chart["Position"].mean()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Clicks (7d)",      f"{total_clicks:,}",      help="All organic clicks")
k2.metric("Total Impressions (7d)", f"{total_impressions:,}", help="Times site appeared in search")
k3.metric("Avg CTR",                f"{avg_ctr:.2f}%",        delta="-low", delta_color="inverse")
k4.metric("Avg Position",           f"{avg_pos:.1f}",         delta="page 1, but not top 3", delta_color="off")

st.divider()


# ── 1. Traffic trend ──────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📈 Traffic trend</div>', unsafe_allow_html=True)

fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
fig_trend.add_trace(
    go.Bar(x=chart["Date"], y=chart["Clicks"], name="Clicks",
           marker_color="#ff6b35", opacity=0.85),
    secondary_y=False,
)
fig_trend.add_trace(
    go.Scatter(x=chart["Date"], y=chart["Impressions"], name="Impressions",
               line=dict(color="#1565c0", width=2)),
    secondary_y=True,
)
fig_trend.update_layout(
    height=300, margin=dict(t=10, b=10),
    legend=dict(orientation="h", y=1.1),
    hovermode="x unified",
)
fig_trend.update_yaxes(title_text="Clicks",      secondary_y=False)
fig_trend.update_yaxes(title_text="Impressions", secondary_y=True)
st.plotly_chart(fig_trend, use_container_width=True)


# ── 2. Critical findings ──────────────────────────────────────────────────────
st.markdown('<div class="section-header">🔴 Critical Findings</div>', unsafe_allow_html=True)

st.markdown("""
<div class="alert-red">
<strong>Blog is stealing 70%+ of traffic — but generates zero sales.</strong><br>
Top clicked pages are informational articles: "make money with skid steer" (27 clicks, 0.72% CTR),
"skid steer depreciation" (19 clicks), "how to release hydraulic pressure" (16 clicks).
These are NOT buyers of excavator attachments.
</div>

<div class="alert-red">
<strong>Massive pool of zero-click impressions.</strong><br>
"What is a grapple" — 108 impressions, 0 clicks.
Specific product pages (rotating grapple, mini excavator bucket) — 50–94 impressions, 0 clicks.
The site is visible, but people are not clicking. Title tags are broken.
</div>

<div class="alert-red">
<strong>Brand traffic = almost everything.</strong><br>
Top queries: "jma attachments" (27 clicks), "jm attachments" (10), "jm attachments llc" (6).
Non-brand organic traffic is nearly zero — the site depends entirely on people who already know JMA.
</div>

<div class="alert-amber">
<strong>Desktop is underperforming vs mobile — a B2B red flag.</strong><br>
Mobile: 424 clicks, avg position 4.89. Desktop: 248 clicks, avg position 8.38.
B2B buyers of excavator equipment make purchasing decisions at a desk.
Poor desktop ranking means we're losing the buyers that matter most.
</div>
""", unsafe_allow_html=True)


# ── 3. Query intent breakdown ─────────────────────────────────────────────────
st.markdown('<div class="section-header">🎯 Search Intent Analysis</div>', unsafe_allow_html=True)

def classify_intent(query):
    q = str(query).lower()
    brand_terms = ["jma", "jm attachments"]
    if any(b in q for b in brand_terms):
        return "Brand"
    info_terms  = ["how to", "what is", "make money", "depreciation",
                   "financing", "how long", "how much", "can you", "is a",
                   "starting a", "clearing land", "hourly rate"]
    if any(i in q for i in info_terms):
        return "Informational (no purchase intent)"
    return "Commercial / Product"

queries["Intent"] = queries["Query"].apply(classify_intent)

intent_summary = (
    queries.groupby("Intent")
    .agg(Queries=("Query","count"), Clicks=("Clicks","sum"), Impressions=("Impressions","sum"))
    .reset_index()
)

col_a, col_b = st.columns([1, 1])

with col_a:
    fig_intent = px.pie(
        intent_summary, values="Impressions", names="Intent",
        color_discrete_sequence=["#d32f2f", "#f9a825", "#388e3c"],
        hole=0.45,
        title="Impressions by search intent",
    )
    fig_intent.update_traces(textinfo="percent+label")
    fig_intent.update_layout(height=340, margin=dict(t=40, b=10), showlegend=False)
    st.plotly_chart(fig_intent, use_container_width=True)

with col_b:
    fig_intent2 = px.bar(
        intent_summary, x="Intent", y="Clicks",
        color="Intent",
        color_discrete_sequence=["#d32f2f", "#f9a825", "#388e3c"],
        title="Clicks by search intent",
        text="Clicks",
    )
    fig_intent2.update_layout(height=340, margin=dict(t=40, b=10), showlegend=False)
    fig_intent2.update_traces(textposition="outside")
    st.plotly_chart(fig_intent2, use_container_width=True)

st.markdown("""
<div class="alert-amber">
<strong>Insight:</strong> The vast majority of impressions come from informational queries.
Commercial / product queries (actual buyers) receive almost no visibility.
The SEO strategy is attracting the wrong audience.
</div>
""", unsafe_allow_html=True)


# ── 4. Top pages ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📄 Top Pages by Clicks</div>', unsafe_allow_html=True)

pages_top = pages.nlargest(15, "Clicks").copy()
pages_top["Short"] = pages_top["Page"].str.replace("https://jmattachments.com", "", regex=False)
pages_top["Short"] = pages_top["Short"].str[:60]
pages_top["Type"]  = pages_top["Short"].apply(
    lambda x: "Blog (no purchase intent)" if any(
        k in x for k in ["make-money", "depreciation", "hydraulic-pressure",
                          "financing", "clearing-land", "put-track", "grapple",
                          "high-flow", "profitable"]
    ) else "Product / Category"
)

fig_pages = px.bar(
    pages_top, x="Clicks", y="Short", orientation="h",
    color="Type",
    color_discrete_map={
        "Blog (no purchase intent)": "#d32f2f",
        "Product / Category":        "#388e3c",
    },
    title="Top 15 pages — red = blog traffic that doesn't convert",
    text="Clicks",
    height=480,
)
fig_pages.update_layout(
    margin=dict(t=40, b=10, l=10),
    yaxis=dict(autorange="reversed"),
    legend=dict(orientation="h", y=1.08),
)
fig_pages.update_traces(textposition="outside")
st.plotly_chart(fig_pages, use_container_width=True)


# ── 5. Devices ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📱 Device Breakdown</div>', unsafe_allow_html=True)

col_d1, col_d2 = st.columns(2)

with col_d1:
    fig_dev = px.bar(
        devices, x="Device", y=["Clicks", "Impressions"],
        barmode="group",
        color_discrete_sequence=["#ff6b35", "#1565c0"],
        title="Clicks vs Impressions by device",
    )
    fig_dev.update_layout(height=320, margin=dict(t=40, b=10))
    st.plotly_chart(fig_dev, use_container_width=True)

with col_d2:
    fig_pos = px.bar(
        devices, x="Device", y="Position",
        color="Device",
        color_discrete_sequence=["#1565c0", "#ff6b35", "#388e3c"],
        title="Avg. ranking position by device (lower = better)",
        text="Position",
    )
    fig_pos.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig_pos.update_layout(height=320, margin=dict(t=40, b=10), showlegend=False)
    fig_pos.update_yaxes(autorange="reversed")
    st.plotly_chart(fig_pos, use_container_width=True)

st.markdown("""
<div class="alert-red">
<strong>Desktop ranking is 8.38 — bottom of page 1.</strong><br>
B2B procurement happens on desktop. While mobile ranks at position 4.89,
desktop buyers see JMA below 7–8 competitors. This directly impacts revenue.
</div>
""", unsafe_allow_html=True)


# ── 6. Zero-click opportunities ───────────────────────────────────────────────
st.markdown('<div class="section-header">💡 Quick Wins — High Impressions, Zero Clicks</div>', unsafe_allow_html=True)

zero_clicks = (
    queries[queries["Clicks"] == 0]
    .nlargest(20, "Impressions")
    [["Query", "Impressions", "Position"]]
    .reset_index(drop=True)
)
zero_clicks.index += 1

st.markdown("These queries are **already ranking** — fixing title/meta tags could drive clicks immediately:")
st.dataframe(zero_clicks, use_container_width=True, height=420)

st.markdown("""
<div class="alert-green">
<strong>Opportunity:</strong> "What is a grapple" — 108 impressions, position 3. 
Rewrite the meta description with a clear CTA ("Shop grapple attachments →") 
and this page alone could bring 15–25 additional clicks per week at zero extra cost.
</div>
""", unsafe_allow_html=True)


# ── 7. Countries ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🌍 Geographic Distribution</div>', unsafe_allow_html=True)

countries_top = countries.nlargest(10, "Clicks")

fig_geo = px.bar(
    countries_top, x="Country", y="Clicks",
    color="CTR",
    color_continuous_scale="RdYlGn",
    title="Top 10 countries — color = CTR%",
    text="Clicks",
)
fig_geo.update_traces(textposition="outside")
fig_geo.update_layout(height=340, margin=dict(t=40, b=10))
st.plotly_chart(fig_geo, use_container_width=True)

st.markdown("""
<div class="alert-amber">
<strong>87% of traffic is USA.</strong> Canada (40 clicks, 2.68% CTR) and UK (9 clicks) 
show healthy CTR — these markets may be worth targeting more aggressively.
</div>
""", unsafe_allow_html=True)


# ── 8. Hotjar placeholder ─────────────────────────────────────────────────────
st.markdown('<div class="section-header">🎥 User Behavior Analysis (Hotjar)</div>', unsafe_allow_html=True)

st.markdown("""
<div class="alert-amber">
<strong>Hotjar data pending.</strong> 
GSC tells us <em>who finds the site</em> — Hotjar will tell us <em>why they don't buy</em>.
Priority pages to analyze: homepage heatmap, product page recordings (quick couplers),
cart → checkout funnel drop-off.
</div>
""", unsafe_allow_html=True)

hj1, hj2, hj3 = st.columns(3)

with hj1:
    st.markdown("""
    <div class="hotjar-placeholder">
        <div style="font-size:2rem">🔥</div>
        <strong>Heatmap — Homepage</strong><br>
        <small>Upload screenshot from Hotjar</small>
    </div>
    """, unsafe_allow_html=True)

with hj2:
    st.markdown("""
    <div class="hotjar-placeholder">
        <div style="font-size:2rem">🎬</div>
        <strong>Session recordings — Cart exits</strong><br>
        <small>Filter: visited /cart/, no purchase</small>
    </div>
    """, unsafe_allow_html=True)

with hj3:
    st.markdown("""
    <div class="hotjar-placeholder">
        <div style="font-size:2rem">📊</div>
        <strong>Funnel: Product → Cart → Order</strong><br>
        <small>Where exactly do buyers drop off?</small>
    </div>
    """, unsafe_allow_html=True)


# ── 9. Recommendations ───────────────────────────────────────────────────────
st.markdown('<div class="section-header">✅ Recommended Actions (Priority Order)</div>', unsafe_allow_html=True)

actions = [
    ("🔴 URGENT",  "Fix meta titles on top product pages",
     "Pages ranking pos 3–8 with 0 clicks are losing buyers to competitors. Rewrite title tags to include product + spec + CTA. Est. impact: +30–50 clicks/week."),
    ("🔴 URGENT",  "Add CTAs from blog posts to product pages",
     "Blog drives 70% of traffic but has no path to purchase. Add relevant product banners/links to every article. Zero dev cost, high impact."),
    ("🟠 HIGH",    "Improve desktop SEO",
     "Desktop avg. position 8.38 — B2B buyers can't find JMA. Run a technical SEO audit specifically for desktop (Core Web Vitals, structured data, backlinks)."),
    ("🟠 HIGH",    "Set up Hotjar funnel tracking",
     "We don't know where buyers drop off. Install funnel: Product → Cart → Checkout. This data will identify the single biggest conversion blocker."),
    ("🟡 MEDIUM",  "Create commercial landing pages for top non-brand queries",
     '"excavator attachments", "quick coupler for excavator", "mini excavator bucket" — high volume, low CTR. Dedicated landing pages with specs, compatibility, price = buyers find JMA.'),
    ("🟢 LOW",     "Target Canada & UK more aggressively",
     "Both markets show CTR above US average. Small geo-targeted SEO effort could yield disproportionate results."),
]

for priority, title, desc in actions:
    color = {"🔴": "alert-red", "🟠": "alert-amber",
             "🟡": "alert-amber", "🟢": "alert-green"}[priority[0]]
    st.markdown(f"""
    <div class="{color}">
        <strong>{priority} — {title}</strong><br>{desc}
    </div>
    """, unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<small style='color:#888'>Audit prepared by Rano · Data source: Google Search Console (7-day window) · "
    "Next step: Add Hotjar behavioral data to complete the picture.</small>",
    unsafe_allow_html=True,
)
