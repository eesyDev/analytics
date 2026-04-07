import streamlit as st
import pandas as pd
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
    client_name = st.text_input("Client / Site Name", value="My Site")

    with st.expander("Intent Classification"):
        brand_raw = st.text_area("Brand terms (one per line)", "")
        info_raw  = st.text_area(
            "Informational terms (one per line)",
            "how to\nwhat is\nmake money\ndepreciation\nfinancing\n"
            "how long\nhow much\ncan you\nis a\nstarting a\n"
            "clearing land\nhourly rate\nguide\ntips\nvs\nreviews",
        )
        blog_kw_raw = st.text_area(
            "URL keywords → Blog page (one per line)",
            "how-to\nwhat-is\nguide\ntips\nblog\narticle",
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
    f_prev_queries = st.file_uploader("Queries.csv (prev)",  type="csv", key="pq")
    f_prev_pages   = st.file_uploader("Pages.csv (prev)",    type="csv", key="pp")
    f_prev_chart   = st.file_uploader("Chart.csv (prev)",    type="csv", key="pch")

    st.divider()
    st.subheader("🔍 Cannibalization")
    st.caption(
        "GSC → Performance → add 'Pages' + 'Queries' dimensions → export. "
        "One row per Query+Page combination."
    )
    f_query_page = st.file_uploader("Query+Page export CSV", type="csv", key="qp")

    st.divider()
    st.subheader("🎥 Hotjar (optional)")
    f_hotjar     = st.file_uploader("Funnel export CSV",    type="csv",                key="hj")
    f_hm_home    = st.file_uploader("Homepage heatmap",     type=["png","jpg","jpeg"], key="hm1")
    f_hm_product = st.file_uploader("Product page heatmap", type=["png","jpg","jpeg"], key="hm2")
    f_hm_cart    = st.file_uploader("Cart page heatmap",    type=["png","jpg","jpeg"], key="hm3")

    st.divider()
    st.caption("Universal SEO Audit Tool · Built with Streamlit + Plotly")


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
    st.info("Or place CSV files in the `data/` directory next to app.py.")
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


# ── Cannibalization data (optional) ──────────────────────────────────────────
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


_COMMERCIAL_SIGNALS = [
    "buy", "price", "cost", "for sale", "shop", "order", "purchase",
    "quote", "dealer", "supplier", "wholesale", "oem", "cheap", "best",
    "top", "review", "vs", "compare", "compatible", "attachment",
    "kit", "part", "replace", "install", "near me", "shipping",
]

def classify_intent(q: str) -> str:
    q = str(q).lower()
    # Commercial signals take priority — even if query also contains info words
    if any(c in q for c in _COMMERCIAL_SIGNALS):
        return "Commercial / Product"
    if brand_terms and any(b in q for b in brand_terms):
        return "Brand"
    if any(i in q for i in info_terms):
        return "Informational"
    return "Commercial / Product"


def tag_page(url: str) -> str:
    u = str(url).lower()
    if blog_kws and any(k in u for k in blog_kws):
        return "Informational / Blog"
    return "Product / Category"


queries["Intent"] = queries["Query"].apply(classify_intent)
pages["Type"]     = pages["Page"].apply(tag_page)


# ── CTR benchmark & opportunity scoring ───────────────────────────────────────
# Non-brand benchmark (Backlinko / Advanced Web Ranking)
_CTR_BENCH = {
    1: 28.5, 2: 15.7, 3: 11.0, 4: 8.0, 5: 7.2,
    6: 5.1,  7: 4.0,  8: 3.2,  9: 2.8, 10: 2.5,
}
# Brand benchmark — brand queries convert clicks at much higher rate
_CTR_BENCH_BRAND = {
    1: 42.0, 2: 28.0, 3: 18.0, 4: 12.0, 5: 9.0,
    6: 6.5,  7: 5.0,  8: 4.0,  9: 3.5,  10: 3.0,
}


def expected_ctr(pos, intent: str = "") -> float:
    try:
        p = max(1, int(round(float(pos))))
    except (ValueError, TypeError):
        return 0.3
    bench = _CTR_BENCH_BRAND if intent == "Brand" else _CTR_BENCH
    if p <= 10:
        return bench[p]
    if p <= 20:
        return 1.5 if intent == "Brand" else 1.0
    return 0.5 if intent == "Brand" else 0.3


queries["Expected CTR"] = queries.apply(
    lambda r: expected_ctr(r["Position"], r["Intent"]), axis=1
)
queries["CTR Gap"]           = (queries["Expected CTR"] - queries["CTR"]).round(2)
queries["Opportunity Score"] = (
    (queries["Impressions"] * queries["CTR Gap"]) / 100
).clip(lower=0).round(1)


# ── Summary stats ─────────────────────────────────────────────────────────────
total_clicks      = int(chart["Clicks"].sum())
total_impressions = int(chart["Impressions"].sum())

imp_total    = queries["Impressions"].sum()
imp_total_s  = imp_total if imp_total > 0 else 1

weighted_ctr = (queries["CTR"] * queries["Impressions"]).sum() / imp_total_s
weighted_pos = (queries["Position"] * queries["Impressions"]).sum() / imp_total_s

zero_click_imp    = int(queries[queries["Clicks"] == 0]["Impressions"].sum())
total_opportunity = queries["Opportunity Score"].sum()

blog_clicks    = int(pages[pages["Type"] == "Informational / Blog"]["Clicks"].sum())
product_clicks = int(pages[pages["Type"] == "Product / Category"]["Clicks"].sum())
all_page_clicks = blog_clicks + product_clicks
blog_pct = 100 * blog_clicks / all_page_clicks if all_page_clicks > 0 else 0.0

intent_summary = (
    queries
    .groupby("Intent")
    .agg(Queries=("Query","count"), Clicks=("Clicks","sum"), Impressions=("Impressions","sum"))
    .reset_index()
)

# FIX: brand_pct and comm_pct from CLICKS not impressions — more meaningful
clicks_total = queries["Clicks"].sum() if queries["Clicks"].sum() > 0 else 1
brand_clicks = intent_summary.loc[intent_summary["Intent"] == "Brand",                "Clicks"].sum()
comm_clicks  = intent_summary.loc[intent_summary["Intent"] == "Commercial / Product", "Clicks"].sum()
brand_pct    = 100 * brand_clicks / clicks_total
comm_pct     = 100 * comm_clicks  / clicks_total

# For impressions-based intent gap warning (separate metric)
comm_imp_pct = 100 * intent_summary.loc[
    intent_summary["Intent"] == "Commercial / Product", "Impressions"
].sum() / imp_total_s


def device_stat(name: str, col: str):
    mask = devices["Device"].str.lower() == name.lower()
    vals = devices.loc[mask, col].values
    return float(vals[0]) if len(vals) else None


mobile_pos  = device_stat("mobile",  "Position")
desktop_pos = device_stat("desktop", "Position")

# FIX: consistent filter for position analysis
queries_ranked = queries[queries["Position"] > 0].copy()

top_opps = (
    queries[queries["Opportunity Score"] > 0]
    .sort_values("Opportunity Score", ascending=False)
    .head(25)
    [["Query","Impressions","Clicks","CTR","Position","Expected CTR","CTR Gap","Opportunity Score","Intent"]]
    .reset_index(drop=True)
)
top_opps.index += 1

date_range = (
    f"{chart['Date'].min().strftime('%b %d')} – {chart['Date'].max().strftime('%b %d, %Y')}"
    if not chart["Date"].isna().all() else "N/A"
)

top_country = countries.nlargest(1, "Clicks").iloc[0] if len(countries) > 0 else None

# ── Query length analysis ─────────────────────────────────────────────────────
queries["Word Count"] = queries["Query"].str.split().str.len()
queries["Length Group"] = pd.cut(
    queries["Word Count"],
    bins=[0, 1, 2, 3, 4, 99],
    labels=["1 word", "2 words", "3 words", "4 words", "5+ words"],
)
length_summary = (
    queries.groupby("Length Group", observed=True)
    .agg(
        Queries=("Query",       "count"),
        Impressions=("Impressions", "sum"),
        Clicks=("Clicks",      "sum"),
        Avg_Position=("Position",   "mean"),
        Avg_CTR=("CTR",        "mean"),
    )
    .reset_index()
)
length_summary["CTR"] = length_summary["Avg_CTR"].round(2)
length_summary["Position"] = length_summary["Avg_Position"].round(1)

# ── Featured snippet opportunities ────────────────────────────────────────────
# Queries ranking 2–5 with informational intent: prime candidates for answer boxes
snippet_opps = (
    queries[
        (queries["Position"] >= 2) &
        (queries["Position"] <= 5) &
        (queries["Intent"] == "Informational") &
        (queries["Impressions"] >= 10)
    ]
    .sort_values("Impressions", ascending=False)
    .head(20)
    [["Query", "Position", "Impressions", "Clicks", "CTR", "Expected CTR"]]
    .reset_index(drop=True)
)
snippet_opps.index += 1


# ── Period-over-period deltas ─────────────────────────────────────────────────
def pct_delta(curr, prev):
    if prev is None or prev == 0:
        return None, None
    val = (curr - prev) / abs(prev) * 100
    return f"{val:+.1f}%", val


prev_clicks = int(prev_chart["Clicks"].sum())       if prev_chart   is not None else None
prev_imps   = int(prev_chart["Impressions"].sum())   if prev_chart   is not None else None

prev_imp_total = prev_queries["Impressions"].sum()  if prev_queries is not None else None
prev_wctr = (
    (prev_queries["CTR"] * prev_queries["Impressions"]).sum() / prev_imp_total
    if prev_queries is not None and prev_imp_total and prev_imp_total > 0 else None
)
prev_wpos = (
    (prev_queries["Position"] * prev_queries["Impressions"]).sum() / prev_imp_total
    if prev_queries is not None and prev_imp_total and prev_imp_total > 0 else None
)

delta_clicks_str, delta_clicks_val = pct_delta(total_clicks,  prev_clicks)
delta_imps_str,   delta_imps_val   = pct_delta(total_impressions, prev_imps)
delta_ctr_str,    delta_ctr_val    = pct_delta(weighted_ctr,  prev_wctr)
# FIX: position delta — lower is better, so improvement = negative delta_val
# We flip the sign for display: if position improved (went down), show green
delta_pos_str,    delta_pos_val    = pct_delta(weighted_pos,  prev_wpos)
# positive delta_pos_val = position got worse (number went up) → red
# negative delta_pos_val = position improved (number went down) → green
pos_delta_color = "inverse"  # always inverse: lower position number = green


# ── Period comparison query movers ────────────────────────────────────────────
query_movers = page_movers = None

if prev_queries is not None and "Query" in prev_queries.columns:
    query_movers = queries[["Query","Clicks","Impressions","Position","Intent"]].merge(
        prev_queries[["Query","Clicks","Impressions","Position"]].rename(columns={
            "Clicks": "Clicks_prev", "Impressions": "Impressions_prev", "Position": "Position_prev"
        }),
        on="Query", how="outer",
    ).fillna(0)
    query_movers["Clicks_delta"] = query_movers["Clicks"] - query_movers["Clicks_prev"]
    query_movers["Imps_delta"]   = query_movers["Impressions"] - query_movers["Impressions_prev"]
    query_movers["Pos_delta"]    = query_movers["Position_prev"] - query_movers["Position"]

if prev_pages is not None and "Page" in prev_pages.columns:
    page_movers = pages[["Page","Clicks","Impressions","CTR","Type"]].merge(
        prev_pages[["Page","Clicks","Impressions","CTR"]].rename(columns={
            "Clicks": "Clicks_prev", "Impressions": "Impressions_prev", "CTR": "CTR_prev"
        }),
        on="Page", how="outer",
    ).fillna(0)
    page_movers["Clicks_delta"] = page_movers["Clicks"] - page_movers["Clicks_prev"]


# ── Cannibalization analysis ──────────────────────────────────────────────────
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

    # FIX: flatten Page_list to readable string (st.dataframe can't render lists)
    def fmt_pages(lst):
        clean = [str(p).replace("https://", "").replace("http://", "")[:60] for p in lst[:3]]
        suffix = f" +{len(lst)-3} more" if len(lst) > 3 else ""
        return " | ".join(clean) + suffix

    cannibal_issues["Competing Pages"] = cannibal_issues["Page_list"].apply(fmt_pages)


# ══════════════════════════════════════════════════════════════════════════════
# LAYOUT
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(f"## 📊 {client_name} — SEO Performance Audit")
st.markdown(
    f"**Period:** {date_range} &nbsp;|&nbsp; **Source:** Google Search Console"
    f" &nbsp;|&nbsp; **Queries analyzed:** {len(queries):,}",
    unsafe_allow_html=True,
)

# ── TL;DR Executive Card ──────────────────────────────────────────────────────
with st.expander("📋 TL;DR — Executive Summary (click to expand)", expanded=True):
    tldr_problems = []
    tldr_actions  = []

    if zero_click_imp > 0:
        tldr_problems.append(
            f"**{zero_click_imp:,} impressions** go to waste — site ranks but users don't click "
            f"(CTR below benchmark on {int((queries['Clicks']==0).sum())} queries)"
        )
        tldr_actions.append(
            f"Rewrite title tags for top {min(10, int((queries['Clicks']==0).sum()))} zero-click queries "
            f"→ est. **+{int(total_opportunity * 0.3):,} clicks/period** at zero cost"
        )

    if blog_pct > 50:
        tldr_problems.append(
            f"**{blog_pct:.0f}% of clicks** land on blog/informational pages with no purchase path"
        )
        tldr_actions.append(
            "Add product CTAs to every blog post → convert existing traffic without new content"
        )

    if mobile_pos is not None and desktop_pos is not None and (desktop_pos - mobile_pos) > 1.5:
        tldr_problems.append(
            f"Desktop ranks at **position {desktop_pos:.1f}** vs mobile **{mobile_pos:.1f}** "
            "— B2B buyers can't find the site"
        )
        tldr_actions.append(
            "Run desktop technical SEO audit (Core Web Vitals, structured data) → close position gap"
        )

    if len(snippet_opps) > 0:
        tldr_actions.append(
            f"**{len(snippet_opps)} featured snippet opportunities** identified (pos 2–5, informational) "
            "→ format as Q&A / bullet lists to capture answer boxes"
        )

    if cannibal_issues is not None and len(cannibal_issues) > 0:
        tldr_problems.append(
            f"**{len(cannibal_issues)} cannibalizing queries** — multiple pages competing, splitting authority"
        )

    col_p, col_a = st.columns(2)
    with col_p:
        st.markdown("**🔴 Top Problems**")
        for i, p in enumerate(tldr_problems[:3], 1):
            st.markdown(f"{i}. {p}")
        if not tldr_problems:
            st.markdown("No critical issues found.")
    with col_a:
        st.markdown("**✅ Priority Actions**")
        for i, a in enumerate(tldr_actions[:3], 1):
            st.markdown(f"{i}. {a}")

    if total_opportunity > 0:
        st.caption(
            f"Total estimated missed clicks this period: **~{int(total_opportunity):,}**. "
            f"Addressing top quick wins could recover **{int(total_opportunity * 0.3):,}–"
            f"{int(total_opportunity * 0.6):,} clicks** without new content or backlinks."
        )

st.divider()


# ── KPI Row ───────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📌 KPIs</div>', unsafe_allow_html=True)

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Clicks",            f"{total_clicks:,}",
          delta=delta_clicks_str,
          delta_color="normal" if (delta_clicks_val or 0) >= 0 else "inverse")
k2.metric("Total Impressions",        f"{total_impressions:,}",
          delta=delta_imps_str,
          delta_color="normal" if (delta_imps_val or 0) >= 0 else "inverse")
k3.metric("Weighted CTR",             f"{weighted_ctr:.2f}%",
          delta=delta_ctr_str,
          delta_color="normal" if (delta_ctr_val or 0) >= 0 else "inverse",
          help="Impressions-weighted CTR — more accurate than simple average")
# FIX: position — lower number = better, so we invert delta_color always
k4.metric("Weighted Avg Position",    f"{weighted_pos:.1f}",
          delta=delta_pos_str,
          delta_color=pos_delta_color,
          help="Lower = better. Green delta = position improved (number decreased).")
k5.metric("Estimated Missed Clicks",  f"~{int(total_opportunity):,}",
          help="Additional clicks if all queries reached benchmark CTR for their position")
st.divider()


# ── Traffic Trend ─────────────────────────────────────────────────────────────
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


# ── Period Comparison ─────────────────────────────────────────────────────────
if has_prev:
    st.markdown('<div class="section-header">📊 Period-over-Period Comparison</div>',
                unsafe_allow_html=True)

    if prev_chart is not None:
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
                [["Query","Clicks","Clicks_prev","Clicks_delta","Intent"]]
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
                [["Query","Clicks","Clicks_prev","Clicks_delta","Intent"]]
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
                Label=page_movers["Page"]
                .str.replace(r"https?://[^/]+", "", regex=True)
                .str[:70]
            )
            .sort_values("Clicks_delta", key=abs, ascending=False)
            .head(15)
            [["Label","Clicks","Clicks_prev","Clicks_delta","Type"]]
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

    if query_movers is not None:
        new_queries = query_movers[
            (query_movers["Clicks_prev"] == 0) & (query_movers["Clicks"] > 0)
        ].nlargest(5, "Clicks")[["Query","Clicks","Impressions","Intent"]]

        lost_queries = query_movers[
            (query_movers["Clicks"] == 0) & (query_movers["Clicks_prev"] > 0)
        ].nlargest(5, "Clicks_prev")[["Query","Clicks_prev","Intent"]]

        col_new, col_lost = st.columns(2)
        with col_new:
            if len(new_queries) > 0:
                st.markdown("**New queries this period**")
                st.dataframe(new_queries.reset_index(drop=True),
                             use_container_width=True, hide_index=True)
        with col_lost:
            if len(lost_queries) > 0:
                st.markdown("**Queries that dropped out**")
                st.dataframe(lost_queries.reset_index(drop=True),
                             use_container_width=True, hide_index=True)


# ── Critical Findings ─────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🔴 Critical Findings</div>', unsafe_allow_html=True)

findings = []

if blog_pct > 50:
    findings.append(("red",
        f"Blog / informational pages drive <strong>{blog_pct:.0f}%</strong> of clicks "
        f"but have no direct purchase intent. Only <strong>{100-blog_pct:.0f}%</strong> "
        "of clicks land on product or category pages."))

if zero_click_imp > 0:
    zero_count = int((queries["Clicks"] == 0).sum())
    findings.append(("red",
        f"<strong>{zero_click_imp:,} impressions</strong> across "
        f"<strong>{zero_count}</strong> queries received zero clicks. "
        "The site ranks — but users don't click. "
        "Title tags and meta descriptions need immediate attention."))

if brand_pct > 60:
    findings.append(("red",
        f"<strong>{brand_pct:.0f}%</strong> of clicks are branded queries. "
        "Non-brand organic traffic is critically low — almost all traffic comes "
        "from users who already know the brand."))

if mobile_pos is not None and desktop_pos is not None and (desktop_pos - mobile_pos) > 1.5:
    findings.append(("amber",
        f"Desktop ranking ({desktop_pos:.1f}) is significantly worse than "
        f"mobile ({mobile_pos:.1f}) — a gap of {desktop_pos - mobile_pos:.1f} positions. "
        "B2B buyers who research and purchase on desktop see you below competitors."))

underperformers = queries[
    (queries["Impressions"] >= 20) &
    (queries["CTR"] < queries["Expected CTR"] * 0.5)
]
if len(underperformers) > 0:
    findings.append(("amber",
        f"<strong>{len(underperformers)}</strong> queries with 20+ impressions achieve "
        "less than half the benchmark CTR for their ranking position. "
        "These pages rank well but fail to attract clicks."))

if not findings:
    findings.append(("green", "No critical issues detected based on current data."))

for severity, text in findings:
    st.markdown(f'<div class="alert-{severity}">{text}</div>', unsafe_allow_html=True)


# ── Opportunity Matrix ────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🎯 Opportunity Matrix — CTR vs Position</div>',
            unsafe_allow_html=True)
st.caption("Queries below the red benchmark line are underperforming. Size = Impressions.")

opp_df = queries[queries["Impressions"] >= 5].copy()
fig_opp = px.scatter(
    opp_df, x="Position", y="CTR",
    size="Impressions", color="Intent",
    hover_name="Query",
    hover_data={"Impressions": True, "Clicks": True, "CTR": ":.2f", "Position": ":.1f"},
    color_discrete_map={
        "Brand":                "#1565c0",
        "Informational":        "#f9a825",
        "Commercial / Product": "#388e3c",
    },
    title="Each bubble = one query (≥5 impressions) — size = impressions",
    height=480,
)
bench_x = list(range(1, 31))
bench_y = [expected_ctr(p) for p in bench_x]
fig_opp.add_trace(go.Scatter(
    x=bench_x, y=bench_y, mode="lines",
    name="Industry benchmark CTR",
    line=dict(color="#d32f2f", width=1.5, dash="dash"),
))
fig_opp.update_layout(
    xaxis_title="Avg. Position (lower = better)", yaxis_title="CTR %",
    xaxis=dict(range=[0, 31]),
    plot_bgcolor="white", paper_bgcolor="white",
)
fig_opp.update_xaxes(gridcolor="#f0f0f0")
fig_opp.update_yaxes(gridcolor="#f0f0f0")
st.plotly_chart(fig_opp, use_container_width=True)


# ── Quick Wins Table ──────────────────────────────────────────────────────────
st.markdown('<div class="section-header">💡 Prioritized Quick Wins</div>', unsafe_allow_html=True)
st.markdown("**Opportunity Score** = estimated additional clicks if CTR reaches benchmark for current position.")

if len(top_opps) > 0:
    st.dataframe(
        top_opps.style
        .background_gradient(subset=["Opportunity Score"], cmap="YlOrRd")
        .background_gradient(subset=["Impressions"],       cmap="Blues")
        .format({
            "CTR":               "{:.2f}%",
            "Expected CTR":      "{:.1f}%",
            "CTR Gap":           "{:.1f}pp",
            "Opportunity Score": "{:.1f}",
            "Position":          "{:.1f}",
        }),
        use_container_width=True, height=500,
    )
    st.markdown(
        f'<div class="alert-green">Total estimated missed clicks this period: '
        f'<strong>~{int(total_opportunity):,}</strong>. '
        f'Fixing title tags for the top 10 queries can recover a significant share at zero cost.</div>',
        unsafe_allow_html=True,
    )
else:
    st.info("No opportunity data — check that Queries.csv has Position and CTR columns.")


# ── Cannibalization ───────────────────────────────────────────────────────────
st.markdown('<div class="section-header">⚠️ Keyword Cannibalization</div>', unsafe_allow_html=True)

if cannibal_df is not None:
    st.caption("Queries where 2+ pages compete for the same keyword — Google picks one, others dilute authority.")
    if cannibal_issues is not None and len(cannibal_issues) > 0:
        c1, c2, c3 = st.columns(3)
        c1.metric("Cannibalizing queries",  len(cannibal_issues))
        c2.metric("Impressions at risk",    f"{int(cannibal_issues['Impressions'].sum()):,}")
        c3.metric("Clicks at risk",         f"{int(cannibal_issues['Clicks'].sum()):,}")

        st.markdown("**Top cannibalizing queries (by impressions)**")
        st.dataframe(
            cannibal_issues.head(20)[["Query","Pages","Impressions","Clicks","Competing Pages"]]
            .style.background_gradient(subset=["Impressions"], cmap="YlOrRd"),
            use_container_width=True, height=420,
        )
        st.markdown(
            '<div class="alert-amber"><strong>How to fix:</strong> For each group, pick one '
            "canonical page and consolidate content there. 301-redirect or noindex the weaker "
            "pages, and add internal links pointing to the canonical.</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<div class="alert-green">No cannibalization detected.</div>',
                    unsafe_allow_html=True)
else:
    st.markdown(
        '<div class="alert-blue"><strong>To detect cannibalization:</strong> In GSC → Performance, '
        "click the <em>Pages</em> tab, then add the <em>Queries</em> dimension, and export. "
        "Upload the result as \"Query+Page export CSV\" in the sidebar.</div>",
        unsafe_allow_html=True,
    )


# ── Search Intent ─────────────────────────────────────────────────────────────
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
        hole=0.45, title="Share of impressions by intent",
    )
    fig_pie.update_traces(textinfo="percent+label")
    fig_pie.update_layout(height=340, margin=dict(t=40, b=10), showlegend=False)
    st.plotly_chart(fig_pie, use_container_width=True)

with col_b:
    fig_intent_bar = px.bar(
        intent_summary, x="Intent", y=["Impressions","Clicks"],
        barmode="group",
        color_discrete_sequence=["#1565c0","#ff6b35"],
        title="Impressions vs Clicks by intent",
    )
    fig_intent_bar.update_layout(height=340, margin=dict(t=40,b=10), plot_bgcolor="white")
    st.plotly_chart(fig_intent_bar, use_container_width=True)

if comm_imp_pct < 30:
    st.markdown(
        f'<div class="alert-amber">Commercial / Product queries represent only '
        f'<strong>{comm_imp_pct:.0f}%</strong> of impressions. '
        f'The SEO strategy is optimised for awareness, not purchase intent.</div>',
        unsafe_allow_html=True,
    )


# ── Top Pages ─────────────────────────────────────────────────────────────────
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
    st.dataframe(
        pages_top[["Label","Clicks","CTR","Position"]]
        .sort_values("Clicks", ascending=False)
        .style
        .format({"CTR": "{:.2f}%", "Position": "{:.1f}"})
        .background_gradient(subset=["CTR"], cmap="RdYlGn"),
        height=560, use_container_width=True,
    )


# ── Position Distribution ─────────────────────────────────────────────────────
st.markdown('<div class="section-header">📊 Ranking Position Distribution</div>',
            unsafe_allow_html=True)

col_hist, col_tier = st.columns([2, 1])
with col_hist:
    # FIX: use queries_ranked everywhere for consistency
    fig_hist = px.histogram(
        queries_ranked[queries_ranked["Position"] <= 100],
        x="Position", nbins=20,
        color="Intent",
        color_discrete_map={
            "Brand":                "#1565c0",
            "Informational":        "#f9a825",
            "Commercial / Product": "#388e3c",
        },
        title="Distribution of ranking positions",
        barmode="stack",
    )
    fig_hist.update_layout(height=340, plot_bgcolor="white")
    fig_hist.add_vline(x=10, line_dash="dash", line_color="red",
                       annotation_text="Page 2 boundary")
    st.plotly_chart(fig_hist, use_container_width=True)

with col_tier:
    tier_data = [
        {"Tier": "Top 3",      "min": 0,   "max": 3},
        {"Tier": "Pos 4–10",   "min": 3,   "max": 10},
        {"Tier": "Pos 11–20",  "min": 10,  "max": 20},
        {"Tier": "Pos 21–100", "min": 20,  "max": 100},
        {"Tier": "Pos 100+",   "min": 100, "max": 9999},
    ]
    rows = []
    for t in tier_data:
        # FIX: use queries_ranked to match histogram
        subset = queries_ranked[
            (queries_ranked["Position"] > t["min"]) &
            (queries_ranked["Position"] <= t["max"])
        ]
        rows.append({
            "Tier":        t["Tier"],
            "Queries":     len(subset),
            "Impressions": int(subset["Impressions"].sum()),
            "Clicks":      int(subset["Clicks"].sum()),
        })
    tier_df = pd.DataFrame(rows)
    st.markdown("**Queries by position tier**")
    st.dataframe(tier_df, use_container_width=True, hide_index=True)

    p4_10_q  = tier_df[tier_df["Tier"] == "Pos 4–10"]["Queries"].values
    p11_20_q = tier_df[tier_df["Tier"] == "Pos 11–20"]["Queries"].values
    if len(p4_10_q) and len(p11_20_q) and p11_20_q[0] > p4_10_q[0]:
        st.markdown(
            f'<div class="alert-amber"><strong>{p11_20_q[0]}</strong> queries on page 2 vs '
            f'<strong>{p4_10_q[0]}</strong> on page 1. '
            "Content updates could push many to page 1.</div>",
            unsafe_allow_html=True,
        )


# ── Query Length Analysis ─────────────────────────────────────────────────────
st.markdown('<div class="section-header">🔤 Query Length Analysis (Head vs Long-Tail)</div>',
            unsafe_allow_html=True)
st.caption("Longer queries = lower volume but higher purchase intent and easier to rank for.")

col_ql1, col_ql2 = st.columns(2)

with col_ql1:
    fig_ql_imp = px.bar(
        length_summary, x="Length Group", y="Impressions",
        color="Length Group",
        color_discrete_sequence=["#d32f2f","#f9a825","#1565c0","#388e3c","#7b1fa2"],
        title="Impressions by query length",
        text="Impressions",
    )
    fig_ql_imp.update_traces(textposition="outside", showlegend=False)
    fig_ql_imp.update_layout(height=320, plot_bgcolor="white", margin=dict(t=40, b=10))
    st.plotly_chart(fig_ql_imp, use_container_width=True)

with col_ql2:
    fig_ql_ctr = px.bar(
        length_summary, x="Length Group", y=["CTR", "Position"],
        barmode="group",
        color_discrete_sequence=["#1565c0", "#ff6b35"],
        title="Avg CTR % and Position by query length",
    )
    fig_ql_ctr.update_layout(height=320, plot_bgcolor="white", margin=dict(t=40, b=10))
    st.plotly_chart(fig_ql_ctr, use_container_width=True)

# Insight: long-tail share
longtail = queries[queries["Word Count"] >= 3]
longtail_imps_pct = 100 * longtail["Impressions"].sum() / imp_total_s if imp_total_s > 0 else 0
longtail_ctr = longtail["CTR"].mean() if len(longtail) > 0 else 0
headterm_ctr = queries[queries["Word Count"] <= 2]["CTR"].mean() if len(queries[queries["Word Count"] <= 2]) > 0 else 0

if longtail_ctr > headterm_ctr:
    st.markdown(
        f'<div class="alert-green">'
        f"Long-tail queries (3+ words) make up <strong>{longtail_imps_pct:.0f}%</strong> of impressions "
        f"but convert at <strong>{longtail_ctr:.2f}% CTR</strong> vs "
        f"<strong>{headterm_ctr:.2f}%</strong> for head terms. "
        "Targeting more specific, intent-rich long-tail keywords is a high-ROI strategy."
        "</div>",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f'<div class="alert-blue">'
        f"Long-tail queries (3+ words) account for <strong>{longtail_imps_pct:.0f}%</strong> of impressions."
        "</div>",
        unsafe_allow_html=True,
    )


# ── Featured Snippet Opportunities ───────────────────────────────────────────
st.markdown('<div class="section-header">⭐ Featured Snippet Opportunities</div>',
            unsafe_allow_html=True)
st.caption(
    "Queries ranking **position 2–5** with informational intent are prime candidates for "
    "answer boxes (position 0). Structured content (H2 headers, bullet lists, Q&A schema) "
    "can jump above position 1 and drive outsized CTR."
)

if len(snippet_opps) > 0:
    col_sn1, col_sn2 = st.columns([2, 1])
    with col_sn1:
        st.dataframe(
            snippet_opps.style
            .background_gradient(subset=["Impressions"], cmap="Blues")
            .format({
                "Position":     "{:.1f}",
                "CTR":          "{:.2f}%",
                "Expected CTR": "{:.1f}%",
            }),
            use_container_width=True,
            height=420,
        )
    with col_sn2:
        st.markdown("**How to capture the snippet:**")
        st.markdown("""
1. Identify what the query is asking
2. Add a direct 40–60 word answer paragraph at the top of the page
3. Use the exact query phrase as an H2 header
4. For list queries: use `<ul>` / `<ol>` with concise items
5. For definition queries: use a bolded term + 1-sentence definition
6. Add FAQ schema markup
7. Internally link to this page with anchor text = the query
        """)
        st.markdown(
            f'<div class="alert-green">'
            f"<strong>{len(snippet_opps)}</strong> snippet opportunities found. "
            f"Top opportunity: <em>\"{snippet_opps.iloc[0]['Query']}\"</em> "
            f"— position {snippet_opps.iloc[0]['Position']:.1f}, "
            f"{int(snippet_opps.iloc[0]['Impressions']):,} impressions."
            f"</div>",
            unsafe_allow_html=True,
        )
else:
    st.markdown(
        '<div class="alert-blue">No featured snippet opportunities in current data '
        '(need queries at position 2–5 with informational intent and 10+ impressions).</div>',
        unsafe_allow_html=True,
    )


# ── Device Breakdown ──────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📱 Device Performance</div>', unsafe_allow_html=True)

col_d1, col_d2 = st.columns(2)
with col_d1:
    fig_dev = px.bar(
        devices, x="Device", y=["Clicks","Impressions"],
        barmode="group",
        color_discrete_sequence=["#1565c0","#ff6b35"],
        title="Clicks vs Impressions by device",
    )
    fig_dev.update_layout(height=320, margin=dict(t=40,b=10), plot_bgcolor="white")
    st.plotly_chart(fig_dev, use_container_width=True)

with col_d2:
    fig_pos_dev = px.bar(
        devices, x="Device", y="Position",
        color="Device",
        color_discrete_sequence=["#1565c0","#388e3c","#f9a825"],
        title="Avg. ranking position by device (lower = better)",
        text="Position",
    )
    fig_pos_dev.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig_pos_dev.update_layout(
        height=320, margin=dict(t=40,b=10),
        showlegend=False, plot_bgcolor="white",
    )
    fig_pos_dev.update_yaxes(autorange="reversed")
    st.plotly_chart(fig_pos_dev, use_container_width=True)

if mobile_pos is not None and desktop_pos is not None:
    gap = desktop_pos - mobile_pos
    if gap > 2:
        st.markdown(
            f'<div class="alert-red">Desktop position {desktop_pos:.1f} vs mobile {mobile_pos:.1f} '
            f'— gap of {gap:.1f} positions. Run a dedicated desktop technical audit: '
            'Core Web Vitals, structured data, PageSpeed.</div>',
            unsafe_allow_html=True,
        )
    elif gap > 0.5:
        st.markdown(
            f'<div class="alert-amber">Desktop ({desktop_pos:.1f}) slightly weaker than '
            f'mobile ({mobile_pos:.1f}). Monitor for widening.</div>',
            unsafe_allow_html=True,
        )


# ── Geographic ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🌍 Geographic Performance</div>', unsafe_allow_html=True)

countries_top = countries.nlargest(10, "Clicks").copy()
col_geo1, col_geo2 = st.columns([2, 1])
with col_geo1:
    fig_geo = px.bar(
        countries_top, x="Country", y="Clicks",
        color="CTR", color_continuous_scale="RdYlGn",
        title="Top 10 countries — color = CTR%", text="Clicks",
    )
    fig_geo.update_traces(textposition="outside")
    fig_geo.update_layout(height=360, margin=dict(t=40,b=10), plot_bgcolor="white")
    st.plotly_chart(fig_geo, use_container_width=True)

with col_geo2:
    st.markdown("**Country CTR breakdown**")
    st.dataframe(
        countries_top[["Country","Clicks","Impressions","CTR","Position"]]
        .style
        .format({"CTR": "{:.2f}%", "Position": "{:.1f}"})
        .background_gradient(subset=["CTR"], cmap="RdYlGn"),
        height=360, use_container_width=True,
    )

if top_country is not None and len(countries_top) > 1:
    top_clicks_sum  = countries_top["Clicks"].sum()
    top_country_pct = 100 * top_country["Clicks"] / top_clicks_sum if top_clicks_sum > 0 else 0
    others          = countries_top[countries_top["Country"] != top_country["Country"]]
    high_ctr_others = others[others["CTR"] > others["CTR"].mean()]
    if top_country_pct > 75 and len(high_ctr_others) > 0:
        names = ", ".join(high_ctr_others["Country"].tolist())
        st.markdown(
            f'<div class="alert-amber">'
            f"<strong>{top_country['Country']} drives {top_country_pct:.0f}% of clicks.</strong> "
            f"Markets with above-average CTR: <strong>{names}</strong> — "
            "geo-targeted content may unlock disproportionate growth here.</div>",
            unsafe_allow_html=True,
        )


# ── Hotjar ────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🎥 User Behavior Analysis (Hotjar)</div>',
            unsafe_allow_html=True)

if not f_hotjar and not any([f_hm_home, f_hm_product, f_hm_cart]):
    st.markdown(
        '<div class="alert-amber"><strong>Hotjar data not yet connected.</strong> '
        "GSC shows <em>who finds the site</em> — Hotjar reveals <em>why they don't convert.</em> "
        "Upload a funnel CSV and/or heatmap screenshots in the sidebar.</div>",
        unsafe_allow_html=True,
    )

if f_hotjar:
    try:
        hj_df = pd.read_csv(f_hotjar)
        if "Step" in hj_df.columns and "Users" in hj_df.columns:
            st.markdown("**Conversion Funnel**")
            fig_funnel = px.funnel(hj_df, x="Users", y="Step",
                                   title="Conversion Funnel (Hotjar)")
            fig_funnel.update_layout(height=380)
            st.plotly_chart(fig_funnel, use_container_width=True)

            first_val = hj_df["Users"].iloc[0]
            hj_display = hj_df.copy()
            hj_display["Conversion Rate"] = (hj_df["Users"] / first_val * 100).round(1).astype(str) + "%"
            hj_display["Drop-off %"]      = ((1 - hj_df["Users"] / first_val) * 100).round(1).astype(str) + "%"
            st.dataframe(hj_display, use_container_width=True, hide_index=True)

            if len(hj_df) > 1:
                diffs      = hj_df["Users"].diff().abs().fillna(0)
                worst_idx  = diffs.idxmax()
                worst_step = hj_df.loc[worst_idx, "Step"]
                worst_lost = int(diffs[worst_idx])
                st.markdown(
                    f'<div class="alert-red"><strong>Biggest drop-off:</strong> '
                    f"{worst_lost:,} users lost at <strong>{worst_step}</strong>. "
                    "Highest-priority fix in the funnel.</div>",
                    unsafe_allow_html=True,
                )
        else:
            # FIX: informative error instead of silent fallback
            st.warning(
                "Hotjar CSV uploaded but missing required columns: **Step** and **Users**. "
                "Please export the funnel report with these column headers."
            )
            st.dataframe(hj_df.head(), use_container_width=True)
    except Exception as e:
        st.error(f"Error reading Hotjar file: {e}")

heatmaps = [
    ("🔥 Homepage Heatmap",     f_hm_home,    "Focus: hero CTA, navigation, above-the-fold"),
    ("🔥 Product Page Heatmap", f_hm_product, "Focus: add-to-cart, specs, pricing"),
    ("🔥 Cart Page Heatmap",    f_hm_cart,    "Focus: checkout button, trust signals"),
]
loaded_hm      = [(l, f, c) for l, f, c in heatmaps if f]
placeholder_hm = [(l, c)    for l, f, c in heatmaps if not f]

if loaded_hm:
    st.markdown("**Heatmaps**")
    for label, f, caption in loaded_hm:
        st.markdown(f"*{label}*")
        # FIX: use_container_width replaces deprecated use_column_width
        st.image(f, use_container_width=True)
        st.caption(caption)

if placeholder_hm:
    cols = st.columns(len(placeholder_hm))
    for col, (label, caption) in zip(cols, placeholder_hm):
        col.markdown(
            f'<div class="hotjar-placeholder">'
            f'<div style="font-size:2rem">🔥</div>'
            f'<strong>{label}</strong><br><small>{caption}</small>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ── Recommendations ───────────────────────────────────────────────────────────
st.markdown('<div class="section-header">✅ Prioritized Recommendations</div>',
            unsafe_allow_html=True)

recs = []

if zero_click_imp > 0:
    recs.append(("🔴", "URGENT", "Rewrite title tags & meta descriptions for zero-click queries",
        f"{zero_click_imp:,} impressions, 0 clicks. Start with Quick Wins table top 10 — "
        "these already rank, fixing CTR costs nothing."))

if blog_pct > 50:
    recs.append(("🔴", "URGENT", "Add product CTAs to all informational / blog pages",
        f"{blog_pct:.0f}% of clicks land on blog pages with no path to purchase. "
        "Add contextually relevant product banners and internal links to every article."))

if mobile_pos is not None and desktop_pos is not None and (desktop_pos - mobile_pos) > 2:
    recs.append(("🟠", "HIGH", "Desktop SEO technical audit",
        f"Desktop ranks at {desktop_pos:.1f} vs mobile {mobile_pos:.1f}. "
        "Audit Core Web Vitals, structured data, and PageSpeed for desktop."))

recs.append(("🟠", "HIGH", "Set up Hotjar conversion funnel tracking",
    "Install: Product → Add to Cart → Checkout → Order confirmation. "
    "This identifies the single biggest conversion bottleneck."))

if comm_imp_pct < 30:
    recs.append(("🟠", "HIGH", "Create dedicated commercial landing pages",
        f"Only {comm_imp_pct:.0f}% of impressions are commercial (buyer) queries. "
        'Build pages targeting product + intent keywords ("X for sale", "X price", etc.).'))

if cannibal_issues is not None and len(cannibal_issues) > 0:
    recs.append(("🟠", "HIGH", "Fix keyword cannibalization",
        f"{len(cannibal_issues)} queries have 2+ competing pages. "
        "Consolidate to one canonical per topic, redirect the rest."))

if top_country is not None and len(countries_top) > 1:
    high_ctr_intl = countries_top[
        (countries_top["Country"] != top_country["Country"]) &
        (countries_top["CTR"] > countries_top["CTR"].mean())
    ]
    if len(high_ctr_intl) > 0:
        intl_names = ", ".join(high_ctr_intl["Country"].tolist())
        recs.append(("🟢", "LOW", "Expand into high-CTR international markets",
            f"{intl_names} show above-average CTR. "
            "Geo-targeted content or hreflang could yield disproportionate growth."))

PRIORITY_COLOR = {"URGENT": "alert-red", "HIGH": "alert-amber", "LOW": "alert-green"}
for emoji, priority, title, desc in recs:
    cls = PRIORITY_COLOR.get(priority, "alert-blue")
    st.markdown(
        f'<div class="{cls}"><strong>{emoji} {priority} — {title}</strong><br>{desc}</div>',
        unsafe_allow_html=True,
    )


# ── Export ────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">⬇️ Export</div>', unsafe_allow_html=True)

col_e1, col_e2, col_e3 = st.columns(3)
with col_e1:
    st.download_button(
        "📥 Quick Wins (CSV)",
        top_opps.to_csv(index=False).encode("utf-8"),
        "quick_wins.csv", "text/csv",
    )
with col_e2:
    recs_df = pd.DataFrame(recs, columns=["Emoji","Priority","Title","Description"])
    st.download_button(
        "📥 Recommendations (CSV)",
        recs_df.to_csv(index=False).encode("utf-8"),
        "recommendations.csv", "text/csv",
    )
with col_e3:
    full_q = queries[[
        "Query","Clicks","Impressions","CTR","Position",
        "Expected CTR","CTR Gap","Opportunity Score","Intent",
    ]].sort_values("Opportunity Score", ascending=False)
    st.download_button(
        "📥 All Queries Scored (CSV)",
        full_q.to_csv(index=False).encode("utf-8"),
        "all_queries_scored.csv", "text/csv",
    )


# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    f"<small style='color:#888'>Audit generated · {date_range} · "
    "Source: Google Search Console · Built with Streamlit + Plotly</small>",
    unsafe_allow_html=True,
)
