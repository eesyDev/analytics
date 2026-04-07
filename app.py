import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="SEO Performance Audit",
    page_icon="📊",
    layout="wide",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.block-container { padding-top: 2rem; padding-bottom: 2rem; }
.alert-red {
    background: #fdecea; border-left: 4px solid #d32f2f;
    border-radius: 6px; padding: 0.8rem 1rem;
    margin-bottom: 0.6rem; font-size: 0.92rem;
}
.alert-amber {
    background: #fff8e1; border-left: 4px solid #f9a825;
    border-radius: 6px; padding: 0.8rem 1rem;
    margin-bottom: 0.6rem; font-size: 0.92rem;
}
.alert-green {
    background: #e8f5e9; border-left: 4px solid #388e3c;
    border-radius: 6px; padding: 0.8rem 1rem;
    margin-bottom: 0.6rem; font-size: 0.92rem;
}
.alert-blue {
    background: #e3f2fd; border-left: 4px solid #1565c0;
    border-radius: 6px; padding: 0.8rem 1rem;
    margin-bottom: 0.6rem; font-size: 0.92rem;
}
.section-header {
    font-size: 1.1rem; font-weight: 600; color: #1a1a1a;
    margin-top: 2rem; margin-bottom: 0.5rem;
    border-bottom: 2px solid #1565c0; padding-bottom: 0.3rem;
}
.hotjar-placeholder {
    background: #f5f5f5; border: 2px dashed #bbb;
    border-radius: 10px; padding: 2rem;
    text-align: center; color: #888; margin-top: 0.5rem;
}
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    client_name = st.text_input("Client / Site Name", value="JMA Attachments")

    with st.expander("Intent Classification"):
        brand_raw = st.text_area(
            "Brand terms (one per line)",
            "jma\njm attachments",
        )
        info_raw = st.text_area(
            "Informational terms (one per line)",
            "how to\nwhat is\nmake money\ndepreciation\nfinancing\n"
            "how long\nhow much\ncan you\nis a\nstarting a\n"
            "clearing land\nhourly rate\nguide\ntips\nvs\nreviews",
        )
        blog_kw_raw = st.text_area(
            "URL keywords → Informational/Blog page (one per line)",
            "make-money\ndepreciation\nhydraulic\nfinancing\n"
            "clearing-land\nhow-to\nwhat-is\nguide\ntips\nblog\narticle\n"
            "profitable\ntrack\nhigh-flow\ngrapple",
        )

    st.divider()
    st.subheader("📁 Current Period — GSC")
    st.caption("Google Search Console → Performance → Export CSV")
    f_queries   = st.file_uploader("Queries.csv",             type="csv", key="q")
    f_pages     = st.file_uploader("Pages.csv",               type="csv", key="p")
    f_devices   = st.file_uploader("Devices.csv",             type="csv", key="d")
    f_countries = st.file_uploader("Countries.csv",           type="csv", key="c")
    f_chart     = st.file_uploader("Chart.csv (time series)", type="csv", key="ch")

    st.divider()
    st.subheader("📁 Previous Period — GSC")
    st.caption("Same exports for the prior period (WoW / MoM)")
    f_prev_queries = st.file_uploader("Queries.csv (prev)",   type="csv", key="pq")
    f_prev_pages   = st.file_uploader("Pages.csv (prev)",     type="csv", key="pp")
    f_prev_chart   = st.file_uploader("Chart.csv (prev)",     type="csv", key="pch")

    st.divider()
    st.subheader("🔍 Cannibalization")
    st.caption(
        "GSC → Performance → add 'Pages' dimension → export. "
        "This gives one row per Query+Page combination."
    )
    f_query_page = st.file_uploader("Query+Page export CSV", type="csv", key="qp")

    st.divider()
    st.subheader("🎥 Hotjar (optional)")
    f_hotjar = st.file_uploader("Funnel export CSV", type="csv", key="hj")
    st.caption("Heatmap screenshots (PNG/JPG):")
    f_hm_home    = st.file_uploader("Homepage heatmap",      type=["png","jpg","jpeg"], key="hm1")
    f_hm_product = st.file_uploader("Product page heatmap",  type=["png","jpg","jpeg"], key="hm2")
    f_hm_cart    = st.file_uploader("Cart page heatmap",     type=["png","jpg","jpeg"], key="hm3")

    st.divider()
    st.caption("Built for SEO & Data Analytics teams")


# ── Data loading ──────────────────────────────────────────────────────────────
def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    if "CTR" in df.columns:
        df["CTR"] = (
            df["CTR"].astype(str)
            .str.replace("%", "", regex=False)
            .str.strip()
            .pipe(pd.to_numeric, errors="coerce")
            .fillna(0.0)
        )
    for col in ("Position", "Clicks", "Impressions"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df


def read(upload, fallback: str) -> pd.DataFrame:
    src = upload if upload else fallback
    return clean_df(pd.read_csv(src))


try:
    queries   = read(f_queries,   "data/Queries.csv")
    pages     = read(f_pages,     "data/Pages.csv")
    devices   = read(f_devices,   "data/Devices.csv")
    countries = read(f_countries, "data/Countries.csv")
    chart     = read(f_chart,     "data/Chart.csv")
except FileNotFoundError:
    st.warning("⬆️  Upload GSC CSV files in the sidebar to get started.")
    st.info("Or place CSV files in the `data/` directory.")
    st.stop()

queries.rename(columns={"Top queries": "Query"}, inplace=True, errors="ignore")
pages.rename(columns={"Top pages":    "Page"},   inplace=True, errors="ignore")
chart["Date"] = pd.to_datetime(chart["Date"], errors="coerce")

# ── Previous period (optional) ────────────────────────────────────────────────
prev_queries = prev_pages = prev_chart = None
has_prev = any([f_prev_queries, f_prev_pages, f_prev_chart])

if has_prev:
    try:
        if f_prev_queries:
            prev_queries = clean_df(pd.read_csv(f_prev_queries))
            prev_queries.rename(columns={"Top queries": "Query"}, inplace=True, errors="ignore")
        if f_prev_pages:
            prev_pages = clean_df(pd.read_csv(f_prev_pages))
            prev_pages.rename(columns={"Top pages": "Page"}, inplace=True, errors="ignore")
        if f_prev_chart:
            prev_chart = clean_df(pd.read_csv(f_prev_chart))
            prev_chart["Date"] = pd.to_datetime(prev_chart["Date"], errors="coerce")
    except Exception as e:
        st.sidebar.warning(f"Previous period load error: {e}")
        has_prev = False

# ── Query+Page cannibalization data (optional) ────────────────────────────────
cannibal_df = None
if f_query_page:
    try:
        cannibal_df = clean_df(pd.read_csv(f_query_page))
        cannibal_df.rename(columns={
            "Top queries": "Query",
            "Top pages":   "Page",
        }, inplace=True, errors="ignore")
    except Exception as e:
        st.sidebar.warning(f"Query+Page load error: {e}")


# ── Intent classification ─────────────────────────────────────────────────────
brand_terms = [t.strip().lower() for t in brand_raw.split("\n") if t.strip()]
info_terms  = [t.strip().lower() for t in info_raw.split("\n")  if t.strip()]
blog_kws    = [t.strip().lower() for t in blog_kw_raw.split("\n") if t.strip()]


def classify_intent(q: str) -> str:
    q = str(q).lower()
    if any(b in q for b in brand_terms):
        return "Brand"
    if any(i in q for i in info_terms):
        return "Informational"
    return "Commercial / Product"


def tag_page(url: str) -> str:
    u = str(url).lower()
    if any(k in u for k in blog_kws):
        return "Informational / Blog"
    return "Product / Category"


queries["Intent"] = queries["Query"].apply(classify_intent)
pages["Type"]     = pages["Page"].apply(tag_page)


# ── CTR benchmark & opportunity scoring ───────────────────────────────────────
# Source: Backlinko / Advanced Web Ranking industry averages
_CTR_BENCH = {
    1: 28.5, 2: 15.7, 3: 11.0, 4: 8.0, 5: 7.2,
    6: 5.1,  7: 4.0,  8: 3.2,  9: 2.8, 10: 2.5,
}


def expected_ctr(pos) -> float:
    try:
        p = max(1, int(round(float(pos))))
    except (ValueError, TypeError):
        return 0.3
    if p <= 10:
        return _CTR_BENCH[p]
    if p <= 20:
        return 1.0
    return 0.3


queries["Expected CTR"]     = queries["Position"].apply(expected_ctr)
queries["CTR Gap"]          = (queries["Expected CTR"] - queries["CTR"]).round(2)
queries["Opportunity Score"] = (
    (queries["Impressions"] * queries["CTR Gap"]) / 100
).clip(lower=0).round(1)


# ── Summary stats (all computed from data) ────────────────────────────────────
total_clicks      = int(chart["Clicks"].sum())
total_impressions = int(chart["Impressions"].sum())

imp_total    = queries["Impressions"].sum()
weighted_ctr = (
    (queries["CTR"] * queries["Impressions"]).sum() / imp_total
    if imp_total > 0 else 0.0
)
weighted_pos = (
    (queries["Position"] * queries["Impressions"]).sum() / imp_total
    if imp_total > 0 else 0.0
)

zero_click_imp   = int(queries[queries["Clicks"] == 0]["Impressions"].sum())
total_opportunity = queries["Opportunity Score"].sum()

blog_clicks    = int(pages[pages["Type"] == "Informational / Blog"]["Clicks"].sum())
product_clicks = int(pages[pages["Type"] == "Product / Category"]["Clicks"].sum())
all_page_clicks = blog_clicks + product_clicks
blog_pct = 100 * blog_clicks / all_page_clicks if all_page_clicks > 0 else 0.0

intent_summary = (
    queries
    .groupby("Intent")
    .agg(Queries=("Query", "count"), Clicks=("Clicks", "sum"), Impressions=("Impressions", "sum"))
    .reset_index()
)
brand_imps = intent_summary.loc[intent_summary["Intent"] == "Brand", "Impressions"].sum()
brand_pct  = 100 * brand_imps / imp_total if imp_total > 0 else 0.0

commercial_imps = intent_summary.loc[intent_summary["Intent"] == "Commercial / Product", "Impressions"].sum()
comm_pct = 100 * commercial_imps / imp_total if imp_total > 0 else 0.0

def device_pos(name: str):
    mask = devices["Device"].str.lower() == name.lower()
    vals = devices.loc[mask, "Position"].values
    return float(vals[0]) if len(vals) else None

mobile_avg  = device_pos("mobile")
desktop_avg = device_pos("desktop")

top_opps = (
    queries[queries["Opportunity Score"] > 0]
    .sort_values("Opportunity Score", ascending=False)
    .head(25)
    [["Query", "Impressions", "Clicks", "CTR", "Position", "Expected CTR", "CTR Gap", "Opportunity Score", "Intent"]]
    .reset_index(drop=True)
)
top_opps.index += 1

date_range = (
    f"{chart['Date'].min().strftime('%b %d')} – {chart['Date'].max().strftime('%b %d, %Y')}"
    if not chart["Date"].isna().all() else "N/A"
)

top_country = countries.nlargest(1, "Clicks").iloc[0] if len(countries) > 0 else None

# ── Period-over-period deltas ─────────────────────────────────────────────────
def pct_delta(curr, prev):
    """Return formatted delta string and numeric value for st.metric."""
    if prev is None or prev == 0:
        return None, None
    val = (curr - prev) / prev * 100
    return f"{val:+.1f}%", val

prev_clicks = int(prev_chart["Clicks"].sum()) if prev_chart is not None else None
prev_imps   = int(prev_chart["Impressions"].sum()) if prev_chart is not None else None

prev_imp_total = prev_queries["Impressions"].sum() if prev_queries is not None else None
prev_wctr = (
    (prev_queries["CTR"] * prev_queries["Impressions"]).sum() / prev_imp_total
    if prev_queries is not None and prev_imp_total and prev_imp_total > 0 else None
)
prev_wpos = (
    (prev_queries["Position"] * prev_queries["Impressions"]).sum() / prev_imp_total
    if prev_queries is not None and prev_imp_total and prev_imp_total > 0 else None
)

delta_clicks_str, delta_clicks_val = pct_delta(total_clicks, prev_clicks)
delta_imps_str,   _                = pct_delta(total_impressions, prev_imps)
delta_ctr_str,    delta_ctr_val    = pct_delta(weighted_ctr, prev_wctr)
delta_pos_str,    delta_pos_val    = pct_delta(weighted_pos, prev_wpos)

# ── Period comparison query movers ────────────────────────────────────────────
query_movers = None
if prev_queries is not None and "Query" in prev_queries.columns:
    merged = queries[["Query", "Clicks", "Impressions", "Position", "Intent"]].merge(
        prev_queries[["Query", "Clicks", "Impressions", "Position"]].rename(columns={
            "Clicks": "Clicks_prev", "Impressions": "Impressions_prev", "Position": "Position_prev"
        }),
        on="Query", how="outer",
    ).fillna(0)
    merged["Clicks_delta"]   = merged["Clicks"]   - merged["Clicks_prev"]
    merged["Imps_delta"]     = merged["Impressions"] - merged["Impressions_prev"]
    merged["Pos_delta"]      = merged["Position_prev"] - merged["Position"]  # positive = improved
    query_movers = merged

page_movers = None
if prev_pages is not None and "Page" in prev_pages.columns:
    pmerged = pages[["Page", "Clicks", "Impressions", "CTR", "Type"]].merge(
        prev_pages[["Page", "Clicks", "Impressions", "CTR"]].rename(columns={
            "Clicks": "Clicks_prev", "Impressions": "Impressions_prev", "CTR": "CTR_prev"
        }),
        on="Page", how="outer",
    ).fillna(0)
    pmerged["Clicks_delta"] = pmerged["Clicks"] - pmerged["Clicks_prev"]
    page_movers = pmerged

# ── Cannibalization analysis ───────────────────────────────────────────────────
cannibal_issues = None
if cannibal_df is not None and "Query" in cannibal_df.columns and "Page" in cannibal_df.columns:
    grp = (
        cannibal_df.groupby("Query")
        .agg(
            Pages=("Page", "nunique"),
            Page_list=("Page", lambda x: list(x.unique())),
            Impressions=("Impressions", "sum"),
            Clicks=("Clicks", "sum"),
        )
        .reset_index()
    )
    cannibal_issues = (
        grp[grp["Pages"] >= 2]
        .sort_values("Impressions", ascending=False)
        .reset_index(drop=True)
    )
    cannibal_issues.index += 1


# ══════════════════════════════════════════════════════════════════════════════
# LAYOUT
# ══════════════════════════════════════════════════════════════════════════════

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"## 📊 {client_name} — SEO Performance Audit")
st.markdown(
    f"**Period:** {date_range} &nbsp;|&nbsp; **Source:** Google Search Console"
    f" &nbsp;|&nbsp; **Queries analyzed:** {len(queries):,}",
    unsafe_allow_html=True,
)
st.divider()


# ── 0. KPI Row ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📌 Executive Summary</div>', unsafe_allow_html=True)

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Clicks",           f"{total_clicks:,}",
          delta=delta_clicks_str,
          delta_color="normal" if delta_clicks_val and delta_clicks_val >= 0 else "inverse")
k2.metric("Total Impressions",      f"{total_impressions:,}",
          delta=delta_imps_str)
k3.metric("Weighted CTR",           f"{weighted_ctr:.2f}%",
          delta=delta_ctr_str,
          delta_color="normal" if delta_ctr_val and delta_ctr_val >= 0 else "inverse",
          help="Impressions-weighted CTR across all queries — more accurate than simple average")
k4.metric("Weighted Avg Position",  f"{weighted_pos:.1f}",
          delta=delta_pos_str,
          delta_color="normal" if delta_pos_val and delta_pos_val >= 0 else "inverse",
          help="Impressions-weighted position. Lower = better. Delta: positive = improved (moved up).")
k5.metric("Estimated Missed Clicks", f"~{int(total_opportunity):,}",
          help="Additional clicks if all queries reached industry-average CTR for their position")
st.divider()


# ── 1. Traffic Trend ──────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📈 Traffic Trend</div>', unsafe_allow_html=True)

fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
fig_trend.add_trace(
    go.Bar(x=chart["Date"], y=chart["Clicks"], name="Clicks",
           marker_color="#1565c0", opacity=0.8),
    secondary_y=False,
)
fig_trend.add_trace(
    go.Scatter(x=chart["Date"], y=chart["Impressions"], name="Impressions",
               line=dict(color="#ff6b35", width=2), mode="lines+markers"),
    secondary_y=True,
)
fig_trend.update_layout(
    height=300, margin=dict(t=10, b=10),
    legend=dict(orientation="h", y=1.15),
    hovermode="x unified",
    plot_bgcolor="white", paper_bgcolor="white",
)
fig_trend.update_yaxes(title_text="Clicks",      secondary_y=False, gridcolor="#f0f0f0")
fig_trend.update_yaxes(title_text="Impressions", secondary_y=True)
st.plotly_chart(fig_trend, use_container_width=True)


# ── 2. Period Comparison ──────────────────────────────────────────────────────
if has_prev:
    st.markdown('<div class="section-header">📊 Period-over-Period Comparison</div>',
                unsafe_allow_html=True)

    if prev_chart is not None:
        # Overlay chart
        fig_cmp = go.Figure()
        fig_cmp.add_trace(go.Scatter(
            x=list(range(len(chart))), y=chart["Clicks"],
            name="Current period", line=dict(color="#1565c0", width=2),
            mode="lines+markers",
        ))
        fig_cmp.add_trace(go.Scatter(
            x=list(range(len(prev_chart))), y=prev_chart["Clicks"],
            name="Previous period", line=dict(color="#bdbdbd", width=2, dash="dash"),
            mode="lines+markers",
        ))
        fig_cmp.update_layout(
            height=280, margin=dict(t=10, b=10),
            hovermode="x unified", plot_bgcolor="white",
            xaxis_title="Day", yaxis_title="Clicks",
            legend=dict(orientation="h", y=1.15),
        )
        fig_cmp.update_xaxes(gridcolor="#f0f0f0")
        fig_cmp.update_yaxes(gridcolor="#f0f0f0")
        st.plotly_chart(fig_cmp, use_container_width=True)

    if query_movers is not None:
        col_gain, col_lose = st.columns(2)

        with col_gain:
            st.markdown("**Top growing queries (by clicks)**")
            gainers = (
                query_movers[query_movers["Clicks_delta"] > 0]
                .nlargest(10, "Clicks_delta")
                [["Query", "Clicks", "Clicks_prev", "Clicks_delta", "Intent"]]
                .reset_index(drop=True)
            )
            gainers.index += 1
            st.dataframe(
                gainers.style
                .background_gradient(subset=["Clicks_delta"], cmap="Greens")
                .format({"Clicks_delta": "+{:.0f}"}),
                use_container_width=True, height=340,
            )

        with col_lose:
            st.markdown("**Top declining queries (by clicks)**")
            losers = (
                query_movers[query_movers["Clicks_delta"] < 0]
                .nsmallest(10, "Clicks_delta")
                [["Query", "Clicks", "Clicks_prev", "Clicks_delta", "Intent"]]
                .reset_index(drop=True)
            )
            losers.index += 1
            st.dataframe(
                losers.style
                .background_gradient(subset=["Clicks_delta"], cmap="Reds_r")
                .format({"Clicks_delta": "{:.0f}"}),
                use_container_width=True, height=340,
            )

    if page_movers is not None:
        st.markdown("**Page movers**")
        pm_display = (
            page_movers.assign(
                Label=page_movers["Page"].str.replace(r"https?://[^/]+", "", regex=True).str[:70]
            )
            .sort_values("Clicks_delta", key=abs, ascending=False)
            .head(15)
            [["Label", "Clicks", "Clicks_prev", "Clicks_delta", "Type"]]
            .reset_index(drop=True)
        )
        pm_display.index += 1

        fig_pm = px.bar(
            pm_display, x="Clicks_delta", y="Label", orientation="h",
            color="Clicks_delta",
            color_continuous_scale="RdYlGn",
            color_continuous_midpoint=0,
            title="Click change vs previous period (green = growth, red = decline)",
            height=440,
        )
        fig_pm.update_layout(
            margin=dict(t=40, b=10, l=10),
            yaxis=dict(autorange="reversed"),
            plot_bgcolor="white",
        )
        st.plotly_chart(fig_pm, use_container_width=True)

    # Newly appeared and disappeared queries
    if query_movers is not None:
        new_queries = query_movers[
            (query_movers["Clicks_prev"] == 0) & (query_movers["Clicks"] > 0)
        ].nlargest(5, "Clicks")[["Query", "Clicks", "Impressions", "Intent"]]

        lost_queries = query_movers[
            (query_movers["Clicks"] == 0) & (query_movers["Clicks_prev"] > 0)
        ].nlargest(5, "Clicks_prev")[["Query", "Clicks_prev", "Intent"]]

        col_new, col_lost = st.columns(2)
        with col_new:
            if len(new_queries) > 0:
                st.markdown("**New queries this period**")
                st.dataframe(new_queries.reset_index(drop=True), use_container_width=True, hide_index=True)
        with col_lost:
            if len(lost_queries) > 0:
                st.markdown("**Queries that dropped out**")
                st.dataframe(lost_queries.reset_index(drop=True), use_container_width=True, hide_index=True)


# ── 3. Critical Findings (dynamic) ────────────────────────────────────────────
st.markdown('<div class="section-header">🔴 Critical Findings</div>', unsafe_allow_html=True)

findings = []

if blog_pct > 50:
    findings.append(("red",
        f"Blog / informational pages drive <strong>{blog_pct:.0f}%</strong> of clicks "
        f"but have no direct purchase intent. Only <strong>{100 - blog_pct:.0f}%</strong> "
        "of clicks land on product or category pages."))

if zero_click_imp > 0:
    zero_count = int((queries["Clicks"] == 0).sum())
    findings.append(("red",
        f"<strong>{zero_click_imp:,} impressions</strong> across <strong>{zero_count}</strong> "
        "queries received zero clicks. The site ranks — but users don't click. "
        "Title tags and meta descriptions need immediate attention."))

if brand_pct > 60:
    findings.append(("red",
        f"<strong>{brand_pct:.0f}%</strong> of impressions are branded queries. "
        "Non-brand organic visibility is critically low — almost all traffic comes from users "
        "who already know the brand."))

if mobile_avg is not None and desktop_avg is not None and (desktop_avg - mobile_avg) > 1.5:
    findings.append(("amber",
        f"Desktop ranking ({desktop_avg:.1f}) is significantly worse than mobile ({mobile_avg:.1f}) "
        f"— a gap of {desktop_avg - mobile_avg:.1f} positions. "
        "B2B buyers who research and purchase on desktop see you below competitors."))

underperformers = queries[
    (queries["Impressions"] >= 20) &
    (queries["CTR"] < queries["Expected CTR"] * 0.5)
]
if len(underperformers) > 0:
    findings.append(("amber",
        f"<strong>{len(underperformers)}</strong> queries with 20+ impressions achieve less than "
        "half the industry-benchmark CTR for their ranking position. These pages rank well but "
        "fail to attract clicks."))

if not findings:
    findings.append(("green", "No critical issues detected based on current data."))

for severity, text in findings:
    st.markdown(f'<div class="alert-{severity}">{text}</div>', unsafe_allow_html=True)


# ── 3. Opportunity Matrix ─────────────────────────────────────────────────────
st.markdown('<div class="section-header">🎯 Opportunity Matrix — CTR vs Position</div>',
            unsafe_allow_html=True)
st.caption(
    "Queries **below** the red benchmark line are underperforming for their position — "
    "these are your highest-leverage fixes. Size = Impressions."
)

opp_df = queries[queries["Impressions"] >= 5].copy()
fig_opp = px.scatter(
    opp_df,
    x="Position", y="CTR",
    size="Impressions",
    color="Intent",
    hover_name="Query",
    hover_data={"Impressions": True, "Clicks": True, "CTR": ":.2f", "Position": ":.1f"},
    color_discrete_map={
        "Brand":                 "#1565c0",
        "Informational":         "#f9a825",
        "Commercial / Product":  "#388e3c",
    },
    title="Each bubble = one query (≥5 impressions) — size = impressions",
    height=480,
)
bench_x = list(range(1, 31))
bench_y = [expected_ctr(p) for p in bench_x]
fig_opp.add_trace(go.Scatter(
    x=bench_x, y=bench_y,
    mode="lines", name="Industry benchmark CTR",
    line=dict(color="#d32f2f", width=1.5, dash="dash"),
))
fig_opp.update_layout(
    xaxis_title="Avg. Position (lower = better)",
    yaxis_title="CTR %",
    xaxis=dict(range=[0, 31]),
    plot_bgcolor="white", paper_bgcolor="white",
)
fig_opp.update_xaxes(gridcolor="#f0f0f0")
fig_opp.update_yaxes(gridcolor="#f0f0f0")
st.plotly_chart(fig_opp, use_container_width=True)


# ── 4. Quick Wins Table ───────────────────────────────────────────────────────
st.markdown('<div class="section-header">💡 Prioritized Quick Wins (by Opportunity Score)</div>',
            unsafe_allow_html=True)
st.markdown(
    "**Opportunity Score** = estimated additional clicks if CTR reaches industry benchmark "
    "for the query's current ranking position. Focus here first.",
)

if len(top_opps) > 0:
    st.dataframe(
        top_opps.style
        .background_gradient(subset=["Opportunity Score"], cmap="YlOrRd")
        .background_gradient(subset=["Impressions"],       cmap="Blues")
        .format({
            "CTR":              "{:.2f}%",
            "Expected CTR":     "{:.1f}%",
            "CTR Gap":          "{:.1f}pp",
            "Opportunity Score":"{:.1f}",
            "Position":         "{:.1f}",
        }),
        use_container_width=True,
        height=500,
    )
    st.markdown(
        f'<div class="alert-green">'
        f"<strong>Total estimated missed clicks this period:</strong> "
        f"~{int(total_opportunity):,} clicks. "
        f"Fixing title tags and meta descriptions for the top 10 queries above "
        f"can recover a significant share of these at zero incremental cost."
        f"</div>",
        unsafe_allow_html=True,
    )
else:
    st.info("No opportunity data — check that Queries.csv has Position and CTR columns.")


# ── 5. Cannibalization ────────────────────────────────────────────────────────
if cannibal_df is not None:
    st.markdown('<div class="section-header">⚠️ Keyword Cannibalization</div>',
                unsafe_allow_html=True)
    st.caption(
        "Queries where **2+ pages compete** for the same keyword. "
        "Google picks one winner — the other pages dilute authority and confuse ranking signals."
    )

    if cannibal_issues is not None and len(cannibal_issues) > 0:
        # Summary metric
        col_can1, col_can2, col_can3 = st.columns(3)
        col_can1.metric("Cannibalizing queries",   len(cannibal_issues))
        col_can2.metric("Impressions at risk",
                        f"{int(cannibal_issues['Impressions'].sum()):,}")
        col_can3.metric("Clicks at risk",
                        f"{int(cannibal_issues['Clicks'].sum()):,}")

        # Show top issues
        st.markdown("**Top cannibalizing queries (by impressions)**")
        top_can = cannibal_issues.head(20).copy()
        top_can["Competing pages"] = top_can["Page_list"].apply(
            lambda lst: "\n".join(
                str(p).replace("https://", "").replace("http://", "") for p in lst[:3]
            )
            + (f"\n+ {len(lst)-3} more" if len(lst) > 3 else "")
        )
        st.dataframe(
            top_can[["Query", "Pages", "Impressions", "Clicks", "Competing pages"]]
            .style.background_gradient(subset=["Impressions"], cmap="YlOrRd"),
            use_container_width=True,
            height=420,
        )

        st.markdown(
            '<div class="alert-amber">'
            "<strong>How to fix:</strong> For each cannibalizing group, pick one canonical page "
            "and consolidate content there. 301-redirect or noindex the weaker pages, "
            "and add internal links pointing to the canonical. "
            "This alone can improve rankings for commercial queries significantly."
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<div class="alert-green">No cannibalization detected.</div>',
                    unsafe_allow_html=True)
elif f_query_page is None:
    st.markdown('<div class="section-header">⚠️ Keyword Cannibalization</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="alert-blue">'
        "<strong>To detect cannibalization:</strong> In GSC → Performance, click the "
        "<em>Pages</em> tab, then also add the <em>Queries</em> dimension, and export. "
        "Upload the result as \"Query+Page export CSV\" in the sidebar."
        "</div>",
        unsafe_allow_html=True,
    )


# ── 6. Search Intent Analysis ─────────────────────────────────────────────────
st.markdown('<div class="section-header">🎯 Search Intent Distribution</div>', unsafe_allow_html=True)

col_a, col_b = st.columns(2)
with col_a:
    fig_pie = px.pie(
        intent_summary, values="Impressions", names="Intent",
        color="Intent",
        color_discrete_map={
            "Brand":                "#1565c0",
            "Informational":        "#f9a825",
            "Commercial / Product": "#388e3c",
        },
        hole=0.45,
        title="Share of impressions by intent",
    )
    fig_pie.update_traces(textinfo="percent+label")
    fig_pie.update_layout(height=340, margin=dict(t=40, b=10), showlegend=False)
    st.plotly_chart(fig_pie, use_container_width=True)

with col_b:
    fig_intent_bar = px.bar(
        intent_summary, x="Intent", y=["Impressions", "Clicks"],
        barmode="group",
        color_discrete_sequence=["#1565c0", "#ff6b35"],
        title="Impressions vs Clicks by intent",
    )
    fig_intent_bar.update_layout(height=340, margin=dict(t=40, b=10), plot_bgcolor="white")
    st.plotly_chart(fig_intent_bar, use_container_width=True)

if comm_pct < 30:
    st.markdown(
        f'<div class="alert-amber">'
        f"<strong>Intent gap:</strong> Commercial / Product queries — the ones buyers use — "
        f"represent only <strong>{comm_pct:.0f}%</strong> of total impressions. "
        f"The current SEO strategy is optimised for awareness, not purchase intent."
        f"</div>",
        unsafe_allow_html=True,
    )


# ── 6. Top Pages ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📄 Top Pages — Performance & Type</div>',
            unsafe_allow_html=True)

pages_top = pages.nlargest(20, "Clicks").copy()
pages_top["Label"] = (
    pages_top["Page"]
    .str.replace(r"https?://[^/]+", "", regex=True)
    .str[:70]
)

col_p1, col_p2 = st.columns([3, 2])
with col_p1:
    fig_pgs = px.bar(
        pages_top, x="Clicks", y="Label", orientation="h",
        color="Type",
        color_discrete_map={
            "Informational / Blog": "#d32f2f",
            "Product / Category":   "#388e3c",
        },
        title="Top 20 pages — red = informational/blog",
        text="Clicks", height=560,
    )
    fig_pgs.update_layout(
        margin=dict(t=40, b=10, l=10),
        yaxis=dict(autorange="reversed"),
        legend=dict(orientation="h", y=1.08),
        plot_bgcolor="white",
    )
    fig_pgs.update_traces(textposition="outside")
    st.plotly_chart(fig_pgs, use_container_width=True)

with col_p2:
    st.markdown("**CTR & Position for top pages**")
    page_table = (
        pages_top[["Label", "Clicks", "CTR", "Position"]]
        .sort_values("Clicks", ascending=False)
    )
    st.dataframe(
        page_table.style
        .format({"CTR": "{:.2f}%", "Position": "{:.1f}"})
        .background_gradient(subset=["CTR"], cmap="RdYlGn"),
        height=560, use_container_width=True,
    )


# ── 7. Position Distribution ──────────────────────────────────────────────────
st.markdown('<div class="section-header">📊 Ranking Position Distribution</div>',
            unsafe_allow_html=True)

col_hist, col_tier = st.columns([2, 1])
with col_hist:
    fig_hist = px.histogram(
        queries[queries["Position"] <= 100],
        x="Position", nbins=20,
        color="Intent",
        color_discrete_map={
            "Brand":                "#1565c0",
            "Informational":        "#f9a825",
            "Commercial / Product": "#388e3c",
        },
        title="Distribution of ranking positions (all queries)",
        barmode="stack",
    )
    fig_hist.update_layout(height=340, plot_bgcolor="white")
    fig_hist.add_vline(x=10, line_dash="dash", line_color="red",
                       annotation_text="Page 2 boundary")
    st.plotly_chart(fig_hist, use_container_width=True)

with col_tier:
    tier_data = [
        {"Tier": "Top 3 (dominant)",  "min": 0,  "max": 3},
        {"Tier": "Pos 4–10 (page 1)", "min": 3,  "max": 10},
        {"Tier": "Pos 11–20 (page 2)","min": 10, "max": 20},
        {"Tier": "Pos 21+ (buried)",  "min": 20, "max": 9999},
    ]
    rows = []
    for t in tier_data:
        subset = queries[(queries["Position"] > t["min"]) & (queries["Position"] <= t["max"])]
        rows.append({
            "Tier":        t["Tier"],
            "Queries":     len(subset),
            "Impressions": int(subset["Impressions"].sum()),
            "Clicks":      int(subset["Clicks"].sum()),
        })
    tier_df = pd.DataFrame(rows)
    st.markdown("**Queries by position tier**")
    st.dataframe(tier_df, use_container_width=True, hide_index=True)

    p4_10  = tier_df[tier_df["Tier"] == "Pos 4–10 (page 1)"]["Queries"].values[0]
    p11_20 = tier_df[tier_df["Tier"] == "Pos 11–20 (page 2)"]["Queries"].values[0]
    if p11_20 > p4_10:
        st.markdown(
            f'<div class="alert-amber">'
            f"<strong>{p11_20}</strong> queries sit on page 2 vs "
            f"<strong>{p4_10}</strong> on page 1 (pos 4–10). "
            "Targeted content updates and link building could move these to page 1."
            "</div>",
            unsafe_allow_html=True,
        )


# ── 8. Device Breakdown ───────────────────────────────────────────────────────
st.markdown('<div class="section-header">📱 Device Performance</div>', unsafe_allow_html=True)

col_d1, col_d2 = st.columns(2)
with col_d1:
    fig_dev = px.bar(
        devices, x="Device", y=["Clicks", "Impressions"],
        barmode="group",
        color_discrete_sequence=["#1565c0", "#ff6b35"],
        title="Clicks vs Impressions by device",
    )
    fig_dev.update_layout(height=320, margin=dict(t=40, b=10), plot_bgcolor="white")
    st.plotly_chart(fig_dev, use_container_width=True)

with col_d2:
    fig_pos_dev = px.bar(
        devices, x="Device", y="Position",
        color="Device",
        color_discrete_sequence=["#1565c0", "#388e3c", "#f9a825"],
        title="Avg. ranking position by device (lower = better)",
        text="Position",
    )
    fig_pos_dev.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig_pos_dev.update_layout(
        height=320, margin=dict(t=40, b=10),
        showlegend=False, plot_bgcolor="white",
    )
    fig_pos_dev.update_yaxes(autorange="reversed")
    st.plotly_chart(fig_pos_dev, use_container_width=True)

if mobile_avg is not None and desktop_avg is not None:
    gap = desktop_avg - mobile_avg
    if gap > 2:
        st.markdown(
            f'<div class="alert-red">'
            f"Desktop position {desktop_avg:.1f} vs mobile {mobile_avg:.1f} — "
            f"a gap of {gap:.1f} positions. "
            "B2B buyers who research on desktop see competitors ranked above. "
            "Run a dedicated desktop technical audit: Core Web Vitals, structured data, PageSpeed."
            "</div>",
            unsafe_allow_html=True,
        )
    elif gap > 0.5:
        st.markdown(
            f'<div class="alert-amber">'
            f"Desktop ({desktop_avg:.1f}) is slightly weaker than mobile ({mobile_avg:.1f}). "
            "Monitor and investigate if the gap widens."
            "</div>",
            unsafe_allow_html=True,
        )


# ── 9. Geographic Distribution ────────────────────────────────────────────────
st.markdown('<div class="section-header">🌍 Geographic Performance</div>', unsafe_allow_html=True)

countries_top = countries.nlargest(10, "Clicks").copy()

col_geo1, col_geo2 = st.columns([2, 1])
with col_geo1:
    fig_geo = px.bar(
        countries_top, x="Country", y="Clicks",
        color="CTR", color_continuous_scale="RdYlGn",
        title="Top 10 countries — color = CTR%",
        text="Clicks",
    )
    fig_geo.update_traces(textposition="outside")
    fig_geo.update_layout(height=360, margin=dict(t=40, b=10), plot_bgcolor="white")
    st.plotly_chart(fig_geo, use_container_width=True)

with col_geo2:
    st.markdown("**Country CTR breakdown**")
    st.dataframe(
        countries_top[["Country", "Clicks", "Impressions", "CTR", "Position"]]
        .style
        .format({"CTR": "{:.2f}%", "Position": "{:.1f}"})
        .background_gradient(subset=["CTR"], cmap="RdYlGn"),
        height=360, use_container_width=True,
    )

if top_country is not None and len(countries_top) > 1:
    top_clicks_sum  = countries_top["Clicks"].sum()
    top_country_pct = 100 * top_country["Clicks"] / top_clicks_sum if top_clicks_sum > 0 else 0
    others          = countries_top[countries_top["Country"] != top_country["Country"]]
    avg_ctr_all     = countries_top["CTR"].mean()
    high_ctr_others = others[others["CTR"] > avg_ctr_all]

    if top_country_pct > 75 and len(high_ctr_others) > 0:
        names = ", ".join(high_ctr_others["Country"].tolist())
        st.markdown(
            f'<div class="alert-amber">'
            f"<strong>{top_country['Country']} drives {top_country_pct:.0f}% of clicks.</strong> "
            f"Markets with above-average CTR: <strong>{names}</strong> — "
            "geo-targeted content or hreflang may unlock disproportionate growth here."
            "</div>",
            unsafe_allow_html=True,
        )


# ── 10. Hotjar Section ────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🎥 User Behavior Analysis (Hotjar)</div>',
            unsafe_allow_html=True)

if not f_hotjar and not any([f_hm_home, f_hm_product, f_hm_cart]):
    st.markdown(
        '<div class="alert-amber">'
        "<strong>Hotjar data not yet connected.</strong> "
        "GSC tells us <em>who finds the site and what they search for</em> — "
        "Hotjar reveals <em>why they don't convert.</em> "
        "Upload a funnel CSV and/or heatmap screenshots in the sidebar."
        "</div>",
        unsafe_allow_html=True,
    )

# Funnel chart
if f_hotjar:
    try:
        hj_df = pd.read_csv(f_hotjar)
        st.markdown("**Conversion Funnel**")
        if all(c in hj_df.columns for c in ["Step", "Users"]):
            # Compute drop-off if not present
            if "Drop-off Rate" not in hj_df.columns:
                hj_df["Drop-off Rate"] = (
                    (1 - hj_df["Users"] / hj_df["Users"].iloc[0]) * 100
                ).round(1)
            fig_funnel = px.funnel(hj_df, x="Users", y="Step",
                                   title="Conversion Funnel (Hotjar)")
            fig_funnel.update_layout(height=380)
            st.plotly_chart(fig_funnel, use_container_width=True)

            # Drop-off table
            st.markdown("**Step-by-step drop-off**")
            hj_display = hj_df.copy()
            hj_display["Conversion Rate"] = (
                (hj_df["Users"] / hj_df["Users"].iloc[0] * 100).round(1).astype(str) + "%"
            )
            hj_display["Drop-off Rate"] = hj_display["Drop-off Rate"].astype(str) + "%"
            st.dataframe(hj_display, use_container_width=True, hide_index=True)

            # Biggest drop-off callout
            if len(hj_df) > 1:
                diffs = hj_df["Users"].diff().abs().fillna(0)
                worst_idx = diffs.idxmax()
                worst_step = hj_df.loc[worst_idx, "Step"]
                worst_lost = int(diffs[worst_idx])
                st.markdown(
                    f'<div class="alert-red">'
                    f"<strong>Biggest drop-off:</strong> {worst_lost:,} users lost at "
                    f"<strong>{worst_step}</strong>. This is the highest-priority fix in the funnel."
                    f"</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.dataframe(hj_df, use_container_width=True)
    except Exception as e:
        st.error(f"Error reading Hotjar file: {e}")

# Heatmap screenshots
heatmaps = [
    ("🔥 Homepage Heatmap",     f_hm_home,    "Focus areas: hero CTA, navigation, above-the-fold content"),
    ("🔥 Product Page Heatmap", f_hm_product, "Focus areas: add-to-cart button, specs, pricing"),
    ("🔥 Cart Page Heatmap",    f_hm_cart,    "Focus areas: checkout button, trust signals, upsells"),
]

loaded_heatmaps = [(label, f, caption) for label, f, caption in heatmaps if f]
placeholder_heatmaps = [(label, caption) for label, f, caption in heatmaps if not f]

if loaded_heatmaps:
    st.markdown("**Heatmaps**")
    for label, f, caption in loaded_heatmaps:
        st.markdown(f"*{label}*")
        st.image(f, use_column_width=True)
        st.caption(caption)

if placeholder_heatmaps:
    cols = st.columns(len(placeholder_heatmaps))
    for col, (label, caption) in zip(cols, placeholder_heatmaps):
        with col:
            col.markdown(f"""<div class="hotjar-placeholder">
                <div style="font-size:2rem">🔥</div>
                <strong>{label}</strong><br>
                <small>{caption}</small>
            </div>""", unsafe_allow_html=True)


# ── 11. Prioritized Recommendations (dynamic) ─────────────────────────────────
st.markdown('<div class="section-header">✅ Prioritized Recommendations</div>',
            unsafe_allow_html=True)

recs = []

if zero_click_imp > 0:
    recs.append(("🔴", "URGENT", "Rewrite title tags & meta descriptions for zero-click queries",
        f"{zero_click_imp:,} impressions received 0 clicks. "
        "Start with the top 10 rows in the Quick Wins table — "
        "these queries already rank, fixing CTR costs nothing."))

if blog_pct > 50:
    recs.append(("🔴", "URGENT", "Add product CTAs to all informational / blog pages",
        f"{blog_pct:.0f}% of clicks land on blog pages with no path to purchase. "
        "Add contextually relevant product banners, internal links, and CTAs to every article."))

if mobile_avg is not None and desktop_avg is not None and (desktop_avg - mobile_avg) > 2:
    recs.append(("🟠", "HIGH", "Desktop SEO technical audit",
        f"Desktop ranks at position {desktop_avg:.1f} vs mobile {mobile_avg:.1f}. "
        "Audit Core Web Vitals, structured data, and PageSpeed for desktop specifically."))

recs.append(("🟠", "HIGH", "Set up Hotjar conversion funnel tracking",
    "Install: Product page → Add to Cart → Checkout → Order confirmation. "
    "This will identify the single biggest conversion bottleneck."))

if comm_pct < 30:
    recs.append(("🟠", "HIGH", "Create dedicated commercial landing pages",
        f"Only {comm_pct:.0f}% of impressions are commercial (buyer) queries. "
        "Build dedicated pages targeting product + intent keywords "
        '("excavator bucket for sale", "quick coupler price", etc.).'))

if top_country is not None and len(countries_top) > 1:
    high_ctr_intl = countries_top[
        (countries_top["Country"] != top_country["Country"]) &
        (countries_top["CTR"] > countries_top["CTR"].mean())
    ]
    if len(high_ctr_intl) > 0:
        intl_names = ", ".join(high_ctr_intl["Country"].tolist())
        recs.append(("🟢", "LOW", "Expand into high-CTR international markets",
            f"{intl_names} show above-average CTR. "
            "Geo-targeted content or hreflang implementation could yield "
            "disproportionate growth with limited effort."))

PRIORITY_COLOR = {
    "URGENT": "alert-red",
    "HIGH":   "alert-amber",
    "MEDIUM": "alert-amber",
    "LOW":    "alert-green",
}
for emoji, priority, title, desc in recs:
    cls = PRIORITY_COLOR.get(priority, "alert-blue")
    st.markdown(
        f'<div class="{cls}"><strong>{emoji} {priority} — {title}</strong><br>{desc}</div>',
        unsafe_allow_html=True,
    )


# ── 12. Export ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">⬇️ Export</div>', unsafe_allow_html=True)

col_e1, col_e2, col_e3 = st.columns(3)

with col_e1:
    st.download_button(
        "📥 Quick Wins (CSV)",
        top_opps.to_csv(index=False).encode("utf-8"),
        "quick_wins.csv", "text/csv",
    )

with col_e2:
    recs_df = pd.DataFrame(recs, columns=["Emoji", "Priority", "Title", "Description"])
    st.download_button(
        "📥 Recommendations (CSV)",
        recs_df.to_csv(index=False).encode("utf-8"),
        "recommendations.csv", "text/csv",
    )

with col_e3:
    full_queries = queries[[
        "Query", "Clicks", "Impressions", "CTR", "Position",
        "Expected CTR", "CTR Gap", "Opportunity Score", "Intent",
    ]].sort_values("Opportunity Score", ascending=False)
    st.download_button(
        "📥 All Queries with Scores (CSV)",
        full_queries.to_csv(index=False).encode("utf-8"),
        "all_queries_scored.csv", "text/csv",
    )


# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    f"<small style='color:#888'>Audit generated · {date_range} · "
    "Source: Google Search Console · "
    "Built with Streamlit + Plotly</small>",
    unsafe_allow_html=True,
)
